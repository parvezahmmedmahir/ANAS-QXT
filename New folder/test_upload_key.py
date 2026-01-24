
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_and_verify_key():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 1. Define a NEW Test Key
        new_key = "TEST_KEY_2025"
        category = "USER"
        
        print(f"\n--- 1. INSERTING NEW KEY: {new_key} ---")
        try:
            # Try to insert
            cur.execute("""
                INSERT INTO licenses (key_code, category, status)
                VALUES (%s, %s, 'PENDING')
                ON CONFLICT (key_code) DO NOTHING
            """, (new_key, category))
            conn.commit()
            print("Insertion successful (or key already existed).")
        except Exception as e:
            print(f"Insert failed: {e}")

        # 2. VERIFY the Key
        print(f"\n--- 2. VERIFYING KEY ON SERVER ---")
        cur.execute("SELECT key_code, category, status FROM licenses WHERE key_code = %s", (new_key,))
        result = cur.fetchone()
        
        if result:
            print(f"✅ SUCCESS! Found Key on Server: {result[0]}")
            print(f"   Category: {result[1]}")
            print(f"   Status: {result[2]}")
            print("   (This confirms your local script can WRITE to the global cloud database)")
        else:
            print(f"❌ FAILED! Key {new_key} was NOT found on server.")

        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Database Error: {e}")

if __name__ == "__main__":
    create_and_verify_key()
