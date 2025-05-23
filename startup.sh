#!/bin/bash
echo "Starting deployment..."
pip install --upgrade pip
echo "Installing requirements..."
pip install -r requirements.txt
echo "Starting Gunicorn..."
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT 