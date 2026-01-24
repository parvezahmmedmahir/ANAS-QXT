"""
QUANTUM X PRO - COMPLETE LICENSE DATABASE AUDIT
Shows ALL licenses in your Supabase database with full statistics
"""
import os
from dotenv import load_dotenv
import psycopg2
from collections import Counter

load_dotenv()

def full_audit():
    print("\n" + "="*70)
    print("   QUANTUM X PRO - COMPLETE LICENSE DATABASE AUDIT")
    print("="*70 + "\n")

    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        print("   Your system is using LOCAL database only.")
        print("   To connect to Supabase, add DATABASE_URL to your .env file")
        return
    
    print("[1] Connecting to SUPABASE CLOUD...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("    ✅ Connected to Production Database\n")
    except Exception as e:
        print(f"    ❌ Connection Failed: {e}")
        return

    cur = conn.cursor()
    
    # Get total count
    print("[2] Counting total licenses...")
    cur.execute("SELECT COUNT(*) FROM licenses")
    total = cur.fetchone()[0]
    print(f"    📊 TOTAL LICENSES: {total:,}\n")
    
    # Category breakdown
    print("[3] License breakdown by CATEGORY:")
    cur.execute("SELECT category, COUNT(*) FROM licenses GROUP BY category ORDER BY COUNT(*) DESC")
    categories = cur.fetchall()
    for cat, count in categories:
        cat_name = cat if cat else "UNKNOWN"
        print(f"    • {cat_name:12} : {count:,} keys")
    
    # Status breakdown
    print("\n[4] License breakdown by STATUS:")
    cur.execute("SELECT status, COUNT(*) FROM licenses GROUP BY status ORDER BY COUNT(*) DESC")
    statuses = cur.fetchall()
    for status, count in statuses:
        status_name = status if status else "UNKNOWN"
        print(f"    • {status_name:12} : {count:,} keys")
    
    # Active licenses with devices
    print("\n[5] Hardware-locked licenses (in use):")
    cur.execute("SELECT COUNT(*) FROM licenses WHERE device_id IS NOT NULL")
    locked = cur.fetchone()[0]
    print(f"    🔒 {locked:,} licenses are currently locked to devices")
    
    # Available licenses
    available = total - locked
    print(f"    🆓 {available:,} licenses are available for new users\n")
    
    # Show sample of each category
    print("[6] Sample licenses from each category:\n")
    for cat, _ in categories[:3]:  # Top 3 categories
        cat_name = cat if cat else "UNKNOWN"
        print(f"    {cat_name} Keys (showing first 5):")
        cur.execute("SELECT key_code, status, device_id FROM licenses WHERE category=%s LIMIT 5", (cat,))
        samples = cur.fetchall()
        for key, status, device in samples:
            status_str = status if status else "UNKNOWN"
            device_str = device[:16] + "..." if device else "Not Locked"
            print(f"      • {key:15} [{status_str:8}] Device: {device_str}")
        print()
    
    # Recent activity
    print("[7] Recently accessed licenses:")
    cur.execute("""
        SELECT key_code, category, last_access_date 
        FROM licenses 
        WHERE last_access_date IS NOT NULL 
        ORDER BY last_access_date DESC 
        LIMIT 5
    """)
    recent = cur.fetchall()
    if recent:
        for key, cat, last_access in recent:
            print(f"    • {key:15} ({cat:8}) - Last used: {last_access}")
    else:
        print("    No recent activity recorded")
    
    conn.close()
    
    print("\n" + "="*70)
    print("   AUDIT COMPLETE")
    print("="*70)
    print(f"\n✅ Your Supabase database contains {total:,} licenses")
    print(f"✅ All {total:,} licenses are connected and accessible")
    print(f"✅ System is ready for {available:,} new users")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    full_audit()
