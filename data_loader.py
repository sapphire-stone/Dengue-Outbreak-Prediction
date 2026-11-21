
import pandas as pd

DATA_PATH = "data/dengue_dataset.csv"


def load_dengue_data():
    df = pd.read_csv(DATA_PATH)

    df["date"] = pd.to_datetime(df["date"])

    return df


def get_city_data(df):
    city_data = (
        df.groupby(["city", "date"])
        .agg({
            "dengue_cases": "sum",
            "rainfall_mm": "mean",
            "avg_temp_c": "mean",
            "relative_humidity_pct": "mean"
        })
        .reset_index()
        .sort_values(["city", "date"])
    )

    return city_data


def get_latest_city_summary(city_data, city):
    city_records = city_data[city_data["city"] == city]

    if city_records.empty:
        return None

    return city_records.iloc[-1].to_dict()

def get_risk_level(city_data, predicted_cases):
    # Calculate historical dengue case thresholds
    low_limit = city_data["dengue_cases"].quantile(0.25)
    moderate_limit = city_data["dengue_cases"].quantile(0.50)
    high_limit = city_data["dengue_cases"].quantile(0.75)

    if predicted_cases <= low_limit:
        return "Low"
    elif predicted_cases <= moderate_limit:
        return "Moderate"
    elif predicted_cases <= high_limit:
        return "High"
    else:
        return "Critical"
