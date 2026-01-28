
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    # TEST POOLER ON PORT 5432 (IPv4 Proxy)
    host = "aws-1-ap-south-1.pooler.supabase.com"
    port = "5432"
    database = "postgres"
    user = "postgres.cxflxjgtlwzxoltfphwt"
    password = "MahirANAS1122"
    
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    print(f"Testing POOLER on PORT 5432 (IPv4)...")
    try:
        conn = psycopg2.connect(db_url, connect_timeout=10)
        print("✅ SUCCESS: Connection established to Pooler on Port 5432!")
        conn.close()
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test_connection()
