#!/usr/bin/env python3
"""
Tests for Azure Deployment Stacks implementation.

Verifies that all three deployment stack resources have been created:
- azurerm_management_group_deployment_stack
- azurerm_resource_group_deployment_stack  
- azurerm_subscription_deployment_stack

Following Phase 2 guidance: Test OUTCOMES (user's request fulfilled) not 
implementation details (how agent structured the code).
"""

import subprocess
import os
import re


def test_resource_files_exist():
    """
    Test that all 3 resource implementation files exist.
    
    User requested: "create three new (typed!) resources"
    Outcome: 3 resource files must exist in internal/services/resource/
    """
    resource_dir = "/app/internal/services/resource"
    
    required_files = [
        "management_group_deployment_stack_resource.go",
        "resource_group_deployment_stack_resource.go",
        "subscription_deployment_stack_resource.go"
    ]
    
    missing_files = []
    for filename in required_files:
        filepath = os.path.join(resource_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
    
    assert len(missing_files) == 0, \
        f"Missing resource files: {missing_files}. User requested all 3 deployment stack resources."


def test_test_files_exist():
    """
    Test that all 3 test files exist.
    
    User requested: "create three new (typed!) resources and their acceptance tests"
    Outcome: 3 test files must exist in internal/services/resource/
    """
    resource_dir = "/app/internal/services/resource"
    
    required_test_files = [
        "management_group_deployment_stack_resource_test.go",
        "resource_group_deployment_stack_resource_test.go",
        "subscription_deployment_stack_resource_test.go"
    ]
    
    missing_test_files = []
    for filename in required_test_files:
        filepath = os.path.join(resource_dir, filename)
        if not os.path.exists(filepath):
            missing_test_files.append(filename)
    
    assert len(missing_test_files) == 0, \
        f"Missing test files: {missing_test_files}. User requested acceptance tests for all 3 resources."


def test_resources_registered():
    """
    Test that all 3 resources are registered in registration.go.
    
    Resources must be registered in the Resources() method to be available in Terraform.
    Outcome: All 3 resource type names must appear in registration.go
    """
    registration_file = "/app/internal/services/resource/registration.go"
    
    with open(registration_file, 'r') as f:
        content = f.read()
    
    required_resources = [
        "ManagementGroupDeploymentStackResource",
        "ResourceGroupDeploymentStackResource",
        "SubscriptionDeploymentStackResource"
    ]
    
    missing_registrations = []
    for resource_name in required_resources:
        # Look for the resource in the Resources() method
        if resource_name not in content:
            missing_registrations.append(resource_name)
    
    assert len(missing_registrations) == 0, \
        f"Resources not registered: {missing_registrations}. " \
        f"All 3 resources must be registered in registration.go Resources() method."




def test_project_compiles():
    """
    Test that the deployment stack resources compile successfully.

    User requested typed resources following HashiCorp conventions.
    Outcome: Code must compile without errors (Go's type system validates correctness).

    Strategy: Compile only the resource package (not the entire 44K+ file provider)
    to stay within Docker memory constraints while still validating type correctness.
    """
    print("Compiling resource package (this may take 60-120 seconds)...")

    # Create directories for Go build cache
    os.makedirs("/app/.gocache", exist_ok=True)
    os.makedirs("/app/.gotmp", exist_ok=True)

    # Use full path to go binary
    go_binary = "/usr/local/go/bin/go"

    # Compile only the resource package with serial compilation to reduce memory usage
    result = subprocess.run(
        [go_binary, "build", "-p", "1", "-v", "./internal/services/resource/..."],
        cwd="/app",
        capture_output=True,
        text=True,
        timeout=300,
        env={
            **os.environ,
            "GO111MODULE": "on",
            "GOMAXPROCS": "2",  # Limit parallelism to reduce memory pressure
            "GOCACHE": "/app/.gocache",  # Use app directory instead of /tmp to avoid disk space issues
            "GOTMPDIR": "/app/.gotmp"  # Redirect temp files to app directory
        }
    )

    assert result.returncode == 0, \
        f"Resource package failed to compile.\n" \
        f"STDERR (last 100 lines):\n{chr(10).join(result.stderr.split(chr(10))[-100:])}\n" \
        f"Resources must implement correct Go interfaces and compile successfully."


def test_all_sdk_imports_present():
    """
    Test that resources import the correct SDK packages.
    
    User specified: "Using the go-azure-sdk API version 2024-03-01"
    Outcome: Resource files must import from the 2024-03-01 SDK packages.
    """
    resource_dir = "/app/internal/services/resource"
    api_version = "2024-03-01"
    
    resource_files = {
        "management_group_deployment_stack_resource.go": "deploymentstacksatmanagementgroup",
        "resource_group_deployment_stack_resource.go": "deploymentstacksatresourcegroup",
        "subscription_deployment_stack_resource.go": "deploymentstacksatsubscription"
    }
    
    for filename, expected_package in resource_files.items():
        filepath = os.path.join(resource_dir, filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for correct SDK import with API version
        import_pattern = rf"github\.com/hashicorp/go-azure-sdk/resource-manager/resources/{api_version}/{expected_package}"
        
        assert re.search(import_pattern, content), \
            f"{filename} must import SDK package: {import_pattern}"