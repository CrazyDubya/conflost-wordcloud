from flask import Flask, render_template, request, send_file, redirect, url_for, session, abort, jsonify
from wordcloud import WordCloud, STOPWORDS
import os
import uuid
import time
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from PIL import Image
import numpy as np
import json
from datetime import datetime, timedelta
import shutil
import secrets

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Ensure NLTK data is available
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Constants - modified to use local paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(CURRENT_DIR, 'uploads')
TEMP_TOKEN_FOLDER = os.path.join(CURRENT_DIR, 'token_sessions')
STATIC_MASK_FOLDER = os.path.join(CURRENT_DIR, 'cloud', 'static', 'sample_images')
NEW_WORDCLOUD_FOLDER = os.path.join(CURRENT_DIR, 'new_wordclouds')

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_TOKEN_FOLDER, exist_ok=True)
os.makedirs(STATIC_MASK_FOLDER, exist_ok=True)
os.makedirs(NEW_WORDCLOUD_FOLDER, exist_ok=True)

# Configuration
DEFAULT_MAX_WORDS = 200
DEFAULT_WIDTH = 1000
DEFAULT_HEIGHT = 600
TOKEN_EXPIRY = 3600  # Seconds (1 hour)
DEFAULT_COLORMAP = 'viridis'
DEFAULT_BACKGROUND = 'black'
ALLOWED_UPLOAD_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_UPLOAD_EXTENSIONS

def get_mask_path(mask_option, token_uuid=None, uploaded_filename=None):
    """Get the path to the mask image based on selection"""
    if mask_option == 'none':
        return None
    elif mask_option == 'upload' and token_uuid and uploaded_filename:
        return os.path.join(TEMP_TOKEN_FOLDER, token_uuid, 'masks', uploaded_filename)
    else:
        return os.path.join(STATIC_MASK_FOLDER, f"{mask_option}.jpg")

def preprocess_mask(mask_path, invert=False):
    """Load and preprocess a mask image"""
    if not mask_path:
        return None
        
    try:
        mask = np.array(Image.open(mask_path))
        if invert:
            # Invert the mask colors
            mask = 255 - mask
        return mask
    except Exception as e:
        print(f"Error processing mask: {e}")
        return None

def process_text_for_wordcloud(text, additional_stopwords=None, min_word_length=3):
    """Process text for wordcloud with advanced filtering"""
    # Get stopwords
    stop_words = set(STOPWORDS).union(set(stopwords.words('english')))
    
    # Add custom stopwords if provided
    if additional_stopwords:
        custom_stops = [word.strip().lower() for word in additional_stopwords.split(',')]
        stop_words.update(custom_stops)
    
    # Convert text to lowercase and split
    words = text.lower().split()
    
    # Basic filtering
    filtered_words = [word for word in words if len(word) >= min_word_length 
                     and word not in stop_words
                     and not word.isdigit()
                     and not all(c.isdigit() or c.isspace() or c in '.,;:!?' for c in word)]
    
    # Prepare text for wordcloud
    return ' '.join(filtered_words)

def get_word_frequencies(text, min_word_length=3):
    """Calculate word frequencies for display"""
    stop_words = set(STOPWORDS).union(set(stopwords.words('english')))
    
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

