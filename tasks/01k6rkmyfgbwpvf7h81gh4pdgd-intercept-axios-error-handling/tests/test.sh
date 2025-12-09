#!/bin/bash
# NO set -e

cd /tests

# Use uv for isolated test environment (clean process management)
uv venv .tbench-testing
source .tbench-testing/bin/activate
uv pip install pytest==8.4.1

# Run tests with -rA flag (required for Terminal-Bench parser)
uv run pytest test_axios_error_handling.py -rA


if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
