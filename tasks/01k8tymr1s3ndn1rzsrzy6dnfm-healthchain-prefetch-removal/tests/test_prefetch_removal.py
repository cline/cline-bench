"""Tests verifying Prefetch model removal and clean CdsRequest usage."""

import subprocess
from pathlib import Path


def test_prefetch_file_deleted():
    """Prefetch model file should be deleted.
    
    User explicitly requested: "remove the Prefetch model"
    
    This is the ONLY explicit requirement from the user's prompt.
    Everything else (import cleanup, loader refactoring) was the human's
    implementation choice, not a user requirement.
    """
    prefetch_path = Path("/app/healthchain/models/hooks/prefetch.py")
    assert not prefetch_path.exists(), (
        "prefetch.py should be deleted. "
        "User explicitly requested to remove the Prefetch model."
    )


def test_healthchain_works_after_removal():
    """Code should work after Prefetch removal.
    
    OUTCOME test: Ensures removal didn't break the codebase.
    
    We test that core modules can be imported and used.
    This catches:
    - Dead imports (would cause ImportError)
    - Broken dependencies (would crash on import)
    - Module structure issues
    
    But doesn't prescribe HOW cleanup happens - agents can delete imports,
    comment them, refactor modules, whatever works.
    """
    result = subprocess.run(
        [
            "/bin/bash",
            "-c",
            "source /app/.venv/bin/activate && python -c '"
            "# Test core imports work\n"
            "import healthchain.models;\n"
            "import healthchain.models.hooks;\n"
            "import healthchain.models.requests;\n"
            "from healthchain.models.requests import CDSRequest;\n"
            "from healthchain.models.hooks import PatientViewContext;\n"
            "# Test basic usage works\n"
            "data = {\"hook\": \"patient-view\", \"context\": {\"userId\": \"Practitioner/123\", \"patientId\": \"Patient/456\"}};\n"
            "request = CDSRequest(**data);\n"
            "assert request.hook == \"patient-view\";\n"
            "# Test loaders still importable (they existed before, should work after)\n"
            "from healthchain.sandbox.loaders import mimic;\n"
            "from healthchain.sandbox.loaders import synthea;\n"
            "print(\"SUCCESS\")"
            "'",
        ],
        cwd="/app",
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0, (
        f"HealthChain modules failed after Prefetch removal.\n"
        f"Code should still work after cleanup.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )