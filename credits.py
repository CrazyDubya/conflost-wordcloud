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


def fulfill_checkout_session(checkout_session, expected_user_id=None):
    """Grant the credits for one paid checkout session, at most once.

    The Stripe session id is stored in the transaction description, so a reloaded
    success URL, or the success URL followed by the webhook, cannot grant twice.
    When expected_user_id is given, the session must belong to that user.
    Returns the credits granted (0 if nothing was granted).
    """
    if checkout_session.payment_status != 'paid':
        return 0
    metadata = checkout_session.metadata
    user_id = metadata.get('user_id')
    credits = int(metadata.get('credits', 0))
    if not user_id or credits <= 0:
        return 0
    if expected_user_id is not None and str(user_id) != str(expected_user_id):
        return 0
    marker = f"[{checkout_session.id}]"
    already = CreditTransaction.query.filter(
        CreditTransaction.user_id == int(user_id),
        CreditTransaction.description.like(f"%{marker}")
    ).first()
    if already:
        return 0
    package_name = metadata.get('package_name', 'Credit Package')
    add_credits(int(user_id), credits, f"Purchase: {package_name} {marker}")
    return credits

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
            granted = fulfill_checkout_session(checkout_session, expected_user_id=current_user.id)
            if granted:
                flash(f'Payment successful! {granted} credits have been added to your account.', 'success')
            else:
                flash('This payment has already been applied, or does not belong to your account.', 'info')
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
