# Police Neighbourhood Sync - Segmentation Fault

@AndreasThinks's web scraper for UK police neighbourhood events kept crashing with a segmentation fault. Always at the same place - Manchester neighbourhood MC28. The error trace pointed to Python's `concurrent.futures` threading module. Request succeeded (HTTP 200 OK), then crash. Thread worker segfault. The stack trace screamed "concurrency issue!"

So agents do what seems obvious: add threading locks. Synchronize database access. Protect shared state. Claude 4.5 did this and got it wrong. The bug isn't concurrency - it's data. The Police UK API returned coordinates **missing the 'longitude' key**. When the code tries `coord['longitude']`, Python raises KeyError. In a thread worker, unhandled exceptions cause segmentation faults instead of normal exceptions. The fix? Seven lines of try-except wrapping coordinate access, logging the error, and moving on. No locks needed.

But here's why this environment matters: agents consistently misdiagnose. The error trace is misleading - threading module, concurrent workers, segfault. It **looks** like a concurrency problem. Reference solution is simpler (try-except) and faster (no lock overhead) than the locks approach. Our test suite catches this. We test malformed data handling in concurrent context, measure performance against reference, and verify robustness to geometric edge cases. Agents that add unnecessary threading locks fail the performance test. Agents that miss the KeyError fail the malformed data test. Agents that skip geometry validation fail the robustness test. Only clean, targeted solutions - addressing the actual data problem without over-engineering - pass all five tests. This teaches the critical skill: solve the right problem, not the obvious one.

---

## Technical Details

**The bug:** Police UK API returned `[{'latitude': '53.5'}]` (missing `'longitude'` key)

**The crash:**
```python
coords_str = ", ".join([
    f"{coord['longitude']} {coord['latitude']}"  # ← KeyError!
    for coord in boundary_coords
])
# In concurrent.futures thread → unhandled exception → segfault
```

**The fix (reference solution):**
```python
try:
    coords_str = ", ".join([
        f"{coord['longitude']} {coord['latitude']}"
        for coord in boundary_coords
    ])
except (KeyError, TypeError) as e:
    logger.error(f"Invalid coordinate format: {e}")
    return  # Skip this neighbourhood, continue sync
```

Plus: ST_IsValid geometry validation, ST_MakeValid repair, graceful error handling. Total: 90 lines across 2 files.

**Wrong approach (what agents try):**
```python
import threading
_duckdb_lock = threading.RLock()

def insert_neighbourhood(...):
    with _duckdb_lock:  # ← Serializes all DB operations
        coords_str = ", ".join([
            f"{coord['longitude']}"  # ← KeyError STILL happens!
        ])
```

Locks don't prevent KeyError on malformed data. They just mask symptoms with performance cost.

**Verification (5 tests):**

1. **Malformed Data Test**: Passes coordinates with missing 'longitude' key
   - Broken: KeyError → crash
   - Fixed: Handled gracefully

2. **Concurrent Stress Test**: Same malformed data in ThreadPoolExecutor
   - Tests production scenario where crash actually happened
   - Ensures fix works in threading context

3. **Performance Test**: Compares concurrent operation speed vs reference
   - Detects unnecessary threading locks (>3x slowdown = fail)
   - Reference: 0.10s | With locks: 0.6-1.0s | Clean fix: 0.08-0.12s

4. **Invalid Geometry Test**: Self-intersecting, degenerate, duplicate points
   - Tests robustness beyond just KeyError
   - Ensures agents don't skip geometry validation for speed

5. **Ground Truth Test**: Runs actual tests from fixed commit
   - Prevents gaming
   - Validates "ensure everything works"

**Repository:** [AndreasThinks/your-police-events](https://github.com/AndreasThinks/your-police-events)
**Broken:** commit `bdaff376` (Oct 3, 2025)
**Fixed:** commit `b39c3fea` (Oct 3, 2025, 55 minutes later)

**Build environment:**
- Python 3.11 + uv package manager
- FastAPI + DuckDB with spatial extension
- pytest for testing
- Standard container (no special hardware)

**Why it's hard:**

The error trace is **intentionally misleading**. It shows threading module, concurrent.futures, thread workers. Agents naturally diagnose concurrency issues and add locks. This is the wrong mental model. The actual bug is simple data validation - missing dictionary keys. Success requires:

1. Reading past misleading symptoms
2. Understanding thread exception → segfault conversion
3. Diagnosing root cause (data, not concurrency)
4. Implementing targeted fix (try-except, not locks)
5. Handling edge cases (invalid geometry, not just missing keys)

**Agent results:**
- Oracle: 100% (reference solution: try-except + geometry validation)
- Terminus: 0% (added SyncLock mechanism, didn't handle malformed data)
- Cline Run #1: 100% (threading locks + validation - passed performance test with surgical lock scope)
- Cline Run #2: 100% (validation only, no locks - clean solution)
- Cline Run #6: 0% (geometry validation only, missed KeyError - tests caught it!)

**Test philosophy validated:**

The 5-test suite successfully:
- ✅ Tests outcomes (handles malformed data) not implementation (must use try-except)
- ✅ Catches suboptimal approaches (broad threading locks would fail performance)
- ✅ Allows implementation flexibility (validation, error handling, preprocessing all work)
- ✅ Validates production scenarios (concurrent context where crash happened)
- ✅ Ensures robustness (invalid geometry beyond just missing keys)

This is the balance: test what the user wanted (stop crashing, handle bad data) while allowing agents to solve it their way, but still catching solutions that add unnecessary complexity or miss edge cases.

**Build time:** ~30 seconds (lightweight Python app, no complex dependencies)
