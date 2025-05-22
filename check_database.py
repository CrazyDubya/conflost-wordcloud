"""
Utility to check the database schema and troubleshoot issues
"""
import sqlite3
import os

def check_database():
    # Database file path
    db_path = 'wordcloud.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    print(f"Database file exists: {db_path}")
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Tables found in database ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Get columns for this table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"    Columns in {table_name} ({len(columns)}):")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"      - {col_name} ({col_type})")
        
        print("\nChecking specifically for credit_transaction table...")
        
        # Check credit_transaction table specifically
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='credit_transaction';")
        result = cursor.fetchone()
        
        if result:
            print("Table definition for credit_transaction:")
            print(result[0])
        else:
            print("credit_transaction table not found in schema!")
        
        # Close connection
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    
    print("\nCheck complete!")

if __name__ == "__main__":
    check_database()
