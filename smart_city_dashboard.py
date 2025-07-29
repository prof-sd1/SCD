# 🌍 SMART CITY DASHBOARD v2.0
# Real OpenWeatherMap API • Animated Time-Series • Smart Alerts

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
# 🔐 SET YOUR API KEY HERE
# -------------------------------
OPENWEATHER_API_KEY = "b4f73b0c7123cf33a1a24cd995f6b88a"  # ← Replace with your real key

# -------------------------------
# 1. Global City List with Coordinates
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
# 2. Fetch Real Data from OpenWeatherMap API
# -------------------------------
@st.cache_data(ttl=1800)  # Cache for 30 mins
def get_weather_air(city_name, lat, lon):
    try:
        # Current weather
        weather_url = f"http://api.openweathermap.org/data/2.5/weather"
        weather_params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        weather_resp = requests.get(weather_url, params=weather_params)
        weather_data = weather_resp.json()

        # Air quality
        air_url = f"http://api.openweathermap.org/data/2.5/air_pollution"
        air_params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY
        }
        air_resp = requests.get(air_url, params=air_params)
        air_data = air_resp.json()

        aqi = air_data["list"][0]["main"]["aqi"]  # 1-5 scale
        components = air_data["list"][0]["components"]
        pm2_5 = components.get("pm2_5", 0)
        no2 = components.get("no2", 0)

        return {
            "city": city_name,
            "temp": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "wind_speed": weather_data["wind"]["speed"],
            "condition": weather_data["weather"][0]["main"],
            "aqi": aqi,
            "pm2_5": pm2_5,
            "no2": no2,
            "lat": lat,
            "lon": lon
        }
    except Exception as e:
        st.warning(f"Failed to fetch data for {city_name}: {e}")
        return None

# Fetch data
def load_real_data():
    data = []
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()

    for i, (name, country, lat, lon) in enumerate(CITIES):
        status_text.text(f"Loading {name}...")
        result = get_weather_air(name, lat, lon)
        if result:
            result["country"] = country
            data.append(result)
        progress_bar.progress((i + 1) / len(CITIES))
        time.sleep(0.1)  # Be kind to API

    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(data)

# -------------------------------
# 3. Generate Historical Data for Animation (Simulated)
# -------------------------------
def generate_historical(pm25_current):
    # Simulate last 7 days with realistic variation
    base = pm25_current
    noise = np.random.normal(0, 5, 7)
    trend = np.linspace(-10, 10, 7)  # Random trend
    values = base + noise + trend
    dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
    return list(zip(dates, values))

# -------------------------------
# 4. Streamlit App UI
# -------------------------------
st.set_page_config(layout="wide", page_title="🌍 Smart City AI Dashboard", page_icon="🌆")

st.sidebar.title("🌆 Smart City Dashboard")
page = st.sidebar.radio("🧭 Navigate", ["🌍 Live Overview", "📈 Animated Trends", "🔮 Forecast & Alerts", "📊 Insights"])

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Load real data
df = load_real_data()

if df.empty:
    st.error("No data loaded. Check API key or connection.")
    st.stop()

# Risk Score
df["risk_score"] = (df["pm2_5"] / 150 * 0.5 + df["aqi"] / 5 * 0.5) * 100
bins = [0, 30, 60, 80, 100]
labels = ["Low", "Medium", "High", "Critical"]
df["risk_level"] = pd.cut(df["risk_score"], bins=bins, labels=labels)

# -------------------------------
# Page 1: Live Overview
# -------------------------------
if page == "🌍 Live Overview":
    st.title("🌍 Live Global Urban Monitor")
    st.markdown("Powered by **OpenWeatherMap API** | Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cities", len(df))
    col2.metric("Avg Temp", f"{df['temp'].mean():.1f}°C")
    col3.metric("Avg PM2.5", f"{df['pm2_5'].mean():.1f} μg/m³")
    col4.metric("Critical Risks", (df["risk_level"] == "Critical").sum())

    # Map
    m = folium.Map(location=[20, 0], zoom_start=2)
    color_map = {"Low": "green", "Medium": "orange", "High": "red", "Critical": "black"}

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=10,
            color=color_map[row["risk_level"]],
            fill=True,
            fill_color=color_map[row["risk_level"]],
            popup=f"📍 {row['city']}, {row['country']}<br>"
                  f"• PM2.5: {row['pm2_5']} μg/m³<br>"
                  f• Temp: {row['temp']:.1f}°C<br>
                  f• Risk: {row['risk_level']},
            tooltip=f"{row['city']} - {row['risk_level']}"
        ).add_to(m)

    st_folium(m, width="100%", height=500)

# -------------------------------
# Page 2: Animated Time-Series
# -------------------------------
elif page == "📈 Animated Trends":
    st.title("📈 Animated PM2.5 Trends (Simulated)")

    city = st.selectbox("Select City", df["city"])
    row = df[df["city"] == city].iloc[0]
    history = generate_historical(row["pm2_5"])

    hist_df = pd.DataFrame(history, columns=["date", "pm2_5"])
    hist_df["city"] = city

    fig = px.scatter(hist_df, x="date", y="pm2_5", size="pm2_5", text="city",
                     animation_frame=hist_df["date"].dt.strftime("%b %d, %H:%M"),
                     range_y=[0, 150],
                     title=f"Simulated PM2.5 Trend in {city}",
                     labels={"pm2_5": "PM2.5 (μg/m³)"})
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Page 3: Forecast & Alerts
# -------------------------------
elif page == "🔮 Forecast & Alerts":
    st.title("🔮 Smart Alerts & Forecast")

    high_risk = df[df["risk_level"] == "Critical"]
    if len(high_risk) > 0:
        for _, r in high_risk.iterrows():
            st.error(f"🚨 CRITICAL AIR QUALITY in {r['city']} ({r['pm2_5']} μg/m³) – Avoid outdoor activity!")

    # Forecast
    st.subheader("Predicted PM2.5 (Next 24h)")
    trend = st.radio("Pollution Trend", ["Improving", "Stable", "Worsening"])
    factor = {"Improving": 0.8, "Stable": 1.0, "Worsening": 1.3}
    predicted = df["pm2_5"].mean() * factor

    st.metric("Predicted Global Avg PM2.5", f"{predicted:.1f} μg/m³")

# -------------------------------
# Page 4: AI Insights (Rule-Based)
# -------------------------------
elif page == "📊 Insights":
    st.title("🧠 AI-Powered Insights")

    avg_pm25 = df["pm2_5"].mean()
    critical_cities = df[df["risk_level"] == "Critical"]["city"].tolist()

    if avg_pm25 > 75:
        st.warning("⚠️ **Air quality is unhealthy globally.** Recommend reducing emissions.")
    elif avg_pm25 > 35:
        st.info("ℹ️ Moderate pollution. Sensitive groups should monitor levels.")
    else:
        st.success("✅ Air quality is good across most cities.")

    if critical_cities:
        st.error(f"🔴 Critical levels in: {', '.join(critical_cities)}")

    st.markdown("### 💡 Recommendations")
    st.write("""
    - 🏙️ Cities with high PM2.5 should restrict traffic.
    - 🌳 Increase green zones in high-risk areas.
    - 📢 Issue public health alerts in Delhi, Cairo, etc.
    """)

# -------------------------------
# Footer
# -------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("🔐 API: OpenWeatherMap • 🌐 Real-time • 🚀 Built with Streamlit")
