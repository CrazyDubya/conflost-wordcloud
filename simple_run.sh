#!/bin/bash

# The simplest way to run the app - adapts to existing database

# Run the fix script first
echo "================== FIXING THE APPLICATION =================="
python fix_app.py

if [ $? -ne 0 ]; then
    echo "Error running fix script. Please check the error messages above."
    exit 1
fi

echo ""
echo "================== STARTING APPLICATION =================="
echo "Access the application at: http://127.0.0.1:5001"
echo ""

# Run the application
python app_enhanced.py
