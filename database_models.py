"""
Database models for the WordCloud application
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    credits = db.Column(db.Integer, default=5)  # New users get 5 free credits
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Transaction history
class CreditTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Positive for purchases, negative for usage
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    
    # Virtual property for transaction type based on amount
    @property
    def transaction_type(self):
        if self.amount > 0:
            return 'purchase'
        elif self.amount < 0:
            return 'usage'
        else:
            return 'other'

# Store wordcloud session information
class WordcloudSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    session_uuid = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Can be null for guests
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref=db.backref('wordcloud_sessions', lazy=True))

# Credit packages
class CreditPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)  # Price in cents
    description = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
