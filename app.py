import base64
from pathlib import Path
import pandas as pd
import streamlit as st
from predict import get_available_wards, predict_for_ward

st.set_page_config(
    page_title="DengueWatch",
    page_icon="🦟",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "dengue_data.csv"

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

.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 3rem;
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

.risk-card {{
    background: #1B1116;
    border: 1px solid #6C2B3B;
    padding: 25px;
    border-radius: 18px;
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
    ["Home", "Check My Area", "Prevention Guide", "Symptom Guide", "AI Surveillance"]
)

language = st.sidebar.radio(
    "Language / ভাষা",
    ["English", "বাংলা"],
    horizontal=True
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
        ("🛡️ Prevent Mosquito Bites", "Use mosquito nets, repellents and protective clothing.")
    ]
else:
    title = "আপনার এলাকার ঝুঁকি জানুন, ডেঙ্গু থেকে সচেতন থাকুন।"
    subtitle = "আবহাওয়া ও পর্যবেক্ষণ তথ্যের ভিত্তিতে ওয়ার্ডভিত্তিক ডেঙ্গু ঝুঁকির পূর্বাভাস।"
    check_text = "আপনার ওয়ার্ডের ঝুঁকি দেখুন"
    tips_title = "এই সপ্তাহে নিজেকে সুরক্ষিত রাখুন"
    tips = [
        ("🪣 জমে থাকা পানি সরান", "বালতি, টব ও অন্যান্য পাত্রের জমে থাকা পানি ফেলে দিন।"),
        ("🚰 পানির পাত্র ঢেকে রাখুন", "পানির ট্যাংক ও পাত্র ভালোভাবে ঢেকে রাখুন।"),
        ("🛡️ মশার কামড় থেকে বাঁচুন", "মশারি, মশা প্রতিরোধক ও সুরক্ষামূলক পোশাক ব্যবহার করুন।")
    ]

# ---------- Hero ----------
st.markdown(f"""
<div class="hero">
    <div class="small-label">AI-POWERED DENGUE EARLY WARNING</div>
    <h1>{title}</h1>
    <p>{subtitle}</p>
</div>
""", unsafe_allow_html=True)

st.write("")


@st.cache_data
def get_ward_weather_row(ward_id: str) -> dict:
    df = pd.read_csv(DATA_PATH)
    if "ward_id" not in df.columns:
        return {}
    rows = df[df["ward_id"].astype(str) == str(ward_id)].copy()
    if rows.empty:
        return {}
    if "date" in rows.columns:
        rows["date"] = pd.to_datetime(rows["date"], errors="coerce")
        rows = rows.sort_values("date")
    latest = rows.iloc[-1]
    return {
        "city": latest.get("city", "N/A"),
        "avg_temp_c": latest.get("avg_temp_c"),
        "relative_humidity_pct": latest.get("relative_humidity_pct"),
        "rainfall_mm": latest.get("rainfall_mm"),
    }


# ---------- Risk Checker ----------
st.markdown(f"## 📍 {check_text}")

available_wards = get_available_wards()

col1, col2 = st.columns([1, 1.5])

with col1:
    selected_ward = st.selectbox(
        "Select Ward ID / ওয়ার্ড আইডি নির্বাচন করুন",
        options=available_wards if available_wards else ["No wards found"],
        index=0
    )

    typed_ward = st.text_input(
        "Or type a Ward ID",
        placeholder="Example: CCC_Ward_01"
    )

    ward_to_check = (
        typed_ward.strip()
        if typed_ward.strip()
        else (selected_ward if available_wards else "")
    )

    check_button = st.button("Check Dengue Risk", use_container_width=True)

with col2:
    if check_button:
        if not ward_to_check:
            st.warning("Please select or enter a Ward ID first.")
        else:
            try:
                with st.spinner(f"Running model prediction for {ward_to_check}..."):
                    pred = predict_for_ward(ward_to_check)
                    weather = get_ward_weather_row(ward_to_check)

                risk = pred["risk_tier"]
                risk_colors = {
                    "Low": "#B6D96C",
                    "Medium": "#E8C76A",
                    "Moderate": "#E8C76A",
                    "High": "#E46C78",
                    "Critical": "#FF4D5D"
                }
                risk_color = risk_colors.get(risk, "#E8C76A")

                temp_val = weather.get("avg_temp_c")
                hum_val = weather.get("relative_humidity_pct")
                rain_val = weather.get("rainfall_mm")
                city_name = weather.get("city", "N/A")

                temp_str = f"{float(temp_val):.1f}°C" if pd.notna(temp_val) else "N/A"
                hum_str = f"{float(hum_val):.1f}%" if pd.notna(hum_val) else "N/A"
                rain_str = f"{float(rain_val):.1f} mm" if pd.notna(rain_val) else "N/A"

                st.markdown(f"""
                <div class="risk-card">
                    <div class="small-label">MODEL RISK PREDICTION</div>
                    <h2 style="color:{risk_color};">⚠️ {risk} Risk</h2>
                    <p><b>Ward ID:</b> {pred["ward_id"]} &nbsp;|&nbsp; <b>City:</b> {city_name} &nbsp;|&nbsp; <b>Date:</b> {pred["date"]}</p>
                    <p><b>Predicted Cases:</b> {pred["predicted_cases"]:.2f}</p>
                    <hr>
                    <b>Weather Information (from dataset)</b>
                    <ul>
                        <li>Temperature: {temp_str}</li>
                        <li>Humidity: {hum_str}</li>
                        <li>Rainfall: {rain_str}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                if pred.get("top_drivers"):
                    st.markdown("### 📊 Top Model Drivers")
                    for item in pred["top_drivers"]:
                        st.write(f"- **{item['feature']}**: {item['importance']}")

            except Exception as error:
                st.error(f"Could not predict for '{ward_to_check}': {error}")
    else:
        st.info("Select or type a Ward ID and click **Check Dengue Risk** to see your trained model's prediction.")

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
DengueWatch AI · Community Awareness & Early Warning<br>
An academic project — predictions are not a medical diagnosis.
</div>
""", unsafe_allow_html=True)
