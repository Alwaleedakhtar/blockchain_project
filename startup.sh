#!/bin/bash

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Get the port from environment variable or use default
PORT=${PORT:-8000}

# Start the application
echo "Starting application on port $PORT"
cd /home/site/wwwroot
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 