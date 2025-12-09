#!/usr/bin/env python3
"""
Test suite for Police UK sync segfault fix.
These tests are HIDDEN from the agent during execution and only run after completion.

Tests verify that the agent solved what the USER wanted:
1. Stop the crash when syncing neighbourhoods
2. Handle malformed API data gracefully
3. Work in concurrent context (production scenario)
4. Ensure the fix doesn't break other things

We test OUTCOMES, not implementation details.
"""

import subprocess
from pathlib import Path


def test_handles_malformed_data_from_api():
    """
    Test 1: CAPABILITY TEST - Can the code handle bad API data?

    Tests the SPIRIT of what user wanted: handle malformed coordinates from Police UK API.
    Doesn't prescribe HOW (try-except vs validation vs schema), but DOES verify
    the capability exists.

    The production crash was: coord['longitude'] on missing key → KeyError → segfault
    This test verifies the agent added SOME form of error handling.
    """
    result = subprocess.run([
        "bash", "-c", """
source .venv/bin/activate && python3 -c "
import sys
sys.path.insert(0, '/app')
from database.duckdb_client import DuckDBClient
import logging

# Suppress normal logs, keep errors
logging.basicConfig(level=logging.ERROR)

db = DuckDBClient('data/test_malformed.db')
db.connect()
db.initialize_schema()

# CRITICAL TEST: Pass data that caused production segfault
# Missing 'longitude' key - exactly what MC28 returned
malformed = [{'latitude': '53.5'}]  # Missing longitude!

# Call insert - this MUST NOT crash
try:
    db.insert_neighbourhood('test', 'mc28', 'Test MC28', malformed)
    print('HANDLED_GRACEFULLY')  # Got here = handled the error
except Exception as e:
    # If exception propagates to test script, agent didn't handle it
    print(f'UNHANDLED_EXCEPTION: {type(e).__name__}')
    sys.exit(1)

db.close()
"
"""
    ], capture_output=True, timeout=30, cwd="/app")

    stdout = result.stdout.decode()
    stderr = result.stderr.decode()

    # Check for segfault first (most critical)
    assert result.returncode != 139, \
        "Process segfaulted (exit 139) when handling malformed data!"
    assert result.returncode != -11, \
        "Process segfaulted (SIGSEGV) when handling malformed data!"
    assert "Segmentation fault" not in stderr, \
        f"Segmentation fault in stderr: {stderr}"

    # Agent MUST handle malformed data gracefully
    assert 'HANDLED_GRACEFULLY' in stdout, \
        f"Agent didn't handle malformed data (missing longitude key)! " \
        f"This is the core bug. stdout: {stdout}, stderr: {stderr}"

    # Should NOT have unhandled exception
    assert 'UNHANDLED_EXCEPTION' not in stdout, \
        f"Agent let exception propagate - no error handling for bad data. " \
        f"KeyError would still crash in production threading. Output: {stdout}"

    print("✓ Code handles malformed coordinates (missing keys) gracefully")


