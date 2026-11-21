import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# 1. Load dataset
csv_path = "data/dengue_data.csv"
df = pd.read_csv(csv_path)

# 2. Sort properly by ward and date
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["ward_id", "date"]).reset_index(drop=True)

# 3. Create 1 to 4 week lags per ward (2-4 week early warning window)
for lag in [1, 2, 3, 4]:
    df[f"rain_lag_{lag}w"] = df.groupby("ward_id")["rainfall_mm"].shift(lag)
    df[f"temp_lag_{lag}w"] = df.groupby("ward_id")["avg_temp_c"].shift(lag)
    df[f"humidity_lag_{lag}w"] = df.groupby("ward_id")["relative_humidity_pct"].shift(lag)

# Drop rows where lag history isn't available yet
df_model = df.dropna().copy()

features = [
    "population_density_sqkm",
    "water_logging_risk_index",
    "sanitation_score",
    "avg_temp_c",
    "rainfall_mm",
    "relative_humidity_pct",
    "rain_lag_1w",
    "rain_lag_2w",
    "rain_lag_3w",
    "rain_lag_4w",
    "temp_lag_1w",
    "temp_lag_2w",
    "humidity_lag_1w",
    "humidity_lag_2w",
]
target = "dengue_cases"

# 4. Chronological (time-based) train/test split: first 80% of dates to train, last 20% to test
cutoff_date = df_model["date"].quantile(0.8)
train_df = df_model[df_model["date"] <= cutoff_date]
test_df = df_model[df_model["date"] > cutoff_date]

X_train, y_train = train_df[features], train_df[target]
X_test, y_test = test_df[features], test_df[target]

# 5. Train a simple, fast model
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)
print(f"Test MAE (average case error): {mae:.2f}")

# 6. Save model and feature list for the dashboard
os.makedirs("models", exist_ok=True)
joblib.dump({"model": model, "features": features, "cutoff_date": cutoff_date}, "models/dengue_model.joblib")
print("Saved model to models/dengue_model.joblib")