from pathlib import Path
import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "dengue_model.joblib"
DATA_PATH = BASE_DIR / "data" / "dengue_data.csv"


def get_risk_tier(predicted_cases: float) -> str:
    if predicted_cases < 1.0:
        return "Low"
    elif predicted_cases < 3.0:
        return "Medium"
    elif predicted_cases < 6.0:
        return "High"
    return "Critical"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"], errors="coerce")
        sort_cols = [c for c in ["ward_id", "date"] if c in data.columns]
        data = data.sort_values(sort_cols).reset_index(drop=True)

    # Create weekly lag features if not already present in the CSV
    lag_targets = ["rainfall_mm", "avg_temp_c", "relative_humidity_pct"]
    for col in lag_targets:
        if col in data.columns:
            for weeks in (1, 2, 3, 4):
                lag_col = f"{col}_lag_{weeks}w"
                if lag_col not in data.columns:
                    group_series = data.groupby("ward_id")[col] if "ward_id" in data.columns else data[col]
                    data[lag_col] = group_series.shift(weeks * 7).bfill()

    return data


def predict_for_ward(ward_id: str, date_str: str | None = None) -> dict:
    model = joblib.load(MODEL_PATH)
    raw_df = pd.read_csv(DATA_PATH)
    prepared_df = build_features(raw_df)

    ward_rows = prepared_df[prepared_df["ward_id"] == ward_id]
    if ward_rows.empty:
        raise ValueError(f"No rows found for ward_id: {ward_id}")

    if date_str and "date" in ward_rows.columns:
        target_date = pd.to_datetime(date_str, errors="coerce")
        matched = ward_rows[ward_rows["date"] == target_date]
        row_df = matched.tail(1) if not matched.empty else ward_rows.tail(1)
    else:
        row_df = ward_rows.tail(1)

    # Match the exact input columns the trained model expects, if recorded
    if hasattr(model, "feature_names_in_"):
        expected_cols = list(model.feature_names_in_)
        for col in expected_cols:
            if col not in row_df.columns:
                row_df[col] = 0
        X_input = row_df[expected_cols]
    else:
        drop_cols = [c for c in ["dengue_cases", "date", "city", "ward_id"] if c in row_df.columns]
        X_input = row_df.drop(columns=drop_cols, errors="ignore")

    pred_value = float(model.predict(X_input)[0])
    predicted_cases = max(0.0, round(pred_value, 2))
    risk_tier = get_risk_tier(predicted_cases)

    top_drivers = []
    if hasattr(model, "feature_importances_"):
        importances = pd.Series(model.feature_importances_, index=X_input.columns)
        top_series = importances.sort_values(ascending=False).head(5)
        top_drivers = [
            {"feature": feat, "importance": round(float(score), 4)}
            for feat, score in top_series.items()
        ]

    actual_date = (
        str(row_df["date"].iloc[0].date())
        if "date" in row_df.columns and pd.notna(row_df["date"].iloc[0])
        else "N/A"
    )

    return {
        "ward_id": ward_id,
        "date": actual_date,
        "predicted_cases": predicted_cases,
        "risk_tier": risk_tier,
        "top_drivers": top_drivers,
    }


if __name__ == "__main__":
    sample_df = pd.read_csv(DATA_PATH)
    sample_ward = sample_df["ward_id"].iloc[0] if "ward_id" in sample_df.columns else "CCC_Ward_01"

    result = predict_for_ward(sample_ward)
    print(f"Ward:            {result['ward_id']}")
    print(f"Date:            {result['date']}")
    print(f"Predicted Cases: {result['predicted_cases']}")
    print(f"Risk Tier:       {result['risk_tier']}")
    print("Top Drivers:")
    for item in result["top_drivers"]:
        print(f"  - {item['feature']}: {item['importance']}")