"""
MacOS-compatible quick fix for MCP WordCloud generator.
This version uses a non-interactive backend for Matplotlib to avoid GUI issues on macOS.
"""

# Set Matplotlib to use a non-interactive backend BEFORE importing it
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend - doesn't require a GUI

from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, send_from_directory
import os
import uuid
import time
import json
import shutil
from datetime import datetime, timedelta
import secrets
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import numpy as np

# Try to import wordcloud - if not available, we'll use a mock version
try:
    from wordcloud import WordCloud, STOPWORDS
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    print("WordCloud package not available. Will use mock wordcloud images.")

# Try to import nltk for stopwords - if not available, we'll use a basic list
try:
    import nltk
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK package not available. Will use basic stopwords list.")

app = Flask(__name__)
app.secret_key = 'macos_fix_secret_key'

# Constants
TEMP_TOKEN_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token_sessions')
os.makedirs(TEMP_TOKEN_FOLDER, exist_ok=True)
TOKEN_EXPIRY = 3600  # 1 hour

# In-memory token store for temporary access
active_tokens = {}

# Color scheme options
COLOR_SCHEMES = {
    'standard': [
        'viridis', 'plasma', 'inferno', 'magma', 'cividis',
        'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
        'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
        'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'
    ],
    'diverging': [
        'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
        'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr'
    ],
    'qualitative': [
        'Pastel1', 'Pastel2', 'Paired', 'Accent',
        'Dark2', 'Set1', 'Set2', 'Set3',
        'tab10', 'tab20', 'tab20b', 'tab20c'
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

# Token management functions
def generate_access_token():
    """Generate a secure random token for session access"""
    token = secrets.token_urlsafe(32)
    timestamp = time.time()
    session_uuid = str(uuid.uuid4())
    
    active_tokens[token] = {
        'created': timestamp,
        'expires': timestamp + TOKEN_EXPIRY,
        'uuid': session_uuid,
        'user_id': None
    }
    return token

def validate_token(token):
    """Check if token exists and is valid"""
    if token in active_tokens:
        if time.time() < active_tokens[token]['expires']:
            return active_tokens[token]['uuid']
    return None

def cleanup_expired_tokens():
    """Remove expired tokens and their associated files"""
    current_time = time.time()
    expired_tokens = []
    
    for token, data in active_tokens.items():
        if current_time > data['expires']:
            expired_tokens.append((token, data['uuid']))
    
    for token, uuid_str in expired_tokens:
        # Clean up token data
        del active_tokens[token]
        
        # Clean up associated files
        token_folder = os.path.join(TEMP_TOKEN_FOLDER, uuid_str)
        if os.path.exists(token_folder):
            try:
                shutil.rmtree(token_folder)
            except Exception as e:
                print(f"Error removing token folder: {e}")

# Helper functions for wordcloud generation
def process_text_for_wordcloud(text, additional_stopwords=None, min_word_length=3):
    """Process text for wordcloud by removing stopwords and other filtering"""
    if NLTK_AVAILABLE:
        # Use NLTK stopwords if available
        stop_words = set(stopwords.words('english'))
        if WORDCLOUD_AVAILABLE:
            stop_words = stop_words.union(set(STOPWORDS))
    else:
        # Basic stopwords list if NLTK not available
        stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
            'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
            'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
        }
    
    # Add custom stopwords if provided
    if additional_stopwords:
        custom_stops = [word.strip().lower() for word in additional_stopwords.split(',')]
        stop_words.update(custom_stops)
    
    # Convert text to lowercase and split
    words = text.lower().split()
    
    # Basic filtering
    filtered_words = [word for word in words if 
                      len(word) >= min_word_length and
                      word not in stop_words and
                      not word.isdigit() and
                      not all(c.isdigit() or c.isspace() or c in '.,;:!?' for c in word)]
    
    # Prepare text for wordcloud
    return ' '.join(filtered_words)

def get_word_frequencies(text, min_word_length=3):
    """Calculate word frequencies for the top words chart"""
    # Similar stopwords logic as the process_text_for_wordcloud function
    if NLTK_AVAILABLE:
        stop_words = set(stopwords.words('english'))
        if WORDCLOUD_AVAILABLE:
            stop_words = stop_words.union(set(STOPWORDS))
    else:
        # Use the basic stopwords list from above
        stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            # ... (similar to the previous function)
        }
    
    # Convert text to lowercase and split
    words = text.lower().split()
    
    # Count word frequencies
    word_counts = {}
    for word in words:
        if (len(word) >= min_word_length and 
            word not in stop_words and 
            not word.isdigit() and
            not all(c.isdigit() or c.isspace() or c in '.,;:!?' for c in word)):
            
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:25]  # Return top 25 words

