import psycopg2
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Database Connection
def get_db_data():
    try:
        with psycopg2.connect(
            host="aws-0-us-east-2.pooler.supabase.com",
            port=6543,
            database="postgres",
            user="postgres.tsiiblalobzwtzcxuzck",
            password="flood-alert-system"
        ) as conn:
            query = "SELECT created_at, flow_rate_1, flow_rate_2, humidity_1, humidity_2, water_level_1, water_level_2 FROM sensor_data"
            df = pd.read_sql_query(query, conn)
            return df
    except psycopg2.OperationalError as e:
        st.error(f"❌ Database connection failed: {e}")
        return pd.DataFrame()

# Helper function to get latest value
def get_latest_value(df, column):
    return df[column].iloc[-1] if column in df and not df[column].empty else "N/A"

# Helper function to safely convert values to float
def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0

# Helper function to calculate risk level
def calculate_risk(flow_rate, humidity, water_level):
    if water_level > 2.5 or flow_rate > 100 or humidity > 80:
        return "High", "red"
    elif 1.5 <= water_level <= 2.5 or 50 <= flow_rate <= 100 or 60 <= humidity <= 80:
        return "Moderate", "yellow"
    else:
        return "Low", "green"

# Page Layout
st.set_page_config(layout="wide")
st.title("Flood Alert System Dashboard")
st.divider()

# Fetch Data
with st.spinner("Loading database data..."):
    db_data = get_db_data()

# Ensure the data is sorted by the latest timestamp
if not db_data.empty:
    db_data["created_at"] = pd.to_datetime(db_data["created_at"])
    db_data = db_data.sort_values(by="created_at", ascending=False)  # Sort by timestamp in descending order
    latest_row = db_data.iloc[0]  # Get the latest row

# Real-time Metrics
top_col1, top_col2, top_col3 = st.columns(3)

with top_col1:
    st.subheader("Flow Rate (L/s)")
    st.metric(label="Sensor 1", value=latest_row["flow_rate_1"])
    st.metric(label="Sensor 2", value=latest_row["flow_rate_2"])

with top_col2:
    st.subheader("Humidity (%)")
    st.metric(label="Sensor 1", value=latest_row["humidity_1"])
    st.metric(label="Sensor 2", value=latest_row["humidity_2"])

with top_col3:
    st.subheader("Water Level (m)")
    st.metric(label="Sensor 1", value=latest_row["water_level_1"])
    st.metric(label="Sensor 2", value=latest_row["water_level_2"])

# Filter data based on the entire date range
if not db_data.empty:
    db_data["created_at"] = pd.to_datetime(db_data["created_at"]).dt.tz_convert(None)
    db_data["time"] = db_data["created_at"].dt.strftime("%H:%M")  # Extract only hour and minute
    start_date = db_data["created_at"].min()
    end_date = db_data["created_at"].max()

    # Filter data based on the date range
    filtered_data = db_data[(db_data["created_at"] >= start_date) & (db_data["created_at"] <= end_date)]

    # Layout: Water Level Graph + Gauge in the same row
    col_graph, col_gauge = st.columns([7, 5])

    with col_graph:
        fig1 = px.line(filtered_data, x="time", y=["water_level_1", "water_level_2"],
                       title="Water Level Over Time (Sensor 1 & 2)", markers=True, line_shape="linear")
        st.plotly_chart(fig1, use_container_width=True)

    with col_gauge:
        flood_level_1 = safe_float(get_latest_value(db_data, "water_level_1"))
        flood_level_2 = safe_float(get_latest_value(db_data, "water_level_2"))
        flow_rate_1 = safe_float(get_latest_value(db_data, "flow_rate_1"))
        flow_rate_2 = safe_float(get_latest_value(db_data, "flow_rate_2"))
        humidity_1 = safe_float(get_latest_value(db_data, "humidity_1"))
        humidity_2 = safe_float(get_latest_value(db_data, "humidity_2"))

        # Compute averages
        avg_flood_level = (flood_level_1 + flood_level_2) / 2
        avg_flow_rate = (flow_rate_1 + flow_rate_2) / 2
        avg_humidity = (humidity_1 + humidity_2) / 2

        # Determine risk level
        risk, color = calculate_risk(avg_flow_rate, avg_humidity, avg_flood_level)

        # Create the single gauge
        fig_tachometer = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_flood_level,
            title={"text": f"<br>{risk} Risk", "font": {"size": 18}},
            gauge={
                "axis": {"range": [0, max(3, avg_flood_level + 0.5)], "tickwidth": 2},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 1.5], "color": "green"},  # Low risk
                    {"range": [1.5, 2.5], "color": "yellow"},  # Moderate risk
                    {"range": [2.5, 3], "color": "red"}  # High risk
                ],
                "borderwidth": 2,
                "bordercolor": "black",
            }
        ))

        fig_tachometer.update_layout(
            height=350,
            margin=dict(t=20, b=20, l=40, r=40)
        )

        st.plotly_chart(fig_tachometer, use_container_width=True)
