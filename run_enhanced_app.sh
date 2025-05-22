#!/bin/bash

# Run the enhanced WordCloud app with authentication and credit tracking

# Install required dependencies
echo "Installing required packages..."
pip install flask flask-sqlalchemy flask-login werkzeug wordcloud matplotlib nltk pillow stripe

# Download NLTK data
python -c "import nltk; nltk.download('stopwords')"

# Set up the database - Force recreation
echo "Setting up the database..."

# Always remove the old database to update the schema
if [ -f "wordcloud.db" ]; then
    echo "Removing old database to update schema..."
    rm wordcloud.db
fi

python -c "
from app_enhanced import app, init_db
with app.app_context():
    init_db()
    print('Database initialized with current schema')
"

# Set up environment variables for Stripe
# Replace these with your actual keys
export STRIPE_PUBLIC_KEY="pk_test_your_publishable_key"
export STRIPE_SECRET_KEY="sk_test_your_secret_key"
export STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"

# Echo instructions about Stripe configuration
echo ""
echo "-------------------------------------------------------------------------"
echo "IMPORTANT: To use Stripe, edit this script and replace the placeholder"
echo "API keys with your actual Stripe keys from your Stripe dashboard."
echo "-------------------------------------------------------------------------"
echo ""

# Run the application
echo "Starting the enhanced WordCloud application..."
echo "Access at http://127.0.0.1:5001"
python app_enhanced.py
