"""
QUANTUM X PRO - License Management Admin Script
Run this script to manage licenses in your database
"""

import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Connect to the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connected to database")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def list_all_licenses():
    """Display all licenses with their current status"""
    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            key_code,
            category,
            status,
            device_id,
            activation_date,
            expiry_date,
            usage_count,
            last_access_date,
            ip_address
        FROM licenses
        ORDER BY status, category, key_code
    """)
    
    licenses = cur.fetchall()
    
    print("\n" + "="*120)
    print(f"{'LICENSE KEY':<15} {'CATEGORY':<10} {'STATUS':<10} {'DEVICE':<25} {'ACTIVATED':<20} {'EXPIRES':<20} {'USES':<6} {'IP':<15}")
    print("="*120)
    
    for lic in licenses:
        key, cat, status, device, activated, expires, uses, last_access, ip = lic
        
        device_str = (device[:22] + "...") if device else "NOT BOUND"
        activated_str = activated.strftime("%Y-%m-%d %H:%M") if activated else "NEVER"
        expires_str = expires.strftime("%Y-%m-%d") if expires else "NEVER"
        uses_str = str(uses) if uses else "0"
        ip_str = ip if ip else "N/A"
        
        print(f"{key:<15} {cat:<10} {status:<10} {device_str:<25} {activated_str:<20} {expires_str:<20} {uses_str:<6} {ip_str:<15}")
    
    print("="*120)
    print(f"Total licenses: {len(licenses)}\n")
    
    cur.close()
    conn.close()

def create_license(key_code, category="USER", expiry_days=30):
    """Create a new license key"""
    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    # Calculate expiry date
    expiry_date = datetime.utcnow() + timedelta(days=expiry_days) if expiry_days > 0 else None
    
    try:
        cur.execute("""
            INSERT INTO licenses (key_code, category, status, expiry_date)
            VALUES (%s, %s, 'PENDING', %s)
        """, (key_code.upper(), category.upper(), expiry_date))
        
        conn.commit()
        print(f"✅ License created: {key_code.upper()}")
        print(f"   Category: {category.upper()}")
        print(f"   Status: PENDING")
        print(f"   Expires: {expiry_date.strftime('%Y-%m-%d') if expiry_date else 'NEVER'}")
    except Exception as e:
        print(f"❌ Failed to create license: {e}")
    
    cur.close()
    conn.close()

def activate_license(key_code):
    """Manually activate a PENDING license"""
    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE licenses 
            SET status = 'ACTIVE',
                activation_date = CURRENT_TIMESTAMP
            WHERE UPPER(key_code) = %s
            RETURNING key_code, status
        """, (key_code.upper(),))
        
        result = cur.fetchone()
        if result:
            conn.commit()
            print(f"✅ License activated: {result[0]}")
        else:
            print(f"❌ License not found: {key_code}")
    except Exception as e:
        print(f"❌ Failed to activate license: {e}")
    
    cur.close()
    conn.close()

def block_license(key_code):
    """Block a license (prevent access)"""
    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE licenses 
            SET status = 'BLOCKED'
            WHERE UPPER(key_code) = %s
            RETURNING key_code
        """, (key_code.upper(),))
        
        result = cur.fetchone()
        if result:
            conn.commit()
            print(f"✅ License blocked: {result[0]}")
        else:
            print(f"❌ License not found: {key_code}")
    except Exception as e:
        print(f"❌ Failed to block license: {e}")
    
    cur.close()
    conn.close()

def reset_license(key_code):
    """Reset a license to PENDING state (unbind device)"""
    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE licenses 
            SET status = 'PENDING',
                device_id = NULL,
                ip_address = NULL,
                user_agent = NULL,
                activation_date = NULL,
                last_access_date = NULL,
                usage_count = 0
            WHERE UPPER(key_code) = %s
            RETURNING key_code
        """, (key_code.upper(),))
        
        result = cur.fetchone()
        if result:
            conn.commit()
            print(f"✅ License reset to PENDING: {result[0]}")
            print("   Device binding cleared")
            print("   User can activate again")
        else:
            print(f"❌ License not found: {key_code}")
    except Exception as e:
        print(f"❌ Failed to reset license: {e}")
    
    cur.close()
    conn.close()

