import time
from src.background import run_detection_background


def dummy_task(delay, output):
    time.sleep(delay)
    return output


def test_run_detection_background():
    status = {}
    t = run_detection_background(dummy_task, args=(0.1, 'ok'), status_container=status)
    t.join(timeout=2)
    assert not status.get('running', True)
    assert status.get('result') == 'ok'
    assert status.get('error') is None
