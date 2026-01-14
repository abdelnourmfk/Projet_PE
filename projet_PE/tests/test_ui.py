from pathlib import Path
import importlib.util


def test_streamlit_app_imports():
    p = Path(__file__).resolve().parents[1] / 'ui' / 'streamlit_app.py'
    assert p.exists(), f"{p} not found"

    spec = importlib.util.spec_from_file_location("ui_app", str(p))
    module = importlib.util.module_from_spec(spec)
    # execute module to catch syntax/import errors
    spec.loader.exec_module(module)

    # basic smoke assertions
    assert hasattr(module, 'REPO_ROOT')
    assert hasattr(module, '__file__')
