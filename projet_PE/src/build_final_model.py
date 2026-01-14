"""Train a final model on a larger synthetic dataset and save it to models/final_model.pkl"""
from src.traffic_gen import generate_synthetic_traffic
from src.features import extract_features_from_csv
from src.train_model import train_and_save_model
import os

os.makedirs('models', exist_ok=True)
# Generate a larger "normal" dataset
generate_synthetic_traffic('data/final_train.csv', duration_seconds=300, pps=60, attack_windows=[])
feats = extract_features_from_csv('data/final_train.csv', window_size=1.0)
feats.to_csv('data/final_features.csv', index=False)
train_and_save_model('data/final_features.csv', 'models/final_model.pkl', contamination=0.01)
print('Saved models/final_model.pkl')
