
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Smart City Dashboard", layout="wide")

st.title("ðﾟﾌﾍ Smart City Dashboard")
st.markdown("Analyze traffic flow, air quality, and energy consumption interactively.")

# Sample data loaders
@st.cache_data
def load_traffic_data():
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=100, freq="H"),
        "road_id": np.random.choice(["A1", "B2", "C3"], 100),
        "vehicle_count": np.random.poisson(20, size=100),
        "avg_speed_kph": np.random.normal(45, 5, size=100),
        "lat": np.random.uniform(9.00, 9.10, 100),
        "lon": np.random.uniform(38.70, 38.80, 100)
    })

@st.cache_data
def load_air_quality_data():
    return pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=100),
        "location": np.random.choice(["Site A", "Site B", "Site C"], 100),
        "pm25": np.random.uniform(10, 70, 100),
        "no2": np.random.uniform(5, 30, 100),
        "o3": np.random.uniform(15, 40, 100)
    })

@st.cache_data
def load_energy_data():
    return pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=100),
        "district": np.random.choice(["North", "South", "East", "West"], 100),
        "energy_kwh": np.random.uniform(1000, 5000, 100)
    })

# Tabs for different domains
tab1, tab2, tab3 = st.tabs(["ðﾟﾚﾦ Traffic", "ðﾟﾌﾫ️ Air Quality", "⚡ Energy"])

# ------------------ Traffic Tab ------------------ #
with tab1:
    st.header("ðﾟﾚﾦ Traffic Monitoring")

    df = load_traffic_data()
    selected_road = st.selectbox("Select Road ID", df['road_id'].unique())
    filtered_df = df[df['road_id'] == selected_road]

    col1, col2 = st.columns(2)
    col1.metric("Total Vehicles", int(filtered_df['vehicle_count'].sum()))
    col2.metric("Avg Speed", f"{filtered_df['avg_speed_kph'].mean():.1f} km/h")

    st.subheader("Traffic Volume and Speed Over Time")
    st.line_chart(filtered_df.set_index("timestamp")[["vehicle_count", "avg_speed_kph"]])

    st.subheader("Traffic Map")
    map = folium.Map(location=[9.05, 38.75], zoom_start=12)
    for _, row in filtered_df.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=5,
            popup=f"Road: {row['road_id']}\nVehicles: {row['vehicle_count']}",
            color="blue",
            fill=True,
            fill_opacity=0.6
        ).add_to(map)
    st_folium(map, width=700)

# ------------------ Air Quality Tab ------------------ #
with tab2:
    st.header("ðﾟﾌﾫ️ Air Quality Monitoring")

    df = load_air_quality_data()
    selected_location = st.selectbox("Select Monitoring Site", df['location'].unique())
    filtered_df = df[df['location'] == selected_location]

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg PM2.5", f"{filtered_df['pm25'].mean():.1f} µg/m³")
    col2.metric("Avg NO₂", f"{filtered_df['no2'].mean():.1f} µg/m³")
    col3.metric("Avg O₃", f"{filtered_df['o3'].mean():.1f} µg/m³")

    st.subheader("Pollutant Levels Over Time")
    fig = px.line(filtered_df, x="date", y=["pm25", "no2", "o3"], labels={"value": "Pollution (µg/m³)", "date": "Date"})
    st.plotly_chart(fig, use_container_width=True)

# ------------------ Energy Tab ------------------ #
with tab3:
    st.header("⚡ Energy Consumption")

    df = load_energy_data()
    selected_district = st.selectbox("Select District", df['district'].unique())
    filtered_df = df[df['district'] == selected_district]

    st.metric("Total Energy Used", f"{filtered_df['energy_kwh'].sum():,.0f} kWh")

    st.subheader("Energy Usage Over Time")
    fig = px.area(filtered_df, x="date", y="energy_kwh", labels={"energy_kwh": "Energy (kWh)", "date": "Date"})
    st.plotly_chart(fig, use_container_width=True)
