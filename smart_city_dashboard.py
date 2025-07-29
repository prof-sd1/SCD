# 🌆 FINAL SMART CITY DASHBOARD - Google Colab Version

# -------------------------------
# Step 1: Install Required Libraries (Run this only once per session)
# -------------------------------
# Uncomment and run if packages are not installed
# !pip install streamlit pyngrok folium streamlit-folium pandas plotly numpy

# -------------------------------
# Step 2: Import Libraries
# -------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import folium
from streamlit_folium import st_folium

# -------------------------------
# Step 3: Mock Data with Real City Coordinates
# -------------------------------
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]

# Real coordinates for accurate mapping
city_locations = {
    "New York": [40.7128, -74.0060],
    "Los Angeles": [34.0522, -118.2437],
    "Chicago": [41.8781, -87.6298],
    "Houston": [29.7604, -95.3698],
    "Phoenix": [33.4484, -112.0740]
}

# Simulated data
np.random.seed(42)
df_air = pd.DataFrame({
    "city": CITIES,
    "aqi": np.random.randint(1, 6, 5),  # 1-5 scale
    "pm2_5": np.random.uniform(5, 100, 5),
    "pm10": np.random.uniform(10, 150, 5),
    "no2": np.random.uniform(10, 80, 5)
})

df_traffic = pd.DataFrame({
    "city": CITIES,
    "congestion_level": np.random.uniform(0.3, 0.9, 5),
    "avg_speed_kmh": np.random.uniform(20, 60, 5)
})

# Merge and calculate risk score
df_summary = df_air[["city", "aqi", "pm2_5"]].merge(df_traffic[["city", "congestion_level"]], on="city")
df_summary["risk_score"] = (df_summary["aqi"] * 0.4 + df_summary["congestion_level"] * 0.6) * 20
df_summary["risk_level"] = pd.cut(df_summary["risk_score"], bins=[0, 30, 60, 100], labels=["Low", "Medium", "High"])

# -------------------------------
# Step 4: Streamlit Dashboard
# -------------------------------
st.set_page_config(layout="wide", page_title="🌆 Smart City Dashboard")

st.title("🌆 Smart City Dashboard")
st.markdown("Real-time urban analytics for smarter cities | 🏙️ Air Quality + Traffic + Risk Forecast")

# Sidebar Filters
st.sidebar.header("🔍 Filters")
selected_cities = st.sidebar.multiselect(
    "Select Cities",
    CITIES,
    default=CITIES
)

df_filtered = df_summary[df_summary.city.isin(selected_cities)]

# Handle empty selection
if df_filtered.empty:
    st.warning("No cities selected. Please choose at least one city.")
else:
    # Metrics
    st.header("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Air Quality Index", f"{df_filtered['aqi'].mean():.1f}/5")
    col2.metric("Avg Congestion Level", f"{df_filtered['congestion_level'].mean():.2f}")
    col3.metric("Avg PM2.5", f"{df_filtered['pm2_5'].mean():.1f} μg/m³")
    high_risk_count = (df_filtered["risk_level"] == "High").sum()
    col4.metric("High Risk Cities", int(high_risk_count))

    # Risk Map
    st.header("📍 Risk Map")
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)  # USA center

    color_map = {"Low": "green", "Medium": "orange", "High": "red"}

    for _, row in df_filtered.iterrows():
        lat, lon = city_locations[row["city"]]
        folium.CircleMarker(
            location=[lat, lon],
            radius=12,
            color=color_map[row["risk_level"]],
            fill=True,
            fill_color=color_map[row["risk_level"]],
            popup=f"📍 {row['city']}\n"
                  f"• Risk: {row['risk_level']}\n"
                  f"• PM2.5: {row['pm2_5']:.1f} μg/m³\n"
                  f"• Congestion: {row['congestion_level']:.2f}",
            tooltip=f"{row['city']} - Click for details"
        ).add_to(m)

    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 180px; height: 110px;
                border:2px solid grey; z-index:9998; font-size:14px; background-color:white;
                padding: 10px; border-radius: 8px;">
    <b>Legend: Risk Level</b><br>
    <i style="color:green">●</i> Low (0–30)<br>
    <i style="color:orange">●</i> Medium (31–60)<br>
    <i style="color:red">●</i> High (61–100)
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=700, height=500)

    # Charts
    st.header("📈 Analytics")

    fig1 = px.bar(df_filtered, x='city', y='congestion_level', color='risk_level',
                  title="Traffic Congestion by City",
                  color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"},
                  labels={"congestion_level": "Congestion Level"})
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(df_filtered, x='pm2_5', y='congestion_level', text='city', size='aqi',
                      title="Air Quality vs Traffic Congestion",
                      labels={"pm2_5": "PM2.5 (μg/m³)", "congestion_level": "Congestion Level"},
                      hover_name="city")
    st.plotly_chart(fig2, use_container_width=True)

    # Forecast
    st.header("🔮 Forecast: Predicted PM2.5")
    congestion_input = st.slider("Expected Avg Congestion Level", 0.0, 1.0, 0.5)
    health_input = st.slider("Expected Avg Respiratory Cases (per 10k)", 10, 100, 30)

    # Simple predictive proxy (can be replaced with ML model)
    predicted_pm25 = 5 + 80 * congestion_input + 0.5 * health_input
    status = "Unhealthy" if predicted_pm25 > 75 else "Moderate" if predicted_pm25 > 35 else "Good"

    st.markdown(f"### 📊 Predicted PM2.5: **{predicted_pm25:.1f} μg/m³** → **{status}**")
    st.info("💡 *Prediction based on historical correlation. Replace with ML model in production.*")

# Footer
st.markdown("---")
st.markdown("✅ Built with Python • [Streamlit](https://streamlit.io) • [Folium](https://python-visualization.github.io/folium/) | "
            "Deployable on **Streamlit Cloud**")
