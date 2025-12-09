#!/bin/bash
set -e

echo "Building broken state Docker image..."
cd clinebench/tasks/01k6n26zm27ffa7qqbcx0prrnw-police-sync-segfault

# Build image with ONLY the broken state (no solution.sh)
docker build -t test-broken-state:latest .

echo ""
echo "Running tests against BROKEN state (should FAIL)..."
echo "=================================================="

# Run container with broken code
docker run --rm -v $(pwd)/tests:/tests:ro test-broken-state:latest bash -c "
cd /tests
bash run-tests.sh
"

echo ""
echo "If you see this, tests INCORRECTLY PASSED on broken state!"
echo "Tests should FAIL with KeyError or segfault."
