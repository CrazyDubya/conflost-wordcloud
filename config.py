"""
Configuration settings for the WordCloud application
"""
import os
from datetime import timedelta

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'development_secret_key')
APP_PORT = 5001
DEBUG = True

# Database settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///wordcloud.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Session settings
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Stripe settings (configure via environment variables)
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', 'pk_test_replace_with_your_publishable_key')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_replace_with_your_secret_key')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_replace_with_your_webhook_secret')

# Credit settings
DEFAULT_SIGNUP_CREDITS = 5  # Credits given to new users

# Token settings
TOKEN_EXPIRY = 3600  # 1 hour for token expiry
