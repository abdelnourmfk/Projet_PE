"""Demo pipeline: generate traffic, extract features, train model on normal, test on mixed traffic"""
from src.traffic_gen import generate_synthetic_traffic
from src.features import extract_features_from_csv
from src.train_model import train_and_save_model
from src.detect import detect_and_write_alerts
import os
import pandas as pd

DATA_TRAIN = 'data/train_normal.csv'
DATA_TEST = 'data/test_mixed.csv'
FEATURES_TRAIN = 'data/features_train.csv'
FEATURES_TEST = 'data/features_test.csv'
MODEL_PATH = 'models/model.pkl'
ALERTS_OUT = 'outputs/alerts.json'


def run_demo(data_train: str = DATA_TRAIN,
             data_test: str = DATA_TEST,
             features_train: str = FEATURES_TRAIN,
             features_test: str = FEATURES_TEST,
             model_path: str = MODEL_PATH,
             alerts_out: str = ALERTS_OUT,
             duration_seconds: int = 120,
             pps: int = 50,
             attack_window: tuple = (40, 40, 'syn_single_src')):
    os.makedirs(os.path.dirname(data_train) or 'data', exist_ok=True)
    os.makedirs(os.path.dirname(model_path) or 'models', exist_ok=True)
    os.makedirs(os.path.dirname(alerts_out) or 'outputs', exist_ok=True)

    # generate training (clean) traffic
    generate_synthetic_traffic(data_train, duration_seconds=duration_seconds, pps=pps, attack_windows=[])
    # generate test traffic with an attack window
    generate_synthetic_traffic(data_test, duration_seconds=duration_seconds, pps=pps, attack_windows=[attack_window])

    # extract features
    feat_train = extract_features_from_csv(data_train, window_size=1.0)
    feat_train.to_csv(features_train, index=False)
    feat_test = extract_features_from_csv(data_test, window_size=1.0)
    feat_test.to_csv(features_test, index=False)

    # train model on normal
    train_and_save_model(features_train, model_path, contamination=0.02)

    # detect on test
    alerts = detect_and_write_alerts(model_path, features_test, alerts_out)

    # evaluate simple metric: detection rate on windows inside attack interval
    test_df = pd.read_csv(features_test)
    t_min = test_df['ts_start'].min()
    attack_start = t_min + attack_window[0]
    attack_end = t_min + (attack_window[0] + attack_window[1])
    test_df['is_attack_window'] = ((test_df['ts_start'] >= attack_start) & (test_df['ts_start'] < attack_end))
    # mark windows that generated alerts by comparing epoch seconds (allow small tolerance)
    alerted_secs = set(pd.to_datetime(a['timestamp']).timestamp() for a in alerts)
    def _alerted_for_ts(t):
        for s in alerted_secs:
            if abs(t - s) < 0.6:
                return True
        return False
    test_df['alerted'] = test_df['ts_start'].apply(_alerted_for_ts)
    tp = len(test_df[(test_df['is_attack_window']) & (test_df['alerted'])])
    fn = len(test_df[(test_df['is_attack_window']) & (~test_df['alerted'])])
    tpr = tp / (tp+fn) if (tp+fn)>0 else 0
    print(f"Detection TPR: {tpr*100:.1f}% (goal >= 85%)")
    print(f"Alerts written to {alerts_out}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run demo pipeline')
    parser.add_argument('--duration', type=int, default=120, help='trace duration in seconds')
    parser.add_argument('--pps', type=int, default=50, help='packets per second baseline')
    parser.add_argument('--data-dir', type=str, default='data', help='data directory')
    parser.add_argument('--models-dir', type=str, default='models', help='models directory')
    parser.add_argument('--outputs-dir', type=str, default='outputs', help='outputs directory')
    args = parser.parse_args()

    DATA_DIR = args.data_dir
    MODELS_DIR = args.models_dir
    OUTPUTS_DIR = args.outputs_dir

    run_demo(data_train=f"{DATA_DIR}/train_normal.csv",
             data_test=f"{DATA_DIR}/test_mixed.csv",
             features_train=f"{DATA_DIR}/features_train.csv",
             features_test=f"{DATA_DIR}/features_test.csv",
             model_path=f"{MODELS_DIR}/model.pkl",
             alerts_out=f"{OUTPUTS_DIR}/alerts.json",
             duration_seconds=args.duration,
             pps=args.pps)
