import re
import base64
from pathlib import Path
import requests
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from streamlit_geolocation import streamlit_geolocation
st.set_page_config(
    page_title="DengueWatch AI",
    page_icon="🦟",
    layout="wide"
)

# ---------- Live Weather ----------
@st.cache_data(ttl=600)
def get_live_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "precipitation_sum",
        "forecast_days": 1,
        "timezone": "auto"
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()

def get_weather_description(code):
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Fog",
        51: "Light drizzle",
        53: "Drizzle",
        55: "Heavy drizzle",
        61: "Light rain",
        63: "Rain",
        65: "Heavy rain",
        80: "Rain showers",
        81: "Rain showers",
        82: "Heavy rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm",
        99: "Thunderstorm"
    }

    return descriptions.get(code, "Weather conditions unavailable")

# ---------- Manual Location Search ----------
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

    clean_place = re.sub(r"\s+", " ", place.strip())
    try:
        result = geocoder(
            f"{clean_place}, Bangladesh",
            country_codes="bd",
            exactly_one=True,
            timeout=15
        )
        if result:
            return {
                "address": result.address,
                "latitude": result.latitude,
                "longitude": result.longitude
            }

    except Exception:
        return None
    
    return None

# ---------- Homepage Background ----------
image_path = Path("assets/mosquito_bg.png")

if image_path.exists():
    encoded = base64.b64encode(
        image_path.read_bytes()
    ).decode()

    background = f"url('data:image/png;base64,{encoded}')"
else:
    background = "none"

# ---------- Full Homepage Background ----------
surveillance_image_path = Path("assets/surveillance_bg.png")

if surveillance_image_path.exists():
    surveillance_encoded = base64.b64encode(
        surveillance_image_path.read_bytes()
    ).decode()

    surveillance_background = (
        f"url('data:image/png;base64,{surveillance_encoded}')"
    )
else:
    surveillance_background = "none"

# ---------- Language ----------
if "language" not in st.session_state:
    st.session_state.language = "English"

# ---------- Styling ----------
st.markdown(f"""
<style>
.stApp {{
    background: transparent !important;
    color: #F4E9E9;
}}

[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(9, 11, 13, 0.55), rgba(9, 11, 13, 0.70)),
        {surveillance_background};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}}

[data-testid="stMain"] {{
    background: transparent !important;
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
    ["Home", "Check My Area", "Prevention Guide", "Symptom Guide"]
)

language = st.sidebar.radio(
    "Language / ভাষা",
    ["English", "বাংলা"],
    horizontal=True
)

# ---------- Text Content ----------
if language == "English":
    title = "Know Your Area. Stay Ahead of Dengue."
    subtitle = (
        "Community-level dengue awareness and early risk monitoring "
        "powered by weather patterns and AI."
    )

    check_text = "Check Your Area's Risk"
    tips_title = "Protect Yourself This Week"

    tips = [
        (
            "🪣 Remove Standing Water",
            "Empty water from buckets, pots, trays and unused containers."
        ),
        (
            "🚰 Cover Water Storage",
            "Keep water tanks and containers tightly covered."
        ),
        (
            "🛡️ Prevent Mosquito Bites",
            "Use mosquito nets, repellents and protective clothing."
        )
    ]

else:
    title = "আপনার এলাকার ঝুঁকি জানুন, ডেঙ্গু থেকে সচেতন থাকুন।"
    subtitle = "আবহাওয়ার তথ্য ও AI-এর সাহায্যে ডেঙ্গুর ঝুঁকি পর্যবেক্ষণ এবং জনসচেতনতা।"

    check_text = "আপনার এলাকার ঝুঁকি দেখুন"
    tips_title = "এই সপ্তাহে নিজেকে সুরক্ষিত রাখুন"

    tips = [
        (
            "🪣 জমে থাকা পানি সরান",
            "বালতি, টব ও অন্যান্য পাত্রের জমে থাকা পানি ফেলে দিন।"
        ),
        (
            "🚰 পানির পাত্র ঢেকে রাখুন",
            "পানির ট্যাংক ও পাত্র ভালোভাবে ঢেকে রাখুন।"
        ),
        (
            "🛡️ মশার কামড় থেকে বাঁচুন",
            "মশারি, মশা প্রতিরোধক ও সুরক্ষামূলক পোশাক ব্যবহার করুন।"
        )
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

st.markdown("### 📍 Detect Your Current Location")

gps_location = streamlit_geolocation()

latitude = None
longitude = None
location_name = "Your detected location"

# ---------- GPS Location ----------
if (
    gps_location
    and gps_location.get("latitude") is not None
    and gps_location.get("longitude") is not None
):
    latitude = gps_location["latitude"]
    longitude = gps_location["longitude"]

    st.success("Your location was detected successfully!")

    st.caption(
        f"GPS Coordinates: {latitude:.5f}, {longitude:.5f}"
    )

else:
    st.info(
        "Allow location access in your browser to detect your current location."
    )

# ---------- Manual Location Backup ----------
st.markdown("### Or Search Your Location")

col1, col2 = st.columns([1.5, 1])

with col1:
    location_query = st.text_input(
        "Enter your area",
        placeholder="Example: Agrabad, Chattogram"
    )

with col2:
    st.write("")
    st.write("")

    check_button = st.button(
        "Use This Location",
        use_container_width=True
    )

if check_button:
    if not location_query.strip():
        st.warning("Please enter a location.")
    else:
        with st.spinner("Finding your location..."):
            manual_location = search_location(location_query)

        if manual_location:
            latitude = manual_location["latitude"]
            longitude = manual_location["longitude"]
            location_name = manual_location["address"]

            st.session_state.manual_latitude = latitude
            st.session_state.manual_longitude = longitude
            st.session_state.manual_location_name = location_name

            st.success("Location found successfully!")

        else:
            st.error("Location not found. Please check the spelling.")

# Use manually selected location when available
if (
    not check_button
    and st.session_state.get("manual_latitude") is not None
):
    latitude = st.session_state.manual_latitude
    longitude = st.session_state.manual_longitude
    location_name = st.session_state.manual_location_name


# ---------- Live Weather and Risk Indicator ----------
if latitude is not None and longitude is not None:

    try:
        with st.spinner("Loading live weather for your area..."):

            weather = get_live_weather(latitude, longitude)
            current = weather["current"]
            daily = weather["daily"]
            temperature = current["temperature_2m"]
            humidity = current["relative_humidity_2m"]
            wind_speed = current["wind_speed_10m"]
            weather_code = current["weather_code"]
            rainfall = daily["precipitation_sum"][0]
        st.markdown("---")
        st.markdown("### 🌦️ Live Weather Conditions")
        if location_name != "Your detected location":
            st.caption(f"Location: {location_name}")
        st.info(get_weather_description(weather_code))
        metric1, metric2 = st.columns(2)
        metric1.metric(
            "Temperature",
            f"{temperature} °C"
        )

        metric2.metric(
            "Humidity",
            f"{humidity}%"
        )

        metric3, metric4 = st.columns(2)
        metric3.metric(
            "Today's Rainfall",
            f"{rainfall} mm"
        )

        metric4.metric(
            "Wind Speed",
            f"{wind_speed} km/h"
        )

        # ---------- Weather-Based Risk Indicator ----------
        st.markdown("---")
        st.markdown("### 🦟 Weather-Based Dengue Risk Indicator")

        score = 0
        if 25 <= temperature <= 32:
            score += 1

        if humidity >= 70:
            score += 1

        if rainfall >= 2:
            score += 1

        if score == 0:
            risk_level = "Low"
            explanation = (
                "Fewer of the selected mosquito-favorable "
                "weather conditions are currently present."
            )
        elif score == 1:
            risk_level = "Moderate"
            explanation = (
                "Some current weather conditions may favor "
                "mosquito activity."
            )

        else:
            risk_level = "High"
            explanation = (
                "Several current weather conditions may favor "
                "mosquito activity."
            )

        st.markdown(
            f"""
            <div class="risk-card">
                <div class="small-label">LOCAL WEATHER INDICATOR</div>
                <h1 style="color:#E8C76A;">{risk_level} Risk</h1>
                <p>{explanation}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "This is an illustrative weather-based environmental indicator, "
            "not a validated dengue prediction. Weather alone cannot confirm "
            "dengue cases or an outbreak."
        )

        st.caption(
            f"Weather data time: {current['time']}"
        )

    except Exception as error:
        st.error("Unable to load live weather data.")
        st.caption(f"Technical detail: {error}")

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
An academic project — weather indicators are not a medical diagnosis.
</div>
""", unsafe_allow_html=True)
