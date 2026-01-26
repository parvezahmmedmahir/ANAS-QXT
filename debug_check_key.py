
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_key():
    key = "!*6wSh9A"
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM licenses WHERE key_code=%s", (key,))
        row = cur.fetchone()
        
        print(f"Checking Key: {key}")
        if row:
            print("Found:", row)
        else:
            print("Key NOT found via exact match.")
            # Try upper
            cur.execute("SELECT * FROM licenses WHERE UPPER(key_code)=UPPER(%s)", (key,))
            row = cur.fetchone()
            if row:
                print("Found via UPPER match:", row)
            else:
                print("Key does not exist at all.")
                
        cur.close()
        conn.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_key()
