
import streamlit as st
import base64
from pathlib import Path
from pathlib import Path
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from predict import predict_for_ward
from data_loader import load_dengue_data

st.set_page_config(
    page_title="DengueWatch",
    page_icon="🦟",
    layout="wide"
)

# ---------- Background Image ----------
image_path = Path("assets/mosquito_bg.png")

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
st.sidebar.title("🦟 DengueWatch AI")
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
    subtitle = "Community-level dengue awareness and early risk monitoring powered by weather patterns and AI."
    check_text = "Check Your Area's Risk"
    tips_title = "Protect Yourself This Week"
    tips = [
        ("🪣 Remove Standing Water", "Empty water from buckets, pots, trays and unused containers."),
        ("🚰 Cover Water Storage", "Keep water tanks and containers tightly covered."),
        ("🛡️ Prevent Mosquito Bites", "Use mosquito nets, repellents and protective clothing.")
    ]
else:
    title = "আপনার এলাকার ঝুঁকি জানুন, ডেঙ্গু থেকে সচেতন থাকুন।"
    subtitle = "আবহাওয়ার তথ্য ও AI-এর সাহায্যে ডেঙ্গুর ঝুঁকি পর্যবেক্ষণ এবং জনসচেতনতা।"
    check_text = "আপনার এলাকার ঝুঁকি দেখুন"
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


# ---------- Risk Checker ----------
st.markdown(f"## 📍 {check_text}")

# Sample data for demonstration only
area_data = {
    "Agrabad": {"risk": "High", "temperature": 32, "humidity": 82, "rainfall": 145},
    "Halishahar": {"risk": "Critical", "temperature": 33, "humidity": 88, "rainfall": 190},
    "Panchlaish": {"risk": "Moderate", "temperature": 31, "humidity": 76, "rainfall": 95},
    "Nasirabad": {"risk": "Low", "temperature": 30, "humidity": 68, "rainfall": 40},
    "Patenga": {"risk": "High", "temperature": 32, "humidity": 85, "rainfall": 160},
    "Khulshi": {"risk": "Moderate", "temperature": 31, "humidity": 74, "rainfall": 80}
}

col1, col2 = st.columns([1, 1.5])

with col1:
    area = st.selectbox(
        "Select your area / এলাকা নির্বাচন করুন",
        list(area_data.keys())
    )

    check_button = st.button("Check Dengue Risk", use_container_width=True)

with col2:
    if check_button:
        data = area_data[area]
        risk = data["risk"]

        risk_colors = {
            "Low": "#B6D96C",
            "Moderate": "#E8C76A",
            "High": "#E46C78",
            "Critical": "#FF4D5D"
        }

        risk_color = risk_colors[risk]

        st.markdown(f"""
        <div class="risk-card">
            <div class="small-label">SAMPLE RISK RESULT</div>
            <h2 style="color:{risk_color};">⚠️ {risk} Risk</h2>
            <p>Area: <b>{area}</b></p>
            <hr>
            <b>Weather Information</b>
            <ul>
                <li>Temperature: {data['temperature']}°C</li>
                <li>Humidity: {data['humidity']}%</li>
                <li>Recent rainfall: {data['rainfall']} mm</li>
            </ul>
            <b>Why this risk level?</b>
            <p>Temperature, humidity and recent rainfall are sample environmental indicators used to demonstrate dengue risk monitoring.</p>
            <p style="color:#B6D96C;">This is sample data only, not an actual AI prediction.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Select an area and click the button to view its sample dengue risk.")

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
