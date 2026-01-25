import secrets
import string
import os
import psycopg2
from dotenv import load_dotenv

# Load env for DB credentials
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
OUTPUT_FILE = "generated_keys.txt"

def generate_secure_key():
    """
    Generates an 8-char key: 2 Lower, 2 Upper, 2 Digits, 2 Symbols
    """
    lower = [secrets.choice(string.ascii_lowercase) for _ in range(2)]
    upper = [secrets.choice(string.ascii_uppercase) for _ in range(2)]
    digits = [secrets.choice(string.digits) for _ in range(2)]
    symbols = [secrets.choice("!@#$%^&*") for _ in range(2)]
    
    combined = lower + upper + digits + symbols
    secrets.SystemRandom().shuffle(combined)
    return "".join(combined)

def setup_keys():
    print("Connecting to Supabase PostgreSQL...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    # Clear existing keys (Optional: Remove if you want to append)
    # cursor.execute("DELETE FROM licenses") 
    
    # Create Table if likely missing (app.py does this too, but good to be safe)
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                key_code TEXT PRIMARY KEY,
                category TEXT,
                status TEXT,
                device_id TEXT,
                ip_address TEXT,
                activation_date TIMESTAMP,
                expiry_date TIMESTAMP
            )
    ''')
    conn.commit()

    keys_data = {
        "OWNER": [],
        "USER": [],
        "TRIAL": []
    }

    print("Generating Keys...")

    # Generate Owner Keys (3)
    for _ in range(3):
        k = generate_secure_key()
        keys_data["OWNER"].append(k)
        cursor.execute("INSERT INTO licenses (key_code, category, status) VALUES (%s, 'OWNER', 'PENDING') ON CONFLICT DO NOTHING", (k,))

    # Generate User Keys (600)
    for _ in range(600):
        k = generate_secure_key()
        keys_data["USER"].append(k)
        cursor.execute("INSERT INTO licenses (key_code, category, status) VALUES (%s, 'USER', 'PENDING') ON CONFLICT DO NOTHING", (k,))

    # Generate Trial Keys (600)
    for _ in range(600):
        k = generate_secure_key()
        keys_data["TRIAL"].append(k)
        cursor.execute("INSERT INTO licenses (key_code, category, status) VALUES (%s, 'TRIAL', 'PENDING') ON CONFLICT DO NOTHING", (k,))

    conn.commit()
    cursor.close()
    conn.close()

    # Write to File
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== QUANTUM X PRO LICENSE KEYS (SUPABASE SYNCED) ===\n\n")
        
        f.write("--- OWNER KEYS (PERMANENT / ADMIN) ---\n")
        for k in keys_data["OWNER"]:
            f.write(f"{k}\n")
        f.write("\n")

        f.write("--- USER KEYS (PERMANENT / 1 DEVICE LOCK) ---\n")
        for k in keys_data["USER"]:
            f.write(f"{k}\n")
        f.write("\n")

        f.write("--- TRIAL KEYS (1 HOUR VALIDITY / 1 DEVICE LOCK) ---\n")
        for k in keys_data["TRIAL"]:
            f.write(f"{k}\n")
        f.write("\n")

    print(f"Success! Uploaded {len(keys_data['OWNER'])+len(keys_data['USER'])+len(keys_data['TRIAL'])} keys to Supabase.")
    print(f"Key List updated: {OUTPUT_FILE}")

if __name__ == "__main__":
    setup_keys()
