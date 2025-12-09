"""
Outcome-based tests for aenet PyTorch PBC neighbor list bug.

Tests verify that periodic boundary conditions work correctly for force
calculations without prescribing specific implementation details (e.g., epsilon
values). The bug manifests as incorrect forces for periodic structures due to
floating-point precision errors at cutoff boundaries.
"""

import subprocess
import sys


def test_neighborlist_module_exists():
    """Test that the neighborlist module can be imported."""
    result = subprocess.run(
        [
            "conda", "run", "-n", "aenet-torch", "python", "-c",
            "from aenet.torch_featurize.neighborlist import TorchNeighborList; print('OK')"
        ],
        cwd="/app",
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Failed to import neighborlist: {result.stderr}"
    assert "OK" in result.stdout, f"Import check failed: {result.stdout}"


def test_repository_tests_pass():
    """
    Test that the repository's own test suite passes.

    This is outcome-based verification: the fix should make the repository's
    tests pass. We're not prescribing HOW the fix works (epsilon tolerance,
    etc.), only that the tests pass.
    """
    result = subprocess.run(
        [
            "conda", "run", "-n", "aenet-torch", "pytest",
            "src/aenet/tests/test_nblist.py", "-v"
        ],
        cwd="/app",
        capture_output=True,
        text=True,
        timeout=300
    )

    # Tests should pass after fix
    assert result.returncode == 0, (
        f"Neighbor list tests failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def test_pbc_neighbor_enumeration():
    """
    Test that PBC neighbor enumeration works correctly AT THE CUTOFF BOUNDARY.

    This tests the core functionality that was broken: neighbor list generation
    for periodic structures when atoms are EXACTLY at the cutoff distance.
    The bug caused neighbors at exactly the cutoff to be missed due to 
    floating-point precision issues, leading to incorrect forces.
    
    Without the epsilon tolerance fix, this test will FAIL because atoms
    at exactly 6.0A with a 6.0A cutoff won't be found as neighbors.
    """
    test_code = """
import torch
from aenet.torch_featurize.neighborlist import TorchNeighborList

# CRITICAL TEST: Atoms EXACTLY at cutoff boundary
# This is where the floating-point precision bug occurs
# Cell: 6.0 Angstrom cubic cell
# Atoms at (0,0,0) and (6.0, 0, 0) - distance EXACTLY 6.0A
# Cutoff: 6.0A
# Without epsilon tolerance, these neighbors are MISSED due to FP precision
cell = torch.eye(3) * 6.0
positions = torch.tensor([[0.0, 0.0, 0.0], [6.0, 0.0, 0.0]])
pbc = torch.tensor([True, True, True])

# Create neighbor list with 6.0 Angstrom cutoff (same as cell size)
nblist = TorchNeighborList(cutoff=6.0, dtype=torch.float64, device='cpu')

# Get neighbors with PBC
edge_index, distances, cell_offsets = nblist.get_neighbors_pbc(
    positions=positions,
    cell=cell,
    pbc=pbc,
    fractional=False
)

# CRITICAL ASSERTION: Should find neighbors even at exact cutoff boundary
# Without epsilon fix, this fails with 0 neighbors
assert edge_index.shape[1] > 0, f"No neighbors found - epsilon tolerance missing! PBC neighbor finding at cutoff boundary is broken. edge_index shape: {edge_index.shape}"
assert distances.shape[0] > 0, f"No distances computed - epsilon tolerance missing! distances shape: {distances.shape}"

# The distances should include neighbors at or very close to the cutoff
# With epsilon fix, we find neighbors slightly beyond 6.0A due to 1e-6 tolerance
max_dist = distances.max().item()
assert max_dist >= 5.99, f"Expected to find neighbors at ~6.0A cutoff boundary, but max distance is {max_dist}A"

print(f"PBC neighbor enumeration at cutoff boundary works: found {edge_index.shape[1]} neighbor pairs, max distance {max_dist:.4f}A")
print(f"✓ Epsilon tolerance is working correctly - neighbors at cutoff boundary are found")
"""

    result = subprocess.run(
        ["conda", "run", "-n", "aenet-torch", "python", "-c", test_code],
        cwd="/app",
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"PBC neighbor enumeration failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
    assert "at cutoff boundary works" in result.stdout or "works correctly" in result.stdout


if __name__ == "__main__":
    # Run tests manually if executed directly
    test_neighborlist_module_exists()
    print("✓ Test 1 passed: neighborlist module imports")

    test_repository_tests_pass()
    print("✓ Test 2 passed: repository tests pass")

    test_pbc_neighbor_enumeration()
    print("✓ Test 3 passed: PBC neighbor enumeration works")

    print("\n✓ All tests passed!")