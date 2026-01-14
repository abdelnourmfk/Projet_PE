import os
from src.auth import validate_password


def test_validate_password_no_env():
    if 'STREAMLIT_UI_PASSWORD' in os.environ:
        del os.environ['STREAMLIT_UI_PASSWORD']
    assert validate_password('') is True
    assert validate_password('anything') is True


def test_validate_password_with_env(tmp_path, monkeypatch):
    monkeypatch.setenv('STREAMLIT_UI_PASSWORD', 's3cret')
    assert validate_password('s3cret') is True
    assert validate_password('wrong') is False
    assert validate_password('') is False
