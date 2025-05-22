# Tasks for Site Owner (Human)

## Stripe Setup
1. **Create a Stripe Account**:
   - Go to [stripe.com](https://stripe.com) and sign up for an account if you don't have one
   - Complete the verification process

2. **Get API Keys**:
   - Navigate to Dashboard > Developers > API Keys
   - Copy your Publishable Key and Secret Key
   - Update the following lines in `mcp_wordcloud.py`:
     ```python
     app.config['STRIPE_PUBLIC_KEY'] = 'your_stripe_public_key'  # Replace with your actual public key
     app.config['STRIPE_SECRET_KEY'] = 'your_stripe_secret_key'  # Replace with your actual secret key
     ```

3. **Set Up Webhook Endpoint**:
   - Go to Dashboard > Developers > Webhooks
   - Click "Add endpoint"
   - Enter your webhook URL (e.g., `https://temp188.com/stripe-webhook`)
   - Select the event `checkout.session.completed`
   - Copy the "Signing Secret"
   - Update this line in `mcp_wordcloud.py`:
     ```python
     webhook_secret = 'your_stripe_webhook_secret'  # Replace with your webhook secret
     ```

4. **Create Products in Stripe Dashboard (Optional)**:
   - You can create products in Stripe to match your credit packages
   - This helps with analytics and reporting in Stripe
   - Not required for the current implementation as we create products dynamically

## Server Setup
1. **Install Required Python Packages**:
   ```bash
   pip install flask flask-sqlalchemy flask-login stripe werkzeug pillow matplotlib nltk wordcloud
   ```

2. **Initialize NLTK**:
   ```bash
   python -c "import nltk; nltk.download('stopwords')"
   ```

3. **Set Up Domain (temp188.com)**:
   - Configure your DNS settings to point to your server
   - Set up SSL certificate (via Let's Encrypt or your hosting provider)

4. **Configure Server**:
   - Set up a proper production server (Gunicorn/uWSGI with Nginx)
   - Make sure the server is configured for handling file uploads and webhooks

## Testing
1. **Test Credit System**:
   - Create an account to test the initial 5 credit bonus
   - Try generating a wordcloud to see if credits are deducted
   - Verify credit transactions appear in the dashboard

2. **Test Stripe Payments**:
   - Use Stripe test cards to purchase credits:
     - Success: 4242 4242 4242 4242
     - Decline: 4000 0000 0000 0002
   - Verify credits are added to your account after successful payment
   - Check that transactions are recorded in both your app and Stripe Dashboard

3. **Test User Experience**:
   - Verify all error messages are clear and helpful
   - Test the flow from account creation to service use

## Future Considerations
1. **Email Verification**:
   - Set up email verification for user accounts
   - Consider using a service like SendGrid or Mailgun

2. **Legal Documents**:
   - Create and add Terms of Service and Privacy Policy
   - Ensure compliance with relevant laws (GDPR, CCPA, etc.)

3. **Analytics**:
   - Set up analytics to track user behavior and service usage
   - Monitor which services are most popular

4. **Backup System**:
   - Implement regular database backups
   - Consider automated backup solutions

5. **Scaling Plan**:
   - Prepare for scaling as user base grows
   - Consider load balancing and CDN for static assets