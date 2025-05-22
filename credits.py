"""
Credit management for the WordCloud application
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
import stripe

from database_models import db, User, CreditTransaction, CreditPackage
from auth import add_credits
from config import STRIPE_SECRET_KEY

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

credits_bp = Blueprint('credits', __name__)

@credits_bp.route('/mcp/dashboard')
@login_required
def dashboard():
    """User dashboard showing credits and transaction history"""
    # Get user's recent transactions
    transactions = CreditTransaction.query.filter_by(user_id=current_user.id)\
        .order_by(CreditTransaction.created_at.desc())\
        .limit(10).all()
    
    # Get available credit packages
    packages = CreditPackage.query.filter_by(active=True).all()
    
    return render_template('dashboard.html', 
                         user=current_user, 
                         transactions=transactions,
                         packages=packages)

@credits_bp.route('/mcp/buy-credits/<int:package_id>', methods=['POST'])
@login_required
def buy_credits(package_id):
    """Create Stripe checkout session for the credit package"""
    package = CreditPackage.query.get_or_404(package_id)
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'{package.name} - {package.credits} Credits',
                            'description': package.description,
                        },
                        'unit_amount': package.price, # Price in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.host_url + 'mcp/payment-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'mcp/payment-cancel',
            metadata={
                'user_id': str(current_user.id),
                'package_id': str(package.id),
                'package_name': package.name,
                'credits': str(package.credits)
            }
        )
        
        return jsonify({
            'id': checkout_session.id,
            'url': checkout_session.url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credits_bp.route('/mcp/payment-success')
@login_required
def payment_success():
    """Handle successful payment redirect"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        flash('Invalid payment session', 'danger')
        return redirect(url_for('credits.dashboard'))
    
    try:
        # Retrieve session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # If using webhook, this is redundant, but provides immediate feedback
        if checkout_session.payment_status == 'paid':
            # Get metadata
            credits = int(checkout_session.metadata.get('credits', 0))
            package_name = checkout_session.metadata.get('package_name', 'Credit Package')
            
            # Add credits to user account
            add_credits(current_user.id, credits, f"Purchase: {package_name}")
            
            flash(f'Payment successful! {credits} credits have been added to your account.', 'success')
        else:
            flash('Payment is being processed. Credits will be added once payment is confirmed.', 'info')
            
    except Exception as e:
        flash(f'Error processing payment: {str(e)}', 'danger')
    
    return redirect(url_for('credits.dashboard'))

@credits_bp.route('/mcp/payment-cancel')
@login_required
def payment_cancel():
    """Handle canceled payment"""
    flash('Payment was canceled. No credits have been added to your account.', 'warning')
    return redirect(url_for('credits.dashboard'))

@credits_bp.route('/mcp/add-free-credits')
@login_required
def add_free_credits():
    """Admin function to add free credits (for testing)"""
    if current_user.username == 'admin':
        # Add free credits to all users
        users = User.query.all()
        for user in users:
            add_credits(user.id, 10, "Free credits from admin")
        flash('Added 10 free credits to all users', 'success')
    else:
        flash('Only admin can add free credits', 'danger')
    return redirect(url_for('credits.dashboard'))

# Function to initialize credit packages 
def init_credit_packages():
    """Initialize default credit packages if they don't exist"""
    if CreditPackage.query.count() == 0:
        packages = [
            CreditPackage(name='Basic', credits=5, price=100, description='$1 for 5 credits'),
            CreditPackage(name='Standard', credits=30, price=500, description='$5 for 30 credits'),
            CreditPackage(name='Premium', credits=100, price=1000, description='$10 for 100 credits'),
            CreditPackage(name='Business', credits=500, price=3000, description='$30 for 500 credits')
        ]
        for package in packages:
            db.session.add(package)
        db.session.commit()
        print("Default credit packages created")
