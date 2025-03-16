import psycopg2
import pandas as pd
import streamlit as st

try:
    conn = psycopg2.connect(
        host="aws-0-us-east-2.pooler.supabase.com",
        port=6543,
        database="postgres",
        user="postgres.tsiiblalobzwtzcxuzck",
        password="flood-alert-system"
    )
    print("✅ Connected successfully!")

    # Perform query
    query = "SELECT * FROM sensor_data"
    df = pd.read_sql(query, conn)
    print(df)
    st.write(df)

    conn.close()
except psycopg2.OperationalError as e:
    print(f"❌ Connection failed: {e}")