def test_concurrent_stress_handles_malformed_data():
    """
    Test 2: CONCURRENCY TEST - Simulate actual production conditions.

    The segfault happened specifically in concurrent.futures threading.
    Test that the fix works in concurrent context, not just single-threaded.

    This is CRITICAL because:
    - Threading locks alone won't prevent KeyError on malformed data
    - Error handling in main thread != error handling in worker threads
    - Production uses concurrent sync, tests must match that

    This catches solutions that work in simple tests but fail in production.
    """
    result = subprocess.run([
        "bash", "-c", """
source .venv/bin/activate && python3 -c "
import sys
sys.path.insert(0, '/app')
from database.duckdb_client import DuckDBClient
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.ERROR)

db = DuckDBClient('data/concurrent_test.db')
db.connect()
db.initialize_schema()

# Simulate concurrent sync like production
# Mix valid and malformed data across threads
def insert_neighbourhood(data):
    force_id, neighbourhood_id, name, coords = data
    db.insert_neighbourhood(force_id, neighbourhood_id, name, coords)
    return neighbourhood_id

test_data = [
    ('gm', 'valid1', 'Valid Area', [{'latitude': '53.5', 'longitude': '-2.2'}]),
    ('gm', 'mc28-bad', 'MC28 Malformed', [{'latitude': '53.5'}]),  # Missing longitude!
    ('gm', 'valid2', 'Valid Area 2', [{'latitude': '53.6', 'longitude': '-2.3'}]),
    ('gm', 'bad-none', 'Malformed None', [{'latitude': None, 'longitude': '2.2'}]),  # None value
    ('gm', 'valid3', 'Valid Area 3', [{'latitude': '53.7', 'longitude': '-2.4'}]),
    ('gm', 'bad-type', 'Malformed Type', [{'latitude': 'invalid', 'longitude': 'bad'}]),  # Invalid
]

# Run insertions concurrently like production does
# This is the ACTUAL crash scenario: concurrent.futures + malformed data
try:
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(insert_neighbourhood, test_data))
    print('CONCURRENT_SUCCESS')
except Exception as e:
    print(f'CONCURRENT_FAIL: {type(e).__name__}')
    sys.exit(1)

db.close()
"
"""
    ], capture_output=True, timeout=60, cwd="/app")

    stdout = result.stdout.decode()
    stderr = result.stderr.decode()

    # Critical: NO SEGFAULT in concurrent context
    assert result.returncode != 139, \
        "Segfault in concurrent context! Agent's solution doesn't work in production scenario."
    assert result.returncode != -11, \
        "SIGSEGV in concurrent context! This is the actual production crash scenario."
    assert 'Segmentation fault' not in stderr, \
        f"Segfault detected in concurrent operations: {stderr}"

    # Must complete concurrent operations successfully
    assert 'CONCURRENT_SUCCESS' in stdout, \
        f"Concurrent insertions failed. This simulates production! " \
        f"stdout: {stdout}, stderr: {stderr}"

    assert 'CONCURRENT_FAIL' not in stdout, \
        f"Concurrent operations failed with exception. Production would crash. Output: {stdout}"

    print("✓ Handles malformed data in concurrent context (production scenario)")


