# Setting Up Stripe for the WordCloud Generator

This guide explains how to set up Stripe payments for the WordCloud Generator application.

## Step 1: Create a Stripe Account

1. Go to [Stripe.com](https://stripe.com) and sign up for an account
2. Verify your email and complete the Stripe account setup

## Step 2: Get Your API Keys

1. Log in to your Stripe Dashboard
2. Go to Developers → API keys
3. You'll need both the **Publishable key** and the **Secret key**
   - For testing, use the keys that start with `pk_test_` and `sk_test_`
   - For production, use the keys that start with `pk_live_` and `sk_live_`

## Step 3: Set Up Webhook (Optional but Recommended)

To ensure payments are properly processed even if users close their browser:

1. Go to Developers → Webhooks
2. Click "Add endpoint"
3. For the endpoint URL, enter your server's URL followed by `/webhook`
   - For local testing: Use a service like [ngrok](https://ngrok.com/) to expose your local server
   - For production: Use your actual domain, e.g., `https://temp188.com/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
5. Click "Add endpoint"
6. Copy the "Signing Secret" (starts with `whsec_`)

## Step 4: Configure the Application

### Option 1: Set Environment Variables

Set the following environment variables:

```bash
export STRIPE_PUBLIC_KEY="pk_test_your_publishable_key"
export STRIPE_SECRET_KEY="sk_test_your_secret_key"
export STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"
```

### Option 2: Edit the Configuration File

Edit `config.py` and replace the placeholder values:

```python
# Stripe settings
STRIPE_PUBLIC_KEY = 'pk_test_your_publishable_key'
STRIPE_SECRET_KEY = 'sk_test_your_secret_key'
STRIPE_WEBHOOK_SECRET = 'whsec_your_webhook_secret'
```

### Option 3: Edit the Run Script

Edit `run_enhanced_app.sh` and replace the placeholder values:

```bash
# Set up environment variables for Stripe
export STRIPE_PUBLIC_KEY="pk_test_your_publishable_key"
export STRIPE_SECRET_KEY="sk_test_your_secret_key"
export STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"
```

## Step 5: Test the Integration

1. Run the application: `./run_enhanced_app.sh`
2. Log in and go to your dashboard
3. Try purchasing credits using Stripe's test card numbers:
   - Success: `4242 4242 4242 4242`
   - Requires authentication: `4000 0025 0000 3155`
   - Decline: `4000 0000 0000 0002`

For all test cards, use any future expiration date, any 3-digit CVC, and any postal code.

## Step 6: Go Live (When Ready)

1. Complete Stripe's account verification to enable live payments
2. Update your API keys to the live versions
3. Test the entire flow with a small real payment

## Troubleshooting

- **Webhook not working**: Check the webhook logs in the Stripe Dashboard
- **Payment not processing**: Verify your API keys are correctly set
- **Error in checkout**: Look for error messages in the browser console and server logs

## Customizing the Credit Packages

You can modify the credit packages in the `init_credit_packages()` function in `credits.py`. For each package, you can set:

- `name`: Display name of the package
- `credits`: Number of credits the user receives
- `price`: Price in cents (e.g., 500 = $5.00)
- `description`: Description shown to users

Example:
```python
packages = [
    CreditPackage(name='Basic', credits=5, price=100, description='$1 for 5 credits'),
    # Add more packages as needed
]
```
