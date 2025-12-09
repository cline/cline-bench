#!/bin/bash
# Test runner for Terminal-Bench
# Uses uv pattern for clean process management (no set -e)

cd /tests

# Create isolated Python environment with uv
uv venv .tbench-testing
source .tbench-testing/bin/activate

# Install pytest
uv pip install pytest

# Run tests with -rA flag (required for TB pytest parser)
# -rA forces pytest to print summary info even when all tests pass
uv run pytest test_orpc_migration.py -rA


if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
