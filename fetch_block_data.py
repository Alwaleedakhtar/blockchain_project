from pymongo.collection import Collection
import requests
import time

def get_latest_block_height():
    try:
        response = requests.get("https://blockchain.info/q/getblockcount", timeout=10)
        if response.status_code == 200:
            return int(response.text.strip())
        else:
            print(f"Error fetching block height: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception while fetching block height: {e}")
        return None

def fetch_block_by_height(height):
    try:
        url = f"https://blockchain.info/block-height/{height}?format=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            block = data["blocks"][0]  # blockchain.info returns a list
            cleaned_block = {
                "height": block.get("height"),
                "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(block.get("time"))),
                "n_tx": block.get("n_tx"),
                "total_fees": block.get("fee", 0),
                "size": block.get("size")
            }
            return cleaned_block
        else:
            print(f"Failed to fetch block {height}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception fetching block {height}: {e}")
        return None

def store_block_to_mongo(block, collection: Collection):
    if collection.find_one({"height": block["height"]}):
        print(f"Block {block['height']} already exists. Skipping insert.")
    else:
        collection.insert_one(block)
        print(f"Stored cleaned block {block['height']}")
