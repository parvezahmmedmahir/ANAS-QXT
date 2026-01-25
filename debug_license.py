
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"Testing connection to: {DATABASE_URL}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connection Successful!")
    
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM licenses")
    count = cur.fetchone()[0]
    print(f"Total licenses: {count}")
    
    test_key = "TSC"
    cur.execute("SELECT * FROM licenses WHERE key_code = %s", (test_key,))
    row = cur.fetchone()
    
    if row:
        print(f"Key {test_key} found: {row}")
    else:
        print(f"Key {test_key} NOT found!")
        
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
