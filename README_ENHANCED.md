# Enhanced MCP WordCloud Generator

This is an enhanced version of the MCP WordCloud Generator with proper user authentication and credit tracking.

## New Features

- **User Accounts**: Register and login to maintain your credit balance
- **Credit System**: Each wordcloud generation costs 1 credit
- **Credit Packages**: Purchase credit packages to generate more wordclouds
- **Transaction History**: Track your credit usage and purchases
- **Admin Features**: Administrative functions for managing users and credits

## Setup Instructions

1. Make the run script executable:
   ```bash
   chmod +x run_enhanced_app.sh
   ```

2. Run the enhanced application:
   ```bash
   ./run_enhanced_app.sh
   ```

3. Open your browser and go to:
   ```
   http://127.0.0.1:5001/mcp/wordcloud
   ```

## Default Accounts

- **Admin Account**:
  - Username: admin
  - Password: adminpass
  - Credits: 100

## Using the Application

1. **Register an Account**:
   - Visit `/mcp/signup`
   - New accounts receive 5 free credits

2. **Login**:
   - Visit `/mcp/login`

3. **Dashboard**:
   - View your credits and transaction history
   - Purchase credit packages

4. **Generate WordClouds**:
   - Enter your text and customize settings
   - Each generation costs 1 credit
   - Login to keep your credits and access to your wordclouds

## Admin Features

When logged in as an admin, you can:

1. **Add Free Credits**:
   - Visit `/mcp/add-free-credits` to add 10 free credits to all users

## Project Structure

- `app_enhanced.py`: Main application file
- `auth.py`: Authentication routes and functions
- `credits.py`: Credit management routes and functions
- `database_models.py`: Database models for users, transactions, etc.
- `wordcloud.db`: SQLite database file (created on first run)

## Original App

The original application (`app.py`) remains available and can be run separately.
