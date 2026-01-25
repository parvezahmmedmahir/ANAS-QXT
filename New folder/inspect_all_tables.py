"""
QUANTUM X PRO - COMPLETE DATABASE INSPECTION
Checks ALL tables in your Supabase database
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def inspect_all_tables():
    print("\n" + "="*80)
    print("   COMPLETE SUPABASE DATABASE INSPECTION")
    print("="*80 + "\n")

    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found")
        return
    
    print("[1] Connecting to Supabase...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        print("    ✅ Connected\n")
    except Exception as e:
        print(f"    ❌ Failed: {e}")
        return

    # Get all tables
    print("[2] Discovering all tables...")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    
    print(f"    📊 Found {len(tables)} tables:\n")
    
    for (table_name,) in tables:
        print(f"    • {table_name}")
    
    print("\n" + "="*80)
    print("   DETAILED TABLE ANALYSIS")
    print("="*80 + "\n")
    
    # Analyze each table
    for (table_name,) in tables:
        print(f"\n[TABLE: {table_name}]")
        print("-" * 80)
        
        # Get column information
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        
        print(f"  Columns ({len(columns)}):")
        for col_name, data_type, nullable in columns:
            null_str = "NULL" if nullable == "YES" else "NOT NULL"
            print(f"    - {col_name:30} {data_type:20} {null_str}")
        
        # Get row count
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"\n  Total Rows: {count:,}")
        except:
            print(f"\n  Total Rows: Unable to count")
        
        # Show sample data (first 3 rows)
        try:
            cur.execute(f"SELECT * FROM {table_name} LIMIT 3")
            samples = cur.fetchall()
            if samples:
                print(f"\n  Sample Data (first 3 rows):")
                for i, row in enumerate(samples, 1):
                    print(f"    Row {i}: {row[:5]}...")  # Show first 5 columns
        except Exception as e:
            print(f"\n  Sample Data: Unable to fetch ({e})")
    
    conn.close()
    
    print("\n" + "="*80)
    print("   INSPECTION COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    inspect_all_tables()
