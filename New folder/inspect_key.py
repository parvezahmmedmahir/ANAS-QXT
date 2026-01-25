import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def inspect_owner_key():
    key = "Zz&1d^9A"
    print(f"Inspecting Owner Key: {key}")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT key_code, category, status, device_id, expiry_date FROM licenses WHERE key_code = %s", (key,))
        row = cur.fetchone()
        
        if row:
            print(f"Key Found: {row[0]}")
            print(f"Category:  {row[1]}")
            print(f"Status:    {row[2]}")
            print(f"Device ID: {row[3]}")
            print(f"Expiry:    {row[4]}")
            
            # Logic check from app.py
            # if locked_device and category != 'OWNER':
            # Owner should bypass.
            
            if row[2] == 'BLOCKED':
                print("\n[CRITICAL] Key is BLOCKED.")
            elif row[2] == 'EXPIRED':
                print("\n[CRITICAL] Key is EXPIRED.")
            else:
                print("\n[INFO] Key looks healthy. It should work.")

        else:
            print("[ERROR] Key NOT found in DB.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_owner_key()
