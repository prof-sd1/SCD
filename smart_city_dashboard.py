# 🌍 SMART CITY DASHBOARD v2.0
# Real OpenWeatherMap API • Animated Trends • Smart Alerts
# Deployable on Streamlit Cloud

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import time

# -------------------------------
# 🔐 API KEY (Set in .streamlit/secrets.toml or directly here)
# -------------------------------
# For security, use st.secrets in production
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except:
    API_KEY = "b4f73b0c7123cf33a1a24cd995f6b88a"  # Replace with your key

if not API_KEY or API_KEY == "your-api-key-here":
    st.error("❌ OpenWeatherMap API key not set. Go to https://openweathermap.org/api to get one.")
    st.stop()

# -------------------------------
# 1. Global City List
# -------------------------------
CITIES = [
    ("New York", "USA", 40.7128, -74.0060),
    ("Los Angeles", "USA", 34.0522, -118.2437),
    ("London", "UK", 51.5074, -0.1278),
    ("Paris", "France", 48.8566, 2.3522),
    ("Tokyo", "Japan", 35.6762, 139.6503),
    ("Mumbai", "India", 19.0760, 72.8777),
    ("Sydney", "Australia", -33.8688, 151.2093),
    ("São Paulo", "Brazil", -23.5505, -46.6333),
    ("Cairo", "Egypt", 30.0444, 31.2357),
    ("Moscow", "Russia", 55.7558, 37.6173),
    ("Johannesburg", "South Africa", -26.2041, 28.0473),
    ("Singapore", "Singapore", 1.3521, 103.8198)
]

# -------------------------------
# 2. Fetch Real Data from OpenWeatherMap
# -------------------------------
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_weather_air(city_name, lat, lon):
    try:
        # Current weather
        weather_url = "http://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric"
        }
        weather_resp = requests.get(weather_url, params=weather_params)
        if weather_resp.status_code != 200:
            st.warning(f"Failed to get weather for {city_name}: {weather_resp.status_code}")
            return None
        weather_data = weather_resp.json()

        # Air pollution
        air_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        air_params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY
        }
        air_resp = requests.get(air_url, params=air_params)
        if air_resp.status_code != 200:
            st.warning(f"Failed to get air quality for {city_name}: {air_resp.status_code}")
            return None
        air_data = air_resp.json()

        aqi = air_data["list"][0]["main"]["aqi"]
        components = air_data["list"][0]["components"]
        pm2_5 = components.get("pm2_5", 0)

        return {
            "city": city_name,
            "country": country,
            "temp": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "wind_speed": weather_data["wind"]["speed"],
            "condition": weather_data["weather"][0]["main"],
            "aqi": aqi,
            "pm2_5": pm2_5,
            "lat": lat,
            "lon": lon
        }
    except Exception as e:
        st.warning(f"Error fetching data for {city_name}: {e}")
        return None

# Load data
def load_data():
    data = []
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()

    for i, (name, country, lat, lon) in enumerate(CITIES):
        status_text.text(f"📡 Loading {name}...")
        result = get_weather_air(name, lat, lon)
        if result:
            data.append(result)
        progress_bar.progress((i + 1) / len(CITIES))
        time.sleep(0.1)  # Avoid rate limits

    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(data)

# -------------------------------
# 3. Generate Simulated Historical Data for Animation
# -------------------------------
def generate_history(pm25_current):
    base = pm25_current
    noise = np.random.normal(0, 5, 7)
    trend = np.linspace(-10, 10, 7)
    values = base + noise + trend
    dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
    return pd.DataFrame({"date": dates, "pm2_5": values})

# -------------------------------
# 4. Streamlit UI
# -------------------------------
st.set_page_config(layout="wide", page_title="🌍 Smart City AI Dashboard", page_icon="🌆")

st.sidebar.title("🌆 Smart City Dashboard")
page = st.sidebar.radio("🧭 Navigate", ["🌍 Live Overview", "📈 Animated Trends", "🔮 Forecast & Alerts", "📊 AI Insights"])

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Load data
df = load_data()

if df.empty:
    st.error("No data loaded. Check your API key or internet connection.")
    st.stop()

