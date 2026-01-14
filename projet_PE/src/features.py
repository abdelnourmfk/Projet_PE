"""Feature extraction utilities: per-window throughput and entropy"""
import pandas as pd
import numpy as np


def _entropy(values):
    if len(values) == 0:
        return 0.0
    counts = values.value_counts(normalize=True)
    probs = counts.values
    return float(-(probs * np.log2(probs)).sum())


def extract_features_from_csv(csv_path: str, window_size: float = 1.0, include_label: bool = False):
    """Read traffic CSV and aggregate features per window.

    Returns DataFrame with columns: ts_start, packets_per_sec, bytes_per_sec, entropy_src_ip, entropy_dst_ip, syn_ratio
    Optionally expects a 'label' column if include_label is True.
    """
    df = pd.read_csv(csv_path)
    df['ts'] = df['ts'].astype(float)
    df = df.sort_values('ts')

    t0 = df['ts'].min()
    t1 = df['ts'].max()
    bins = np.arange(t0, t1 + window_size, window_size)
    df['window'] = pd.cut(df['ts'], bins=bins, include_lowest=True, right=False)

    # avoid FutureWarning from pandas when grouping by a categorical: keep current behavior
    groups = df.groupby('window', observed=False)
    rows = []
    for name, g in groups:
        if g.empty:
            continue
        ts_start = g['ts'].min()
        duration = window_size
        packets = len(g)
        bytes_ = g['length'].sum() if 'length' in g.columns else 0
        pps = packets / duration
        bps = bytes_ / duration
        e_src = _entropy(g['src_ip'])
        e_dst = _entropy(g['dst_ip'])
        syns = (g['flags'].astype(str).str.contains('S')).sum()
        syn_ratio = syns / packets if packets>0 else 0
        row = {
            'ts_start': ts_start,
            'packets_per_sec': pps,
            'bytes_per_sec': bps,
            'entropy_src_ip': e_src,
            'entropy_dst_ip': e_dst,
            'syn_ratio': syn_ratio
        }
        rows.append(row)

    feat_df = pd.DataFrame(rows)
    return feat_df

if __name__ == '__main__':
    print('Sample: extract features from data/demo_traffic.csv')
