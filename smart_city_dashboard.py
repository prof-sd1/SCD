
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import folium
from streamlit_folium import st_folium

# -------------------------------
# Mock Data (In real app, load from API or CSV)
# -------------------------------
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]

df_air = pd.DataFrame({
    "city": CITIES,
    "aqi": np.random.randint(1, 6, 5),
    "pm2_5": np.random.uniform(5, 100, 5),
    "pm10": np.random.uniform(10, 150, 5),
    "no2": np.random.uniform(10, 80, 5)
})

df_traffic = pd.DataFrame({
    "city": CITIES,
    "congestion_level": np.random.uniform(0.3, 0.9, 5),
    "avg_speed_kmh": np.random.uniform(20, 60, 5)
})

df_summary = df_air[["city", "aqi", "pm2_5"]].merge(df_traffic[["city", "congestion_level"]], on="city")
df_summary["risk_score"] = (df_summary["aqi"] * 0.4 + df_summary["congestion_level"] * 0.6) * 20
df_summary["risk_level"] = pd.cut(df_summary["risk_score"], bins=3, labels=["Low", "Medium", "High"])

# -------------------------------
# Streamlit App
# -------------------------------
st.set_page_config(layout="wide", page_title="ðﾟﾏﾙ️ Smart City Dashboard")

st.title("ðﾟﾏﾙ️ Smart City Dashboard")
st.markdown("Real-time urban analytics for smarter cities")

# Sidebar Filters
st.sidebar.header("Filters")
selected_cities = st.sidebar.multiselect("Select Cities", CITIES, default=CITIES)

df_filtered = df_summary[df_summary.city.isin(selected_cities)]

# Metrics
st.header("ðﾟﾓﾊ Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Air Quality Index", f"{df_filtered['aqi'].mean():.1f}")
col2.metric("Avg Congestion Level", f"{df_filtered['congestion_level'].mean():.2f}")
col3.metric("Avg PM2.5", f"{df_filtered['pm2_5'].mean():.1f} μg/m³")
col4.metric("High Risk Cities", (df_filtered["risk_level"] == "High").sum())

# Map
st.header("ðﾟﾌﾍ Risk Map")
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
for _, row in df_filtered.iterrows():
    color = {"Low": "green", "Medium": "orange", "High": "red"}[row["risk_level"]]
    folium.CircleMarker(
        location=[39 + np.random.rand(), -98 + np.random.rand()],
        radius=10,
        color=color,
        fill=True,
        fill_color=color,
        popup=f"{row['city']}: {row['risk_level']} Risk"
    ).add_to(m)
st_folium(m, width=700)

# Charts
st.header("ðﾟﾓﾈ Analytics")

fig1 = px.bar(df_filtered, x='city', y='congestion_level', color='risk_level',
              title="Traffic Congestion by City", color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"})
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.scatter(df_filtered, x='pm2_5', y='congestion_level', text='city', size='aqi',
                  title="Air Quality vs Traffic Congestion",
                  labels={"pm2_5": "PM2.5 (μg/m³)", "congestion_level": "Congestion Level"})
st.plotly_chart(fig2, use_container_width=True)

# Forecast
st.header("ðﾟﾔﾮ Forecast: Predicted PM2.5")
congestion_input = st.slider("Expected Avg Congestion Level", 0.0, 1.0, 0.5)
health_input = st.slider("Expected Avg Respiratory Cases", 10, 100, 30)

# Simple linear proxy (replace with real model in production)
predicted_pm25 = 5 + 80 * congestion_input + 0.5 * health_input
st.info(f"Predicted PM2.5 Level: **{predicted_pm25:.1f} μg/m³**")

st.markdown("---")
st.markdown("✅ Built with Python, Streamlit, and Plotly | Ready for **Streamlit Cloud** deployment")
