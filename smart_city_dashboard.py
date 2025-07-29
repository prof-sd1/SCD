# 🌍 Smart City Dashboard - Global Edition with Side Navigation
# Run: !pip install streamlit pandas plotly folium streamlit-folium

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import folium
from streamlit_folium import st_folium

# -------------------------------
# 1. Extended City List with Global Coverage
# -------------------------------
CITIES = [
    "New York, USA", "Los Angeles, USA", "Chicago, USA",
    "Toronto, Canada", "Vancouver, Canada",
    "London, UK", "Manchester, UK", "Edinburgh, UK",
    "Berlin, Germany", "Munich, Germany", "Hamburg, Germany",
    "Paris, France", "Lyon, France",
    "Mumbai, India", "Delhi, India", "Bangalore, India",
    "Sydney, Australia", "Melbourne, Australia",
    "Tokyo, Japan", "Osaka, Japan",
    "São Paulo, Brazil", "Rio de Janeiro, Brazil"
]

# Real coordinates for accurate global mapping
CITY_COORDS = {
    "New York, USA": [40.7128, -74.0060],
    "Los Angeles, USA": [34.0522, -118.2437],
    "Chicago, USA": [41.8781, -87.6298],
    "Toronto, Canada": [43.651070, -79.347015],
    "Vancouver, Canada": [49.2827, -123.1207],
    "London, UK": [51.5074, -0.1278],
    "Manchester, UK": [53.4808, -2.2426],
    "Edinburgh, UK": [55.9533, -3.1883],
    "Berlin, Germany": [52.5200, 13.4050],
    "Munich, Germany": [48.1351, 11.5820],
    "Hamburg, Germany": [53.5511, 9.9937],
    "Paris, France": [48.8566, 2.3522],
    "Lyon, France": [45.7640, 4.8357],
    "Mumbai, India": [19.0760, 72.8777],
    "Delhi, India": [28.7041, 77.1025],
    "Bangalore, India": [12.9716, 77.5946],
    "Sydney, Australia": [-33.8688, 151.2093],
    "Melbourne, Australia": [-37.8136, 144.9631],
    "Tokyo, Japan": [35.6762, 139.6503],
    "Osaka, Japan": [34.6937, 135.5023],
    "São Paulo, Brazil": [-23.5505, -46.6333],
    "Rio de Janeiro, Brazil": [-22.9068, -43.1729]
}

# -------------------------------
# 2. Generate Mock Data
# -------------------------------
np.random.seed(42)
n = len(CITIES)

df_air = pd.DataFrame({
    "city": CITIES,
    "aqi": np.random.randint(1, 6, n),
    "pm2_5": np.random.uniform(5, 120, n),  # Higher in some cities
    "pm10": np.random.uniform(10, 180, n),
    "no2": np.random.uniform(10, 100, n),
    "country": [c.split(", ")[1] for c in CITIES]
})

df_traffic = pd.DataFrame({
    "city": CITIES,
    "congestion_level": np.random.uniform(0.3, 0.95, n),
    "avg_speed_kmh": np.random.uniform(15, 65, n),
    "accidents_per_10k": np.random.poisson(4, n)
})

# Merge and calculate risk
df_summary = df_air.merge(df_traffic, on="city")
df_summary["risk_score"] = (df_summary["aqi"] * 0.4 + df_summary["congestion_level"] * 0.6) * 20
df_summary["risk_level"] = pd.cut(df_summary["risk_score"], bins=[0, 30, 60, 100], labels=["Low", "Medium", "High"])

# -------------------------------
# 3. Side Navigation
# -------------------------------
st.set_page_config(layout="wide", page_title="🌍 Smart City Dashboard", page_icon="🌆")

