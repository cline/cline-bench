# PyTorch Periodic Boundary Conditions: The Epsilon Tolerance Bug

A computational materials scientist spent months implementing a PyTorch version of their neural network atomic force predictor, aiming for 100% compatibility with their trusted Fortran code. When they tested on titanium dioxide clusters - isolated atoms in empty space - everything worked perfectly. Forces matched to five decimal places. Then they tested periodic structures - atoms in a crystal lattice with periodic boundary conditions. The forces were completely wrong: off by 3.5 eV/Å, enough to make molecular dynamics simulations explode.

They checked everything. Model weights: ✓ exported correctly. File loading: ✓ working. API calls: ✓ look right. Fortran and PyTorch used the exact same model. The cluster worked. The periodic structure failed. After 35.5 hours of investigation, they found it: floating-point precision errors at cutoff boundaries. When enumerating neighbors in periodic structures, coordinate transformations and distance calculations introduce tiny rounding errors. Atoms at exactly the 6.0 Å cutoff boundary become 5.99999999 or 6.00000001 Å. The PyTorch code used strict `<` comparison and missed those boundary neighbors entirely. No neighbors meant no forces - catastrophically wrong predictions. The Fortran code had built-in epsilon tolerance and worked fine. The fix? Add `_radius_with_inclusive()` method that returns `cutoff + epsilon` (1e-6 for float64). One method, eight lines of code, 35.5 hours to diagnose.

This environment recreates that debugging journey. When we tested Terminus (Claude Sonnet 4), it spent 53 episodes over 8 minutes creating debug infrastructure, exploring APIs, and fixing `predictor.py` - changing how cell/PBC parameters get passed. The agent never touched `neighborlist.py` where the actual bug lived. It validated the wrong fix and declared victory. That's the challenge: misleading symptoms ("forces are wrong") suggest loading or API problems, but the real issue is numerical precision mathematics. Only agents with deep understanding of periodic boundary conditions, floating-point error accumulation, and scientific computing best practices succeed. This is real computational science debugging, captured in a reproducible environment.

---

## Technical Details

**Repository:** [atomisticnet/aenet-python](https://github.com/atomisticnet/aenet-python)  
**Broken:** commit `ab777f94` (Oct 30, 2025 04:04 UTC)  
**Fixed:** commit `8ceabcc3` (Nov 2, 2025 16:27 UTC)  
**Timeline:** 35.5 hours from task start to fix

### The Bug

**Symptom:**
- Cluster structures: PyTorch matches Fortran forces perfectly
  - Both predict: (0.61093, 0.42372, -0.86518) eV/Å
- Periodic structures: PyTorch forces completely wrong
  - Fortran: (0.61093, 0.42372, -0.86518) eV/Å ✓
  - PyTorch: (-2.00440, 2.27056, -0.89533) eV/Å ✗ (~3.5 eV/Å error)

**Root Cause:**
Floating-point errors accumulate during:
1. Periodic unit cell replication
2. Coordinate transformations (fractional ↔ Cartesian)  
3. Distance computation in torch_cluster

Atoms at exactly the cutoff distance (6.0 Å) are incorrectly excluded from neighbor lists due to strict `<` comparison without epsilon tolerance.

### The Fix

**File:** `src/aenet/torch_featurize/neighborlist.py`

**Change:** Added `_radius_with_inclusive()` method to TorchNeighborList class:
```python
def _radius_with_inclusive(self) -> float:
    """Return radius slightly larger than cutoff to include boundary atoms.
    
    Uses conservative epsilon to account for accumulated FP error from
    replication, transforms, and torch_cluster distance computation.
    """
    epsilon = 1e-6 if self.dtype == torch.float64 else 1e-5
    return self.cutoff + epsilon
```

This epsilon tolerance ensures atoms at exactly the cutoff boundary are included in neighbor lists, matching Fortran's `<=` behavior and preventing force calculation errors.

### Difficulty Analysis

**Complexity:** HIGH

**Why It's Hard:**
- **Misleading symptoms:** "Wrong forces" suggests loading/API issues, not numerical precision
- **Domain expertise required:** Understanding PBC neighbor enumeration, floating-point boundaries
- **Subtle manifestation:** Bug only appears with periodic structures, not clusters
- **Cross-framework validation:** Requires comparing PyTorch and Fortran implementations
- **Diagnostic sophistication:** Need controlled experiments to isolate PBC as the variable

**Key Skills Tested:**
- Systematic scientific debugging methodology
- Numerical precision in computational geometry
- Periodic boundary condition implementation
- Epsilon tolerance design (dtype-specific values)
- Root cause analysis vs symptom fixing

### Agent Performance

**Oracle (reference solution):** 1.0 accuracy (4/4 tests, 23-27s)  
**Terminus-2 (Claude Sonnet 4):** 0.0 accuracy (53 episodes, 8 minutes)
- Created debug infrastructure (30+ episodes)
- Explored API and notebooks (20+ episodes)  
- Fixed `predictor.py` instead of `neighborlist.py` (wrong diagnosis)
- Validated wrong fix with custom tests
- Never discovered epsilon tolerance requirement

### Verification

**Outcome-based tests** (verify results, not implementation):

1. **Module import** - `TorchNeighborList` can be loaded
2. **Repository tests** - Existing `test_nblist.py` passes  
3. **PBC neighbor enumeration** - Atoms at cutoff boundary are found

Tests verify **outcomes** (correct neighbor finding at boundaries) not **implementation details** (specific epsilon values or method names). Agent can implement any solution that makes neighbors findable at cutoff boundaries.

### Build Environment

**Docker:** Ubuntu 24.04 + Miniforge3  
**Conda env:** aenet-torch (Python 3.11)  
**Dependencies:**
- PyTorch 2.1.0 with CPU backend
- torch-scatter 2.1.2 (compiled from source, ~10min)
- torch-cluster 1.6.3 (compiled from source, ~10min)
- scipy >=1.9.0,<2.0 (pyproject.toml typo fixed)

**Build time:** ~15 minutes total (compilation dominates)

### Learning Value

This environment teaches agents:

1. **Numerical precision awareness** - Floating-point errors at boundaries
2. **Scientific debugging** - Controlled experiments (cluster vs periodic)
3. **Domain expertise** - PBC implementation, neighbor enumeration
4. **Root cause analysis** - Distinguishing symptoms from causes
5. **Cross-framework validation** - Comparing PyTorch/Fortran behavior
6. **Epsilon tolerance design** - Dtype-specific precision handling

Perfect for training on authentic computational science challenges where misleading symptoms require deep technical expertise to diagnose correctly.