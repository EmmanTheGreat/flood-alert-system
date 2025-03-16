import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables
load_dotenv()

# Database credentials
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

# Create database connection
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

# Fetch latest sensor data
def fetch_latest_sensor_data():
    conn = get_db_connection()
    query = "SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fetch historical sensor data
def fetch_historical_data():
    conn = get_db_connection()
    query = "SELECT timestamp, water_level FROM sensor_data ORDER BY timestamp DESC LIMIT 100"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Streamlit UI
st.set_page_config(layout="wide")
st.title("🌊 Flood Alert System Dashboard")
st.divider()

# Fetch latest sensor data
latest_data = fetch_latest_sensor_data()

if not latest_data.empty:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Flow Rate (L/s)")
        st.metric(label="Sensor Flow Rate", value=latest_data["flow_rate"].values[0])

    with col2:
        st.subheader("Humidity (%)")
        st.metric(label="Sensor Humidity", value=latest_data["humidity"].values[0])

    with col3:
        st.subheader("Water Level (m)")
        st.metric(label="Current Water Level", value=latest_data["water_level"].values[0])

    # Gauge Chart
    flood_level = float(latest_data["water_level"].values[0])
    fig_tachometer = go.Figure(go.Indicator(
        mode="gauge+number",
        value=flood_level,
        title={"text": "Flood Risk Level", "font": {"size": 20}},
        gauge={
            "axis": {"range": [1, 3]},  
            "bar": {"color": "black"},
            "steps": [
                {"range": [1, 1.5], "color": "green"},  # Low risk
                {"range": [1.5, 2.5], "color": "yellow"},  # Moderate risk
                {"range": [2.5, 3], "color": "red"}  # High risk
            ],
        }
    ))
    st.plotly_chart(fig_tachometer, use_container_width=True)

else:
    st.warning("⚠️ No sensor data available.")

# Fetch historical data
historical_data = fetch_historical_data()

# Display line chart for water levels
if not historical_data.empty:
    fig = px.line(historical_data, x="timestamp", y="water_level", title="📈 Water Level Over Time", markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No historical data available.")