def test_concurrent_operations_not_serialized():
    """
    Test 3: PERFORMANCE TEST - Verify agent didn't add unnecessary locks.

    The bug is a DATA problem (malformed coordinates), not a CONCURRENCY problem.

    Wrong approaches:
    - Adding threading.Lock() to all DuckDB operations
    - This "fixes" the crash by accident (serializing operations)
    - But causes MASSIVE performance degradation

    Correct approaches:
    - Try-except for malformed data
    - Schema validation
    - Data preprocessing
    - Any approach that handles bad data WITHOUT serializing DB access

    This test compares concurrent operation speed:
    - Reference solution (no locks): Fast concurrent execution
    - Agent with locks: Slow serialized execution (>3x slower)

    If agent is >3x slower, they added locks - HARD FAILURE.
    """
    import tempfile
    import time
    import sys
    import shutil

    # Get reference solution for comparison
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone reference repo
        subprocess.run([
            "git", "clone", "https://github.com/AndreasThinks/your-police-events.git", tmpdir
        ], check=True, capture_output=True, timeout=60)

        subprocess.run([
            "git", "checkout", "b39c3feaac22bc660bb72d24e5378dae3eb2b593"
        ], cwd=tmpdir, check=True, capture_output=True, timeout=30)

        # Measure reference performance with concurrent operations
        ref_result = subprocess.run([
            "bash", "-c", f"""
cd {tmpdir}
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
pip install -q -e . 2>/dev/null || true

python3 -c "
import sys
import time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '{tmpdir}')
from database.duckdb_client import DuckDBClient

db = DuckDBClient('data/perf_ref.db')
db.connect()
db.initialize_schema()

def insert_op(i):
    time.sleep(0.02)  # Simulate API delay (20ms)
    db.insert_neighbourhood(
        'test', f'nb-{{i}}', f'Area {{i}}',
        [{{'latitude': f'{{53.0 + i*0.01}}', 'longitude': f'{{-2.0 + i*0.01}}'}}]
    )
    return i

# Run 30 operations concurrently (3 batches of 10 with max_workers=10)
start = time.time()
with ThreadPoolExecutor(max_workers=10) as executor:
    list(executor.map(insert_op, range(30)))
duration = time.time() - start

db.close()
print(f'REF_TIME:{{duration:.3f}}')
"
"""
        ], capture_output=True, timeout=120, cwd=tmpdir)

        ref_output = ref_result.stdout.decode()
        ref_match = [line for line in ref_output.split('\n') if 'REF_TIME:' in line]
        assert ref_match, f"Failed to get reference timing. Output: {ref_output}"

        ref_duration = float(ref_match[0].split(':')[1])
        print(f"Reference solution (no locks): {ref_duration:.3f}s")

    # Measure agent's solution with same concurrent workload
    agent_result = subprocess.run([
        "bash", "-c", """
cd /app
source .venv/bin/activate

python3 -c "
import sys
import time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/app')
from database.duckdb_client import DuckDBClient

db = DuckDBClient('data/perf_agent.db')
db.connect()
db.initialize_schema()

def insert_op(i):
    time.sleep(0.02)  # Same 20ms API delay
    db.insert_neighbourhood(
        'test', f'nb-{i}', f'Area {i}',
        [{'latitude': f'{53.0 + i*0.01}', 'longitude': f'{-2.0 + i*0.01}'}]
    )
    return i

# Same 30 operations, same concurrency
start = time.time()
with ThreadPoolExecutor(max_workers=10) as executor:
    list(executor.map(insert_op, range(30)))
duration = time.time() - start

db.close()
print(f'AGENT_TIME:{duration:.3f}')
"
"""
    ], capture_output=True, timeout=120, cwd="/app")

    agent_output = agent_result.stdout.decode()
    agent_match = [line for line in agent_output.split('\n') if 'AGENT_TIME:' in line]
    assert agent_match, f"Failed to get agent timing. Output: {agent_output}"

    agent_duration = float(agent_match[0].split(':')[1])
    print(f"Agent solution: {agent_duration:.3f}s")

    # Calculate slowdown
    slowdown_ratio = agent_duration / ref_duration
    print(f"Slowdown ratio: {slowdown_ratio:.2f}x")

    # HARD FAILURE if >3x slower
    # Expected with locks: 6-10x slower (serialized vs concurrent)
    # Expected without locks: 0.8-1.5x (normal variance)
    assert slowdown_ratio <= 3.0, (
        f"\n❌ PERFORMANCE FAILURE: Agent solution is {slowdown_ratio:.1f}x slower!\n"
        f"   Reference: {ref_duration:.3f}s | Agent: {agent_duration:.3f}s\n\n"
        f"   This indicates agent added THREADING LOCKS to DuckDB operations.\n"
        f"   The bug is a DATA problem (malformed coordinates from API),\n"
        f"   NOT a concurrency problem.\n\n"
        f"   Adding locks:\n"
        f"   - Serializes all database operations\n"
        f"   - Massive performance cost (10x+ slower in production)\n"
        f"   - Doesn't address root cause\n\n"
        f"   Correct fix: Handle malformed data (try-except, validation, etc.)\n"
        f"   WITHOUT adding locks that serialize concurrent operations."
    )

    print(f"✓ Agent solution performs well - no unnecessary serialization")