def extend_license(key_code, days=30):
    """Extend license expiry date"""
    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE licenses 
            SET expiry_date = COALESCE(expiry_date, CURRENT_TIMESTAMP) + INTERVAL '%s days'
            WHERE UPPER(key_code) = %s
            RETURNING key_code, expiry_date
        """, (days, key_code.upper()))
        
        result = cur.fetchone()
        if result:
            conn.commit()
            print(f"✅ License extended: {result[0]}")
            print(f"   New expiry: {result[1].strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"❌ License not found: {key_code}")
    except Exception as e:
        print(f"❌ Failed to extend license: {e}")
    
    cur.close()
    conn.close()

def show_license_details(key_code):
    """Show detailed information about a specific license"""
    conn = get_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            key_code, category, status, device_id, 
            activation_date, expiry_date, usage_count,
            last_access_date, ip_address, user_agent
        FROM licenses
        WHERE UPPER(key_code) = %s
    """, (key_code.upper(),))
    
    lic = cur.fetchone()
    
    if not lic:
        print(f"❌ License not found: {key_code}")
        cur.close()
        conn.close()
        return
    
    print("\n" + "="*80)
    print(f"LICENSE DETAILS: {lic[0]}")
    print("="*80)
    print(f"Category:        {lic[1]}")
    print(f"Status:          {lic[2]}")
    print(f"Device ID:       {lic[3] if lic[3] else 'NOT BOUND'}")
    print(f"Activated:       {lic[4].strftime('%Y-%m-%d %H:%M:%S') if lic[4] else 'NEVER'}")
    print(f"Expires:         {lic[5].strftime('%Y-%m-%d %H:%M:%S') if lic[5] else 'NEVER'}")
    print(f"Usage Count:     {lic[6] if lic[6] else 0}")
    print(f"Last Access:     {lic[7].strftime('%Y-%m-%d %H:%M:%S') if lic[7] else 'NEVER'}")
    print(f"IP Address:      {lic[8] if lic[8] else 'N/A'}")
    print(f"User Agent:      {lic[9] if lic[9] else 'N/A'}")
    print("="*80 + "\n")
    
    # Show recent sessions
    cur.execute("""
        SELECT login_time, ip_address, platform
        FROM user_sessions
        WHERE license_key = %s
        ORDER BY login_time DESC
        LIMIT 5
    """, (lic[0],))
    
    sessions = cur.fetchall()
    if sessions:
        print("Recent Sessions:")
        print("-" * 80)
        for sess in sessions:
            print(f"  {sess[0].strftime('%Y-%m-%d %H:%M:%S')} | IP: {sess[1]} | Platform: {sess[2]}")
        print()
    
    cur.close()
    conn.close()

def main():
    """Main menu"""
    while True:
        print("\n" + "="*80)
        print("QUANTUM X PRO - LICENSE MANAGEMENT")
        print("="*80)
        print("1. List all licenses")
        print("2. Create new license")
        print("3. Show license details")
        print("4. Activate license (set to ACTIVE)")
        print("5. Block license")
        print("6. Reset license (unbind device)")
        print("7. Extend license expiry")
        print("0. Exit")
        print("="*80)
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            list_all_licenses()
        
        elif choice == "2":
            key = input("Enter license key: ").strip()
            category = input("Enter category (USER/OWNER) [USER]: ").strip() or "USER"
            days = input("Enter expiry days (0 for never) [30]: ").strip() or "30"
            create_license(key, category, int(days))
        
        elif choice == "3":
            key = input("Enter license key: ").strip()
            show_license_details(key)
        
        elif choice == "4":
            key = input("Enter license key to activate: ").strip()
            activate_license(key)
        
        elif choice == "5":
            key = input("Enter license key to block: ").strip()
            block_license(key)
        
        elif choice == "6":
            key = input("Enter license key to reset: ").strip()
            reset_license(key)
        
        elif choice == "7":
            key = input("Enter license key: ").strip()
            days = input("Enter days to extend [30]: ").strip() or "30"
            extend_license(key, int(days))
        
        elif choice == "0":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env file")
        print("Please set your Supabase connection string in .env")
        exit(1)
    
    main()
