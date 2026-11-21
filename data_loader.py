
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
