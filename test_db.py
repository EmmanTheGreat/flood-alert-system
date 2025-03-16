import streamlit as st
from st_supabase_connection import SupabaseConnection

# Initialize connection.
conn = st.connection("supabase",type=SupabaseConnection)

# Perform query.
rows = conn.query("*", table="sensor_data", ttl="10m").execute()

# Print results.
for row in rows.data:
    st.write(f"{row['sensor1.flow_rate']} has a :{row['sensor1.humidity']}:")