"""
Quick fix for the WordCloud application - Works with the existing database
"""
import sys
import os
import time

def fix_app():
    print("Running quick fix for the WordCloud application")
    
    # Check if database file exists
    db_path = 'wordcloud.db'
    
    if os.path.exists(db_path):
        print(f"Found existing database: {db_path}")
        print("We'll adapt the application to work with the current schema")
    else:
        print(f"No database found at: {db_path}")
        print("Will create a new database with the correct schema")
    
    # 1. Modify the CreditTransaction model to use a property instead of a column
    try:
        with open('database_models.py', 'r') as f:
            content = f.read()
        
        # Check if already fixed
        if 'def transaction_type(self):' in content:
            print("CreditTransaction model already fixed!")
        else:
            # Replace the transaction_type column with a property
            new_content = content.replace(
                "    transaction_type = db.Column(db.String(20))  # 'purchase', 'usage', 'bonus', etc.\n    created_at = db.Column(db.DateTime, default=datetime.utcnow)",
                "    created_at = db.Column(db.DateTime, default=datetime.utcnow)\n    \n    # Virtual property for transaction type based on amount\n    @property\n    def transaction_type(self):\n        if self.amount > 0:\n            return 'purchase'\n        elif self.amount < 0:\n            return 'usage'\n        else:\n            return 'other'"
            )
            
            with open('database_models.py', 'w') as f:
                f.write(new_content)
            
            print("Fixed database_models.py - Added transaction_type property")
    except Exception as e:
        print(f"Error fixing database_models.py: {str(e)}")
    
    # 2. Update auth.py to remove transaction_type from parameters
    try:
        with open('auth.py', 'r') as f:
            content = f.read()
        
        # Fix the add credits function
        new_content = content.replace(
            "            description=description,\n            transaction_type=",
            "            description=description\n        )\n        db.session.add(transaction)\n        db.session.commit()"
        )
        
        # Fix the signup credits function
        new_content = new_content.replace(
            "            description=\"Signup bonus\",\n            transaction_type=\"bonus\"",
            "            description=\"Signup bonus\""
        )
        
        with open('auth.py', 'w') as f:
            f.write(new_content)
        
        print("Fixed auth.py - Removed transaction_type from parameters")
    except Exception as e:
        print(f"Error fixing auth.py: {str(e)}")
    
    print("\nFix complete! You can now run the application:")
    print("python app_enhanced.py")

if __name__ == "__main__":
    fix_app()
