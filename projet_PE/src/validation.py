"""Small validation helpers for features CSV and model loading

Functions:
- validate_features_df(df): checks required columns, types, non-empty, returns (ok, errors)
- validate_model_path(path): checks file exists and model can be loaded, returns (ok, error)
"""
from typing import Tuple, List
import os
import pandas as pd
import joblib

REQUIRED_COLUMNS = ['packets_per_sec', 'bytes_per_sec', 'entropy_src_ip', 'entropy_dst_ip', 'syn_ratio', 'ts_start']


def validate_features_df(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Return (ok, errors)."""
    errors: List[str] = []

    if df is None:
        errors.append('Features data is None')
        return False, errors

    # Check columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f'Missing columns: {missing}')

    # minimal rows
    if df.shape[0] == 0:
        errors.append('No rows in features CSV')

    # types: check numeric columns
    numeric_cols = ['packets_per_sec', 'bytes_per_sec', 'entropy_src_ip', 'entropy_dst_ip', 'syn_ratio']
    for c in numeric_cols:
        if c in df.columns:
            if not pd.api.types.is_numeric_dtype(df[c]):
                # try to coerce
                try:
                    pd.to_numeric(df[c])
                except Exception:
                    errors.append(f'Column {c} is not numeric')

    # ts_start presence and numeric
    if 'ts_start' in df.columns:
        if not pd.api.types.is_numeric_dtype(df['ts_start']):
            try:
                pd.to_numeric(df['ts_start'])
            except Exception:
                errors.append('Column ts_start is not numeric (epoch seconds expected)')
    else:
        if 'ts_start' not in missing:
            errors.append('Column ts_start missing')

    return (len(errors) == 0), errors


def validate_model_path(path: str) -> Tuple[bool, str]:
    if not os.path.exists(path):
        return False, f'Model path does not exist: {path}'
    try:
        joblib.load(path)
    except Exception as e:
        return False, f'Unable to load model: {e}'
    return True, ''
