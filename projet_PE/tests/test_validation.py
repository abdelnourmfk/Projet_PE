import pandas as pd
from src.validation import validate_features_df, validate_model_path


def test_validate_features_ok(tmp_path):
    df = pd.DataFrame({
        'packets_per_sec': [1.0, 2.0],
        'bytes_per_sec': [100, 200],
        'entropy_src_ip': [1.0, 1.2],
        'entropy_dst_ip': [0.9, 1.1],
        'syn_ratio': [0.0, 1.0],
        'ts_start': [1600000000, 1600000001]
    })
    ok, errors = validate_features_df(df)
    assert ok
    assert errors == []


def test_validate_features_missing_column():
    df = pd.DataFrame({
        'packets_per_sec': [1.0],
        'bytes_per_sec': [100],
        # missing entropy and others
    })
    ok, errors = validate_features_df(df)
    assert not ok
    assert any('Missing columns' in e or 'Column' in e for e in errors)


def test_validate_features_bad_types():
    df = pd.DataFrame({
        'packets_per_sec': ['a', 'b'],
        'bytes_per_sec': [100, 200],
        'entropy_src_ip': [1.0, 1.2],
        'entropy_dst_ip': [0.9, 1.1],
        'syn_ratio': [0.0, 1.0],
        'ts_start': ['notanumber', 'also']
    })
    ok, errors = validate_features_df(df)
    assert not ok
    assert any('not numeric' in e.lower() or 'ts_start' in e for e in errors)


def test_validate_model_path(tmp_path):
    # create a dummy file that is not a model
    p = tmp_path / 'fake_model.pkl'
    p.write_text('not a pickle')
    ok, msg = validate_model_path(str(p))
    assert not ok
    assert 'Unable to load model' in msg

    # non-existent
    ok2, msg2 = validate_model_path(str(tmp_path / 'nope.pkl'))
    assert not ok2
    assert 'does not exist' in msg2
