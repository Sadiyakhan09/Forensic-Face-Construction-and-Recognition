#!/bin/bash
# Start script for Render deployment

# Create necessary directories
mkdir -p data/photos data/sketches data/embeddings data/analytics

# Download sample data if not exists (for demo purposes)
if [ ! -f "data/photos/sample.jpg" ]; then
    echo "Creating sample data directory structure..."
    # This would normally download sample data
    # For now, we'll create empty directories
fi

# Start the application
uvicorn main:app --host 0.0.0.0 --port $PORT
