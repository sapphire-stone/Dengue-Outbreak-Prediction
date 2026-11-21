
import streamlit as st
import base64
from pathlib import Path
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

st.set_page_config(
    page_title="DengueWatch AI",
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
# ---------- Bangladesh Location Search ----------

area_data = {
    "Agrabad": {"risk": "High", "temperature": 32, "humidity": 82, "rainfall": 145},
    "Halishahar": {"risk": "Critical", "temperature": 33, "humidity": 88, "rainfall": 190},
    "Panchlaish": {"risk": "Moderate", "temperature": 31, "humidity": 76, "rainfall": 95},
    "Nasirabad": {"risk": "Low", "temperature": 30, "humidity": 68, "rainfall": 40},
    "Patenga": {"risk": "High", "temperature": 32, "humidity": 85, "rainfall": 160},
    "Khulshi": {"risk": "Moderate", "temperature": 31, "humidity": 74, "rainfall": 80}
}

@st.cache_resource
def get_geocoder():
    geolocator = Nominatim(
        user_agent="denguewatch_ai_student_project"
    )
    return RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1
    )


@st.cache_data(ttl=86400)
def search_location(place):
    geocoder = get_geocoder()

    result = geocoder(
        f"{place}, Bangladesh",
        country_codes="bd",
        exactly_one=True,
        timeout=10
    )

    if result:
        return {
            "address": result.address,
            "latitude": result.latitude,
            "longitude": result.longitude
        }

    return None


col1, col2 = st.columns([1, 1.5])

with col1:
    location_query = st.text_input(
        "Search your location / আপনার এলাকা লিখুন",
        placeholder="Example: Agrabad, Dhaka, Cox's Bazar..."
    )

    check_button = st.button(
        "Check Dengue Risk",
        use_container_width=True
    )

with col2:
    if check_button:

        if not location_query.strip():
            st.warning("Please enter a location first.")

        else:
            try:
                with st.spinner("Searching for your location..."):
                    location = search_location(location_query.strip())

                if location is None:
                    st.error(
                        "Location not found in Bangladesh. "
                        "Please check the spelling or try another location."
                    )

                else:
                    st.success("Location found in Bangladesh!")

                    st.write("**Matched location:**")
                    st.write(location["address"])

                    st.caption(
                        f"Coordinates: {location['latitude']:.5f}, "
                        f"{location['longitude']:.5f}"
                    )

                    matched_area = next(
                        (
                            name for name in area_data
                            if name.casefold() in location["address"].casefold()
                        ),
                        None
                    )

                    if matched_area:
                        data = area_data[matched_area]
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
                            <h2 style="color:{risk_color};">
                                ⚠️ {risk} Risk
                            </h2>
                            <p>Area: <b>{matched_area}</b></p>
                            <hr>
                            <b>Weather Information</b>
                            <ul>
                                <li>Temperature: {data['temperature']}°C</li>
                                <li>Humidity: {data['humidity']}%</li>
                                <li>Recent rainfall: {data['rainfall']} mm</li>
                            </ul>
                            <b>Why this risk level?</b>
                            <p>
                                Temperature, humidity and recent rainfall
                                are sample environmental indicators.
                            </p>
                            <p style="color:#B6D96C;">
                                Sample data only — not an actual AI prediction.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                    else:
                        st.warning(
                            "This location was found, but it is not covered "
                            "by our current sample dengue risk data."
                        )

                        st.info(
                            "We cannot provide a reliable local risk prediction "
                            "for this location yet."
                        )

            except Exception:
                st.error(
                    "Could not connect to the location search service. "
                    "Please try again later."
                )

    else:
        st.info(
            "Enter a Bangladesh location and click the button "
            "to search for it."
        )


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