def generate_wordcloud(text, session_id, colormap=DEFAULT_COLORMAP, background_color=DEFAULT_BACKGROUND, 
                      max_words=DEFAULT_MAX_WORDS, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, 
                      mask=None, font_path=None, prefer_horizontal=0.9):
    """Generate wordcloud and save to file"""
    try:
        # Ensure output directory exists
        output_dir = os.path.join(TEMP_TOKEN_FOLDER, session_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create wordcloud object
        wc = WordCloud(
            background_color=background_color,
            max_words=max_words,
            width=width,
            height=height,
            colormap=colormap,
            prefer_horizontal=prefer_horizontal,
            mask=mask,
            font_path=font_path,
            random_state=42
        )
        
        # Generate wordcloud
        wc.generate(text)
        
        # Create a unique filename
        filename = f"wordcloud_{uuid.uuid4()}.png"
        output_path = os.path.join(output_dir, filename)
        
        # Save wordcloud
        wc.to_file(output_path)
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

# Simple route for basic wordcloud generation (no login required)
@app.route('/wordcloud', methods=['GET'])
def wordcloud_form():
    """Display the wordcloud generator form without login requirement"""
    # Clear any expired tokens
    cleanup_expired_tokens()
    
    return render_template('mcp_wordcloud.html', 
                         color_schemes=COLOR_SCHEMES,
                         available_fonts=available_fonts,
                         sample_masks=sample_masks)

@app.route('/wordcloud/generate', methods=['POST'])
def generate():
    """Process the form and generate wordclouds without login requirement"""
    try:
        # Get form data
        text = request.form.get('text', '')
        if not text or len(text.strip()) < 50:
            return jsonify({'error': 'Please enter at least 50 characters of text'}), 400
        
        # Additional parameters
        max_words = int(request.form.get('max_words', DEFAULT_MAX_WORDS))
        min_word_length = int(request.form.get('min_word_length', 3))
        additional_stopwords = request.form.get('additional_stopwords', '')
        width = int(request.form.get('width', DEFAULT_WIDTH))
        height = int(request.form.get('height', DEFAULT_HEIGHT))
        
        # Get color schemes
        colormap1 = request.form.get('colormap1', DEFAULT_COLORMAP)
        colormap2 = request.form.get('colormap2', 'plasma')
        colormap3 = request.form.get('colormap3', 'inferno')
        
        # Get backgrounds
        background1 = request.form.get('background1', DEFAULT_BACKGROUND)
        background2 = request.form.get('background2', 'white')
        background3 = request.form.get('background3', '#333333')
        
        # Get font choices
        font_choice = request.form.get('font', None)
        font_path = None
        if font_choice and font_choice.endswith('.ttf'):
            # This is a file path
            font_path = font_choice
            
        # Get mask options
        mask_option = request.form.get('mask_option', 'none')
        invert_mask = request.form.get('invert_mask', 'false') == 'true'
        
        # Create a new session token
        token = generate_access_token()
        session_id = active_tokens[token]['uuid']
        
        # Create directories for this session
        session_dir = os.path.join(TEMP_TOKEN_FOLDER, session_id)
        os.makedirs(session_dir, exist_ok=True)
        mask_dir = os.path.join(session_dir, 'masks')
        os.makedirs(mask_dir, exist_ok=True)
        
        # Handle uploaded mask if provided
        uploaded_mask_file = None
        if mask_option == 'upload' and 'mask_file' in request.files:
            from werkzeug.utils import secure_filename
            mask_file = request.files['mask_file']
            if mask_file and mask_file.filename and allowed_file(mask_file.filename):
                uploaded_mask_file = secure_filename(mask_file.filename)
                mask_path = os.path.join(mask_dir, uploaded_mask_file)
                mask_file.save(mask_path)
        
        # Get the mask image
        mask_path = get_mask_path(mask_option, session_id, uploaded_mask_file)
        mask_array = preprocess_mask(mask_path, invert_mask) if mask_path else None
        
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
            height=height,
            mask=mask_array,
            font_path=font_path
        )
        
        wordcloud2 = generate_wordcloud(
            processed_text, session_id,
            colormap=colormap2, 
            background_color=background2,
            max_words=max_words,
            width=width, 
            height=height,
            mask=mask_array,
            font_path=font_path
        )
        
        wordcloud3 = generate_wordcloud(
            processed_text, session_id,
            colormap=colormap3, 
            background_color=background3,
            max_words=max_words,
            width=width, 
            height=height,
            mask=mask_array,
            font_path=font_path
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
                'mask': mask_option,
                'width': width,
                'height': height
            }
        }
        
        with open(os.path.join(session_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Return the URL for viewing results
        result_url = f"/wordcloud/view/{token}"
        return jsonify({
            'success': True,
            'message': 'Wordclouds generated successfully',
            'redirect': result_url
        })
        
    except Exception as e:
        print(f"Error in generate: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/wordcloud/view/<token>', methods=['GET'])
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

@app.route('/wordcloud/image/<token>/<filename>', methods=['GET'])
def serve_image(token, filename):
    """Serve generated image files"""
    # Validate token
    session_id = validate_token(token)
    if not session_id:
        abort(403)
    
    from werkzeug.utils import secure_filename
    # Ensure the filename is safe
    safe_filename = secure_filename(filename)
    return send_file(os.path.join(TEMP_TOKEN_FOLDER, session_id, safe_filename))

@app.route('/wordcloud/download/<token>/<filename>', methods=['GET'])
def download_image(token, filename):
    """Download image files"""
    # Validate token
    session_id = validate_token(token)
    if not session_id:
        abort(403)
    
    from werkzeug.utils import secure_filename
    # Ensure the filename is safe
    safe_filename = secure_filename(filename)
    
    # Set headers for download
    return send_file(
        os.path.join(TEMP_TOKEN_FOLDER, session_id, safe_filename),
        as_attachment=True
    )

@app.route('/wordcloud/download-all/<token>', methods=['GET'])
def download_all(token):
    """Create a zip of all generated files and serve it"""
    # Validate token
    session_id = validate_token(token)
    if not session_id:
        abort(403)
    
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
        return send_file(
            zip_path,
            as_attachment=True
        )
    except Exception as e:
        print(f"Error creating zip file: {e}")
        abort(500)

@app.route('/', methods=['GET'])
def index():
    """Home page with service overview"""
    return render_template('index.html')

@app.route('/index.html', methods=['GET'])
def home():
    """Home page (alternative route)"""
    return render_template('index.html')

# Simple wordcloud without the advanced options
@app.route('/simple', methods=['GET'])
def simple_wordcloud_form():
    return render_template('new_cloud_gen.html')

@app.route('/simple/generate', methods=['POST'])
def simple_generate_wordcloud():
    words = request.form['words'].splitlines()
    weights = request.form.get('weights', '').splitlines()

    if len(weights) < len(words):
        weights += ['5'] * (len(words) - len(weights))

    weighted_words = []
    for word, weight in zip(words, weights):
        weighted_words.extend([word] * int(weight))

    # Generate three variations of the word cloud with red, white, and blue text
    cloud1_filename = f"new_wordcloud1_{uuid.uuid4()}.png"
    cloud2_filename = f"new_wordcloud2_{uuid.uuid4()}.png"
    cloud3_filename = f"new_wordcloud3_{uuid.uuid4()}.png"

    generate_and_save_wordcloud(weighted_words, cloud1_filename, colormap='bwr')
    generate_and_save_wordcloud(weighted_words, cloud2_filename, colormap='bwr_r')  # Creates a white-ish appearance on a black background
    generate_and_save_wordcloud(weighted_words, cloud3_filename, colormap='RdBu')

    session['cloud1_filename'] = cloud1_filename
    session['cloud2_filename'] = cloud2_filename
    session['cloud3_filename'] = cloud3_filename
    session['timestamp'] = time.time()

    return redirect(url_for('display_wordcloud'))

@app.route('/simple/display')
def display_wordcloud():
    if 'cloud1_filename' not in session or time.time() - session.get('timestamp', 0) > 3600:
        abort(403)

    return render_template('result.html', 
                          cloud1_filename=session['cloud1_filename'], 
                          cloud2_filename=session['cloud2_filename'], 
                          cloud3_filename=session['cloud3_filename'])

@app.route('/new_wordclouds/<filename>')
def uploaded_file(filename):
    from werkzeug.utils import secure_filename
    safe_filename = secure_filename(filename)
    file_path = os.path.join(NEW_WORDCLOUD_FOLDER, safe_filename)
    
    if os.path.exists(file_path):
        app.logger.info(f"Serving file: {file_path}")
        return send_file(file_path)
    else:
        app.logger.error(f"File not found: {file_path}")
        abort(404)

def generate_and_save_wordcloud(words, filename, colormap):
    wordcloud = WordCloud(
        width=1000,
        height=600,
        background_color='black',
        colormap=colormap,
        prefer_horizontal=0.5  # Ensures both horizontal and vertical orientations
    ).generate(" ".join(words))
    wordcloud.to_file(os.path.join(NEW_WORDCLOUD_FOLDER, filename))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
