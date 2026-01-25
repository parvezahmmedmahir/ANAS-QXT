import sqlite3
import os
import datetime
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def add_master_key():
    print("\n" + "="*50)
    print("   QUANTUM X PRO - MASTER KEY REPAIR TOOL")
    print("="*50 + "\n")

    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if DATABASE_URL:
        print("[DB] Target: REMOTE SUPABASE CLOUD")
        try:
            conn = psycopg2.connect(DATABASE_URL)
            db_type = 'postgres'
        except Exception as e:
            print(f"❌ SUPABASE CONNECTION ERROR: {e}")
            return
    else:
        print("[DB] Target: LOCAL SECURITY.DB")
        conn = sqlite3.connect("security.db")
        db_type = 'sqlite'

    cur = conn.cursor()
    
    # 1. Ensure table exists
    if db_type == 'postgres':
        cur.execute("CREATE TABLE IF NOT EXISTS licenses (key_code TEXT PRIMARY KEY, category TEXT, status TEXT, device_id TEXT, expiry_date TIMESTAMP)")
    else:
        cur.execute("CREATE TABLE IF NOT EXISTS licenses (key_code TEXT PRIMARY KEY, category TEXT, status TEXT, device_id TEXT, expiry_date TIMESTAMP)")

    # 2. Add a known MASTER key for testing
    master_key = "QX-MASTER-2026"
    expiry = (datetime.datetime.utcnow() + datetime.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        if db_type == 'postgres':
            cur.execute("INSERT INTO licenses (key_code, category, status, expiry_date) VALUES (%s, %s, %s, %s) ON CONFLICT (key_code) DO NOTHING", 
                       (master_key, 'OWNER', 'ACTIVE', expiry))
        else:
            cur.execute("INSERT OR IGNORE INTO licenses (key_code, category, status, expiry_date) VALUES (?, ?, ?, ?)", 
                       (master_key, 'OWNER', 'ACTIVE', expiry))
        
        conn.commit()
        print(f"✅ SUCCESS: Master Key '{master_key}' is now active in your {db_type} database.")
        print(f"Category: OWNER | Expiry: {expiry}")
        print("\nUse this key to log in and verify your system works.")
        
    except Exception as e:
        print(f"❌ ERROR ADDING KEY: {e}")
        
    conn.close()
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    add_master_key()
