"""
Check actual column names in user_sessions and user_activity tables
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def check_columns():
    DATABASE_URL = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print("   ACTUAL TABLE STRUCTURES")
    print("="*80 + "\n")
    
    # Check user_sessions columns
    print("[1] user_sessions TABLE COLUMNS:")
    print("-" * 80)
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'user_sessions'
        ORDER BY ordinal_position
    """)
    for col, dtype in cur.fetchall():
        print(f"  - {col:30} ({dtype})")
    
    # Show sample data
    print("\n  Sample Data (first 3 rows):")
    cur.execute("SELECT * FROM user_sessions LIMIT 3")
    rows = cur.fetchall()
    for i, row in enumerate(rows, 1):
        print(f"    Row {i}: {row}")
    
    # Check user_activity columns
    print("\n\n[2] user_activity TABLE COLUMNS:")
    print("-" * 80)
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'user_activity'
        ORDER BY ordinal_position
    """)
    for col, dtype in cur.fetchall():
        print(f"  - {col:30} ({dtype})")
    
    # Show sample data
    print("\n  Sample Data (first 3 rows):")
    cur.execute("SELECT * FROM user_activity LIMIT 3")
    rows = cur.fetchall()
    for i, row in enumerate(rows, 1):
        print(f"    Row {i}: {row}")
    
    conn.close()
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    check_columns()
