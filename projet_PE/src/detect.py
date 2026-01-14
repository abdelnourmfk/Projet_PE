"""Load model and detect anomalies on features; emit alerts JSON lines"""
import joblib
import json
import pandas as pd
from uuid import uuid4
from datetime import datetime, timezone


def detect_and_write_alerts(model_path: str, features_csv: str, alerts_output: str):
    model = joblib.load(model_path)
    df = pd.read_csv(features_csv)
    X = df[['packets_per_sec','bytes_per_sec','entropy_src_ip','entropy_dst_ip','syn_ratio']].fillna(0)
    scores = model.decision_function(X)  # higher => more normal in sklearn
    preds = model.predict(X)  # -1 anomaly, 1 normal

    alerts = []
    for i, row in df.iterrows():
        score = float(scores[i])
        pred = int(preds[i])
        if pred == -1:
            alert = {
                # represent UTC times using Z suffix (RFC3339) — remove +00:00 and use Z
                'timestamp': datetime.fromtimestamp(row['ts_start'], timezone.utc).isoformat().replace('+00:00', 'Z'),
                'alert_id': str(uuid4()),
                'score': score,
                'features': {
                    'packets_per_sec': float(row['packets_per_sec']),
                    'bytes_per_sec': float(row['bytes_per_sec']),
                    'entropy_src_ip': float(row['entropy_src_ip']),
                    'entropy_dst_ip': float(row['entropy_dst_ip']),
                    'syn_ratio': float(row['syn_ratio'])
                },
                'verdict': 'anomaly',
                'explanation': 'IsolationForest negative prediction (possible SYN flood)'
            }
            alerts.append(alert)

    # write JSON lines
    with open(alerts_output, 'w') as f:
        for a in alerts:
            f.write(json.dumps(a) + '\n')
    return alerts

if __name__ == '__main__':
    print('Use detect.detect_and_write_alerts(...) from run_demo.py')