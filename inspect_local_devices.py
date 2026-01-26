import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def inspect_licenses():
    if os.path.exists("security.db"):
        conn = sqlite3.connect("security.db")
        cur = conn.cursor()
        print("Connected to LOCAL sqlite (security.db)")
        query = "SELECT key_code, device_id, status FROM licenses WHERE device_id IS NOT NULL AND device_id != '' LIMIT 10"
        cur.execute(query)
        rows = cur.fetchall()
        print(f"Found {len(rows)} licenses with assigned device_id")
        for row in rows:
            print(row)
        cur.close()
        conn.close()
    else:
        print("security.db does not exist")

if __name__ == "__main__":
    inspect_licenses()
