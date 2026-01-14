from pathlib import Path
import importlib.util


def test_run_scripts_and_files_exist():
    root = Path(__file__).resolve().parents[2]
    assert (root / 'run_streamlit.bat').exists(), 'run_streamlit.bat should exist in repo root'
    assert (root / 'scripts' / 'run_streamlit.py').exists(), 'scripts/run_streamlit.py should exist'

    # import without executing main
    spec = importlib.util.spec_from_file_location('scripts.run_streamlit', str(root / 'scripts' / 'run_streamlit.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, 'ROOT')
    assert hasattr(module, 'APP')
