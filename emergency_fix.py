"""
QUANTUM X PRO - EMERGENCY LICENSE REPAIR SYSTEM
This script will diagnose and fix ALL license system issues
"""
import sqlite3
import os
import datetime
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def emergency_repair():
    print("\n" + "="*60)
    print("   QUANTUM X PRO - EMERGENCY LICENSE REPAIR")
    print("="*60 + "\n")

    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Connect to the appropriate database
    if DATABASE_URL:
        print("[1] Connecting to SUPABASE CLOUD...")
        try:
            conn = psycopg2.connect(DATABASE_URL)
            db_type = 'postgres'
            print("    ✅ SUPABASE Connected")
        except Exception as e:
            print(f"    ❌ SUPABASE Failed: {e}")
            print("\n[FALLBACK] Using LOCAL DATABASE...")
            conn = sqlite3.connect("security.db")
            db_type = 'sqlite'
    else:
        print("[1] Using LOCAL SQLITE DATABASE...")
        conn = sqlite3.connect("security.db")
        db_type = 'sqlite'

    cur = conn.cursor()
    
    # Step 1: Ensure table exists
    print("\n[2] Verifying 'licenses' table...")
    try:
        if db_type == 'postgres':
            cur.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    key_code TEXT PRIMARY KEY,
                    category TEXT,
                    status TEXT,
                    device_id TEXT,
                    usage_count INTEGER DEFAULT 0,
                    last_access_date TIMESTAMP,
                    expiry_date TIMESTAMP,
                    activation_date TIMESTAMP
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    key_code TEXT PRIMARY KEY,
                    category TEXT,
                    status TEXT,
                    device_id TEXT,
                    usage_count INTEGER DEFAULT 0,
                    last_access_date TIMESTAMP,
                    expiry_date TIMESTAMP,
                    activation_date TIMESTAMP
                )
            """)
        conn.commit()
        print("    ✅ Table verified")
    except Exception as e:
        print(f"    ❌ Table creation failed: {e}")
        return

    # Step 2: Check existing licenses
    print("\n[3] Scanning existing licenses...")
    cur.execute("SELECT key_code, category, status FROM licenses")
    existing = cur.fetchall()
    
    if existing:
        print(f"    Found {len(existing)} existing licenses:")
        for row in existing[:5]:  # Show first 5
            print(f"    - {row[0]} ({row[1]}) [{row[2]}]")
    else:
        print("    ⚠️  NO LICENSES FOUND")

    # Step 3: Add guaranteed working keys
    print("\n[4] Installing GUARANTEED MASTER KEYS...")
    
    expiry = (datetime.datetime.utcnow() + datetime.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
    
    master_keys = [
        ('QXMASTER', 'OWNER', 'ACTIVE'),
        ('ADMIN2026', 'OWNER', 'ACTIVE'),
        ('TESTKEY01', 'USER', 'ACTIVE'),
        ('TRIAL2026', 'TRIAL', 'ACTIVE'),
    ]
    
    for key, category, status in master_keys:
        try:
            if db_type == 'postgres':
                cur.execute("""
                    INSERT INTO licenses (key_code, category, status, expiry_date) 
                    VALUES (%s, %s, %s, %s) 
                    ON CONFLICT (key_code) DO UPDATE SET status='ACTIVE'
                """, (key, category, status, expiry))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO licenses (key_code, category, status, expiry_date) 
                    VALUES (?, ?, ?, ?)
                """, (key, category, status, expiry))
            print(f"    ✅ {key} ({category})")
        except Exception as e:
            print(f"    ❌ {key} failed: {e}")
    
    conn.commit()
    
    # Step 4: Verify installation
    print("\n[5] VERIFICATION - Testing key lookup...")
    test_key = 'QXMASTER'
    
    if db_type == 'postgres':
        cur.execute("SELECT * FROM licenses WHERE UPPER(key_code)=%s", (test_key,))
    else:
        cur.execute("SELECT * FROM licenses WHERE UPPER(key_code)=?", (test_key,))
    
    result = cur.fetchone()
    
    if result:
        print(f"    ✅ SUCCESS: Key '{test_key}' is accessible")
        print(f"    Database: {db_type.upper()}")
    else:
        print(f"    ❌ CRITICAL: Key lookup failed!")
    
    conn.close()
    
    print("\n" + "="*60)
    print("   REPAIR COMPLETE")
    print("="*60)
    print("\n📋 WORKING LICENSE KEYS:")
    print("   • QXMASTER    (Owner - works on any device)")
    print("   • ADMIN2026   (Owner - works on any device)")
    print("   • TESTKEY01   (User - locks to first device)")
    print("   • TRIAL2026   (Trial - locks to first device)")
    print("\n🔧 NEXT STEPS:")
    print("   1. Make sure Python backend is running: python app.py")
    print("   2. Open index.html in browser")
    print("   3. Enter: QXMASTER")
    print("   4. Click UNLOCK")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    emergency_repair()
