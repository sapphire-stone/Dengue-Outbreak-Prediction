
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from pathlib import Path

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="Dengue AI | Surveillance System",
    page_icon="🦟",
    layout="wide"
)

# ==============================
# OPTIONAL BACKGROUND IMAGE
# ==============================
image_path = Path("assets/mosquito_bg.png")

background = ""
if image_path.exists():
    encoded = base64.b64encode(image_path.read_bytes()).decode()
    background = f"url('data:image/png;base64,{encoded}')"

# ==============================
# CUSTOM CSS
# ==============================
st.markdown(f"""
<style>

.stApp {{
    background: #090B0D;
    color: #F3E9EC;
}}

[data-testid="stSidebar"] {{
    background-color: #16070C;
    border-right: 1px solid #39212A;
}}

[data-testid="stSidebar"] * {{
    color: #F3E9EC;
}}

.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}}

h1, h2, h3 {{
    color: #F5E9EC !important;
}}

p, label {{
    color: #C8B9BE;
}}

.hero {{
    background-image:
        linear-gradient(
            90deg,
            rgba(12, 7, 10, 0.88),
            rgba(31, 9, 17, 0.62),
            rgba(12, 7, 10, 0.35)
        ),
        {background if background else "linear-gradient(135deg, #28151B, #090B0D)"};

    background-size: cover;
    background-position: center;

    padding: 38px;
    border-radius: 18px;
    border: 1px solid #482632;
    margin-bottom: 25px;
}}

.hero-label {{
    color: #B6D96C;
    font-size: 12px;
    letter-spacing: 3px;
    font-weight: bold;
}}

.hero-title {{
    color: #FFFFFF;
    font-size: 36px;
    font-weight: 700;
    margin-top: 10px;
}}

.hero-subtitle {{
    color: #D0BEC5;
    font-size: 15px;
    margin-top: 10px;
}}

.metric-card {{
    background: rgba(35, 18, 25, 0.85);
    border: 1px solid #442630;
    border-radius: 14px;
    padding: 20px;
    min-height: 125px;
}}

.metric-label {{
    color: #BBAAB1;
    font-size: 13px;
}}

.metric-value {{
    color: #FFFFFF;
    font-size: 29px;
    font-weight: bold;
    margin-top: 8px;
}}

.metric-note {{
    color: #B6D96C;
    font-size: 12px;
    margin-top: 5px;
}}

.section-title {{
    color: #F3E9EC;
    font-size: 20px;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 12px;
}}

.status-low {{
    color: #B6D96C;
    font-weight: bold;
}}

.status-medium {{
    color: #E8B66B;
    font-weight: bold;
}}

.status-high {{
    color: #F08B79;
    font-weight: bold;
}}

.status-critical {{
    color: #FF4C65;
    font-weight: bold;
}}

div[data-testid="stDataFrame"] {{
    border: 1px solid #39212A;
    border-radius: 12px;
}}

.stPlotlyChart {{
    background: rgba(22, 12, 16, 0.7);
    border-radius: 14px;
}}

hr {{
    border-color: #39212A;
}}

</style>
""", unsafe_allow_html=True)


# ==============================
# SIDEBAR
# ==============================
st.sidebar.markdown("## 🦟 DENGUE AI")
st.sidebar.caption("URBAN SURVEILLANCE SYSTEM")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Risk Analysis",
        "Weather Insights",
        "About Project"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### System Status")
st.sidebar.markdown("🟢 Dashboard Online")
st.sidebar.caption("Prototype v0.1 | Sample Data")


# ==============================
# DEMO DATA
# ==============================
weather = pd.DataFrame({
    "Week": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
    "Rainfall (mm)": [35, 48, 65, 30, 88, 110, 72, 95],
    "Humidity (%)": [65, 69, 72, 70, 77, 82, 78, 84],
    "Temperature (°C)": [29, 30, 31, 30, 32, 31, 30, 32]
})

risk_data = pd.DataFrame({
    "Area": [
        "Zone 01",
        "Zone 02",
        "Zone 03",
        "Zone 04",
        "Zone 05",
        "Zone 06"
    ],
    "Rainfall (mm)": [110, 45, 95, 30, 125, 85],
    "Humidity (%)": [85, 62, 81, 58, 89, 76],
    "Temperature (°C)": [31, 29, 32, 28, 33, 30],
    "Risk Level": [
        "High",
        "Low",
        "High",
        "Low",
        "Critical",
        "Medium"
    ]
})


