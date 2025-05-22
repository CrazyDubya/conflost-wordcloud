"""
Script to completely reset the database and recreate it with the current schema.
This resolves the "no such column" error by ensuring the database matches the current models.
"""
import os
import sys

def reset_database():
    # Database file path
    db_path = 'wordcloud.db'
    
    # Check if database exists and remove it
    if os.path.exists(db_path):
        print(f"Removing existing database: {db_path}")
        os.remove(db_path)
        print("Database removed successfully.")
    else:
        print("No existing database found.")
    
    # Import app and create tables
    print("Creating new database with updated schema...")
    from app_enhanced import app, init_db
    with app.app_context():
        init_db()
    
    print("Database successfully reset and recreated!")
    print("Now you can run the application.")

if __name__ == "__main__":
    reset_database()
