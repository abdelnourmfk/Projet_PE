"""Helper to launch the Streamlit UI using the project's Python interpreter.

Usage: python scripts/run_streamlit.py
This will execute `python -m streamlit run projet_PE/ui/streamlit_app.py`.
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = 'projet_PE/ui/streamlit_app.py'

if __name__ == '__main__':
    cmd = [sys.executable, '-m', 'streamlit', 'run', str(ROOT / APP)]
    print('Running:', ' '.join(cmd))
    subprocess.run(cmd, check=True)
