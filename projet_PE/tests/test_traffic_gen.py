import os
from src.traffic_gen import generate_synthetic_traffic


def test_generate_basic(tmp_path):
    out = tmp_path / "t.csv"
    generate_synthetic_traffic(str(out), duration_seconds=5, pps=10, attack_windows=[(2,2,'syn_single_src')], seed=123)
    assert out.exists()
    text = out.read_text()
    assert 'ts,src_ip' in text
    # Ensure attack packets (flags S) exist
    assert 'S' in text
