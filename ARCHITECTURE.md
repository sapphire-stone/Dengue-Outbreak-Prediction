# DengueWatch — System Architecture

## 1. High-Level Overview
DengueWatch is a ward-level dengue early-warning and weather-simulation web application built with **Python**, **Streamlit**, **Pandas**, **NumPy**, **Scikit-Learn**, and **Joblib**. Users select or enter a ward ID (`ward_id`), adjust weather inputs (**Rainfall (mm)**, **Humidity (%)**, and **Temperature (°C)**), compare those inputs against historical ward dataset averages, and inspect the resulting **Risk Level** (`Low`, `Medium`, `High`, `Critical`), **Infestation Probability (%)**, and **Predicted Cases**.

## 2. System Data Flow Diagram

```text
+-------------------------------------------------------------------+
|                        data/dengue_data.csv                       |
|       (ward_id, date, rainfall_mm, relative_humidity_pct,         |
|                avg_temp_c, surveillance/case fields)              |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|              Feature & Lag Pipeline (predict.py)                  |
|  - Parses dates and sorts chronologically by (ward_id, date)      |
|  - Computes multi-week lags (1w–4w) grouped per ward_id           |
|  - Applies user weather inputs over recent window (window_days=28) |
|  - Aligns feature columns to match trained model schema           |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|           Inference & Weather Suitability Scoring (predict.py)    |
|  - Loads serialized estimator from models/dengue_model.joblib     |
|  - Generates baseline & weather-simulated case predictions        |
|  - Computes weather suitability score from rainfall, humidity &    |
|    temperature                                                    |
|  - Combines model output + weather suitability into:              |
|      * predicted_cases                                            |
|      * infestation_prob (%)                                       |
|      * risk_tier (Low / Medium / High / Critical)                 |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|               Streamlit UI & Comparison View (app.py)             |
|  - Ward dropdown selector & Ward ID text input                    |
|  - Numeric inputs for Rainfall (mm), Humidity (%), Temp (°C)     |
|  - Key metrics: Risk Level, Infestation Probability, Cases      |
|  - Comparison table: Ward Dataset Avg vs. Your Input vs. Diff     |
|  - Prevention guidance & English / Bangla language toggle         |
+-------------------------------------------------------------------+
```

## 3. Core Components

### Frontend Layer (`app.py`)
- **Ward Selection & Weather Inputs:** Provides a ward selector (`get_available_wards`), a Ward ID text input override, and direct numeric inputs for **Rainfall (mm)**, **Humidity (%)**, and **Temperature (°C)** initialized from ward baseline records.
- **Comparison & Risk Readout:** Displays a side-by-side comparison table (`Ward Dataset Avg`, `Your Input`, and `Difference vs Avg`) alongside metrics for **Risk Level**, **Infestation Probability**, and **Predicted Cases**, plus prevention guidance and English/Bangla language support.

### Multi-Week Weather Lag Pipeline & Simulation (`predict.py`)
- **Chronological Grouping:** Records in `data/dengue_data.csv` are parsed into timestamps and sorted by `(ward_id, date)` so lag shifts stay strictly grouped within each ward without cross-ward or future leakage.
- **Multi-Week Lags & Aliases:** Computes 1-to-4-week lag features (`7`, `14`, `21`, and `28` days) for `rainfall_mm`, `relative_humidity_pct`, and `avg_temp_c`, maps lag column names through `alias_map` where needed, and updates derived indicators such as `water_logging_risk_index`.
- **Weather Simulation & Suitability (`predict_with_weather`):** Updates the recent simulation window (`window_days=28`) with user-provided rainfall, humidity, and temperature values, recomputes lag features, runs model inference, and computes a **weather suitability score** (`0.0` to `1.0`). Blending model case predictions with weather suitability prevents lag features from keeping low-weather scenarios stuck at high risk, ensuring low/unfavorable weather lowers infestation probability and risk tier while dengue-favorable conditions raise them.

## 4. Chronological Validation Split & Model Selection Rationale
- **Chronological Validation Split:** Time-series dengue surveillance and weather records should be split chronologically (earlier periods for training, later periods for validation/testing) rather than randomly shuffled so future outbreak patterns do not leak into historical evaluation.
- **Model Selection Rationale:** A tree-based model serialized with `joblib` (`models/dengue_model.joblib`) fits tabular weather, lag, and ward surveillance data well because environmental thresholds (such as optimal mosquito temperature ranges, humidity, and cumulative rainfall) are non-linear and interact across time, while enabling fast, deterministic local inference.

## 5. Compute, Memory & Caching Efficiency
- **Streamlit Caching:** Ward lists (`cached_wards`) and ward baseline lookups (`cached_baseline`) use `@st.cache_data` in `app.py` to avoid repeated CSV reads and re-aggregations across Streamlit reruns.
- **Safe Numeric Handling & Fallbacks:** Safe float conversion (`_safe_float`) guards against missing or `NaN` values, and fallback probability calculation prevents missing-key crashes during UI rendering.
- **Zero External Paid APIs:** All predictions run locally using the bundled CSV and serialized `.joblib` model without paid external LLM or third-party weather API calls at inference time, keeping execution fast and cost-effective on local machines and Streamlit Community Cloud.