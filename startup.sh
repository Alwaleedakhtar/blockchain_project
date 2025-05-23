#!/bin/bash

# Create and activate virtual environment
python -m venv antenv
source antenv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Get the port from environment variable or use default
PORT=${PORT:-8000}

# Start the application
echo "Starting application on port $PORT"
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 