# ==============================
# HERO HEADER
# ==============================
st.markdown("""
<div class="hero">
    <div class="hero-label">AI-POWERED DISEASE SURVEILLANCE</div>
    <div class="hero-title">Dengue Early Warning System</div>
    <div class="hero-subtitle">
        Monitor environmental conditions, analyze multi-week weather patterns,
        and identify potential dengue risk across urban areas.
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("⚠️ Prototype dashboard — current indicators use illustrative sample data, not real outbreak predictions.")


# ==============================
# OVERVIEW PAGE
# ==============================
if page == "Overview":

    st.markdown('<div class="section-title">Surveillance Overview</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">AREAS MONITORED</div>
            <div class="metric-value">12</div>
            <div class="metric-note">Urban zones</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">HIGH-RISK AREAS</div>
            <div class="metric-value">3</div>
            <div class="metric-note">Sample indicator</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">AVG. HUMIDITY</div>
            <div class="metric-value">78%</div>
            <div class="metric-note">Sample weather data</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">7-DAY RAINFALL</div>
            <div class="metric-value">124 mm</div>
            <div class="metric-note">Sample accumulation</div>
        </div>
        """, unsafe_allow_html=True)

    # Risk distribution
    st.markdown('<div class="section-title">Risk Distribution</div>',
                unsafe_allow_html=True)

    risk_counts = risk_data["Risk Level"].value_counts().reset_index()
    risk_counts.columns = ["Risk Level", "Areas"]

    fig_risk = px.pie(
        risk_counts,
        names="Risk Level",
        values="Areas",
        hole=0.65,
        color="Risk Level",
        color_discrete_map={
            "Low": "#B6D96C",
            "Medium": "#E8B66B",
            "High": "#F08B79",
            "Critical": "#C42D49"
        }
    )

    fig_risk.update_layout(
        paper_bgcolor="#090B0D",
        plot_bgcolor="#090B0D",
        font_color="#F3E9EC",
        legend_title="Risk Category"
    )

    st.plotly_chart(fig_risk, use_container_width=True)

    # Area table
    st.markdown('<div class="section-title">Area Risk Overview</div>',
                unsafe_allow_html=True)

    st.dataframe(
        risk_data,
        use_container_width=True,
        hide_index=True
    )


# ==============================
# RISK ANALYSIS PAGE
# ==============================
elif page == "Risk Analysis":

    st.markdown('<div class="section-title">Dengue Risk Analysis</div>',
                unsafe_allow_html=True)

    selected_area = st.selectbox(
        "Select an urban area",
        risk_data["Area"]
    )

    area = risk_data[risk_data["Area"] == selected_area].iloc[0]

    a, b, c = st.columns(3)

    a.metric("Rainfall", f'{area["Rainfall (mm)"]} mm')
    b.metric("Humidity", f'{area["Humidity (%)"]}%')
    c.metric("Temperature", f'{area["Temperature (°C)"]}°C')

    risk_level = area["Risk Level"]

    st.markdown("### Predicted Risk Level")

    if risk_level == "Low":
        st.success(f"Risk Level: {risk_level}")
    elif risk_level == "Medium":
        st.warning(f"Risk Level: {risk_level}")
    elif risk_level == "High":
        st.error(f"Risk Level: {risk_level}")
    else:
        st.error(f"Risk Level: {risk_level}")

    st.markdown("### Environmental Factors")
    st.write(
        "Rainfall, humidity, temperature, and accumulated weather "
        "conditions are important environmental variables for dengue "
        "risk analysis. This prototype is not calculating an actual "
        "disease prediction yet."
    )


# ==============================
# WEATHER INSIGHTS PAGE
# ==============================
elif page == "Weather Insights":

    st.markdown('<div class="section-title">Environmental Data Analysis</div>',
                unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        fig_rain = px.bar(
            weather,
            x="Week",
            y="Rainfall (mm)",
            title="Weekly Rainfall",
            color_discrete_sequence=["#A33D55"]
        )

        fig_rain.update_layout(
            paper_bgcolor="#090B0D",
            plot_bgcolor="#160D11",
            font_color="white"
        )

        st.plotly_chart(fig_rain, use_container_width=True)

    with right:
        fig_humidity = px.line(
            weather,
            x="Week",
            y="Humidity (%)",
            title="Humidity Trends",
            markers=True,
            color_discrete_sequence=["#B6D96C"]
        )

        fig_humidity.update_layout(
            paper_bgcolor="#090B0D",
            plot_bgcolor="#160D11",
            font_color="white"
        )

        st.plotly_chart(fig_humidity, use_container_width=True)

    fig_temp = px.line(
        weather,
        x="Week",
        y="Temperature (°C)",
        title="Temperature Trends",
        markers=True,
        color_discrete_sequence=["#E08A73"]
    )

    fig_temp.update_layout(
        paper_bgcolor="#090B0D",
        plot_bgcolor="#160D11",
        font_color="white"
    )

    st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown("### Weather Data")

    st.dataframe(
        weather,
        use_container_width=True,
        hide_index=True
    )


# ==============================
# ABOUT PAGE
# ==============================
elif page == "About Project":

    st.markdown('<div class="section-title">About This Project</div>',
                unsafe_allow_html=True)

    st.markdown("""
    ### AI for Urban Dengue Outbreak

    An AI-based early warning system designed to explore the relationship
    between weather conditions and dengue risk in urban environments.

    **Key environmental inputs**
    - Temperature
    - Humidity
    - Rainfall
    - Previous weeks' rainfall
    - Multi-week weather patterns

    **System objectives**
    - Analyze environmental patterns
    - Identify areas with elevated dengue risk
    - Explore multi-week weather lag effects
    - Display risk indicators in an interactive dashboard
    - Support early awareness and monitoring

    **Risk Categories**
    - 🟢 Low
    - 🟡 Medium
    - 🟠 High
    - 🔴 Critical

    This dashboard is an academic prototype. Sample values are used
    until the real dataset and prediction model are integrated.
    """)


# ==============================
# FOOTER
# ==============================
st.divider()

st.caption(
    "AI for Urban Dengue Outbreak | Academic Project | Prototype v0.1"
)