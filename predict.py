from pathlib import Path
import joblib
import numpy as np
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


def get_available_wards() -> list[str]:
    df = pd.read_csv(DATA_PATH)
    if "ward_id" not in df.columns:
        return []
    return sorted(df["ward_id"].dropna().astype(str).str.strip().unique().tolist())


def _align_features(row_df: pd.DataFrame, model, feature_cols) -> pd.DataFrame:
    if feature_cols:
        for col in feature_cols:
            if col not in row_df.columns:
                row_df[col] = 0.0
        X_input = row_df[feature_cols].copy()
    elif hasattr(model, "feature_names_in_"):
        expected_cols = list(model.feature_names_in_)
        for col in expected_cols:
            if col not in row_df.columns:
                row_df[col] = 0.0
        X_input = row_df[expected_cols].copy()
    else:
        drop_cols = [c for c in ["dengue_cases", "date", "city", "ward_id"] if c in row_df.columns]
        X_input = row_df.drop(columns=drop_cols, errors="ignore").copy()

    for col in X_input.columns:
        X_input[col] = pd.to_numeric(X_input[col], errors="coerce").fillna(0.0)
    return X_input


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"], errors="coerce")
        sort_cols = [c for c in ["ward_id", "date"] if c in data.columns]
        data = data.sort_values(sort_cols).reset_index(drop=True)

    lag_targets = ["rainfall_mm", "avg_temp_c", "relative_humidity_pct"]
    for col in lag_targets:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
            for weeks in (1, 2, 3, 4):
                lag_col = f"{col}_lag_{weeks}w"
                group_series = data.groupby("ward_id")[col] if "ward_id" in data.columns else data[col]
                data[lag_col] = group_series.shift(weeks * 7).bfill()

    alias_map = {
        "rain_lag_1w": "rainfall_mm_lag_1w",
        "rain_lag_2w": "rainfall_mm_lag_2w",
        "rain_lag_3w": "rainfall_mm_lag_3w",
        "rain_lag_4w": "rainfall_mm_lag_4w",
        "temp_lag_1w": "avg_temp_c_lag_1w",
        "temp_lag_2w": "avg_temp_c_lag_2w",
        "humidity_lag_1w": "relative_humidity_pct_lag_1w",
        "humidity_lag_2w": "relative_humidity_pct_lag_2w",
        "humidity_lag_3w": "relative_humidity_pct_lag_3w",
        "humidity_lag_4w": "relative_humidity_pct_lag_4w",
    }
    for target_col, source_col in alias_map.items():
        if source_col in data.columns:
            data[target_col] = data[source_col]

    if "water_logging_risk_index" in data.columns:
        rain_3w = data["rain_lag_3w"] if "rain_lag_3w" in data.columns else data.get("rainfall_mm", 0.0)
        rain_now = data["rainfall_mm"] if "rainfall_mm" in data.columns else 0.0
        data["water_logging_risk_index"] = (
            0.6 * pd.to_numeric(rain_3w, errors="coerce").fillna(0.0)
            + 0.4 * pd.to_numeric(rain_now, errors="coerce").fillna(0.0)
        )

    return data


def _load_bundle():
    bundle = joblib.load(MODEL_PATH)
    if isinstance(bundle, dict) and "model" in bundle:
        model = bundle["model"]
        feature_cols = bundle.get("features") or bundle.get("feature_cols")
    else:
        model = bundle
        feature_cols = None
    return model, feature_cols


def compute_weather_suitability(
    rainfall_mm: float,
    relative_humidity_pct: float,
    avg_temp_c: float,
) -> float:
    rain_val = max(0.0, float(rainfall_mm))
    hum_val = max(0.0, min(100.0, float(relative_humidity_pct)))
    temp_val = float(avg_temp_c)

    # Rainfall: 0 mm -> 0.0, >= 35 mm -> 1.0
    rain_score = float(np.clip(rain_val / 35.0, 0.0, 1.0))

    # Humidity: <= 45% -> 0.0, >= 85% -> 1.0
    hum_score = float(np.clip((hum_val - 45.0) / 40.0, 0.0, 1.0))

    # Temperature: peak suitability around 24°C–32°C; drops off outside
    if 24.0 <= temp_val <= 32.0:
        temp_score = 1.0
    else:
        dist = min(abs(temp_val - 24.0), abs(temp_val - 32.0))
        temp_score = float(np.clip(1.0 - (dist / 10.0), 0.0, 1.0))

    suitability = (0.40 * rain_score) + (0.35 * hum_score) + (0.25 * temp_score)
    return float(np.clip(suitability, 0.0, 1.0))


