"""
QUANTUM X PRO - VIEW COLLECTED TELEMETRY DATA
Shows what data is currently in your user_sessions and user_activity tables
"""
import os
from dotenv import load_dotenv
import psycopg2
import json

load_dotenv()

def view_telemetry_data():
    print("\n" + "="*80)
    print("   VIEWING YOUR EXISTING TELEMETRY DATA")
    print("="*80 + "\n")

    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 1. Check user_sessions table
    print("[1] USER_SESSIONS TABLE (Login Tracking)")
    print("-" * 80)
    
    cur.execute("SELECT COUNT(*) FROM user_sessions")
    total_sessions = cur.fetchone()[0]
    print(f"Total Sessions Logged: {total_sessions}\n")
    
    # Show latest 10 sessions
    cur.execute("""
        SELECT id, license_key, device_id, ip_address, user_agent, timestamp
        FROM user_sessions 
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    
    sessions = cur.fetchall()
    
    if sessions:
        print("Latest 10 Sessions:")
        for i, (id, key, device, ip, ua, ts) in enumerate(sessions, 1):
            print(f"\n  Session {i}:")
            print(f"    ID: {id}")
            print(f"    License: {key}")
            print(f"    Device: {device[:30]}...")
            print(f"    IP: {ip}")
            print(f"    Time: {ts}")
            
            # Try to parse user_agent JSON if it exists
            if ua:
                try:
                    ua_data = json.loads(ua)
                    print(f"    Browser: {ua_data.get('browser', 'N/A')}")
                    print(f"    OS: {ua_data.get('os', 'N/A')}")
                    print(f"    Location: {ua_data.get('location', 'N/A')}")
                    print(f"    ISP: {ua_data.get('isp', 'N/A')}")
                except:
                    print(f"    User Agent: {ua[:50]}...")
    else:
        print("  No sessions found yet.")
    
    # 2. Check user_activity table
    print("\n\n[2] USER_ACTIVITY TABLE (Activity Tracking)")
    print("-" * 80)
    
    cur.execute("SELECT COUNT(*) FROM user_activity")
    total_activity = cur.fetchone()[0]
    print(f"Total Activity Records: {total_activity}\n")
    
    # Show latest 10 activities
    cur.execute("""
        SELECT id, license_key, device_id, mouse_movements, clicks, current_url, timestamp
        FROM user_activity 
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    
    activities = cur.fetchall()
    
    if activities:
        print("Latest 10 Activities:")
        for i, (id, key, device, mouse, clicks, url, ts) in enumerate(activities, 1):
            print(f"\n  Activity {i}:")
            print(f"    ID: {id}")
            print(f"    License: {key}")
            print(f"    Device: {device[:30]}...")
            print(f"    Mouse Movements: {mouse}")
            print(f"    Clicks: {clicks}")
            print(f"    URL/Data: {url[:60] if url else 'N/A'}...")
            print(f"    Time: {ts}")
    else:
        print("  No activity found yet.")
    
    conn.close()
    
    print("\n" + "="*80)
    print("   EXPLANATION")
    print("="*80)
    print("""
These tables ALREADY EXIST in your Supabase database.
The telemetry system I built will ADD NEW ROWS to these tables when:
  1. A user logs in (adds to user_sessions)
  2. A user is active (adds to user_activity every 30 seconds)

The SQL queries I showed you are just to VIEW this data.
They don't create anything new - they just SHOW what's being collected.

When you deploy the updated app.py and users log in, you'll see:
  - user_sessions: IP, location, browser, OS, ISP, network info
  - user_activity: Continuous tracking data every 30 seconds
    """)
    print("="*80 + "\n")

if __name__ == "__main__":
    view_telemetry_data()
