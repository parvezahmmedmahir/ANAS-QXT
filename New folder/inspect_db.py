import sqlite3
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def check_licenses():
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if DATABASE_URL:
        print("[DB] Connecting to Supabase...")
        try:
            conn = psycopg2.connect(DATABASE_URL)
            db_type = 'postgres'
        except Exception as e:
            print(f"[DB] Supabase connection failed: {e}")
            return
    else:
        print("[DB] Connecting to local SQLite...")
        conn = sqlite3.connect("security.db")
        db_type = 'sqlite'

    cur = conn.cursor()
    
    print("\n" + "="*50)
    print(f"   CURRENT LICENSES IN {db_type.upper()}")
    print("="*50)
    
    try:
        cur.execute("SELECT key_code, category, status, device_id, expiry_date FROM licenses")
        rows = cur.fetchall()
        
        if not rows:
            print("\n❌ NO LICENSES FOUND IN DATABASE!")
            print("You must add at least one license to the 'licenses' table.")
        else:
            for row in rows:
                print(f"Key: {row[0]} | Cat: {row[1]} | Status: {row[2]} | Device: {row[3]} | Exp: {row[4]}")
                
    except Exception as e:
        print(f"Error reading licenses: {e}")
        print("\nPossible reason: Table 'licenses' might not exist yet.")
        
    print("="*50 + "\n")
    conn.close()

if __name__ == "__main__":
    check_licenses()
