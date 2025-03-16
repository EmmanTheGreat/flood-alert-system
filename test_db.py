import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database credentials
DB_HOST = os.getenv("DB_HOST", "http://localhost:8501")
DB_NAME = os.getenv("DB_NAME", "Flood_Alert_System")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "1234")
DB_PORT = os.getenv("DB_PORT", "5432")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    print("✅ Successfully connected to PostgreSQL!")
    conn.close()
except Exception as e:
    print("❌ Error connecting to database:", e)
