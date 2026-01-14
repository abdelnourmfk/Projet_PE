"""Simple authentication helpers for the Streamlit UI.

- validate_password(password): checks password against environment variable STREAMLIT_UI_PASSWORD if present.
"""
import os


def validate_password(password: str) -> bool:
    """Return True if password matches configured password.

    Uses environment variable STREAMLIT_UI_PASSWORD if set; if not set, returns True (no password required).
    """
    cfg = os.environ.get('STREAMLIT_UI_PASSWORD')
    if cfg is None:
        # no password configured — permit access (suitable for local dev only)
        return True
    if not password:
        return False
    return password == cfg
