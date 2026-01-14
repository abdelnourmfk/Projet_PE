import pandas as pd
from src.traffic_gen import generate_synthetic_traffic
from src.features import extract_features_from_csv


def test_feature_extraction_attack_window(tmp_path):
    csv = tmp_path / "t.csv"
    # small trace: duration 6s, attack at seconds 2..3
    generate_synthetic_traffic(str(csv), duration_seconds=6, pps=10, attack_windows=[(2,2,'syn_single_src')], seed=42)
    feats = extract_features_from_csv(str(csv), window_size=1.0)
    assert 'syn_ratio' in feats.columns
    # find attack windows (2 and 3 seconds after start)
    # syn_ratio should be high (close to 1.0) in attack windows
    syns = feats['syn_ratio'].values
    assert syns.max() >= 0.9
    # entropy of src IP should be near 0 for single-src
    low_entropy = feats[feats['syn_ratio'] > 0.9]['entropy_src_ip']
    assert (low_entropy < 0.5).all()
