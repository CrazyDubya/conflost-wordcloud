"""
Authentication functions for the WordCloud application
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from database_models import db, User, CreditTransaction
from flask_login import LoginManager

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/mcp/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('credits.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('signup.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('signup.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('signup.html')
            
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Add initial 5 credits as a signup bonus
        transaction = CreditTransaction(
            user_id=user.id,
            amount=5,
            description="Signup bonus"
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        flash('Account created successfully! You received 5 free credits.', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('signup.html')

@auth_bp.route('/mcp/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('credits.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html')
            
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
            
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Login user
        login_user(user)
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        else:
            return redirect(url_for('credits.dashboard'))
            
    return render_template('login.html')

@auth_bp.route('/mcp/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('mcp_index'))

# Credit management functions
def deduct_credit(user_id, amount=1, description="WordCloud generation"):
    """Deduct credits from user and record the transaction"""
    user = User.query.get(user_id)
    if user and user.credits >= amount:
        user.credits -= amount
        
        # Record transaction
        transaction = CreditTransaction(
            user_id=user_id,
            amount=-amount,
            description=description
        )
        db.session.add(transaction)
        db.session.commit()
        return True
    return False

def add_credits(user_id, amount, description="Credit purchase"):
    """Add credits to a user's account and record the transaction"""
    user = User.query.get(user_id)
    if user:
        user.credits += amount
        
        # Record transaction
        transaction = CreditTransaction(
            user_id=user_id,
            amount=amount,
            description=description
        )
        db.session.add(transaction)
        db.session.commit()
        return True
    return False