# Risk Scoring
df["risk_score"] = (df["pm2_5"] / 150 * 0.5 + df["aqi"] / 5 * 0.5) * 100
bins = [0, 30, 60, 80, 100]
labels = ["Low", "Medium", "High", "Critical"]
df["risk_level"] = pd.cut(df["risk_score"], bins=bins, labels=labels)

color_map = {"Low": "green", "Medium": "orange", "High": "red", "Critical": "black"}

# -------------------------------
# Page 1: Live Overview
# -------------------------------
if page == "🌍 Live Overview":
    st.title("🌍 Live Global Urban Monitor")
    st.markdown(f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')} | Powered by OpenWeatherMap")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cities", len(df))
    col2.metric("Avg Temp", f"{df['temp'].mean():.1f}°C")
    col3.metric("Avg PM2.5", f"{df['pm2_5'].mean():.1f} μg/m³")
    col4.metric("Critical Risks", (df["risk_level"] == "Critical").sum())

    # Map
    m = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=10,
            color=color_map[row["risk_level"]],
            fill=True,
            fill_color=color_map[row["risk_level"]],
            popup=f"📍 {row['city']}, {row['country']}<br>"
                  f"• Temp: {row['temp']:.1f}°C<br>"
                  f"• PM2.5: {row['pm2_5']} μg/m³<br>"
                  f"• Risk: {row['risk_level']}",
            tooltip=f"{row['city']} - {row['risk_level']}"
        ).add_to(m)

    st_folium(m, width="100%", height=500)

# -------------------------------
# Page 2: Animated Trends
# -------------------------------
elif page == "📈 Animated Trends":
    st.title("📈 Animated PM2.5 Trends (Simulated History)")

    city = st.selectbox("Select City", df["city"])
    row = df[df["city"] == city].iloc[0]
    hist_df = generate_history(row["pm2_5"])
    hist_df["city"] = city

    fig = px.scatter(
        hist_df, x="date", y="pm2_5", size="pm2_5", text="city",
        animation_frame=hist_df["date"].dt.strftime("%b %d, %H:%M"),
        range_y=[0, 150],
        title=f"Simulated PM2.5 Trend in {city}",
        labels={"pm2_5": "PM2.5 (μg/m³)"}
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Page 3: Forecast & Alerts
# -------------------------------
elif page == "🔮 Forecast & Alerts":
    st.title("🔮 Forecast & Smart Alerts")

    high_risk = df[df["risk_level"] == "Critical"]
    if not high_risk.empty:
        for _, r in high_risk.iterrows():
            st.error(f"🚨 CRITICAL AIR QUALITY in {r['city']} ({r['pm2_5']} μg/m³) – Take action now!")

    st.subheader("Predicted Global PM2.5")
    trend = st.radio("Expected Trend", ["Improving", "Stable", "Worsening"])
    factor = {"Improving": 0.8, "Stable": 1.0, "Worsening": 1.3}
    predicted = df["pm2_5"].mean() * factor

    st.metric("Predicted Avg PM2.5", f"{predicted:.1f} μg/m³")

# -------------------------------
# Page 4: AI Insights
# -------------------------------
elif page == "📊 AI Insights":
    st.title("🧠 AI-Powered Insights")

    avg_pm25 = df["pm2_5"].mean()
    critical_cities = ", ".join(df[df["risk_level"] == "Critical"]["city"].tolist())

    if avg_pm25 > 75:
        st.warning("⚠️ **Air quality is unhealthy globally.** Recommend reducing emissions.")
    elif avg_pm25 > 35:
        st.info("ℹ️ Moderate pollution. Sensitive groups should monitor levels.")
    else:
        st.success("✅ Air quality is good across most cities.")

    if critical_cities:
        st.error(f"🔴 Critical levels in: {critical_cities}")

    st.markdown("### 💡 Recommendations")
    st.write("""
    - 🚗 Limit traffic in high-risk cities.
    - 🌳 Expand green spaces.
    - 📢 Issue public health advisories.
    """)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown(
    "🔐 API: [OpenWeatherMap](https://openweathermap.org/api) | "
    "🌐 Real-time Urban Intelligence | "
    "🚀 Deployed with [Streamlit](https://streamlit.io)"
)
