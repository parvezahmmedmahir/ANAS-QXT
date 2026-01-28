
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    # Use EXACT information provided by user
    host = "aws-1-ap-south-1.pooler.supabase.com"
    port = "6543"
    database = "postgres"
    user = "postgres.cxflxjgtlwzxoltfphwt"
    password = "MahirANAS1122" # From .env
    
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    print(f"Testing connection to: {host}:{port}...")
    try:
        conn = psycopg2.connect(db_url, connect_timeout=10)
        print("✅ SUCCESS: Connection established to Port 6543!")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        print(f"DB Version: {cur.fetchone()}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test_connection()
