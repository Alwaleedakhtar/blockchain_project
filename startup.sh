#!/bin/bash
pip install --upgrade pip
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app 