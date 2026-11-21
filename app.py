import re
import streamlit as st
import base64
from pathlib import Path
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from data_loader import load_dengue_data
from predictor import predict_next_week
st.set_page_config(
    page_title="DengueWatch AI",
    page_icon="🦟",
    layout="wide"
)

# ---------- Homepage Background ----------
image_path = Path("assets/mosquito_bg.png")

if image_path.exists():
    encoded = base64.b64encode(image_path.read_bytes()).decode()
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

        {surveillance_background};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
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

# ---------- Historical Dataset ----------
@st.cache_data
def get_dataset():
    return load_dengue_data()


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
    clean_place = re.sub(
        r"\bchittagong\b",
        "Chattogram",
        clean_place,
        flags=re.IGNORECASE
    )

    simple_place = re.sub(
        r"^\d+[/\-\w]*\s+",
        "",
        clean_place
    ).strip()

    search_queries = [
        f"{clean_place}, Bangladesh",
        f"{simple_place}, Chattogram, Bangladesh",
        f"{simple_place}, Bangladesh"
    ]

    search_queries = list(dict.fromkeys(search_queries))

    for query in search_queries:
        try:
            result = geocoder(
                query,
                country_codes="bd",
                addressdetails=True,
                exactly_one=True,
                timeout=15
            )

            if result:
                address_details = result.raw.get("address", {})

                if address_details.get("country_code", "").casefold() == "bd":
                    return {
                        "address": result.address,
                        "latitude": result.latitude,
                        "longitude": result.longitude,
                        "address_details": address_details
                    }

        except Exception:
            continue

    return None


def identify_supported_city(location):
    details = location.get("address_details", {})
    searchable_text = " ".join(str(value) for value in details.values()).casefold()
    searchable_text += " " + location.get("address", "").casefold()

    if any(term in searchable_text for term in ["chattogram", "chittagong", "চট্টগ্রাম"]):
        return "Chattogram"

    if any(term in searchable_text for term in ["gazipur", "গাজীপুর"]):
        return "Gazipur"

    if any(term in searchable_text for term in ["narayanganj", "নারায়ণগঞ্জ", "নারায়ণগঞ্জ"]):
        return "Narayanganj"

    if any(term in searchable_text for term in ["dhaka", "ঢাকা"]):
        return "Dhaka (North + South)"

    return None


def get_latest_city_observation(df, supported_city):
    if supported_city == "Dhaka (North + South)":
        selected_cities = ["Dhaka North", "Dhaka South"]
    else:
        selected_cities = [supported_city]

    city_records = df[df["city"].isin(selected_cities)].copy()

    if city_records.empty:
        return None

    weekly = (
        city_records.groupby("date")
        .agg({
            "dengue_cases": "sum",
            "rainfall_mm": "mean",
            "avg_temp_c": "mean",
            "relative_humidity_pct": "mean"
        })
        .reset_index()
        .sort_values("date")
    )

    return weekly.iloc[-1]


col1, col2 = st.columns([1, 1.5])

with col1:
    location_query = st.text_input(
        "Search your location / আপনার এলাকা লিখুন",
        placeholder="Example: Agrabad, Dhaka, Gazipur..."
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

                    supported_city = identify_supported_city(location)

                    if supported_city is None:
                        st.warning(
                            "This location is not in the five cities covered "
                            "by our current dataset."
                        )
                        st.info(
                            "Supported cities: Chattogram, Dhaka North, "
                            "Dhaka South, Gazipur and Narayanganj. "
                            "No local prediction is available for this location."
                        )
                    else:
                        df = get_dataset()
                        observation = get_latest_city_observation(df, supported_city)

                        if observation is None:
                            st.warning("No historical records were found for this city.")
                        else:
                            st.markdown(f"""
                            <div class="risk-card">
                                <div class="small-label">LATEST HISTORICAL DATA</div>
                                <h2 style="color:#E8C76A;">
                                    {supported_city}
                                </h2>
                                <p>
                                    This is a city-level historical observation,
                                    not a live or AI-generated risk prediction.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            st.caption(
                                "Recorded week: "
                                + observation["date"].strftime("%d %B %Y")
                            )

                            metric1, metric2 = st.columns(2)
                            metric1.metric(
                                "Recorded dengue cases",
                                f"{int(observation['dengue_cases']):,}"
                            )
                            metric2.metric(
                                "Average temperature",
                                f"{observation['avg_temp_c']:.1f} °C"
                            )

                            metric3, metric4 = st.columns(2)
                            metric3.metric(
                                "Average humidity",
                                f"{observation['relative_humidity_pct']:.1f}%"
                            )
                            metric4.metric(
                                "Average rainfall",
                                f"{observation['rainfall_mm']:.1f} mm"
                            )

                            if supported_city == "Dhaka (North + South)":
                                st.info(
                                    "Dhaka North and Dhaka South are combined "
                                    "because the search result does not identify "
                                    "which dataset division contains this address."
                                )

                            st.caption(
                                "Source: dengue_dataset.csv. Weather values are "
                                "city-level averages across the dataset's wards."
                            )

                            # ---------- AI Prediction ----------
                            st.markdown("### 🤖 AI Dengue Prediction")
                           

                            try:
                                prediction = predict_next_week(supported_city)

                                if prediction:
                                    st.metric(
                                        "Estimated dengue cases for next week",
                                        f"{prediction['predicted_cases']:,}"
                                    )
                                    st.metric(
                                       "Estimated dengue risk level",
                                        prediction["risk_level"]
                                    )

                                    st.caption(
                                        "Based on historical data up to "
                                        + prediction["last_recorded_week"].strftime("%d %B %Y")
                                    )

                                    st.warning(
                                        "Historical model demonstration only. "
                                        "This is not a live forecast."
                                    )
                                else:
                                    st.info("Prediction is unavailable.")

                            except Exception as error:
                                st.error(f"Prediction error: {error}")
                                st.caption(f"Technical detail: {error}")

            except Exception as error:
                st.error(
                    "Could not load the location or historical dataset. "
                    "Check your internet connection and project files."
                )
                st.caption(f"Technical detail: {error}")
    else:
        st.info(
            "Enter a Bangladesh location and click the button "
            "to check whether historical city-level data is available."
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
