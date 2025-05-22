# Emergency Solution to Fix the Database Issue

If you're still experiencing the error:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: credit_transaction.transaction_type
```

Here's the most direct solution:

## Method 1: Manual Database Reset

1. Delete the database file:
```bash
rm wordcloud.db
```

2. Run the reset script:
```bash
python reset_database.py
```

3. Start the application:
```bash
python app_enhanced.py
```

## Method 2: Downgrade (Temporary Solution)

If the above doesn't work, you can modify the `database_models.py` file to make the new column nullable (this is a temporary fix!):

1. Edit `database_models.py`:
```python
class CreditTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Positive for purchases, negative for usage
    description = db.Column(db.String(200))
    transaction_type = db.Column(db.String(20), nullable=True)  # Make nullable
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
```

2. Update the dashboard template to be more resilient:
```html
<span class="font-medium 
    {% if transaction.transaction_type == 'purchase' %}text-green-600
    {% elif transaction.transaction_type == 'usage' %}text-red-600
    {% elif transaction.amount > 0 %}text-green-600
    {% elif transaction.amount < 0 %}text-red-600
    {% else %}text-blue-600{% endif %}">
    {{ transaction.transaction_type.capitalize() if transaction.transaction_type else ("Purchase" if transaction.amount > 0 else "Usage") }}
</span>
```

## Method 3: Start from scratch (Cleanest solution)

If you're okay with starting afresh:

1. Create a new directory:
```bash
mkdir clean_wordcloud
cd clean_wordcloud
```

2. Copy only the essential files from your current setup:
```bash
cp ../conflost/app_enhanced.py ./app.py
cp ../conflost/database_models.py .
cp ../conflost/auth.py .
cp ../conflost/credits.py .
cp ../conflost/config.py .
cp -r ../conflost/templates .
cp -r ../conflost/static .
```

3. Run the application in the clean directory:
```bash
python app.py
```

This will create a fresh database with the correct schema.
