
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

client = MongoClient("mongodb://localhost:27017")
db = client["blockchain_insight"]
collection = db["bitcoin_blocks"]

def fetch_blocks_last_3h(collection):
    three_hours_ago = datetime.utcnow() - timedelta(hours=3)
    cursor = list(collection.find({"time": {"$gte": three_hours_ago.isoformat()}}, 
                                  {"_id": 0, "height": 1, "time": 1, "n_tx": 1, "total_fees": 1, "size": 1}).sort("time", 1))
    df = pd.DataFrame(cursor)
    if df.empty:
        print("No blocks found in the last 3 hours.")
        return None
    df = df.iloc[:-1]  # Exclude the last block
    df['time'] = pd.to_datetime(df['time'])
    return df

def plot_metrics(df):
    if df is None or df.empty:
        print("No data to plot.")
        return
    plt.figure(figsize=(12, 6))
    plt.plot(df['time'], df['n_tx'], marker='o')
    plt.title("Transactions in the last 3 hours (excluding last block)")
    plt.xlabel("Time")
    plt.ylabel("Number of Transactions")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    df = fetch_blocks_last_3h(collection)
    plot_metrics(df)