def generate_wordcloud(text, session_id, colormap='viridis', background_color='black', 
                      max_words=200, width=1000, height=600, prefer_horizontal=0.9):
    """Generate wordcloud and save to file"""
    try:
        # Ensure output directory exists
        output_dir = os.path.join(TEMP_TOKEN_FOLDER, session_id)
        os.makedirs(output_dir, exist_ok=True)
        
        if WORDCLOUD_AVAILABLE:
            # Create wordcloud object with the actual WordCloud library
            wc = WordCloud(
                background_color=background_color,
                max_words=max_words,
                width=width,
                height=height,
                colormap=colormap,
                prefer_horizontal=prefer_horizontal,
                random_state=42
            )
            
            # Generate wordcloud
            wc.generate(text)
            
            # Create a unique filename
            filename = f"wordcloud_{uuid.uuid4()}.png"
            output_path = os.path.join(output_dir, filename)
            
            # Save wordcloud
            wc.to_file(output_path)
        else:
            # Create a mock wordcloud image if the WordCloud package is not available
            plt.figure(figsize=(width/100, height/100))
            plt.text(0.5, 0.5, "Mock WordCloud - Install WordCloud for real generation", 
                    horizontalalignment='center', verticalalignment='center', fontsize=20)
            plt.axis('off')
            
            # Create a unique filename
            filename = f"wordcloud_{uuid.uuid4()}.png"
            output_path = os.path.join(output_dir, filename)
            
            # Save mock image
            plt.savefig(output_path, facecolor=background_color)
            plt.close()
            
        return filename
    except Exception as e:
        print(f"Error generating wordcloud: {e}")
        return None

