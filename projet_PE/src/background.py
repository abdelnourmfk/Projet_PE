"""Background task helper to run detection in a thread and report status/results.
"""
from threading import Thread
from typing import Callable, Optional
import time


def run_detection_background(fn: Callable, args: tuple = (), kwargs: Optional[dict] = None, status_container: dict = None) -> Thread:
    """Run `fn(*args, **kwargs)` in a background thread.

    status_container is an optional dict that will have keys set: 'running', 'error', 'result'
    Returns the Thread object so callers can join.
    """
    kwargs = kwargs or {}
    if status_container is not None:
        status_container['running'] = True
        status_container['error'] = None
        status_container['result'] = None

    def _target():
        try:
            res = fn(*args, **kwargs)
            if status_container is not None:
                status_container['result'] = res
        except Exception as e:
            if status_container is not None:
                status_container['error'] = str(e)
        finally:
            if status_container is not None:
                status_container['running'] = False

    th = Thread(target=_target, daemon=True)
    th.start()
    return th
