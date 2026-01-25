"""
QUANTUM X PRO - TABLE NAMES ONLY
Quick view of all tables
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def list_tables():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    
    print("\n" + "="*60)
    print(f"   YOUR SUPABASE TABLES ({len(tables)} total)")
    print("="*60 + "\n")
    
    for i, (table_name,) in enumerate(tables, 1):
        # Get row count
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"{i:2}. {table_name:30} ({count:,} rows)")
        except:
            print(f"{i:2}. {table_name:30} (unable to count)")
    
    print("\n" + "="*60 + "\n")
    conn.close()

if __name__ == "__main__":
    list_tables()