def generate_top_words_chart(word_frequencies, session_id):
    """Generate bar chart of top word frequencies"""
    try:
        # Ensure output directory exists
        output_dir = os.path.join(TEMP_TOKEN_FOLDER, session_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract words and frequencies
        words = [item[0] for item in word_frequencies]
        frequencies = [item[1] for item in word_frequencies]
        
        # Create figure
        plt.figure(figsize=(10, 6))
        plt.barh(range(len(words)), frequencies, align='center', color='skyblue')
        plt.yticks(range(len(words)), words)
        plt.gca().invert_yaxis()  # Highest frequency at the top
        plt.xlabel('Frequency')
        plt.title('Top 25 Words by Frequency')
        plt.tight_layout()
        
        # Save figure
        filename = "top_25_words.png"
        output_path = os.path.join(output_dir, filename)
        plt.savefig(output_path)
        plt.close()
        
        return filename
    except Exception as e:
        print(f"Error generating top words chart: {e}")
        return None

# Simple routes to handle all the URLs in templates
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/mcp/')
@app.route('/mcp/index.html')
def mcp_index():
    return render_template('index.html')

@app.route('/mcp/wordcloud')
def wordcloud():
    # Clear any expired tokens
    cleanup_expired_tokens()
    
    return render_template('mcp_wordcloud.html', 
                          color_schemes=COLOR_SCHEMES,
                          available_fonts=available_fonts,
                          sample_masks=sample_masks)

@app.route('/mcp/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        flash('Account creation successful! This is a temporary fix app.', 'success')
        session['user'] = {'username': request.form.get('username'), 'credits': 5}
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/mcp/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = {'username': request.form.get('username'), 'credits': 5}
        flash('Login successful! This is a temporary fix app.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/mcp/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/mcp/dashboard')
def dashboard():
    # Get current user from session
    user = session.get('user', {'username': 'Test User', 'credits': 10})
    
    # Dummy data for dashboard
    transactions = []
    packages = [
        {'id': 1, 'name': 'Basic', 'credits': 5, 'price': 100},
        {'id': 2, 'name': 'Standard', 'credits': 30, 'price': 500}
    ]
    
    return render_template('dashboard.html', 
                          user=user, 
                          transactions=transactions,
                          packages=packages,
                          stripe_public_key='pk_test_dummy')

@app.route('/mcp/wordcloud/generate', methods=['POST'])
def generate_wordclouds():
    """Process the form and generate wordclouds"""
    try:
        # Get form data
        text = request.form.get('text', '')
        if not text or len(text.strip()) < 50:
            return jsonify({'error': 'Please enter at least 50 characters of text'}), 400
        
        # Additional parameters
        max_words = int(request.form.get('max_words', 200))
        min_word_length = int(request.form.get('min_word_length', 3))
        additional_stopwords = request.form.get('additional_stopwords', '')
        width = int(request.form.get('width', 1000))
        height = int(request.form.get('height', 600))
        
        # Get color schemes
        colormap1 = request.form.get('colormap1', 'viridis')
        colormap2 = request.form.get('colormap2', 'plasma')
        colormap3 = request.form.get('colormap3', 'inferno')
        
        # Get backgrounds
        background1 = request.form.get('background1', 'black')
        background2 = request.form.get('background2', 'white')
        background3 = request.form.get('background3', '#333333')
        
        # Create a new session token
        token = generate_access_token()
        session_id = active_tokens[token]['uuid']
        
        # Create directories for this session
        session_dir = os.path.join(TEMP_TOKEN_FOLDER, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Process text for wordcloud
        processed_text = process_text_for_wordcloud(text, additional_stopwords, min_word_length)
        if not processed_text:
            return jsonify({'error': 'After filtering, no significant words remain. Try reducing filters or adding more text.'}), 400
        
        # Calculate word frequencies
        word_frequencies = get_word_frequencies(text, min_word_length)
        
        # Generate top words chart
        top_words_chart = generate_top_words_chart(word_frequencies, session_id)
        
        # Generate wordclouds with different color schemes
        wordcloud1 = generate_wordcloud(
            processed_text, session_id,
            colormap=colormap1, 
            background_color=background1,
            max_words=max_words,
            width=width, 
            height=height
        )
        
        wordcloud2 = generate_wordcloud(
            processed_text, session_id,
            colormap=colormap2, 
            background_color=background2,
            max_words=max_words,
            width=width, 
            height=height
        )
        
        wordcloud3 = generate_wordcloud(
            processed_text, session_id,
            colormap=colormap3, 
            background_color=background3,
            max_words=max_words,
            width=width, 
            height=height
        )
        
        # Store generated files in session
        filenames = {
            'wordcloud_1': wordcloud1,
            'wordcloud_2': wordcloud2,
            'wordcloud_3': wordcloud3,
            'top_25_words': top_words_chart
        }
        
        # Save metadata for this session
        metadata = {
            'created': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(seconds=TOKEN_EXPIRY)).isoformat(),
            'files': filenames,
            'settings': {
                'max_words': max_words,
                'colormaps': [colormap1, colormap2, colormap3],
                'backgrounds': [background1, background2, background3],
                'width': width,
                'height': height
            }
        }
        
        with open(os.path.join(session_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Return the URL for viewing results
        result_url = f"/mcp/wordcloud/view/{token}"
        return jsonify({
            'success': True,
            'message': 'Wordclouds generated successfully',
            'redirect': result_url
        })
        
    except Exception as e:
        print(f"Error in generate: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/mcp/wordcloud/view/<token>', methods=['GET'])
def view_results(token):
    """Display the generated wordclouds"""
    # Validate token
    session_id = validate_token(token)
    if not session_id:
        return render_template('error.html', message="Invalid or expired session. Please generate new wordclouds.")
    
    # Get metadata for this session
    metadata_path = os.path.join(TEMP_TOKEN_FOLDER, session_id, 'metadata.json')
    if not os.path.exists(metadata_path):
        return render_template('error.html', message="Session data not found. Please generate new wordclouds.")
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    return render_template('mcp_wordcloud_results.html', 
                         token=token, 
                         session_id=session_id,
                         metadata=metadata)

@app.route('/mcp/wordcloud/image/<token>/<filename>', methods=['GET'])
def serve_image(token, filename):
    """Serve generated image files"""
    # Validate token
    session_id = validate_token(token)
    if not session_id:
        return "Invalid or expired token", 403
    
    # Ensure the filename is safe
    safe_filename = secure_filename(filename)
    return send_from_directory(os.path.join(TEMP_TOKEN_FOLDER, session_id), safe_filename)

@app.route('/mcp/wordcloud/download/<token>/<filename>', methods=['GET'])
def download_image(token, filename):
    """Download image files"""
    # Validate token
    session_id = validate_token(token)
    if not session_id:
        return "Invalid or expired token", 403
    
    # Ensure the filename is safe
    safe_filename = secure_filename(filename)
    
    # Set headers for download
    return send_from_directory(
        os.path.join(TEMP_TOKEN_FOLDER, session_id),
        safe_filename,
        as_attachment=True
    )

@app.route('/mcp/wordcloud/download-all/<token>', methods=['GET'])
def download_all(token):
    """Create a zip of all generated files and serve it"""
    # Validate token
    session_id = validate_token(token)
    if not session_id:
        return "Invalid or expired token", 403
    
    # Path to session directory
    session_dir = os.path.join(TEMP_TOKEN_FOLDER, session_id)
    
    # Create a zip file
    zip_filename = f"wordclouds_{session_id}.zip"
    zip_path = os.path.join(session_dir, zip_filename)
    
    try:
        import zipfile
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in os.listdir(session_dir):
                if file.endswith('.png'):
                    file_path = os.path.join(session_dir, file)
                    zipf.write(file_path, arcname=file)
        
        # Serve the zip file
        return send_from_directory(
            session_dir,
            zip_filename,
            as_attachment=True
        )
    except Exception as e:
        print(f"Error creating zip file: {e}")
        return "Error creating zip file", 500

if __name__ == '__main__':
    print("\n=== MacOS-Compatible MCP WordCloud Quick Fix ===")
    print("This app provides temporary fixes for the route issues.")
    print("Using non-interactive Matplotlib backend to avoid macOS GUI issues.")
    
    if not WORDCLOUD_AVAILABLE:
        print("\nWARNING: WordCloud package not installed.")
        print("Install it with: pip install wordcloud")
        print("Will use mock images instead of real wordclouds.")
    
    print("\nRunning on http://127.0.0.1:5001")
    print("Try these URLs:")
    print("- http://127.0.0.1:5001/mcp/wordcloud (WordCloud Generator)")
    print("- http://127.0.0.1:5001/mcp/signup (Signup Page)")
    print("- http://127.0.0.1:5001/mcp/login (Login Page)")
    print("\nPress Ctrl+C to exit\n")
    
    app.run(debug=True, port=5001)
