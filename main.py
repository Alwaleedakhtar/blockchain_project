import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from fetch_block_data import (
    fetch_block_by_height,
    get_latest_block_height,
    store_block_to_mongo
)
import pandas as pd

from api_block import (
    update_bitcoin_blocks,
    load_bitcoin_data,
    get_last_n_blocks,
    apply_statistical_detectors,
    apply_isolation_forest,
    get_anomalies,
    combine_anomalies
)


if os.getenv("ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

app = FastAPI()

# MongoDB Atlas connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("MONGO_URI is not set")

try:
    client = MongoClient(MONGO_URI)
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Failed to connect to MongoDB Atlas: {e}")
    raise Exception(f"Failed to connect to MongoDB Atlas: {e}")

db = client[os.getenv("DATABASE_NAME", "blockchain_insight")]
collection = db[os.getenv("COLLECTION_NAME", "bitcoin_blocks")]

@app.get("/")
def root():
    try:
        # Test database connection
        client.admin.command('ping')
        return {
            "message": "Blockchain Insight API is running and connected to MongoDB Atlas.",
            "status": "healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@app.get("/blocks")
def get_blocks():
    try:
        blocks = list(collection.find({}, {"_id": 0}).sort("height", -1).limit(40))
        return {"blocks": blocks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching blocks: {str(e)}")

@app.post("/update")
def update_blocks():
    try:
        latest_height = get_latest_block_height()
        latest_in_db = collection.find_one(sort=[("height", -1)])
        start_height = latest_in_db["height"] + 1 if latest_in_db else latest_height - 40

        for height in range(start_height, latest_height + 1):
            block = fetch_block_by_height(height)
            if block:
                store_block_to_mongo(block, collection)

        return {"message": f"Updated blocks {start_height} to {latest_height}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating blocks: {str(e)}")

@app.get("/anomalies")
def anomalies():
    return get_anomalies(collection)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
