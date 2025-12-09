#!/bin/bash
# Note: No set -e in test.sh per Harbor pattern
# Harbor reads /logs/verifier/reward.txt for final reward

cd /tests

# Install uv if not present
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Use full path to uv
UV_PATH="$HOME/.local/bin/uv"
if [ ! -f "$UV_PATH" ]; then
    UV_PATH="$HOME/.cargo/bin/uv"
fi

# Create isolated test environment
$UV_PATH venv .test-env
source .test-env/bin/activate

# Install test dependencies
$UV_PATH pip install pytest

# Run tests and write reward
if $UV_PATH run pytest test_http_data_bleeding.py -rA; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi