import os
from src.traffic_gen import generate_synthetic_traffic
from src.features import extract_features_from_csv
from src.train_model import train_and_save_model
from src.detect import detect_and_write_alerts


def test_detection_pipeline(tmp_path):
    data = tmp_path / 'data.csv'
    ftrain = tmp_path / 'feat_train.csv'
    ftest = tmp_path / 'feat_test.csv'
    model_path = tmp_path / 'model.pkl'
    alerts_out = tmp_path / 'alerts.json'

    generate_synthetic_traffic(str(data), duration_seconds=10, pps=20, attack_windows=[(3,4,'syn_single_src')], seed=123)
    feats = extract_features_from_csv(str(data), window_size=1.0)
    feats.to_csv(str(ftest), index=False)

    # Train using the first half as 'normal' (simulate clean training)
    split = len(feats)//2
    feats.iloc[:split].to_csv(str(ftrain), index=False)

    model = train_and_save_model(str(ftrain), str(model_path), contamination=0.02)
    alerts = detect_and_write_alerts(str(model_path), str(ftest), str(alerts_out))

    # There should be at least one alert during the attack window
    assert os.path.exists(str(alerts_out))
    assert len(alerts) >= 1
    # ensure at least one alert has syn_ratio == 1.0 (attack windows)
    assert any(a['features']['syn_ratio'] >= 0.9 for a in alerts)
