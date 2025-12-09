#!/bin/bash
set -e

cd /tests

echo "Running comprehensive test suite with app's virtualenv..."
cd /app

# Use app's virtualenv which has all dependencies installed
source .venv/bin/activate

# Run the comprehensive test suite
if pytest /tests/test_mimic_loader.py /tests/test_synthea_loader.py /tests/test_bundle_resource_counting.py -v -rA; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi