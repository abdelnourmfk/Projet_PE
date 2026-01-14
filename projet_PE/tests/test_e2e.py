import run_demo
import os


def test_end_to_end_runs(tmp_path, monkeypatch):
    # Call run_demo (it writes into repo folders). Ensure it completes and outputs exist.
    run_demo.run_demo()
    assert os.path.exists('models/model.pkl')
    assert os.path.exists('outputs/alerts.json')
    # Ensure alerts.json is non-empty
    assert os.path.getsize('outputs/alerts.json') > 0
