
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def check_active_users():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found.")
        return

    # Use direct port 6543
    if ":6543" in db_url:
        db_url = db_url.replace(":6543", ":6543")

    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("--- QUANTUM X PRO USER ANALYSIS ---")
        
        # 1. Recent Sessions (Last 24 Hours)
        cur.execute("""
            SELECT license_key, device_id, ip_address, timestamp 
            FROM user_sessions 
            WHERE timestamp > NOW() - INTERVAL '24 hours'
            ORDER BY timestamp DESC
        """)
        sessions = cur.fetchall()
        print(f"\n[SESSIONS] Total sessions in last 24h: {len(sessions)}")
        for s in sessions[:10]:
            print(f" - Key: {s[0]} | Device: {s[1][:10]}... | Time: {s[3]}")

        # 2. Unique Active Users (Last 1 Hour)
        cur.execute("""
            SELECT COUNT(DISTINCT device_id) 
            FROM user_activity 
            WHERE timestamp > NOW() - INTERVAL '1 hour'
        """)
        active_1h = cur.fetchone()[0]
        print(f"\n[ACTIVITY] Unique devices active in last hour: {active_1h}")

        # 3. Latest Activity
        cur.execute("""
            SELECT license_key, current_url, timestamp 
            FROM user_activity 
            ORDER BY timestamp DESC LIMIT 5
        """)
        activities = cur.fetchall()
        print(f"\n[LATEST] Last 5 activities:")
        for a in activities:
            print(f" - Key: {a[0]} | Activity: {a[1][:50]}... | Time: {a[2]}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_active_users()
