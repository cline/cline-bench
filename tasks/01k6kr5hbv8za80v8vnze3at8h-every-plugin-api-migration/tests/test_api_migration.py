"""
Test suite for every-plugin API migration from Effect-based to promise-based runtime.

This suite verifies the migration of:
1. Telegram plugin tests (3 files) from @effect/vitest to standard vitest
2. efizzybusybot/main.ts from Effect-based runtime to promise-based runtime

Outcome-based verification:
- Transformation patterns applied correctly (6 structural tests)
- Code compiles after migration (1 behavioral test)

The tests don't prescribe HOW to solve it (rename vs update imports), only THAT it works.
Total: 7 tests (6 structural + 1 compilation)
"""

import re
import subprocess
from pathlib import Path
import glob


def find_telegram_test_files():
    """Find telegram test files wherever they are (allows for flexible solutions)."""
    # Look for test files in plugins directory (could be telegram or telegram-source)
    patterns = [
        "/app/plugins/*/src/__tests__/unit/message-logic.test.ts",
        "/app/plugins/*/src/__tests__/integration/polling-integration.test.ts",
        "/app/plugins/*/src/__tests__/integration/webhook-integration.test.ts"
    ]

    found_files = {}
    for pattern in patterns:
        matches = glob.glob(pattern)
        test_name = Path(pattern).name
        if matches:
            # Filter for telegram plugin, preferring 'telegram' over 'telegram-source'
            telegram_matches = [m for m in matches if 'telegram' in m.lower()]

            # If both telegram and telegram-source exist, prefer telegram (the renamed one)
            preferred = [m for m in telegram_matches if '/telegram/' in m and '/telegram-source/' not in m]
            if preferred:
                found_files[test_name] = preferred[0]
            elif telegram_matches:
                found_files[test_name] = telegram_matches[0]

    return found_files


def test_telegram_plugin_imports():
    """Test 1: Verify telegram plugin test files use standard vitest imports (not @effect/vitest)."""
    test_files = find_telegram_test_files()

    assert len(test_files) == 3, \
        f"Expected 3 telegram test files, found {len(test_files)}"

    for test_name, test_file in test_files.items():
        content = Path(test_file).read_text()

        # Should have vitest import
        assert 'from "vitest"' in content or "from 'vitest'" in content, \
            f"{test_file}: Missing vitest import (should be migrated from @effect/vitest)"

        # Should NOT have @effect/vitest import
        assert '@effect/vitest' not in content, \
            f"{test_file}: Still has @effect/vitest import (old API)"

        # Should NOT have it.effect pattern
        assert 'it.effect(' not in content, \
            f"{test_file}: Still has it.effect() pattern (old API)"

        print(f"✓ {test_name}: Imports migrated correctly")


def test_telegram_plugin_async_patterns():
    """Test 2: Verify telegram plugin tests use async/await instead of Effect.gen/yield*."""
    test_files = find_telegram_test_files()

    for test_name, test_file in test_files.items():
        content = Path(test_file).read_text()
        
        # Should have async functions in tests
        assert re.search(r'it\([^,]+,\s*async\s*\(', content), \
            f"{test_file}: Missing async function pattern in tests"
        
        # Should have await keywords (indicates promise-based code)
        assert 'await ' in content, \
            f"{test_file}: Missing await keywords (should use promises)"
        
        # Should NOT have Effect.gen pattern
        assert 'Effect.gen(function*' not in content, \
            f"{test_file}: Still has Effect.gen pattern (old API)"
        
        # Should NOT have yield* pattern (except possibly in comments)
        # Count lines with yield* that aren't comments
        yield_lines = [line for line in content.split('\n') 
                      if 'yield*' in line and not line.strip().startswith('//')]
        assert len(yield_lines) == 0, \
            f"{test_file}: Still has yield* pattern (old API) in {len(yield_lines)} lines"
        
        print(f"✓ {test_name}: Async patterns migrated correctly")


def test_telegram_plugin_stream_processing():
    """Test 3: Verify telegram plugin tests use for-await loops instead of Stream.pipe()."""
    test_files = find_telegram_test_files()

    # Find the unit test (has stream processing)
    unit_test = test_files.get("message-logic.test.ts")
    assert unit_test, "Could not find message-logic.test.ts"

    content = Path(unit_test).read_text()
    
    # Should have for-await loops for stream processing
    assert 'for await' in content, \
        f"{unit_test}: Missing 'for await' loops (new API for streams)"

    # Should NOT have Stream.pipe pattern
    assert 'Stream.pipe(' not in content and '.pipe(Stream.' not in content, \
        f"{unit_test}: Still has Stream.pipe() pattern (old API)"

    # Should NOT have Stream.fromAsyncIterable
    assert 'Stream.fromAsyncIterable' not in content, \
        f"{unit_test}: Still has Stream.fromAsyncIterable (old API)"

    print(f"✓ Stream processing migrated correctly")


