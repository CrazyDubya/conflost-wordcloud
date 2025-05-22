# Getting Started with MCP WordCloud Generator

## Quick Start

1. Make the start script executable:
   ```bash
   chmod +x start_wordcloud.sh
   ```

2. Run the application:
   ```bash
   ./start_wordcloud.sh
   ```

3. Alternatively, you can run it directly with Python:
   ```bash
   python app.py
   ```

4. Access the application at http://127.0.0.1:5001/mcp/wordcloud

## Manual Installation

If you prefer to set up everything manually:

1. Install required packages:
   ```bash
   pip install flask wordcloud matplotlib nltk pillow numpy
   ```

2. Download NLTK data:
   ```bash
   python -c "import nltk; nltk.download('stopwords')"
   ```

3. Create necessary directories:
   ```bash
   mkdir -p uploads token_sessions new_wordclouds
   ```

4. Run the application:
   ```bash
   python app.py
   ```

## Application Structure

- `app.py` - Main application file
- `/templates` - HTML templates
- `/static` - CSS and JavaScript files
- `/uploads` - Temporary storage for uploaded mask images
- `/token_sessions` - Temporary storage for generated wordclouds
- `/new_wordclouds` - Output directory for wordclouds

## Troubleshooting

- If you encounter "No module named X" errors, make sure to install all dependencies:
  ```bash
  pip install flask wordcloud matplotlib nltk pillow numpy
  ```

- If the application crashes with GUI-related errors on macOS, the application is already set up to use the Agg backend, which should prevent these issues.

- If you have problems with file permissions, make sure the application has write permissions to the `uploads`, `token_sessions`, and `new_wordclouds` directories.
