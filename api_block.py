import pandas as pd
import requests
from adtk.data import validate_series
from adtk.detector import InterQuartileRangeAD, PersistAD
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def update_bitcoin_blocks(url="https://blockchain-api-al-gyb0h3c0djc3a3ca.polandcentral-01.azurewebsites.net/update"):
    try:
        update_response = requests.post(url)
        update_response.raise_for_status()
        print("Update triggered:", update_response.json())
    except requests.exceptions.RequestException as e:
        print("Request Error:",e)
        return None

def load_bitcoin_data(url="https://blockchain-api-al-gyb0h3c0djc3a3ca.polandcentral-01.azurewebsites.net/blocks"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()["blocks"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df.sort_index(inplace=True)
    df['n_tx'] = pd.to_numeric(df['n_tx'], errors='coerce').fillna(0).astype(int)
    df['total_fees'] = pd.to_numeric(df['total_fees'], errors='coerce').fillna(0).astype(int)
    df['size'] = pd.to_numeric(df['size'], errors='coerce').fillna(0).astype(int)
    df['avg_block_fee'] = df['total_fees'] / df['n_tx'].replace(0, 1)
    df['avg_block_size'] = df['size'] / df['n_tx'].replace(0, 1)
    return df

def get_last_n_blocks(df, n=30):
    return df.tail(n)

def apply_statistical_detectors(series):
    iqr_ad = InterQuartileRangeAD(c=0.5)
    persist_ad = PersistAD(c=0.7, side="both")
    return iqr_ad.fit_detect(series), persist_ad.fit_detect(series)

def apply_isolation_forest(series):
    scaler = StandardScaler()
    scaled = scaler.fit_transform(series.values.reshape(-1, 1))
    iso = IsolationForest(contamination=0.1, random_state=42)
    preds = iso.fit_predict(scaled)
    return pd.Series((preds == -1), index=series.index)

def combine_anomalies(anomaly_lists):
    return sum(anomaly.fillna(False).astype(int) for anomaly in anomaly_lists)

def get_anomalies(collection):
    # Fetch data directly from MongoDB
    data = list(collection.find({}, {"_id": 0}).sort("height", -1).limit(40))
    if not data:
        return {"error": "Failed to fetch data"}

    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df.sort_index(inplace=True)
    df['n_tx'] = pd.to_numeric(df['n_tx'], errors='coerce').fillna(0).astype(int)
    df['total_fees'] = pd.to_numeric(df['total_fees'], errors='coerce').fillna(0).astype(int)
    df['size'] = pd.to_numeric(df['size'], errors='coerce').fillna(0).astype(int)
    df['avg_block_fee'] = df['total_fees'] / df['n_tx'].replace(0, 1)
    df['avg_block_size'] = df['size'] / df['n_tx'].replace(0, 1)

    last_blocks = get_last_n_blocks(df, n=30)
    features = {
        'n_tx': 'Number of Transactions',
        'avg_block_fee': 'Average Block Fee',
        'avg_block_size': 'Average Block Size'
    }

    results = {}
    for feature in features:
        series = validate_series(last_blocks[feature])
        series.name = feature
        iqr, persist = apply_statistical_detectors(series)
        iso = apply_isolation_forest(series)
        combined = combine_anomalies([iqr, persist, iso])
        combined.name = "anomaly_score"
        df_final = pd.merge(
            series.reset_index(),
            combined.reset_index(),
            on="time",
            how="left"
        )
        df_final['time'] = df_final['time'].astype(str)
        results[feature] = df_final.to_dict(orient='records')
    return results

