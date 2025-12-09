#!/bin/bash
# NO set -e

cd /tests

uv venv .tbench-testing
source .tbench-testing/bin/activate
uv pip install pytest pytest-asyncio psycopg2-binary discord.py tzdata

uv run pytest test_approval_session_fix.py -rA


if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