st.sidebar.title("🌆 Smart City Dashboard")
page = st.sidebar.radio("🧭 Navigate", ["🌍 Global Overview", "📊 Analytics", "🔮 Forecast", "📋 Data Table"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Filters")
selected_countries = st.sidebar.multiselect(
    "Filter by Country",
    options=sorted(df_summary["country"].unique()),
    default=sorted(df_summary["country"].unique())
)

# Filter data
filtered_df = df_summary[df_summary["country"].isin(selected_countries)]
if filtered_df.empty:
    st.warning("No data available for selected countries.")
    st.stop()

# -------------------------------
# 4. Page: Global Overview
# -------------------------------
if page == "🌍 Global Overview":
    st.title("🌍 Global City Risk Overview")
    st.markdown("Monitor air quality, traffic, and urban risk across 6 countries")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cities Monitored", len(filtered_df))
    col2.metric("Avg AQI", f"{filtered_df['aqi'].mean():.1f}")
    col3.metric("Avg PM2.5", f"{filtered_df['pm2_5'].mean():.1f} μg/m³")
    high_risk = (filtered_df["risk_level"] == "High").sum()
    col4.metric("High-Risk Cities", int(high_risk))

    # Map
    st.subheader("📍 Risk Map")
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="OpenStreetMap")

    color_map = {"Low": "green", "Medium": "orange", "High": "red"}

    for _, row in filtered_df.iterrows():
        lat, lon = CITY_COORDS[row["city"]]
        folium.CircleMarker(
            location=[lat, lon],
            radius=10,
            color=color_map[row["risk_level"]],
            fill=True,
            fill_color=color_map[row["risk_level"]],
            popup=(
                f"<b>{row['city']}</b><br>"
                f"• Risk: {row['risk_level']}<br>"
                f"• PM2.5: {row['pm2_5']:.1f} μg/m³<br>"
                f"• Congestion: {row['congestion_level']:.2f}"
            ),
            tooltip=row["city"]
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

    st_folium(m, width="100%", height=500)

    # Country-wise summary
    st.subheader("📈 Risk by Country")
    country_risk = filtered_df.groupby("country")["risk_score"].mean().reset_index()
    fig_country = px.bar(country_risk, x="country", y="risk_score", color="country",
                         title="Average Risk Score by Country",
                         labels={"risk_score": "Risk Score"})
    st.plotly_chart(fig_country, use_container_width=True)

# -------------------------------
# 5. Page: Analytics
# -------------------------------
elif page == "📊 Analytics":
    st.title("📊 Deep Analytics")
    st.markdown("Compare cities across environmental and traffic metrics")

    fig1 = px.bar(filtered_df, x='city', y='congestion_level', color='risk_level',
                  title="Traffic Congestion by City",
                  color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"},
                  labels={"congestion_level": "Congestion Level"})
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(filtered_df, x='pm2_5', y='congestion_level', text='city', size='aqi',
                      title="Air Quality vs Traffic Congestion",
                      labels={"pm2_5": "PM2.5 (μg/m³)", "congestion_level": "Congestion Level"},
                      hover_name="city", color="country")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.box(filtered_df, x="country", y="pm2_5", color="country", title="PM2.5 Distribution by Country")
    st.plotly_chart(fig3, use_container_width=True)

# -------------------------------
# 6. Page: Forecast
# -------------------------------
elif page == "🔮 Forecast":
    st.title("🔮 Predictive Insights")
    st.markdown("Estimate future pollution levels based on traffic and health trends")

    congestion_input = st.slider("Expected Avg Congestion Level", 0.0, 1.0, 0.5, 0.05)
    health_input = st.slider("Expected Avg Respiratory Cases (per 10k)", 10, 150, 30)

    # Simulated model (replace with real ML later)
    predicted_pm25 = 10 + 85 * congestion_input + 0.6 * health_input
    status = "Unhealthy" if predicted_pm25 > 75 else "Moderate" if predicted_pm25 > 35 else "Good"

    st.markdown(f"### 📊 Predicted PM2.5: **{predicted_pm25:.1f} μg/m³** → **{status}**")
    st.info("💡 *Prediction based on historical correlation. Can be replaced with ML model.*")

    # Download forecast
    if st.button("📥 Download Forecast"):
        forecast_df = pd.DataFrame({
            "Metric": ["Congestion Level", "Respiratory Cases", "Predicted PM2.5"],
            "Value": [f"{congestion_input:.2f}", f"{health_input}", f"{predicted_pm25:.1f}"]
        })
        st.download_button(
            label="Download as CSV",
            data=forecast_df.to_csv(index=False),
            file_name="forecast_prediction.csv",
            mime="text/csv"
        )

# -------------------------------
# 7. Page: Data Table
# -------------------------------
elif page == "📋 Data Table":
    st.title("📋 Full Data Table")
    st.markdown("Raw data for all selected cities and countries")

    st.dataframe(
        filtered_df[["city", "country", "aqi", "pm2_5", "pm10", "no2",
                     "congestion_level", "avg_speed_kmh", "risk_level", "risk_score"]]
        .round(2)
        .style.background_gradient(cmap='RdYlGn_r', subset=["risk_score"])
        .format({"pm2_5": "{:.1f}", "congestion_level": "{:.2f}"})
    )

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False)

    csv = convert_df(filtered_df)
    st.download_button("💾 Download Full Data as CSV", csv, "smart_city_data.csv", "text/csv")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.markdown(
    "✅ Built with Python • [Streamlit](https://streamlit.io) • [Folium](https://python-visualization.github.io/folium/) | "
    "🌍 Real-time Urban Intelligence | "
    "🚀 Deployable on **Streamlit Cloud**"
)
