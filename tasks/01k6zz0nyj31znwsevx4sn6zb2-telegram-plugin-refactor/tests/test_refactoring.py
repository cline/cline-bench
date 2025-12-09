"""
Test suite for Telegram plugin refactoring to contract/service/index pattern.

Tests verify the plugin follows the template architecture:
- contract.ts: API contract definition using orpc router
- service.ts: Business logic in TelegramService class
- index.ts: Plugin orchestration using createPlugin
"""
import os
import re
import subprocess


def test_required_files_exist():
    """Test 1: Verify the three required files exist in the refactored structure."""
    telegram_src = "/app/plugins/telegram/src"
    
    contract_path = os.path.join(telegram_src, "contract.ts")
    service_path = os.path.join(telegram_src, "service.ts")
    index_path = os.path.join(telegram_src, "index.ts")
    
    assert os.path.exists(contract_path), f"contract.ts not found at {contract_path}"
    assert os.path.exists(service_path), f"service.ts not found at {service_path}"
    assert os.path.exists(index_path), f"index.ts not found at {index_path}"
    
    print("✓ All required files exist: contract.ts, service.ts, index.ts")


def test_contract_exports_orpc_router():
    """Test 2: Verify contract.ts exports an orpc router with the required routes."""
    contract_path = "/app/plugins/telegram/src/contract.ts"
    
    with open(contract_path, 'r') as f:
        content = f.read()
    
    # Check for orpc router export
    assert 'export const contract' in content or 'export default' in content, \
        "contract.ts must export a contract"
    
    assert 'oc.router' in content or 'orpc' in content, \
        "contract.ts must use orpc router"
    
    # Check for required routes
    assert 'webhook' in content, "contract must define webhook route"
    assert 'listen' in content, "contract must define listen route"
    assert 'sendMessage' in content, "contract must define sendMessage route"
    
    print("✓ contract.ts exports orpc router with required routes")


def test_service_exports_class():
    """Test 3: Verify service.ts exports a TelegramService class with business logic."""
    service_path = "/app/plugins/telegram/src/service.ts"
    
    with open(service_path, 'r') as f:
        content = f.read()
    
    # Check for class export
    assert 'export class TelegramService' in content or 'class TelegramService' in content, \
        "service.ts must export TelegramService class"
    
    # Check for key methods (sample - not exhaustive)
    assert 'createBot' in content or 'bot' in content.lower(), \
        "service.ts should contain bot creation logic"
    
    assert 'createQueue' in content or 'queue' in content.lower(), \
        "service.ts should contain queue management logic"
    
    # Check for Effect usage (service should use Effect for operations)
    assert 'Effect' in content, \
        "service.ts should use Effect for operations"
    
    print("✓ service.ts exports TelegramService class with business logic")


def test_index_imports_contract_and_service():
    """Test 4: Verify index.ts imports both contract and service."""
    index_path = "/app/plugins/telegram/src/index.ts"
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Check imports
    assert re.search(r'from\s+["\']\.\/contract["\']', content), \
        "index.ts must import from ./contract"
    
    assert re.search(r'from\s+["\']\.\/service["\']', content), \
        "index.ts must import from ./service"
    
    assert 'TelegramService' in content, \
        "index.ts must import TelegramService"
    
    print("✓ index.ts imports contract and service")


def test_index_uses_createPlugin():
    """Test 5: Verify index.ts uses createPlugin pattern."""
    index_path = "/app/plugins/telegram/src/index.ts"
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Check for createPlugin usage
    assert 'createPlugin' in content, \
        "index.ts must use createPlugin"
    
    assert 'contract' in content, \
        "index.ts must reference the contract"
    
    # Check for initialize/shutdown/createRouter pattern
    assert 'initialize' in content, \
        "index.ts must have initialize function"
    
    assert 'createRouter' in content, \
        "index.ts must have createRouter function"
    
    print("✓ index.ts uses createPlugin with proper structure")


def test_business_logic_extracted_to_service():
    """Test 6: Verify business logic was extracted from index.ts to service (not inline)."""
    index_path = "/app/plugins/telegram/src/index.ts"
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # These patterns should NOT be in index.ts (should be in service.ts)
    # Their presence indicates business logic wasn't extracted
    forbidden_patterns = [
        ('new Telegraf(', 'Bot creation should be in service.ts'),
        ('Queue.bounded', 'Queue creation should be in service.ts'),
        ('bot.use(', 'Middleware setup should be in service.ts'),
        ('bot.telegram.getUpdates', 'Polling logic should be in service.ts'),
        ('bot.telegram.setWebhook', 'Webhook setup should be in service.ts'),
    ]
    
    for pattern, reason in forbidden_patterns:
        assert pattern not in content, \
            f"Business logic not extracted: {reason} (found '{pattern}' inline in index.ts)"
    
    # Verify service is part of the architecture (used in context flow)
    assert 'service' in content, \
        "Service must be part of the plugin architecture"
    
    # Verify service is returned from initialize
    assert re.search(r'return\s*\{[^}]*service[^}]*\}', content), \
        "Service must be returned in initialize's context object"
    
    print("✓ Business logic extracted to service, index.ts is clean orchestration layer")


def test_project_compiles():
    """Test 7: Verify the refactored project compiles successfully with TypeScript."""
    print("Running TypeScript compilation...")
    
    result = subprocess.run(
        ["bun", "run", "build"],
        cwd="/app",
        capture_output=True,
        text=True,
        timeout=120
    )
    
    # Check if build succeeded
    assert result.returncode == 0, \
        f"TypeScript compilation failed:\n{result.stderr}\n{result.stdout}"
    
    print("✓ Project compiles successfully")
    print(f"Build output: {result.stdout[:200]}")


def test_readme_updated():
    """Test 8: Verify README.md was updated (user explicitly requested README update)."""
    readme_path = "/app/plugins/telegram/README.md"
    
    # File must exist
    assert os.path.exists(readme_path), \
        "README.md file not found - user requested it be updated"
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Must be updated (was empty in broken state - 0 lines)
    # Any content means it was updated
    assert len(content.strip()) > 0, \
        "README.md is still empty - user explicitly requested it be updated"
    
    print("✓ README.md was updated")


if __name__ == "__main__":
    # Run tests manually for debugging
    test_required_files_exist()
    test_contract_exports_orpc_router()
    test_service_exports_class()
    test_index_imports_contract_and_service()
    test_index_uses_createPlugin()
    test_business_logic_extracted_to_service()
    test_project_compiles()
    test_readme_updated()
    print("\n✅ All tests passed!")