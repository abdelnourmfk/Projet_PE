# Testing & Continuous Integration

This project includes automated tests and a GitHub Actions workflow to run them.

## Running tests locally

1. Create and activate a Python virtual environment (Python 3.10+ recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. Install dependencies (the actual project lives in the nested `projet_PE/` folder):

   ```powershell
   pip install -r projet_PE/requirements.txt
   ```

3. Run tests:

   ```powershell
   python -m pytest projet_PE/tests -q
   ```

Notes:
- The test suite includes an `tests/conftest.py` that adds the project root to `sys.path` to allow `src.*` imports during test runs. Alternatively, you can install the package in editable mode (see "Make installable" below).
- Some tests may write to `models/` or `outputs/`; the tests are designed to use temporary files where possible.

## Continuous integration (GitHub Actions)

A GitHub Actions workflow is included at `.github/workflows/ci.yml`. It runs on pushes and pull requests against `main`/`master`, and performs:

- Checkout
- Set up Python (3.10 & 3.11 matrix)
- Install project dependencies from `projet_PE/requirements.txt`
- Run `pytest projet_PE/tests -q`

If you want to run CI locally, you can use `act` (https://github.com/nektos/act) or run the same commands as in the workflow.

## Make the project installable (optional)

A `pyproject.toml` has been added to the inner project folder (`projet_PE/`) so you can install it in editable mode. This avoids adding `sys.path` tweaks in tests.

```powershell
# from repository root
cd projet_PE
pip install -e .
```

After installing editable, you can run tests from the repo root without relying on `tests/conftest.py`.

---

If you'd like, I can add a `pyproject.toml` and a CI badge to the `README.md`. Let me know and I will implement it.