import psycopg2, os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("user_activity columns:")
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='user_activity' ORDER BY ordinal_position")
for row in cur.fetchall():
    print(f"  - {row[0]}")
