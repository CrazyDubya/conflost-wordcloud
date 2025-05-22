import nltk

# Download NLTK data needed for wordcloud generation
print("Setting up NLTK data...")
try:
    nltk.download('stopwords')
    print("Stopwords downloaded successfully")
except Exception as e:
    print(f"Error downloading stopwords: {e}")
    
print("NLTK setup complete!")