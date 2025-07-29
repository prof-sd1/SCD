import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import folium
from streamlit_folium import st_folium
import requests

# -------------------------------
# CONFIGURATION
# -------------------------------
st.set_page_config(layout="wide", page_title="🌐 Smart City Dashboard")
WEATHER_API_KEY = "your_openweathermap_api_key"  # Replace this with your real API key

# -------------------------------
# Mock Cities with Coordinates
# -------------------------------
CITIES = [
    ("New York", "USA", 40.7128, -74.0060),
    ("Los Angeles", "USA", 34.0522, -118.2437),
    ("Chicago", "USA", 41.8781, -87.6298),
    ("Houston", "USA", 29.7604, -95.3698),
    ("Phoenix", "USA", 33.4484, -112.0740)
]

# -------------------------------
# Fetch Weather & Air Quality
# -------------------------------
@st.cache_data(ttl=1800)
def get_weather_air(city_name, country, lat, lon):
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        air_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"

        weather_data = requests.get(weather_url).json()
        air_data = requests.get(air_url).json()

        pm2_5 = air_data["list"][0]["components"]["pm2_5"]
        aqi = air_data["list"][0]["main"]["aqi"]

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

# -------------------------------
# Load Data for All Cities
# -------------------------------
def load_data():
    data = []
    for name, country, lat, lon in CITIES:
        result = get_weather_air(name, country, lat, lon)
        if result:
            result["congestion_level"] = np.random.uniform(0.3, 0.9)
            data.append(result)
    return pd.DataFrame(data)

# -------------------------------
# Dashboard UI
# -------------------------------
st.title("🌐 Smart City Dashboard")
st.markdown("Real-time urban analytics for smarter cities")

# Sidebar Filters
st.sidebar.header("Filters")
df_data = load_data()
selected_cities = st.sidebar.multiselect("Select Cities", df_data["city"].unique(), default=df_data["city"].unique())
df_filtered = df_data[df_data["city"].isin(selected_cities)]

# Risk Score Calculation
df_filtered["risk_score"] = (df_filtered["aqi"] * 0.4 + df_filtered["congestion_level"] * 0.6) * 20
df_filtered["risk_level"] = pd.cut(df_filtered["risk_score"], bins=3, labels=["Low", "Medium", "High"])

# -------------------------------
# Metrics
# -------------------------------
st.header("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg AQI", f"{df_filtered['aqi'].mean():.1f}")
col2.metric("Avg Congestion", f"{df_filtered['congestion_level'].mean():.2f}")
col3.metric("Avg PM2.5", f"{df_filtered['pm2_5'].mean():.1f} μg/m³")
col4.metric("High Risk Cities", (df_filtered["risk_level"] == "High").sum())

# -------------------------------
# Risk Map
# -------------------------------
st.header("🗺️ Risk Map")
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
for _, row in df_filtered.iterrows():
    color = {"Low": "green", "Medium": "orange", "High": "red"}[row["risk_level"]]
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=10,
        color=color,
        fill=True,
        fill_color=color,
        popup=f"{row['city']}: {row['risk_level']} Risk"
    ).add_to(m)
st_folium(m, width=700)

# -------------------------------
# Charts
# -------------------------------
st.header("📈 Analytics")

fig1 = px.bar(df_filtered, x='city', y='congestion_level', color='risk_level',
              title="Traffic Congestion by City",
              color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"})
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.scatter(df_filtered, x='pm2_5', y='congestion_level', text='city', size='aqi',
                  title="Air Quality vs Traffic Congestion",
                  labels={"pm2_5": "PM2.5 (μg/m³)", "congestion_level": "Congestion Level"})
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# Forecast Simulation
# -------------------------------
st.header("🧪 Forecast: Predicted PM2.5")
congestion_input = st.slider("Expected Avg Congestion Level", 0.0, 1.0, 0.5)
health_input = st.slider("Expected Avg Respiratory Cases", 10, 100, 30)

predicted_pm25 = 5 + 80 * congestion_input + 0.5 * health_input
st.info(f"Predicted PM2.5 Level: **{predicted_pm25:.1f} μg/m³**")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown("✅ Built with Python, Streamlit, and Plotly | Ready for **Streamlit Cloud** deployment")
