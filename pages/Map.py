import streamlit as st
import pandas as pd
import plotly.express as px
import psutil
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap

# Set page to wide mode
st.set_page_config(layout="wide")

# ============================
# 📍 Geo Heatmap (Barangay Lemon)
# ============================

st.title("Brgy. Lemon Heatmap")
st.divider()

# Define the center of Barangay Lemon, Butuan City
barangay_lemon_coords = [8.942584, 125.593659]

# Sample heatmap data points near Barangay Lemon
heatmap_data = [
    [8.942584, 125.593659, 0.8],
    [8.942000, 125.594000, 0.6],
    [8.943500, 125.593200, 1.0]
]

# Microcontroller locations and statuses
microcontrollers = [
    {"name": "Sensor 1", "coords": [8.943000, 125.593800], "status": "Offline"},
    {"name": "Sensor 2", "coords": [8.942500, 125.594500], "status": "Offline"},
]

# Create an 8:4 column layout
col1, col2 = st.columns([8, 4])

# Store sensor statuses dynamically
sensor_status = {}

with col2:
    for index, mc in enumerate(microcontrollers, start=1):
        # Toggle switch with simple labels: Sensor 1, Sensor 2, etc.
        sensor_status[mc["name"]] = st.toggle(
            f"Sensor {index}",
            value=(mc["status"] == "Online")
        )
        
        # Update status based on user input
        mc["status"] = "Online" if sensor_status[mc["name"]] else "Offline"


# Create a Folium map centered at Barangay Lemon
m = folium.Map(location=barangay_lemon_coords, zoom_start=15)

# Add sensors to the map with dynamic colors
for mc in microcontrollers:
    folium.Marker(
        location=mc["coords"],
        popup=f"{mc['name']} - Status: {mc['status']}",
        icon=folium.Icon(color="green" if mc["status"] == "Online" else "red")
    ).add_to(m)

# Display updated map
with col1:
    folium_static(m)

# Display pie charts only for active (Online) sensors
with col2:
    for mc in microcontrollers:
        if mc["status"] == "Online":
            # Simulated system usage values
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent

            # Data for Pie Chart
            mc_health_data = pd.DataFrame({
                "Component": ["CPU Usage", "Memory Usage", "Disk Usage"],
                "Usage (%)": [cpu_usage, memory_usage, disk_usage]
            })

            # Create Pie Chart
            fig_pie = px.pie(mc_health_data, 
                             names="Component", 
                             values="Usage (%)", 
                             title=f"{mc['name']}",
                             hole=0.4,  
                             width=250, height=250,  
                             color_discrete_sequence=px.colors.qualitative.Set3)

            st.plotly_chart(fig_pie, use_container_width=False)
