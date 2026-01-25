import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_keys():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Keys to check (from generated_keys.txt)
        keys_to_check = [
            "Zz&1d^9A",  # Owner Key
            "y4P#s*T8",  # User Key
            "s!bJ#6W5"   # Trial Key
        ]
        
        print(f"Checking {len(keys_to_check)} sample keys from generated_keys.txt...")
        
        for key in keys_to_check:
            cur.execute("SELECT key_code, category, status FROM licenses WHERE key_code = %s", (key,))
            result = cur.fetchone()
            
            if result:
                print(f"[FOUND] Key: {key} | Category: {result[1]} | Status: {result[2]}")
            else:
                print(f"[MISSING] Key: {key} NOT found in database!")

        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    check_keys()
