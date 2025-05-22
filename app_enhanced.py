"""
Enhanced MCP WordCloud Generator with proper authentication and credit tracking.
This version uses SQLite for persistent user data storage and Stripe for payments.
"""

# Set Matplotlib to use a non-interactive backend BEFORE importing it
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend - doesn't require a GUI

from flask import Flask, render_template, jsonify, url_for, request, flash, redirect
from flask_login import LoginManager, current_user, login_required
import os
import secrets
import stripe

# Import configuration
from config import *

# Import blueprint modules
from auth import auth_bp, deduct_credit
from credits import credits_bp, init_credit_packages
from database_models import db, User

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Initialize extensions
db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(credits_bp)

# Add route alias for dashboard
@app.route('/dashboard')
@app.route('/mcp/dashboard')
def dashboard_redirect():
    return redirect(url_for('credits.dashboard'))

# Initialize the database
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', credits=100)
            admin.set_password('adminpass')  # In production, use a more secure password
            db.session.add(admin)
            db.session.commit()
            print("Admin user created with 100 credits")
        
        # Initialize credit packages
        init_credit_packages()

# Home route
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/mcp/')
@app.route('/mcp/index.html')
def mcp_index():
    return render_template('index.html')

# Constants for wordcloud generation
COLOR_SCHEMES = {
    'standard': [
        'viridis', 'plasma', 'inferno', 'magma', 'cividis',
        'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    ],
    'diverging': [
        'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
        'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr'
    ],
    'qualitative': [
        'Pastel1', 'Pastel2', 'Paired', 'Accent',
        'Dark2', 'Set1', 'Set2', 'Set3', 'tab10'
    ]
}

# Font options
available_fonts = [
    'DejaVuSans-Bold.ttf', 
    'Arial', 
    'Helvetica', 
    'Times New Roman', 
    'Courier New', 
    'Verdana', 
    'Georgia', 
    'Comic Sans MS',
    'Impact'
]

# Available sample masks
sample_masks = {
    'none': 'No mask',
    'heart': 'Heart shape',
    'logo': 'Rounded logo',
    'upload': 'Upload your own'
}

# Stripe webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': str(e)}), 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event.data.object
        fulfill_order(session)
    
    return jsonify({'success': True})

def fulfill_order(session):
    """Process a successful payment"""
    from credits import add_credits
    
    # Get customer details from session
    user_id = session.metadata.get('user_id')
    credits = int(session.metadata.get('credits', 0))
    package_name = session.metadata.get('package_name', 'Credit Package')
    
    if user_id and credits > 0:
        # Add credits to user account
        add_credits(int(user_id), credits, f"Purchase: {package_name}")
        print(f"Added {credits} credits to user {user_id}")

# This is a basic implementation - we'll need to add the wordcloud generation logic
@app.route('/mcp/wordcloud', methods=['GET'])
def wordcloud_form():
    # Check if authenticated user has credits
    if current_user.is_authenticated and current_user.credits <= 0:
        flash('You do not have enough credits to generate a wordcloud. Please purchase credits.', 'warning')
    
    # Include the needed variables for the template
    return render_template('mcp_wordcloud.html',
                         color_schemes=COLOR_SCHEMES,
                         available_fonts=available_fonts,
                         sample_masks=sample_masks)

# This is a stub - we'll need to implement the full wordcloud generation
@app.route('/mcp/wordcloud/generate', methods=['POST'])
def generate_wordclouds():
    # Check if authenticated user has credits
    if current_user.is_authenticated:
        if current_user.credits <= 0:
            return jsonify({'error': 'You do not have enough credits. Please purchase credits.', 'redirect': url_for('credits.dashboard')}), 402
        
        # Deduct a credit for using the service
        deduct_credit(current_user.id)
    
    # This is where the actual wordcloud generation would happen
    # For now, return a stub response
    return jsonify({
        'success': True,
        'message': 'Wordclouds generated successfully (not actually implemented yet)',
        'redirect': '/'
    })

# Stripe integration for app context
@app.context_processor
def inject_stripe_key():
    return dict(stripe_public_key=STRIPE_PUBLIC_KEY)

if __name__ == '__main__':
    # Initialize the database before running the app
    init_db()
    
    # Run the app
    app.run(debug=DEBUG, port=APP_PORT)
