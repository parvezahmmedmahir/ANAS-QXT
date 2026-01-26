import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn, 'postgres'
        except:
            pass
    return None, None

def inspect_db():
    conn, db_type = get_db_connection()
    if not conn: return
    cur = conn.cursor()
    
    print(f"Inspecting {db_type} for potentially loose keys...")
    
    # Check for empty or very short device_id
    cur.execute("SELECT key_code, device_id, status FROM licenses WHERE device_id = '' OR length(device_id) < 5")
    rows = cur.fetchall()
    print(f"Found {len(rows)} licenses with empty or short device_id")
    for row in rows:
        print(row)
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect_db()
