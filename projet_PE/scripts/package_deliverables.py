"""Create a zip archive `deliverables.zip` with final artifacts"""
import zipfile
import os

INCLUDE = [
    'README.md',
    'DELIVERABLES.md',
    'REPORT.md',
    'CHANGELOG.md',
    'LICENSE',
    'models/final_model.pkl',
    'outputs/sample_alerts.json',
    'data/final_features.csv',
    'notebooks/demo.ipynb',
    'src',
    'tests'
]

ZIP_NAME = 'deliverables.zip'

with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zf:
    for path in INCLUDE:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    full = os.path.join(root, f)
                    arc = os.path.relpath(full, '.')
                    zf.write(full, arc)
        elif os.path.exists(path):
            zf.write(path, path)
        else:
            print(f"Warning: {path} not found, skipping")

print(f"Created {ZIP_NAME}")
