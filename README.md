# MCP WordCloud Generator

The MCP WordCloud Generator is an advanced server-side tool for creating beautiful, customizable word clouds with powerful features and secure temporary access.

## Overview

The MCP WordCloud Generator processes text on our servers, extracting meaningful words and generating three different wordcloud visualizations, along with a frequency analysis chart. Your data is accessible through a secure token for one hour, after which it is automatically deleted.

## Getting Started

1. Install the required dependencies:
   ```bash
   pip install flask nltk wordcloud matplotlib pillow numpy
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Access the WordCloud Generator at [http://127.0.0.1:5001/mcp/wordcloud](http://127.0.0.1:5001/mcp/wordcloud)

## Features

### Basic Settings

- **Maximum Words**: Control how many words appear in your wordclouds (50-500).
- **Minimum Word Length**: Filter out short words by setting a minimum length (1-8 characters).
- **Additional Stop Words**: Add custom words to exclude, separated by commas.

### Size Settings

- **Width & Height**: Adjust the dimensions of your wordclouds (500-2000px width, 300-1500px height).
- **Font Selection**: Choose from various fonts including Arial, Impact, Times New Roman, and more.

### Shape Masks

- **Mask Shapes**: Apply shape masks to constrain words within specific outlines:
  - No mask (default rectangular layout)
  - Heart shape
  - Rounded logo
  - Upload your own mask image (PNG, JPG, GIF)

### Color Schemes

- **Three Separate Color Schemes**: Each wordcloud can have its own color scheme from over 50 options:
  - Standard schemes: viridis, plasma, inferno, magma, etc.
  - Diverging schemes: RdBu, coolwarm, etc.
  - Qualitative schemes: Set1, Set2, Paired, etc.
- **Background Colors**: Customize the background color for each wordcloud.

## Results & Downloads

After processing, you'll receive:

- **Three WordClouds**: Each with different color schemes and backgrounds.
- **Top 25 Words Chart**: A bar chart showing the most frequent words.
- **Download Options**:
  - Download individual wordclouds
  - Download the frequency chart
  - Download all images as a ZIP file

## Security & Privacy

- **Temporary Access**: Your wordclouds are available for one hour via a secure token URL.
- **No Permanent Storage**: All data is automatically deleted after expiration.
- **Manual Cleanup**: You can manually delete your session data at any time.

## Technical Information

- Server-side processing using Python, Flask, and NLTK
- Advanced wordcloud generation with WordCloud library
- Secure token-based authentication
- Automatic session management and cleanup

## Notes for Developers

- All files in the `/old` directory are previous versions or unused components
- The main application file is `app.py`
- HTML templates are in the `/templates` directory
- Static assets (CSS, JS) are in the `/static` directory
- The application supports both guest users and authenticated users

## Troubleshooting

- **"NSWindow should only be instantiated on the main thread"**: This application is configured to use a non-interactive Matplotlib backend to avoid this macOS-specific issue.
- **"Session expired" message**: Your one-hour access period has ended. Generate new wordclouds.
- **Error during upload**: Ensure your mask image is in a supported format (PNG, JPG, GIF).
- **No words found**: Try reducing the minimum word length or adding more text.

---

© 2025 temp188.com - MCP WordCloud Generator
