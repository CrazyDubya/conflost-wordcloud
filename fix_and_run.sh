#!/bin/bash

# Script to fix the database and run the application

# First, reset the database completely
echo "==== Resetting database to fix schema ====="
python reset_database.py

if [ $? -ne 0 ]; then
  echo "Error resetting database. Please check the error message above."
  exit 1
fi

echo ""
echo "==== Database reset successfully ===="
echo ""

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
