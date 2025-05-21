# Blockchain Insight API

A FastAPI application that fetches real-time Bitcoin block data and stores it in MongoDB Atlas.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file:
- Copy `.env.template` to `.env`
- Update the MongoDB URI with your credentials

3. Run the application:
```bash
python3 -m uvicorn main:app --reload
```

## API Endpoints

- `GET /`: Check if API is running
- `GET /blocks`: Get the last 40 blocks
- `POST /update`: Fetch and store new blocks

## Features

- Real-time Bitcoin block data fetching
- MongoDB Atlas integration
- Block data storage and retrieval
- Automatic data updates

## Requirements

- Python 3.8+
- MongoDB Atlas account
- Internet connection for blockchain.info API access 