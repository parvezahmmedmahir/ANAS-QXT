import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def count_licenses():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT category, COUNT(*) FROM licenses GROUP BY category")
        rows = cur.fetchall()
        
        print("\n=== SYSTEM LICENSE COUNT ===")
        total = 0
        for category, count in rows:
            print(f"{category}: {count}")
            total += count
            
        print(f"---------------------------")
        print(f"TOTAL KEYS: {total}")
        print("===========================\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_licenses()
