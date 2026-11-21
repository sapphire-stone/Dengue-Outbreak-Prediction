
import os
import sys
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Allow importing data_loader.py from the project folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_dengue_data, get_city_data


# 1. Load and prepare weekly city data
df = load_dengue_data()
weekly = get_city_data(df)

weekly = weekly.sort_values(["city", "date"]).copy()


# 2. Create historical features
for lag in range(1, 5):
    weekly[f"rainfall_lag_{lag}"] = (
        weekly.groupby("city")["rainfall_mm"].shift(lag)
    )
    weekly[f"cases_lag_{lag}"] = (
        weekly.groupby("city")["dengue_cases"].shift(lag)
    )

# Predict dengue cases for the following week
weekly["target_next_week"] = (
    weekly.groupby("city")["dengue_cases"].shift(-1)
)

weekly = weekly.dropna().copy()


# 3. Select model features
features = [
    "rainfall_mm",
    "avg_temp_c",
    "relative_humidity_pct",
    "dengue_cases",
    "rainfall_lag_1",
    "rainfall_lag_2",
    "rainfall_lag_3",
    "rainfall_lag_4",
    "cases_lag_1",
    "cases_lag_2",
    "cases_lag_3",
    "cases_lag_4",
]

X = weekly[features]
y = weekly["target_next_week"]


# 4. Split by time (train through 2024, test on 2025)
train = weekly[weekly["date"].dt.year <= 2024]
test = weekly[weekly["date"].dt.year == 2025]

X_train = train[features]
y_train = train["target_next_week"]

X_test = test[features]
y_test = test["target_next_week"]

if train.empty or test.empty:
    raise ValueError("Training or testing data is empty. Check the dataset dates.")


# 5. Train the model
model = RandomForestRegressor(
    n_estimators=200,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# 6. Evaluate the model
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5
r2 = r2_score(y_test, predictions)

print("MODEL EVALUATION")
print("----------------")
print(f"Training records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R2 Score: {r2:.3f}")


# 7. Save the trained model and feature names
os.makedirs("model", exist_ok=True)

joblib.dump(
    {"model": model, "features": features},
    "model/dengue_model.pkl"
)

print("\nModel saved successfully: model/dengue_model.pkl")
