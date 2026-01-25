"""
QUANTUM X PRO - COMPLETE SYSTEM ANALYSIS
Final deep inspection of all components
"""
import os
from dotenv import load_dotenv
import psycopg2
from collections import defaultdict

load_dotenv()

def complete_system_analysis():
    print("\n" + "="*100)
    print(" "*30 + "QUANTUM X PRO - FINAL SYSTEM ANALYSIS")
    print("="*100 + "\n")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ CRITICAL: DATABASE_URL not found in .env")
        return
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 1. DATABASE TABLES
    print("[1] DATABASE STRUCTURE")
    print("-" * 100)
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    print(f"✅ Found {len(tables)} tables:")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"   • {t:30} ({count:,} rows)")
    
    # 2. LICENSES ANALYSIS
    print("\n[2] LICENSE SYSTEM ANALYSIS")
    print("-" * 100)
    
    # Total licenses
    cur.execute("SELECT COUNT(*) FROM licenses")
    total_licenses = cur.fetchone()[0]
    print(f"Total Licenses: {total_licenses:,}")
    
    # By category
    cur.execute("SELECT category, COUNT(*) FROM licenses GROUP BY category ORDER BY COUNT(*) DESC")
    print("\nBy Category:")
    for cat, count in cur.fetchall():
        print(f"   • {cat or 'NULL':15} : {count:,}")
    
    # By status
    cur.execute("SELECT status, COUNT(*) FROM licenses GROUP BY status ORDER BY COUNT(*) DESC")
    print("\nBy Status:")
    for status, count in cur.fetchall():
        print(f"   • {status or 'NULL':15} : {count:,}")
    
    # Active with device
    cur.execute("SELECT COUNT(*) FROM licenses WHERE device_id IS NOT NULL")
    locked = cur.fetchone()[0]
    print(f"\nHardware-Locked: {locked:,} licenses")
    print(f"Available: {total_licenses - locked:,} licenses")
    
    # Check if licenses table has all required columns
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'licenses'
        ORDER BY ordinal_position
    """)
    license_cols = [row[0] for row in cur.fetchall()]
    required_cols = ['key_code', 'category', 'status', 'device_id', 'ip_address', 
                     'activation_date', 'expiry_date', 'usage_count', 'last_access_date', 'user_agent']
    
    print("\nLicense Table Columns:")
    for col in required_cols:
        status = "✅" if col in license_cols else "❌ MISSING"
        print(f"   {status} {col}")
    
    # 3. TELEMETRY TABLES
    print("\n[3] TELEMETRY SYSTEM ANALYSIS")
    print("-" * 100)
    
    # user_sessions
    cur.execute("SELECT COUNT(*) FROM user_sessions")
    sessions = cur.fetchone()[0]
    print(f"Total Sessions Logged: {sessions:,}")
    
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'user_sessions'
        ORDER BY ordinal_position
    """)
    session_cols = [row[0] for row in cur.fetchall()]
    required_session_cols = ['id', 'license_key', 'device_id', 'ip_address', 'user_agent', 
                              'timezone', 'resolution', 'platform', 'login_time']
    
    print("\nuser_sessions Columns:")
    for col in required_session_cols:
        status = "✅" if col in session_cols else "❌ MISSING"
        print(f"   {status} {col}")
    
    # user_activity
    cur.execute("SELECT COUNT(*) FROM user_activity")
    activities = cur.fetchone()[0]
    print(f"\nTotal Activity Records: {activities:,}")
    
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'user_activity'
        ORDER BY ordinal_position
    """)
    activity_cols = [row[0] for row in cur.fetchall()]
    required_activity_cols = ['id', 'license_key', 'device_id', 'mouse_movements', 'clicks', 
                               'scrolls', 'key_presses', 'session_duration', 'current_url', 
                               'page_title', 'timestamp']
    
    print("\nuser_activity Columns:")
    for col in required_activity_cols:
        status = "✅" if col in activity_cols else "❌ MISSING"
        print(f"   {status} {col}")
    
    # 4. CONNECTIVITY TRACKING
    print("\n[4] SYSTEM CONNECTIVITY")
    print("-" * 100)
    cur.execute("SELECT service_name, status, last_heartbeat FROM system_connectivity ORDER BY service_name")
    for service, status, heartbeat in cur.fetchall():
        status_icon = "✅" if status == "ONLINE" else "⚠️"
        print(f"   {status_icon} {service:20} : {status:15} (Last: {heartbeat})")
    
    # 5. SIGNAL TRACKING
    print("\n[5] WIN RATE TRACKING")
    print("-" * 100)
    cur.execute("SELECT COUNT(*) FROM win_rate_tracking")
    signals = cur.fetchone()[0]
    print(f"Total Signals Tracked: {signals:,}")
    
    cur.execute("SELECT broker, COUNT(*) FROM win_rate_tracking GROUP BY broker")
    print("\nBy Broker:")
    for broker, count in cur.fetchall():
        print(f"   • {broker:15} : {count:,}")
    
    # 6. RECENT ACTIVITY
    print("\n[6] RECENT SYSTEM ACTIVITY")
    print("-" * 100)
    
    # Most recent logins
    cur.execute("""
        SELECT license_key, device_id, ip_address, login_time 
        FROM user_sessions 
        ORDER BY login_time DESC 
        LIMIT 5
    """)
    print("Recent Logins (Last 5):")
    for key, device, ip, time in cur.fetchall():
        print(f"   • {key:15} | Device: {device[:20]}... | IP: {ip:15} | {time}")
    
    # Most active licenses
    cur.execute("""
        SELECT key_code, usage_count, last_access_date 
        FROM licenses 
        WHERE usage_count > 0 
        ORDER BY usage_count DESC 
        LIMIT 5
    """)
    print("\nMost Active Licenses:")
    for key, count, last_access in cur.fetchall():
        print(f"   • {key:15} | Used {count:3} times | Last: {last_access}")
    
    # 7. DATA QUALITY CHECK
    print("\n[7] DATA QUALITY ANALYSIS")
    print("-" * 100)
    
    # Licenses with complete data
    cur.execute("""
        SELECT COUNT(*) FROM licenses 
        WHERE device_id IS NOT NULL 
        AND ip_address IS NOT NULL 
        AND user_agent IS NOT NULL
    """)
    complete = cur.fetchone()[0]
    print(f"Licenses with Complete Telemetry: {complete:,} / {total_licenses:,}")
    
    # Sessions with full data
    cur.execute("""
        SELECT COUNT(*) FROM user_sessions 
        WHERE user_agent IS NOT NULL 
        AND timezone IS NOT NULL 
        AND resolution IS NOT NULL
    """)
    complete_sessions = cur.fetchone()[0]
    print(f"Sessions with Full Data: {complete_sessions:,} / {sessions:,}")
    
    conn.close()
    
    # 8. FILE SYSTEM CHECK
    print("\n[8] CODE FILES CHECK")
    print("-" * 100)
    
    critical_files = [
        'app.py',
        'index.html',
        'quantum_telemetry.js',
        'brokers/quotex_ws.py',
        '.env'
    ]
    
    for file in critical_files:
        path = os.path.join(os.getcwd(), file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   ✅ {file:30} ({size:,} bytes)")
        else:
            print(f"   ❌ {file:30} MISSING")
    
    print("\n" + "="*100)
    print(" "*35 + "ANALYSIS COMPLETE")
    print("="*100 + "\n")

if __name__ == "__main__":
    complete_system_analysis()
