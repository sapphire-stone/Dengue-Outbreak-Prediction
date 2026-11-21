# Urban Dengue Outbreak Early-Warning System

## Overview
Stage 1 prototype predicting ward-level dengue outbreak risk using weather lags and vulnerability indicators

## Team & Roles
- Team Name: The Newbies
- Nilanjana Barua Athoi
- Dilshad Zaman Mithila
- Mary Patricia Argha

# 🦟 Dengue Outbreak Prediction (Ward-Level Risk Assessment)

A machine learning and Streamlit web application built to forecast ward-level dengue outbreak risk in Chattogram using historical meteorological data, ward infrastructure indicators, and multi-week lag features.

---

## 📌 Overview

Dengue transmission is heavily influenced by delayed environmental conditions—such as rainfall accumulation, humidity, and temperature shifts occurring weeks prior to case spikes. This project analyzes ward-level records (`dengue_data.csv`) alongside a trained regression model (`dengue_model.joblib`) to estimate expected dengue cases, classify outbreak risk tiers, and visualize multi-day trends within individual wards.

---

## ✨ Key Features

- **Ward-Specific Risk Prediction (`predict.py`):**
  - Selects a target ward (e.g., `CCC_Ward_01`, `CCC_Ward_03`) and evaluates either the latest available record or a specified historical date (`date_str`).
  - Outputs continuous expected case estimates (`predicted_cases`) mapped into actionable risk tiers:
    - **Low:** `< 1.0`
    - **Medium:** `1.0 – 2.99`
    - **High:** `3.0 – 5.99`
    - **Critical:** `≥ 6.0`
- **Automated Feature Engineering & Lag Alignment (`build_features`):**
  - Chronologically sorts ward time-series records and generates 1-to-4-week lag features (`7`, `14`, `21`, and `28` days) for `rainfall_mm`, `avg_temp_c`, and `relative_humidity_pct`.
  - Maps dataset column names (`rainfall_mm_lag_*`, `avg_temp_c_lag_*`) to the exact feature names expected by the serialized model (`rain_lag_*`, `temp_lag_*`) to ensure accurate inference.
- **Model Explainability (Top Drivers):**
  - Extracts `feature_importances_` from the trained model to highlight the primary environmental and infrastructure drivers behind each ward's prediction.
- **Multi-Day Ward Trend Comparison (`get_ward_history`):**
  - Enables day-by-day historical comparison within a single selected ward rather than relying solely on a single-day snapshot.

---

## 🗂️ Project Structure

```text
Dengue Outbreak/
├── app.py                     # Streamlit frontend interface & multi-day comparison views
├── predict.py                 # Feature engineering, lag alignment, and model inference pipeline
├── data/
│   └── dengue_data.csv        # Historical ward-level weather, infrastructure, and dengue dataset
├── models/
│   └── dengue_model.joblib    # Serialized trained ML model bundle and expected feature list
└── README.md                  # Project documentation and disclosures
```

---

## ⚙️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sapphire-stone/Dengue-Outbreak-Prediction.git
   cd "Dengue Outbreak"
   ```

2. **Install required dependencies:**
   ```bash
   pip install streamlit pandas joblib scikit-learn
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

4. **Test the prediction pipeline via CLI:**
   ```bash
   python predict.py
   ```

---

## 📊 Methodology Notes

- **Why Predicted Cases Are Decimal Values (`float`):** The model outputs continuous expected case estimates rather than discrete headcounts. These continuous predictions preserve granularity across varying weather lags before being grouped into clear risk tiers (`Low`, `Medium`, `High`, `Critical`).
- **Dataset Date Coverage:** Predictions reflect the dates present in `data/dengue_data.csv` (currently running through `2025-12-29`). When no custom `date_str` is supplied, `predict_for_ward()` evaluates the most recent available record for that ward.

---

## 🔒 Data & API Disclosures

- **External APIs:** This prediction pipeline operates **offline using local dataset files** (`data/dengue_data.csv`) and does **not** rely on third-party geocoding (`geopy` / Nominatim) or live external weather APIs during inference.
- **Dataset & Model Assets:** All ward-level environmental indicators (`avg_temp_c`, `relative_humidity_pct`, `rainfall_mm`), infrastructure indices (`population_density_sqkm`, `water_logging_risk_index`, `sanitation_score`), and historical case records are sourced from the project's curated local dataset (`dengue_data.csv`).
- **AI / Development Tooling Disclosure:** AI coding assistance was utilized during development for debugging Git workflows, resolving feature-column mapping issues in `predict.py`, structuring multi-day historical comparison helpers, and drafting documentation.
