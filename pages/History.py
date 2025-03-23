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
            query = "SELECT created_at as date_time ,flow_rate_1, flow_rate_2, humidity_1, humidity_2, water_level_1, water_level_2 FROM sensor_data"
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
st.title("Data Table")
st.divider()

# Fetch Data
with st.spinner("Loading database data..."):
    db_data = get_db_data()
    if not db_data.empty:
        st.write(db_data)


db_data_display = db_data.drop(columns=["date_time"])

# Sidebar Date Selection
st.sidebar.subheader("Select Date Range")
if not db_data.empty:
    db_data["date_time"] = pd.to_datetime(db_data["date_time"]).dt.tz_convert(None)
    start_date = st.sidebar.date_input("Start Date", db_data["date_time"].min().date())
    end_date = st.sidebar.date_input("End Date", db_data["date_time"].max().date())
    
    # Convert selected dates to datetime format
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data based on the selected date range
    filtered_data = db_data[(db_data["date_time"] >= start_date) & (db_data["date_time"] <= end_date)]

    # Layout: Water Level Graph + Gauge in the same row
    col_graph, col_gauge = st.columns([9, 3])


