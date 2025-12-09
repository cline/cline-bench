#!/bin/bash
set -e

cd /tests

# Create isolated test environment with uv (Harbor standard pattern)
uv venv .test-env
source .test-env/bin/activate
uv pip install pytest Pillow

# Run tests and write reward to Harbor's expected location
if uv run pytest test_film_archiver_fixes.py -v -rA; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi