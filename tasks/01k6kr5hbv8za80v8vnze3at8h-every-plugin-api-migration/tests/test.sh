#!/bin/bash
# NO set -e

cd /tests

# Use uv for isolated test environment (ensures clean process exit for TB)
uv venv .tbench-testing
source .tbench-testing/bin/activate
uv pip install pytest==8.4.1

# Run pytest with -rA flag (required for TB parser to get summary even when all pass)
uv run pytest test_api_migration.py -rA


if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
