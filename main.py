from pymongo import MongoClient
from fetch_block_data import (
    fetch_block_by_height,
    get_latest_block_height,
    store_block_to_mongo
)
from detect_anomaly import (
    detect_block_height_anomalies,
    detect_time_gap_anomalies,
    detect_block_metrics_anomalies
)

def main():
    # ✅ Connect to MongoDB Atlas instead of localhost
    client = MongoClient("mongodb+srv://alakhtar:blockchain@cluster0.vt7no8i.mongodb.net/")
    db = client["blockchain_insight"]
    collection = db["bitcoin_blocks"]

    print("Fetching latest Bitcoin block height...")
    latest_height = get_latest_block_height()

    if latest_height is None:
        print("Could not fetch latest block height.")
    else:
        print(f"Latest block height: {latest_height}")

        # Check the latest block already in DB
        latest_in_db = collection.find_one(sort=[("height", -1)])
        start_height = latest_in_db["height"] + 1 if latest_in_db else latest_height - 40

        print(f"Fetching blocks {start_height} to {latest_height} and inserting into MongoDB...")

        for height in range(start_height, latest_height + 1):
            block = fetch_block_by_height(height)
            if block:
                store_block_to_mongo(block, collection)
                print(f"Inserted block {block['height']}")
            else:
                print(f"Failed to fetch block {height}")

        print("\nRunning anomaly detection modules...\n")

        print("Running block height anomaly detection...")
        detect_block_height_anomalies()

        print("\nRunning block time gap anomaly detection...")
        detect_time_gap_anomalies()

        print("\nRunning anomaly detection on block metrics (transactions, fees, size)...")
        detect_block_metrics_anomalies()

    client.close()
    print("MongoDB client connection closed cleanly.")

if __name__ == "__main__":
    main()