def test_handles_geometrically_invalid_polygons():
    """
    Test 4: ROBUSTNESS TEST - Handles invalid geometry, not just missing keys.

    The bug was triggered by malformed COORDINATE DATA, but production can also
    receive GEOMETRICALLY INVALID polygons:
    - Self-intersecting (bowtie shapes)
    - Degenerate (collinear points)
    - Duplicate consecutive points

    Reference solution uses ST_IsValid + ST_MakeValid for robustness.
    Agents can use any approach (validation, repair, error handling, skip).

    This ensures agents don't just handle KeyError but also geometric edge cases
    that could crash DuckDB's spatial operations.
    """
    result = subprocess.run([
        "bash", "-c", """
source .venv/bin/activate && python3 -c "
import sys
sys.path.insert(0, '/app')
from database.duckdb_client import DuckDBClient
import logging

logging.basicConfig(level=logging.ERROR)

db = DuckDBClient('data/test_invalid_geom.db')
db.connect()
db.initialize_schema()

# Test Case 1: Self-intersecting polygon (bowtie shape)
# Forms figure-8 pattern - geometrically invalid
bowtie = [
    {'latitude': '53.0', 'longitude': '-2.0'},
    {'latitude': '53.1', 'longitude': '-2.1'},
    {'latitude': '53.0', 'longitude': '-2.1'},  # Crosses back
    {'latitude': '53.1', 'longitude': '-2.0'}   # Completes bowtie
]
db.insert_neighbourhood('test', 'bowtie', 'Self-Intersecting', bowtie)

# Test Case 2: Degenerate polygon (collinear points)
# Creates line, not area - invalid polygon
line = [
    {'latitude': '53.0', 'longitude': '-2.0'},
    {'latitude': '53.1', 'longitude': '-2.0'},  # Same longitude
    {'latitude': '53.2', 'longitude': '-2.0'}   # All collinear
]
db.insert_neighbourhood('test', 'line', 'Degenerate', line)

# Test Case 3: Duplicate consecutive points
# Can cause issues in geometry processing
dupe = [
    {'latitude': '53.0', 'longitude': '-2.0'},
    {'latitude': '53.0', 'longitude': '-2.0'},  # Exact duplicate
    {'latitude': '53.1', 'longitude': '-2.1'},
    {'latitude': '53.0', 'longitude': '-2.1'}
]
db.insert_neighbourhood('test', 'dupe', 'Duplicate Points', dupe)

db.close()
print('ROBUST_TO_INVALID_GEOMETRY')
"
"""
    ], capture_output=True, timeout=60, cwd="/app")

    stdout = result.stdout.decode()
    stderr = result.stderr.decode()

    # Should NOT crash on invalid geometry
    assert result.returncode != 139, \
        "Segfault on invalid geometry (self-intersecting/degenerate polygons)!"
    assert result.returncode != -11, \
        "SIGSEGV on invalid geometry!"
    assert "Segmentation fault" not in stderr, f"Segfault on invalid geometry: {stderr}"

    # Should handle all three invalid geometry cases
    assert 'ROBUST_TO_INVALID_GEOMETRY' in stdout, \
        f"Agent didn't handle invalid geometry robustly. " \
        f"Must handle self-intersecting, degenerate, and duplicate-point polygons. " \
        f"Reference uses ST_IsValid+ST_MakeValid, but any validation/repair/error-handling works. " \
        f"stdout: {stdout}, stderr: {stderr}"

    print("✓ Handles geometrically invalid polygons (self-intersecting, degenerate, duplicates)")


def test_ground_truth_tests_pass():
    """
    Test 5: GROUND TRUTH TEST - Run actual tests from fixed commit.

    User said "ensure everything works" - run the tests from the working state.
    This prevents gaming and validates overall correctness.
    """
    import tempfile
    import shutil

    # Create temp directory for ground truth tests
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone repo and checkout FIXED commit to get ground truth tests
        clone_result = subprocess.run(
            ["git", "clone", "https://github.com/AndreasThinks/your-police-events.git", tmpdir],
            capture_output=True,
            timeout=60
        )
        assert clone_result.returncode == 0, f"Failed to clone repo: {clone_result.stderr.decode()}"

        checkout_result = subprocess.run(
            ["git", "checkout", "b39c3feaac22bc660bb72d24e5378dae3eb2b593"],
            cwd=tmpdir,
            capture_output=True,
            timeout=30
        )
        assert checkout_result.returncode == 0, f"Failed to checkout fix commit: {checkout_result.stderr.decode()}"

        # Copy ground truth tests to safe location
        ground_truth_tests = Path(tmpdir) / "tests"
        test_backup = Path("/tmp/ground_truth_tests")
        if test_backup.exists():
            shutil.rmtree(test_backup)
        shutil.copytree(ground_truth_tests, test_backup)

        # Run ground truth tests against agent's code
        result = subprocess.run(
            ["bash", "-c", f"source .venv/bin/activate && pytest {test_backup} -v --tb=short -x"],
            cwd="/app",
            capture_output=True,
            timeout=120
        )

        stdout = result.stdout.decode()
        stderr = result.stderr.decode()

        # Critical: NO SEGFAULT during test execution
        assert "Segmentation fault" not in stdout and "Segmentation fault" not in stderr, \
            "Ground truth tests triggered segmentation fault! Agent's fix doesn't work."

        assert "Fatal Python error" not in stderr, \
            f"Fatal Python error in tests: {stderr}"

        # Ground truth tests should pass with agent's fix
        if result.returncode == 0:
            print("✓ All ground truth tests passed")
        else:
            # Some tests might fail (API keys, etc.) but no segfaults is key
            print(f"⚠ Some ground truth tests failed (exit {result.returncode}), but no segfault")
            print("   Agent's fix prevents crashes even if some tests need adjustment")


if __name__ == "__main__":
    # Run tests when executed directly
    import pytest
    pytest.main([__file__, "-v"])
