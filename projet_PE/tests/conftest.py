import sys
import os

# Ensure project root (parent of this tests folder) is on sys.path so tests can import `src` and top-level modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
