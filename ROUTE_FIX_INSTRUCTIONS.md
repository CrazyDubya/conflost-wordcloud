# Fixing Route Issues in MCP WordCloud Generator

You're experiencing issues with route mismatches in your application. Specifically, your template links are pointing to `/mcp/signup` but your application may not have routes defined for that path.

## Understanding the Issue

Your application has links that use paths like:
- `/mcp/signup`
- `/mcp/login`
- `/mcp/dashboard`
- `/mcp/wordcloud`

However, the routes in your Flask application might be defined without the `/mcp` prefix, such as:
- `@app.route('/signup')`
- `@app.route('/login')`

This mismatch is causing 404 errors when you try to access these pages.

## Quick Solution

I've created two scripts to help fix this issue:

1. `fix_routes.py` - This script will:
   - Update route definitions in `mcp_wordcloud.py` to include the `/mcp` prefix
   - Remove the `@login_required` decorator from the wordcloud route
   - Fix any redirect URLs in the code

2. `quick_fix_app.py` - This is a simplified app that:
   - Defines all the routes that match your template URLs
   - Provides basic functionality (no actual wordcloud generation)
   - Allows you to test your templates and navigation

## How to Use the Fix

### Option 1: Update Your Existing App

Run the fix script to update your route definitions:

```bash
python fix_routes.py
```

Then run your original application:

```bash
python mcp_wordcloud.py
```

### Option 2: Use the Quick Fix App

If you want a simpler solution to test that routes are working:

```bash
python quick_fix_app.py
```

This minimal app will respond to all URLs in your templates but won't have full functionality.

## Manual Fix

If you prefer to fix the issues manually:

1. Open `mcp_wordcloud.py`

2. Find all route definitions and update them to include the `/mcp` prefix:

   Change:
   ```python
   @app.route('/signup', methods=['GET', 'POST'])
   ```

   To:
   ```python
   @app.route('/mcp/signup', methods=['GET', 'POST'])
   ```

3. Remove `@login_required` from the wordcloud route:

   Change:
   ```python
   @login_required
   @app.route('/mcp/wordcloud', methods=['GET'])
   ```

   To:
   ```python
   @app.route('/mcp/wordcloud', methods=['GET'])
   ```

4. Update any redirects in your code:

   Change:
   ```python
   return redirect(url_for('login'))
   ```

   To:
   ```python
   return redirect(url_for('login'))
   ```

   (Note: If you're using `url_for()` correctly, you shouldn't need to change these as they'll use the function name, not the URL path)

## Understanding URL Prefixes

There are two ways to handle URL prefixes in Flask:

1. **Include the prefix in each route definition** (what we're doing in the fix):
   ```python
   @app.route('/mcp/login')
   ```

2. **Use Blueprint with a URL prefix** (a cleaner approach for the future):
   ```python
   mcp = Blueprint('mcp', __name__, url_prefix='/mcp')
   
   @mcp.route('/login')
   def login():
       # ...
   
   # Then in your main app:
   app.register_blueprint(mcp)
   ```

## Nginx Configuration

If you're using Nginx as a proxy, make sure it's configured to correctly forward requests with the `/mcp` prefix:

```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:5001/mcp/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

If Nginx is configured to strip the `/mcp` prefix, that could also cause issues.

## Testing Your Fix

After applying the fix, test these URLs:
- http://127.0.0.1:5001/mcp/signup
- http://127.0.0.1:5001/mcp/login
- http://127.0.0.1:5001/mcp/wordcloud

All should now load correctly without 404 errors.
