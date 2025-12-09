#!/usr/bin/env python3
"""
Verification tests for oRPC client migration task.

Tests verify that 4 React components were migrated from fetch() calls
to type-safe oRPC client, following the user's actual implementation in PR #1.

Components migrated:
- src/components/ConnectDiscourse.tsx
- src/components/PublishButton.tsx
- src/components/navigation.tsx
- src/pages/profile.tsx

Test philosophy: Outcome-based verification
- Compilation succeeds (TypeScript type safety)
- Old fetch patterns removed
- New oRPC client patterns present
- Old API route deleted
"""

import subprocess
import sys
from pathlib import Path


def test_typescript_compiles():
    """
    Test 1: Verify TypeScript type-checking passes

    The migration must have correct TypeScript types. We use tsc --noEmit
    to check types without building (Next.js build has unrelated SSR issues).
    """
    print("\n=== Test 1: TypeScript Type Check ===")
    print("Checking TypeScript types...")

    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd="/app",
        capture_output=True,
        timeout=120
    )

    stdout = result.stdout.decode()
    stderr = result.stderr.decode()

    assert result.returncode == 0, \
        f"TypeScript type checking failed:\nStdout: {stdout}\nStderr: {stderr}"

    print("✓ TypeScript types are correct")


def test_connect_discourse_migrated():
    """
    Test 2: ConnectDiscourse.tsx migrated to oRPC client
    
    Negative: No fetch to /api/discourse/auth
  Positive: Imports client, uses client.discourse.getUserApiAuthUrl
    """
    print("\n=== Test 2: ConnectDiscourse.tsx Migration ===")
    
    file_path = Path("/app/src/components/ConnectDiscourse.tsx")
    assert file_path.exists(), "ConnectDiscourse.tsx not found"
    
    content = file_path.read_text()
    
    # Negative test: No fetch to old API
    assert 'fetch("/api/discourse/auth' not in content, \
        "ConnectDiscourse still contains fetch to /api/discourse/auth"
    assert 'fetch("/api/discourse' not in content, \
        "ConnectDiscourse still contains fetch to /api/discourse"
    
    # Positive test: Uses oRPC client
    assert 'import { client } from' in content or "import { client } from" in content, \
        "ConnectDiscourse doesn't import client"
    assert 'client.discourse.getUserApiAuthUrl' in content, \
        "ConnectDiscourse doesn't use client.discourse.getUserApiAuthUrl"
    
    print("✓ ConnectDiscourse migrated correctly")


def test_publish_button_migrated():
    """
    Test 3: PublishButton.tsx migrated to oRPC client
    
    Negative: No fetch to /api/discourse/posts/create
    Positive: Imports client, uses client.discourse.createPost
    """
    print("\n=== Test 3: PublishButton.tsx Migration ===")
    
    file_path = Path("/app/src/components/PublishButton.tsx")
    assert file_path.exists(), "PublishButton.tsx not found"
    
    content = file_path.read_text()
    
    # Negative test: No fetch to old API
    assert 'fetch("/api/discourse/posts' not in content, \
        "PublishButton still contains fetch to /api/discourse/posts"
    assert 'fetch("/api/discourse' not in content, \
        "PublishButton still contains fetch to /api/discourse"
    
    # Positive test: Uses oRPC client
    assert 'import { client } from' in content or "import { client } from" in content, \
        "PublishButton doesn't import client"
    assert 'client.discourse.createPost' in content, \
        "PublishButton doesn't use client.discourse.createPost"
    
    print("✓ PublishButton migrated correctly")


def test_navigation_migrated():
    """
    Test 4: navigation.tsx migrated to oRPC client
    
    Negative: No fetch to /api/discourse/linkage
    Positive: Imports client, uses client.discourse.getLinkage
    """
    print("\n=== Test 4: navigation.tsx Migration ===")
    
    file_path = Path("/app/src/components/navigation.tsx")
    assert file_path.exists(), "navigation.tsx not found"
    
    content = file_path.read_text()
    
    # Negative test: No fetch to old API
    assert 'fetch("/api/discourse/linkage' not in content, \
        "navigation still contains fetch to /api/discourse/linkage"
    assert 'fetch("/api/discourse' not in content, \
        "navigation still contains fetch to /api/discourse"
    
    # Positive test: Uses oRPC client
    assert 'import { client } from' in content or "import { client } from" in content, \
        "navigation doesn't import client"
    assert 'client.discourse.getLinkage' in content, \
        "navigation doesn't use client.discourse.getLinkage"
    
    print("✓ navigation migrated correctly")


def test_profile_migrated():
    """
    Test 5: profile.tsx migrated to oRPC client
    
    Negative: No fetch to /api/discourse/linkage
    Positive: Imports client, uses client.discourse.getLinkage
    """
    print("\n=== Test 5: profile.tsx Migration ===")
    
    file_path = Path("/app/src/pages/profile.tsx")
    assert file_path.exists(), "profile.tsx not found"
    
    content = file_path.read_text()
    
    # Negative test: No fetch to old API
    assert 'fetch("/api/discourse/linkage' not in content, \
        "profile still contains fetch to /api/discourse/linkage"
    assert 'fetch("/api/discourse' not in content, \
        "profile still contains fetch to /api/discourse"
    
    # Positive test: Uses oRPC client
    assert 'import { client } from' in content or "import { client } from" in content, \
        "profile doesn't import client"
    assert 'client.discourse.getLinkage' in content, \
        "profile doesn't use client.discourse.getLinkage"
    
    print("✓ profile migrated correctly")


def test_old_api_route_deleted():
    """
    Test 5: Old oRPC API route file deleted
    
    The old [[...orpc]].ts file should be removed as part of migration.
    Note: The discourse/ directory may still exist with other files (e.g., posts.ts)
    but the specific oRPC wrapper file should be gone.
    """
    print("\n=== Test 5: Old oRPC API Route File Deleted ===")
    
    old_orpc_file = Path("/app/src/pages/api/discourse/[[...orpc]].ts")
    
    assert not old_orpc_file.exists(), \
        f"Old oRPC route file still exists at {old_orpc_file}"
    
    print("✓ Old [[...orpc]].ts file successfully removed")


if __name__ == "__main__":
    try:
        # Run tests in order
        test_connect_discourse_migrated()
        test_publish_button_migrated()
        test_navigation_migrated()
        test_profile_migrated()
        test_old_api_route_deleted()
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED")
        print("="*50)
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)