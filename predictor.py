
import joblib
import pandas as pd

from data_loader import load_dengue_data, get_city_data, get_risk_level


# Load the trained model
saved_model = joblib.load("model/dengue_model.pkl")
model = saved_model["model"]
features = saved_model["features"]


def predict_next_week(city):
    # Load weekly city data
    df = load_dengue_data()
    weekly = get_city_data(df)

    # Select the requested city
    city_data = weekly[weekly["city"] == city].copy()
    city_data = city_data.sort_values("date")

    if len(city_data) < 5:
        return None

    # Get the latest available week
    latest = city_data.iloc[-1]

    # Prepare prediction inputs
    input_data = {
        "rainfall_mm": latest["rainfall_mm"],
        "avg_temp_c": latest["avg_temp_c"],
        "relative_humidity_pct": latest["relative_humidity_pct"],
        "dengue_cases": latest["dengue_cases"],
    }

    # Add previous 4 weeks of rainfall and dengue cases
    for lag in range(1, 5):
        input_data[f"rainfall_lag_{lag}"] = city_data.iloc[-lag - 1]["rainfall_mm"]
        input_data[f"cases_lag_{lag}"] = city_data.iloc[-lag - 1]["dengue_cases"]

    # Arrange inputs in the same order used during training
    input_df = pd.DataFrame([input_data])[features]

    # Predict next week's dengue cases
    prediction = model.predict(input_df)[0]

    return {
        "city": city,
        "last_recorded_week": latest["date"],
        "predicted_cases": max(0, round(prediction)),
        "risk_level": get_risk_level(city_data, max(0, round(prediction))),
        "latest_cases": int(latest["dengue_cases"]),
        "rainfall_mm": round(float(latest["rainfall_mm"]), 2),
        "temperature": round(float(latest["avg_temp_c"]), 2),
        "humidity": round(float(latest["relative_humidity_pct"]), 2),
    }
