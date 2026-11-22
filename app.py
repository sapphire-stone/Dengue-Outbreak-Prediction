import base64
from pathlib import Path
import pandas as pd
import streamlit as st
from predict import (
    get_available_wards,
    get_ward_baseline,
    predict_with_weather,
)

st.set_page_config(
    page_title="DengueWatch",
    page_icon="🦟",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "dengue_data.csv"


def _safe_float(val, default: float) -> float:
    num = pd.to_numeric(val, errors="coerce")
    return float(num) if pd.notna(num) else float(default)


def _compute_infestation_prob(
    predicted_cases: float,
    rainfall_mm: float,
    relative_humidity_pct: float,
    avg_temp_c: float,
) -> float:
    rain_score = min(1.0, max(0.0, float(rainfall_mm) / 35.0))
    hum_score = min(1.0, max(0.0, (float(relative_humidity_pct) - 45.0) / 40.0))
    temp_val = float(avg_temp_c)
    if 24.0 <= temp_val <= 32.0:
        temp_score = 1.0
    else:
        dist = min(abs(temp_val - 24.0), abs(temp_val - 32.0))
        temp_score = min(1.0, max(0.0, 1.0 - (dist / 10.0)))

    suitability = (0.40 * rain_score) + (0.35 * hum_score) + (0.25 * temp_score)
    case_norm = min(1.0, max(0.0, float(predicted_cases) / 6.0))
    prob = ((0.65 * suitability) + (0.35 * case_norm)) * 100.0
    return round(min(99.0, max(2.0, prob)), 1)


@st.cache_data(show_spinner=False)
def cached_wards() -> list[str]:
    return get_available_wards()


@st.cache_data(show_spinner=False)
def cached_baseline(ward_id: str) -> dict:
    return get_ward_baseline(ward_id)


# ---------- Background Image ----------
image_path = BASE_DIR / "assets" / "mosquito_bg.png"

if image_path.exists():
    encoded = base64.b64encode(image_path.read_bytes()).decode()
    background = f"url('data:image/png;base64,{encoded}')"
else:
    background = "none"

# ---------- Language ----------
if "language" not in st.session_state:
    st.session_state.language = "English"

# ---------- Styling ----------
st.markdown(f"""
<style>
.stApp {{
    background: #090B0D;
    color: #F4E9E9;
}}

[data-testid="stSidebar"] {{
    background: #16070C;
}}

.stAppViewContainer .stMain .stMainBlockContainer,
.block-container {{
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
}}

header[data-testid="stHeader"] {{
    height: 2.2rem !important;
    background: transparent !important;
}}

.hero {{
    background-image:
        linear-gradient(90deg, rgba(9,11,13,0.97), rgba(22,7,12,0.75)),
        {background};
    background-size: cover;
    background-position: center;
    padding: 55px 45px;
    border-radius: 20px;
    border: 1px solid #48232C;
}}

.hero h1 {{
    font-size: 48px !important;
    color: #F7EEEE !important;
}}

.hero p {{
    font-size: 18px;
    color: #D5C3C7;
}}

.tip-card {{
    background: #151719;
    border: 1px solid #343638;
    border-radius: 14px;
    padding: 20px;
    height: 100%;
}}

.small-label {{
    color: #B6D96C;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 12px;
}}

div.stButton > button {{
    background: #792C3B;
    color: white;
    border: 1px solid #963E51;
    border-radius: 10px;
}}

div.stButton > button:hover {{
    background: #963E51;
    color: white;
    border: 1px solid #B65A6E;
}}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.title("🦟 DengueWatch")
st.sidebar.caption("Community Dengue Early Warning")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Check My Area", "Prevention Guide", "Symptom Guide", "AI Surveillance"],
)

language = st.sidebar.radio(
    "Language / ভাষা",
    ["English", "বাংলা"],
    horizontal=True,
)

# ---------- Text Content ----------
if language == "English":
    title = "Know Your Area. Stay Ahead of Dengue."
    subtitle = "Ward-level dengue risk prediction powered by historical weather and surveillance data."
    check_text = "Check Your Ward's Risk"
    tips_title = "Protect Yourself This Week"
    tips = [
        ("🪣 Remove Standing Water", "Empty water from buckets, pots, trays and unused containers."),
        ("🚰 Cover Water Storage", "Keep water tanks and containers tightly covered."),
        ("🛡️ Prevent Mosquito Bites", "Use mosquito nets, repellents and protective clothing."),
    ]
else:
    title = "আপনার এলাকার ঝুঁকি জানুন, ডেঙ্গু থেকে সচেতন থাকুন।"
    subtitle = "আবহাওয়া ও পর্যবেক্ষণ তথ্যের ভিত্তিতে ওয়ার্ডভিত্তিক ডেঙ্গু ঝুঁকির পূর্বাভাস।"
    check_text = "আপনার ওয়ার্ডের ঝুঁকি দেখুন"
    tips_title = "এই সপ্তাহে নিজেকে সুরক্ষিত রাখুন"
    tips = [
        ("🪣 জমে থাকা পানি সরান", "বালতি, টব ও অন্যান্য পাত্রের জমে থাকা পানি ফেলে দিন।"),
        ("🚰 পানির পাত্র ঢেকে রাখুন", "পানির ট্যাংক ও পাত্র ভালোভাবে ঢেকে রাখুন।"),
        ("🛡️ মশার কামড় থেকে বাঁচুন", "মশারি, মশা প্রতিরোধক ও সুরক্ষামূলক পোশাক ব্যবহার করুন।"),
    ]

# ---------- Hero ----------
st.markdown(f"""
<div class="hero">
    <div class="small-label"> DENGUE EARLY WARNING</div>
    <h1>{title}</h1>
    <p>{subtitle}</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------- Ward Selection ----------
st.markdown(f"## 📍 {check_text}")

available_wards = cached_wards()

col_pick, col_type = st.columns([1, 1])

with col_pick:
    selected_ward = st.selectbox(
        "Select Ward / ওয়ার্ড নির্বাচন করুন",
        options=available_wards if available_wards else ["No wards found"],
        format_func=lambda w: w.replace("_", " "),
        index=0,
    )

with col_type:
    typed_ward = st.text_input(
        "Or type a Ward ID",
        placeholder="Example: CCC_Ward_01",
    )

active_ward = (
    typed_ward.strip()
    if typed_ward.strip()
    else (selected_ward if available_wards and selected_ward != "No wards found" else "")
)

# ---------- Dataset Comparison & Infestation Check ----------
if active_ward:
    try:
        baseline = cached_baseline(active_ward)
        row = baseline["row"]
        hist_avg = baseline["hist_avg"]
        base_pred = baseline["base_pred"]

        st.subheader(f"Weather vs. Dataset Statistics — {active_ward.replace('_', ' ')}")

        w1, w2, w3 = st.columns(3)
        with w1:
            rain_input = st.number_input(
                "Rainfall (mm)",
                min_value=0.0,
                value=_safe_float(row.get("rainfall_mm"), 0.0),
                step=0.5,
                format="%.1f",
                key=f"rain_in_{active_ward}",
            )
        with w2:
            humidity_input = st.number_input(
                "Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=_safe_float(row.get("relative_humidity_pct"), 75.0),
                step=0.5,
                format="%.1f",
                key=f"hum_in_{active_ward}",
            )
        with w3:
            temp_input = st.number_input(
                "Temperature (°C)",
                min_value=0.0,
                max_value=60.0,
                value=_safe_float(row.get("avg_temp_c"), 28.0),
                step=0.5,
                format="%.1f",
                key=f"temp_in_{active_ward}",
            )

        sim_pred = predict_with_weather(
            ward_id=active_ward,
            rainfall_mm=rain_input,
            relative_humidity_pct=humidity_input,
            avg_temp_c=temp_input,
        )

        sim_cases = _safe_float(sim_pred.get("predicted_cases"), 0.0)
        base_cases = _safe_float(base_pred.get("predicted_cases"), 0.0)

        if "infestation_prob" in sim_pred and pd.notna(sim_pred["infestation_prob"]):
            infestation_prob = _safe_float(sim_pred["infestation_prob"], 0.0)
        else:
            infestation_prob = _compute_infestation_prob(
                sim_cases, rain_input, humidity_input, temp_input
            )

        risk_tier = str(sim_pred.get("risk_tier") or "Low")

        avg_rain = _safe_float(hist_avg.get("rainfall_mm"), 0.0)
        avg_hum = _safe_float(hist_avg.get("relative_humidity_pct"), 75.0)
        avg_temp = _safe_float(hist_avg.get("avg_temp_c"), 28.0)

        diff_rain = rain_input - avg_rain
        diff_hum = humidity_input - avg_hum
        diff_temp = temp_input - avg_temp

        risk_badges = {
            "Low": ("🟢 Low Risk", "success"),
            "Medium": ("🟡 Medium Risk", "warning"),
            "Moderate": ("🟡 Moderate Risk", "warning"),
            "High": ("🟠 High Risk", "error"),
            "Critical": ("🔴 Critical Risk", "error"),
        }
        risk_label, box_style = risk_badges.get(risk_tier, (f"⚠️ {risk_tier} Risk", "warning"))

        m1, m2, m3 = st.columns(3)
        m1.metric("Risk Level", risk_tier)
        m2.metric("Infestation Probability", f"{infestation_prob:.0f}%")
        m3.metric(
            "Predicted Cases",
            f"{sim_cases:.2f}",
            f"{sim_cases - base_cases:+.2f} vs dataset avg",
        )

        comp_df = pd.DataFrame({
            "Metric": ["Rainfall (mm)", "Humidity (%)", "Temperature (°C)", "Predicted Cases"],
            "Ward Dataset Avg": [
                f"{avg_rain:.1f}",
                f"{avg_hum:.1f}",
                f"{avg_temp:.1f}",
                f"{base_cases:.2f}",
            ],
            "Your Input": [
                f"{rain_input:.1f}",
                f"{humidity_input:.1f}",
                f"{temp_input:.1f}",
                f"{sim_cases:.2f}",
            ],
            "Difference vs Avg": [
                f"{diff_rain:+.1f}",
                f"{diff_hum:+.1f}",
                f"{diff_temp:+.1f}",
                f"{sim_cases - base_cases:+.2f}",
            ],
        })
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        summary_msg = (
            f"**{risk_label}** in **{active_ward.replace('_', ' ')}** "
            f"(**{infestation_prob:.0f}%** infestation probability, **{sim_cases:.2f}** est. cases) — "
            f"based on your rainfall, humidity, and temperature inputs compared against ward dataset averages."
        )

        if box_style == "error":
            st.error(summary_msg)
        elif box_style == "warning":
            st.warning(summary_msg)
        else:
            st.success(summary_msg)

    except Exception as error:
        st.warning(f"Could not run comparison: {error}")

# ---------- Prevention ----------
st.markdown(f"## 🛡️ {tips_title}")

cols = st.columns(3)

for col, tip in zip(cols, tips):
    with col:
        st.markdown(f"""
        <div class="tip-card">
            <h3>{tip[0]}</h3>
            <p>{tip[1]}</p>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ---------- Footer ----------
st.markdown("""
---
<div style="text-align:center;color:#8F8589;">
DengueWatch · Community Awareness & Early Warning<br>
An academic project — predictions are not a medical diagnosis.
</div>
""", unsafe_allow_html=True)
