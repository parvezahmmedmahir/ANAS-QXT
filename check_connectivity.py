"""
Check system_connectivity table status
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def check_connectivity():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print("   SYSTEM CONNECTIVITY STATUS")
    print("="*80 + "\n")
    
    cur.execute("SELECT * FROM system_connectivity ORDER BY last_heartbeat DESC")
    rows = cur.fetchall()
    
    if rows:
        print(f"Found {len(rows)} services:\n")
        for service_name, status, details, last_heartbeat in rows:
            print(f"Service: {service_name}")
            print(f"  Status: {status}")
            print(f"  Details: {details}")
            print(f"  Last Heartbeat: {last_heartbeat}")
            print()
    else:
        print("No connectivity data found.")
    
    conn.close()
    print("="*80 + "\n")

if __name__ == "__main__":
    check_connectivity()
