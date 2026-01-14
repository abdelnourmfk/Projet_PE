import pandas as pd
from src.features import _entropy
from src.traffic_gen import generate_synthetic_traffic
from src.features import extract_features_from_csv
from src.train_model import train_and_save_model
from src.detect import detect_and_write_alerts


def test_entropy_empty_and_known():
    # empty series -> zero
    s = pd.Series([], dtype=object)
    assert _entropy(s) == 0.0

    # two values equally likely -> entropy = 1
    s = pd.Series(['a','b','a','b'])
    assert abs(_entropy(s) - 1.0) < 1e-6


def test_alert_timestamps_parseable(tmp_path):
    data = tmp_path / 't.csv'
    ftrain = tmp_path / 'ft.csv'
    ftest = tmp_path / 'ftest.csv'
    model_path = tmp_path / 'model.pkl'
    alerts_out = tmp_path / 'alerts.json'

    # small trace with an attack
    generate_synthetic_traffic(str(data), duration_seconds=10, pps=50, attack_windows=[(2,2,'syn_single_src')], seed=1)
    feats = extract_features_from_csv(str(data), window_size=1.0)
    feats.to_csv(str(ftest), index=False)

    # Train using the first half as 'normal'
    split = len(feats)//2
    feats.iloc[:split].to_csv(str(ftrain), index=False)

    model = train_and_save_model(str(ftrain), str(model_path), contamination=0.02)
    alerts = detect_and_write_alerts(str(model_path), str(ftest), str(alerts_out))

    # ensure all timestamps parse with pandas.to_datetime
    for a in alerts:
        pd.to_datetime(a['timestamp'])  # will raise on parse error
