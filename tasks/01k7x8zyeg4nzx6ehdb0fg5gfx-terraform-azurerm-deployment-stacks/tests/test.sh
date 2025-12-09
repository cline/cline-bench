#!/bin/bash
# NO set -e

cd /tests

# Use uv for clean process management (critical for Terminal-Bench tmux signaling)
uv venv .tbench-testing
source .tbench-testing/bin/activate
uv pip install pytest==8.4.1

# Run tests with -rA flag (required for TB pytest parser to work correctly)
uv run pytest test_deployment_stacks.py -rA


if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
