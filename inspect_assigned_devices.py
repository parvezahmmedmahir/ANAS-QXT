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
    
    conn = sqlite3.connect("security.db")
    return conn, 'sqlite'

def inspect_licenses():
    conn, db_type = get_db_connection()
    cur = conn.cursor()
    
    print(f"Connected to {db_type}")
    
    # Show some rows that HAVE a device_id
    query = "SELECT key_code, device_id, status FROM licenses WHERE device_id IS NOT NULL AND device_id != '' LIMIT 10"
    cur.execute(query)
    rows = cur.fetchall()
    
    print(f"Found {len(rows)} licenses with assigned device_id")
    for row in rows:
        print(row)
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect_licenses()