def test_telegram_plugin_timeout_syntax():
    """Test 4: Verify telegram plugin tests use vitest timeout syntax instead of Effect.timeout."""
    test_files = find_telegram_test_files()

    for test_name, test_file in test_files.items():
        content = Path(test_file).read_text()
        
        # Should have vitest timeout syntax: { timeout: 10000 }
        assert re.search(r'\{\s*timeout:\s*\d+\s*\}', content), \
            f"{test_file}: Missing vitest timeout syntax"
        
        # Should NOT have Effect.timeout pattern
        assert 'Effect.timeout(' not in content and '.pipe(Effect.timeout' not in content, \
            f"{test_file}: Still has Effect.timeout() pattern (old API)"
        
        print(f"✓ {test_name}: Timeout syntax migrated correctly")


def test_telegram_plugin_package_json():
    """Test 5: Verify @effect/vitest is removed from telegram plugin package.json."""
    # Find package.json in telegram plugin directory (wherever it is)
    package_jsons = glob.glob("/app/plugins/*/package.json")
    telegram_packages = [p for p in package_jsons if 'telegram' in p.lower()]

    assert telegram_packages, "Could not find telegram plugin package.json"

    # If both telegram and telegram-source exist, prefer telegram (the transformed one)
    preferred = [p for p in telegram_packages if '/telegram/' in p and '/telegram-source/' not in p]
    package_to_check = preferred[0] if preferred else telegram_packages[0]

    content = Path(package_to_check).read_text()

    # Should NOT have @effect/vitest dependency
    assert '@effect/vitest' not in content, \
        "package.json still has @effect/vitest dependency (should be removed)"

    # Should have standard vitest
    assert '"vitest"' in content, \
        "package.json should have vitest dependency"

    print("✓ Telegram plugin package.json updated correctly")


def test_efizzybusybot_runtime_pattern():
    """Test 6: Verify efizzybusybot/main.ts uses new promise-based runtime pattern."""
    main_file = Path("/app/examples/efizzybusybot/main.ts")
    assert main_file.exists(), "efizzybusybot/main.ts not found"
    
    content = main_file.read_text()
    
    # Should have: const runtime = createPluginRuntime (no PluginService destructuring)
    assert re.search(r'const\s+runtime\s*=\s*createPluginRuntime', content), \
        "Missing new runtime pattern: const runtime = createPluginRuntime()"
    
    # Should NOT have: const { runtime, PluginService } = createPluginRuntime
    assert 'const { runtime, PluginService }' not in content, \
        "Still has old pattern: const { runtime, PluginService } (should be removed)"
    
    # Should have: Effect.promise(() => runtime.usePlugin())
    assert 'Effect.promise(' in content and 'runtime.usePlugin(' in content, \
        "Missing new plugin usage pattern: Effect.promise(() => runtime.usePlugin())"
    
    # Should NOT have: yield* PluginService
    assert 'yield* PluginService' not in content, \
        "Still has old pattern: yield* PluginService (should be removed)"
    
    # Should NOT have Effect.provide(runtime) in final runPromise
    # Check the last Effect.runPromise call doesn't have Effect.provide(runtime)
    last_run_promise = content.rfind('Effect.runPromise(')
    if last_run_promise != -1:
        # Get text after last Effect.runPromise up to the closing of that call
        remaining = content[last_run_promise:]
        # Find the matching closing paren (simplified - assumes no nested calls)
        assert 'Effect.provide(runtime)' not in remaining[:500], \
            "Final Effect.runPromise still has Effect.provide(runtime) (should be removed)"
    
    print("✓ efizzybusybot/main.ts runtime pattern migrated correctly")


def test_project_compiles():
    """Test 7: Verify TypeScript compilation succeeds after migration (behavioral check)."""
    print("Building monorepo...")
    result = subprocess.run(
        ["bun", "run", "build"],
        cwd="/app",
        capture_output=True,
        timeout=120
    )

    stdout = result.stdout.decode()
    stderr = result.stderr.decode()

    assert result.returncode == 0, \
        f"TypeScript compilation failed after migration:\nStdout: {stdout}\nStderr: {stderr}"

    # Verify successful build message
    assert "successful" in stdout, \
        f"Build didn't report success: {stdout}"

    print("✓ Project compiles successfully after migration")


if __name__ == "__main__":
    # Run tests in order
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])