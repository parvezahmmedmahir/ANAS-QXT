import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def reset_owner_keys():
    owner_keys = ["Zz&1d^9A", "R@s@4K8r", "1bPH0*t%"]
    
    print("Resetting Owner Keys to Fresh State...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        for key in owner_keys:
            # Set status to PENDING or ACTIVE (Owner keys usually stay ACTIVE or are pre-set)
            # But importantly, CLEAR the device_id so it has no "lock" history
            # And reset expiry just in case
            
            cur.execute("""
                UPDATE licenses 
                SET device_id = NULL, status = 'ACTIVE', expiry_date = NULL 
                WHERE key_code = %s
            """, (key,))
            
        conn.commit()
        print("Owner keys have been reset. Existing device locks (if any) are cleared.")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_owner_keys()
