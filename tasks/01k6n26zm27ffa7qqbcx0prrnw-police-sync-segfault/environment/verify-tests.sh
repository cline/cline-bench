#!/bin/bash
# Meta-test: Verify our tests actually detect the bug
set -e

echo "=== META-TEST: Validating test suite detects the bug ==="
echo ""

echo "Step 1: Testing BROKEN state (tests should FAIL)..."
docker run --rm \
  -v $(pwd)/tests:/tests \
  test-broken-state bash -c "
cd /tests
uv venv .tbench-testing
source .tbench-testing/bin/activate
uv pip install pytest
uv run pytest test_segfault_fix.py::test_sync_completes_without_segfault -v
" > /tmp/broken-test-output.txt 2>&1

if grep -q "FAILED" /tmp/broken-test-output.txt; then
    echo "✓ Tests FAIL on broken state (as expected)"
    grep "FAILED\|AssertionError" /tmp/broken-test-output.txt | head -5
elif grep -q "KeyError" /tmp/broken-test-output.txt; then
    echo "✓ Tests crash on broken state with KeyError (the bug we're testing)"
else
    echo "✗ PROBLEM: Tests appear to PASS on broken state (they should fail!)"
    cat /tmp/broken-test-output.txt
    exit 1
fi

echo ""
echo "✓ Meta-test passed: Tests correctly detect the bug on broken state"
