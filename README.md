# 🦟 DengueWatch — Ward-Level Dengue Risk Assessment

A Streamlit and Python web application built to estimate ward-level dengue outbreak risk in Chattogram using historical meteorological and ward surveillance data (`dengue_data.csv`), weather simulation, and a serialized machine learning model (`dengue_model.joblib`).

## Team & Roles
- Team Name: The Newbies
- Nilanjana Barua Athoi
- Dilshad Zaman Mithila
- Mary Patricia Argha


---

## 📌 Overview

Dengue transmission is closely linked to environmental conditions—including rainfall, relative humidity, and temperature—as well as multi-week lag patterns. DengueWatch lets users select or enter a ward ID, adjust weather inputs (**Rainfall (mm)**, **Humidity (%)**, and **Temperature (°C)**), compare those inputs directly against ward dataset averages, and view the resulting **Risk Level**, **Infestation Probability (%)**, and **Predicted Cases**.

---

## ✨ Key Features

- **Interactive Weather vs. Dataset Comparison (`app.py`):**
  - Select a ward from the dropdown or enter a Ward ID manually.
  - Adjust **Rainfall (mm)**, **Humidity (%)**, and **Temperature (°C)** and view a comparison table showing **Ward Dataset Avg**, **Your Input**, and **Difference vs Avg**.
  - Displays **Risk Level**, **Infestation Probability (%)**, and **Predicted Cases** (with delta against the ward baseline).
- **Lag Pipeline & Weather-Responsive Prediction (`predict.py`):**
  - Chronologically sorts records per `ward_id` and builds multi-week lag features (`1w–4w` / `7`, `14`, `21`, and `28` days) for `rainfall_mm`, `avg_temp_c`, and `relative_humidity_pct`, aligning feature names with the trained model bundle.
  - Combines model inference with weather suitability scoring (`predict_with_weather`) so low/unfavorable weather conditions lower risk and infestation probability, while dengue-favorable conditions raise them.
  - Maps predicted cases into clear risk tiers:
    - **Low:** `< 1.0`
    - **Medium:** `1.0 – 2.99`
    - **High:** `3.0 – 5.99`
    - **Critical:** `≥ 6.0`
- **Prevention Guidance & Bilingual UI:**
  - Includes weekly mosquito-prevention tips and a quick **English / বাংলা** language toggle.

---

## 🗂️ Project Structure

```text
Dengue-Outbreak-Prediction/
├── app.py                     # Streamlit frontend, weather inputs, comparison table & UI
├── predict.py                 # Feature/lag pipeline, weather suitability & model inference
├── ARCHITECTURE.md            # System architecture, data flow, split rationale & caching notes
├── requirements.txt           # Python package dependencies
├── README.md                  # Project documentation and disclosures
├── data/
│   └── dengue_data.csv        # Historical ward-level weather, lag & surveillance dataset
└── models/
    └── dengue_model.joblib    # Serialized trained model artifact and feature metadata
```

---

## ⚙️ Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sapphire-stone/Dengue-Outbreak-Prediction.git
   cd Dengue-Outbreak-Prediction
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Or directly: `pip install streamlit pandas numpy joblib scikit-learn`)*

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

4. **Run a quick CLI check on `predict.py`:**
   ```bash
   python predict.py
   ```

---

## 📊 Methodology Notes

- **Continuous Case Estimates:** Predicted cases are returned as continuous decimal values (`float`) before being grouped into `Low`, `Medium`, `High`, and `Critical` tiers.
- **Academic Scope:** Predictions are intended for ward-level risk exploration and educational early-warning demonstration—not medical diagnosis.

---
## 🌐 Live Demo
- **Streamlit App:** `https://your-app-name.streamlit.app`

---
## 🔒 Data, API & AI Disclosures

- **External APIs:** No external weather, geocoding, or paid third-party APIs are called during prediction; inference runs locally using `data/dengue_data.csv` and `models/dengue_model.joblib`.
- **AI Assistant Disclosure:** **Gemini** was used as an AI development assistant during building and refinement—including debugging `predict.py` and `app.py`, tuning weather-suitability risk behavior, drafting `ARCHITECTURE.md` and `README.md`, and planning the demo walkthrough.
