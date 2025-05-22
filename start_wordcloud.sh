#!/bin/bash

# Set up the environment
echo "Setting up environment for MCP WordCloud Generator..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python 3.6+ to run this application."
    exit 1
fi

# Check for required packages and install if missing
echo "Checking for required packages..."
python3 -m pip install -q flask wordcloud matplotlib nltk pillow numpy

# Download NLTK data if needed
echo "Setting up NLTK data..."
python3 -c "import nltk; try: nltk.data.find('corpora/stopwords'); except LookupError: nltk.download('stopwords')"

# Create directories if they don't exist
echo "Setting up directories..."
mkdir -p uploads token_sessions new_wordclouds

# Start the application
echo "Starting MCP WordCloud Generator..."
echo "Access the application at http://127.0.0.1:5001/mcp/wordcloud"
echo "Press Ctrl+C to stop the server."
python3 app.py