def predict_for_ward(ward_id: str, date_str: str | None = None) -> dict:
    model, feature_cols = _load_bundle()
    raw_df = pd.read_csv(DATA_PATH)
    prepared_df = build_features(raw_df)

    ward_rows = prepared_df[prepared_df["ward_id"].astype(str).str.strip() == str(ward_id).strip()]
    if ward_rows.empty:
        raise ValueError(f"No rows found for ward_id: {ward_id}")

    if date_str and "date" in ward_rows.columns:
        target_date = pd.to_datetime(date_str, errors="coerce")
        matched = ward_rows[ward_rows["date"] == target_date]
        row_df = matched.tail(1).copy() if not matched.empty else ward_rows.tail(1).copy()
    else:
        row_df = ward_rows.tail(1).copy()

    X_input = _align_features(row_df, model, feature_cols)
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


def get_ward_baseline(ward_id: str, date_str: str | None = None) -> dict:
    base_pred = predict_for_ward(ward_id, date_str=date_str)
    df = pd.read_csv(DATA_PATH)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    ward_df = df[df["ward_id"].astype(str).str.strip() == str(ward_id).strip()].sort_values("date")
    if ward_df.empty:
        raise ValueError(f"No rows found for ward_id: {ward_id}")

    if date_str and "date" in ward_df.columns:
        matched = ward_df[ward_df["date"].dt.strftime("%Y-%m-%d") == str(date_str)]
        if not matched.empty:
            ward_df = matched

    row = ward_df.tail(1).iloc[0].to_dict()

    def _safe_mean(col_name: str, fallback: float) -> float:
        if col_name not in ward_df.columns:
            return fallback
        val = pd.to_numeric(ward_df[col_name], errors="coerce").mean()
        return float(val) if pd.notna(val) else fallback

    hist_avg = {
        "rainfall_mm": _safe_mean("rainfall_mm", 0.0),
        "relative_humidity_pct": _safe_mean("relative_humidity_pct", 75.0),
        "avg_temp_c": _safe_mean("avg_temp_c", 28.0),
    }
    return {"row": row, "hist_avg": hist_avg, "base_pred": base_pred}


def predict_with_weather(
    ward_id: str,
    rainfall_mm: float,
    relative_humidity_pct: float,
    avg_temp_c: float,
    date_str: str | None = None,
    window_days: int = 28,
) -> dict:
    df = pd.read_csv(DATA_PATH)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values(["ward_id", "date"]).reset_index(drop=True)

    mask = df["ward_id"].astype(str).str.strip() == str(ward_id).strip()
    if date_str and "date" in df.columns:
        date_mask = mask & (df["date"].dt.strftime("%Y-%m-%d") == str(date_str))
        if date_mask.any():
            mask = date_mask

    target_indices = df[mask].index
    if len(target_indices) == 0:
        raise ValueError(f"No rows found for ward_id: {ward_id}")

    recent_idx = target_indices[-max(1, int(window_days)):]
    df.loc[recent_idx, "rainfall_mm"] = float(rainfall_mm)
    df.loc[recent_idx, "relative_humidity_pct"] = float(relative_humidity_pct)
    df.loc[recent_idx, "avg_temp_c"] = float(avg_temp_c)

    feat_df = build_features(df)
    last_idx = target_indices[-1]
    row_df = feat_df.loc[[last_idx]].copy()

    model, feature_cols = _load_bundle()
    X_input = _align_features(row_df, model, feature_cols)
    raw_model_cases = max(0.0, float(model.predict(X_input)[0]))

    suitability = compute_weather_suitability(
        rainfall_mm=rainfall_mm,
        relative_humidity_pct=relative_humidity_pct,
        avg_temp_c=avg_temp_c,
    )

    # Weather suitability scales the baseline so dry/cold/low-humidity conditions drop risk and cases,
    # while high rain/humidity/warmth amplifies both model cases and infestation probability.
    weather_scale = 0.08 + (0.92 * suitability)
    weather_cases = suitability * 6.5
    effective_cases = round(max(0.0, (0.50 * raw_model_cases * weather_scale) + (0.50 * weather_cases)), 2)

    case_norm = float(np.clip(effective_cases / 6.0, 0.0, 1.0))
    infestation_prob = round(
        float(np.clip(((0.65 * suitability) + (0.35 * case_norm)) * 100.0, 2.0, 99.0)),
        1,
    )
    risk_tier = get_risk_tier(effective_cases)

    return {
        "predicted_cases": effective_cases,
        "raw_model_cases": round(raw_model_cases, 2),
        "weather_suitability": round(suitability, 3),
        "infestation_prob": infestation_prob,
        "risk_tier": risk_tier,
    }


if __name__ == "__main__":
    sample_df = pd.read_csv(DATA_PATH)
    sample_ward = sample_df["ward_id"].iloc[0] if "ward_id" in sample_df.columns else "CCC_Ward_01"
    result = predict_for_ward(sample_ward)
    print(result)
