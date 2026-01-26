
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def test_update():
    if not DATABASE_URL:
        print("No DATABASE_URL found.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Pick a text key
        test_key = "Zz&1d^9A" # Owner key
        print(f"Testing UPDATE on key: {test_key}")
        
        # Check current count
        cur.execute("SELECT usage_count FROM licenses WHERE key_code=%s", (test_key,))
        row = cur.fetchone()
        if not row:
            print("Key not found!")
            return
        initial_count = row[0] or 0
        print(f"Initial Count: {initial_count}")
        
        # Attempt Update
        cur.execute("UPDATE licenses SET usage_count = usage_count + 1 WHERE key_code=%s", (test_key,))
        rows_affected = cur.rowcount
        print(f"Rows Affected: {rows_affected}")
        
        if rows_affected == 0:
            print("❌ UPDATE FAILED (0 rows affected). This confirms RLS or Permissions issue.")
        else:
            print("✅ UPDATE SUCCESSFUL.")
            conn.commit()
            
            # Verify
            cur.execute("SELECT usage_count FROM licenses WHERE key_code=%s", (test_key,))
            new_count = cur.fetchone()[0]
            print(f"New Count: {new_count}")

            # Revert
            cur.execute("UPDATE licenses SET usage_count = usage_count - 1 WHERE key_code=%s", (test_key,))
            conn.commit()
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_update()
