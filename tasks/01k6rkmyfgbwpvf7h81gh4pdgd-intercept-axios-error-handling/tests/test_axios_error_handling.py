"""
Comprehensive tests for axios adapter error handling bug fix.

Verifies that intercept.reject() properly throws AxiosError for non-2xx status codes,
especially in React Query/async contexts where error throwing is critical.

Test Philosophy:
1. Build succeeds (no regressions)
2. Agent touched test file (engaged with testing)
3. Agent's tests pass on agent's code (solution is consistent)
4. User's ground truth tests pass on agent's code (meets user's quality bar)
5. Agent's tests fail on broken state (meta-test - tests are actually effective)
"""

import subprocess
import shutil
from pathlib import Path


def test_project_builds():
    """
    Test 1: Verify the project builds without errors.

    The fix shouldn't break the build. This ensures TypeScript compilation
    and bundling succeed after applying changes.
    """
    print("\n=== Test 1: Build Verification ===")

    result = subprocess.run(
        ["pnpm", "run", "build"],
        cwd="/app",
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"Build failed:\n{result.stdout}\n{result.stderr}"

    # Verify dist files were created
    assert Path("/app/dist/adapters/axios.js").exists(), \
        "axios adapter not built"
    assert Path("/app/dist/adapters/axios.d.ts").exists(), \
        "axios adapter types not generated"

    print("✓ Project builds successfully")


def test_agent_modified_test_file():
    """
    Test 2: Verify agent updated adapters.test.ts

    Agent should add tests for the bug fix. Any diff from broken state is sufficient.
    We don't prescribe how many tests or what they look like - just that testing was addressed.
    """
    print("\n=== Test 2: Agent Touched Test File ===")

    broken_tests = Path("/app-broken/src/adapters/adapters.test.ts").read_text()
    agent_tests = Path("/app/src/adapters/adapters.test.ts").read_text()

    assert agent_tests != broken_tests, \
        "Agent didn't modify adapters.test.ts - should add tests for bug fix"

    # Verify file grew (tests added, not just modified)
    assert len(agent_tests) > len(broken_tests), \
        "Test file should grow - agent should add new tests, not just modify existing"

    print("✓ Agent added tests to adapters.test.ts")


def test_agent_tests_pass_on_agent_code():
    """
    Test 3: Run agent's test suite on agent's fixed code

    Internal consistency check - agent's solution should pass agent's own tests.
    """
    print("\n=== Test 3: Agent's Tests Pass ===")

    result = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "src/adapters/adapters.test.ts"],
        cwd="/app",
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Agent's tests fail on agent's own code:\n{result.stdout}\n{result.stderr}"

    print("✓ Agent's tests pass on agent's code")


def test_user_ground_truth_tests_pass():
    """
    Test 4: Run USER's actual tests from fixed commit on agent's code

    This is the critical verification - does agent's fix satisfy the user's
    quality bar? We copy the exact test file the user committed and run it
    against agent's code.
    """
    print("\n=== Test 4: User's Ground Truth Tests ===")

    # Setup: Create temp location for user's tests
    temp_dir = Path("/tmp/user-ground-truth")
    temp_dir.mkdir(exist_ok=True)

    # Initialize git and fetch user's test file
    subprocess.run(["git", "init"], cwd=temp_dir, check=True)
    subprocess.run([
        "git", "remote", "add", "origin",
        "https://github.com/klogt-as/intercept.git"
    ], cwd=temp_dir, check=True)

    subprocess.run([
        "git", "fetch", "origin", "052106281c24329e1af1c2dd8cf7adce2752b1d6",
        "--depth=1"
    ], cwd=temp_dir, check=True)

    subprocess.run([
        "git", "checkout", "FETCH_HEAD", "--", "src/adapters/adapters.test.ts"
    ], cwd=temp_dir, check=True)

    # Copy user's tests to agent's code
    shutil.copy(
        temp_dir / "src/adapters/adapters.test.ts",
        "/app/src/adapters/adapters.test.ts"
    )

    # Run user's tests on agent's code
    result = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "src/adapters/adapters.test.ts"],
        cwd="/app",
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"User's ground truth tests failed on agent's code - agent didn't fully fix the bug:\n{result.stdout}\n{result.stderr}"

    print("✓ User's ground truth tests pass on agent's code")


def test_agent_tests_fail_on_broken_state():
    """
    Test 5: META-TEST - Agent's tests must fail on broken state

    This proves agent's tests actually catch the bug. If agent's tests pass
    on broken state, they're not testing the right thing.

    We copy agent's test file to /app-broken and run it there.
    """
    print("\n=== Test 5: Meta-Test - Tests Detect Bug ===")

    # Copy agent's tests to broken state
    agent_tests = Path("/app/src/adapters/adapters.test.ts").read_text()
    Path("/app-broken/src/adapters/adapters.test.ts").write_text(agent_tests)

    # Run agent's tests on broken code
    result = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "src/adapters/adapters.test.ts"],
        cwd="/app-broken",
        capture_output=True,
        text=True,
        timeout=120
    )

    # MUST fail (agent's tests should catch the bug)
    assert result.returncode != 0, \
        "Agent's tests pass on broken state - tests don't detect the bug!"

    # Verify actual test failures (not just build errors)
    output = result.stdout + result.stderr
    assert "failed" in output.lower() or "✖" in output or "FAIL" in output, \
        f"Expected test failures on broken state, got:\n{output}"

    print("✓ Agent's tests correctly fail on broken state")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short", "-rA"])
