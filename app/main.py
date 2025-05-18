from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

app = FastAPI()

@app.get("/blocks")
def get_blocks():
    try:
        blocks = list(collection.find({}, {"_id": 0, "height": 1, "time": 1, "n_tx": 1, "total_fees": 1, "size": 1}).sort("time", 1))
        return {"blocks": blocks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))