"""Train IsolationForest on normal traffic features and save model"""
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib


def train_and_save_model(features_csv: str, model_path: str, contamination: float = 0.01):
    df = pd.read_csv(features_csv)
    X = df[['packets_per_sec','bytes_per_sec','entropy_src_ip','entropy_dst_ip','syn_ratio']].fillna(0)
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(X)
    joblib.dump(model, model_path)
    return model

if __name__ == '__main__':
    print('train_model: not run directly. Use run_demo.py')
