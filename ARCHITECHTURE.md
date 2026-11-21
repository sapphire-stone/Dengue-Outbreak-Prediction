# 🏗️ System Architecture — Dengue Outbreak Prediction

## 1. High-Level Overview

The application uses a lightweight, local-first machine learning architecture designed for ward-level dengue outbreak risk estimation and historical comparison:

```text
+-------------------------------------------------------+
|                   Streamlit UI (app.py)               |
|  - Ward selection & historical date/multi-day views   |
|  - Risk tier badge, predicted cases, top drivers      |
+---------------------------+---------------------------+
                            |
                            v
+-------------------------------------------------------+
|             Prediction Pipeline (predict.py)          |
|  - get_available_wards()                              |
|  - build_features() [sort, lags, alias_map]           |
|  - predict_for_ward() / get_ward_history()            |
+-----------+-------------------------------+-----------+
            |                               |
            v                               v
+-----------------------+       +-----------------------+
|  data/dengue_data.csv |       | models/                 |
|  - Ward & date rows   |       |   dengue_model.joblib |
|  - Weather & lags     |       | - Trained estimator   |
|  - Case history       |       | - Expected features   |
+-----------------------+       +-----------------------+
```

## 2. Core Components

### Frontend Layer (`app.py`)
* **User Controls:** Lets users choose a target ward (such as `CCC_Ward_01`–`CCC_Ward_10`) and explore single-date results or multi-day comparisons within the same ward.
* **Presentation Layer:** Displays estimated cases (`float`), risk classification (`Low`, `Medium`, `High`, `Critical`), top feature drivers, and multi-day weather/case trends.

### Inference & Feature Engineering Layer (`predict.py`)
* **Ward Discovery (`get_available_wards`):** Reads `data/dengue_data.csv` and extracts unique, sorted ward identifiers.
* **Feature Preparation (`build_features`):**
  1. Parses `date` values into datetime objects and sorts records chronologically per ward (`ward_id`, `date`) so time-series shifts stay aligned.
  2. Generates 1-to-4-week lag features (`7`, `14`, `21`, and `28` days) for `rainfall_mm`, `avg_temp_c`, and `relative_humidity_pct` when absent.
  3. Maps dataset lag column names (`rainfall_mm_lag_*`, `avg_temp_c_lag_*`) to the shortened names expected by the model (`rain_lag_*`, `temp_lag_*`) via `alias_map` so expected features are populated rather than defaulting to zero.
* **Single-Point & Multi-Day Inference (`predict_for_ward`, `get_ward_history`):**
  * Loads the serialized bundle from `models/dengue_model.joblib`.
  * Selects either the requested `date_str` or the latest available record (`.tail(1)`) for the chosen ward, or retrieves recent rows for multi-day comparison.
  * Aligns input columns to `bundle["features"]` / `model.feature_names_in_`, computes `predicted_cases`, maps `get_risk_tier()`, and extracts `feature_importances_` when available.

### Data & Model Artifacts
* **`data/dengue_data.csv`:** Stores historical ward records, weather metrics, precomputed/derived lag columns, and dengue case counts.
* **`models/dengue_model.joblib`:** Contains the trained regression/ensemble estimator and metadata such as the expected feature list.

## 3. Data Flow & Runtime Behavior

1. User selects a ward (and optional date or multi-day window) in `app.py`.
2. `predict.py` loads `dengue_data.csv` and runs `build_features()`.
3. Rows are filtered to `ward_id` and ordered by `date`.
4. `predict_for_ward()` aligns features with the model bundle and produces continuous expected case values (`float`) alongside the corresponding risk tier and top drivers.
5. Because the dataset is self-contained and no live external geocoding or weather APIs are queried at runtime, predictions are reproducible from the bundled CSV and `.joblib` file.