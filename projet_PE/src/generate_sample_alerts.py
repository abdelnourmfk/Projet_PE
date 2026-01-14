"""Generate a sample test trace with attack and write alerts using final_model.pkl"""
from src.traffic_gen import generate_synthetic_traffic
from src.features import extract_features_from_csv
from src.detect import detect_and_write_alerts
import os

os.makedirs('outputs', exist_ok=True)
# generate test with attack
generate_synthetic_traffic('data/sample_test.csv', duration_seconds=60, pps=50, attack_windows=[(20,20,'syn_single_src')])
feats = extract_features_from_csv('data/sample_test.csv', window_size=1.0)
feats.to_csv('data/sample_features_test.csv', index=False)
# use final model if available, else fallback to models/model.pkl
model_path = 'models/final_model.pkl' if os.path.exists('models/final_model.pkl') else 'models/model.pkl'
detect_and_write_alerts(model_path, 'data/sample_features_test.csv', 'outputs/sample_alerts.json')
print('Wrote outputs/sample_alerts.json')
