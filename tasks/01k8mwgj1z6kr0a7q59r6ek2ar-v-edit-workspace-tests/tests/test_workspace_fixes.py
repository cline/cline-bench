#!/usr/bin/env python3
"""
Test suite for v-edit workspace bug fixes.
These tests are HIDDEN from the agent during execution and only run after completion.

Tests verify that the 8 specific WorkspaceTest failures are fixed by running the GTest suite.
This is outcome-based testing - we don't care HOW the agent fixed the bugs, only that the
8 tests now pass.
"""

import subprocess
from pathlib import Path


def test_workspace_tests_pass():
    """
    Verify all 8 failing WorkspaceTest tests now pass.
    
    The user's request was to fix these specific tests:
    1. DeleteLines - Off-by-one error
    2. ToplineUpdateAfterEdit - Scrolling boundary condition
    3. BuildFromText - Temp file segment reading
    4. SetCurrentSegmentNavigation - Navigation beyond loaded content
    5. BreakSegmentVariations - Breaking at specific lines
    6. SegmentDeleteOperations - Delete counting
    7. ViewManagementComprehensive - Scrolling clamping logic
    8. ComplexEditWorkflow - Insert operation line counting
    
    This test runs the GTest suite with WorkspaceTest filter and verifies:
    - All tests pass (exit code 0)
    - No failed tests reported
    - The 8 specific tests are in the passing list
    """
    
    # Check that test binary exists (built by Dockerfile or agent rebuild)
    test_binary = Path("/app/build/tests/v_edit_tests")
    assert test_binary.exists(), \
        "Test binary not found at /app/build/tests/v_edit_tests. " \
        "Agent must rebuild project or tests weren't built."
    
    # Run WorkspaceTest suite
    result = subprocess.run(
        [str(test_binary), "--gtest_filter=WorkspaceTest.*"],
        cwd="/app/build",
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Print output for debugging
    print("GTest stdout:")
    print(result.stdout)
    if result.stderr:
        print("GTest stderr:")
        print(result.stderr)
    
    # Verify tests passed (exit code 0)
    assert result.returncode == 0, \
        f"WorkspaceTest suite failed with exit code {result.returncode}. " \
        f"Some tests are still failing. Check output above for details."
    
    # Verify no failed tests in output
    assert "FAILED" not in result.stdout, \
        "Some WorkspaceTest tests still failing. All 8 must pass."
    
    # Verify the 8 specific tests are mentioned as passing
    # We check for the test names in output - GTest prints "[ RUN      ] WorkspaceTest.TestName"
    # and "[       OK ] WorkspaceTest.TestName" for passing tests
    required_tests = [
        "DeleteLines",
        "ToplineUpdateAfterEdit", 
        "BuildFromText",
        "SetCurrentSegmentNavigation",
        "BreakSegmentVariations",
        "SegmentDeleteOperations",
        "ViewManagementComprehensive",
        "ComplexEditWorkflow"
    ]
    
    for test_name in required_tests:
        # Check test ran and passed
        assert f"WorkspaceTest.{test_name}" in result.stdout, \
            f"Test {test_name} not found in output. Was it renamed or removed?"
        assert f"[       OK ] WorkspaceTest.{test_name}" in result.stdout, \
            f"Test {test_name} did not pass. Still failing or got errors."
    
    print(f"✓ All 8 WorkspaceTest failures fixed. Tests now passing.")


if __name__ == "__main__":
    # Run tests when executed directly
    import pytest
    pytest.main([__file__, "-v"])