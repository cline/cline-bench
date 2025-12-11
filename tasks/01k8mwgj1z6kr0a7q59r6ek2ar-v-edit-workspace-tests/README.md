# V-Edit Workspace Test Fixes

@sergev noticed that eight unit tests were failing. Simple problems with clear names: `DeleteLines` had an off-by-one error, `ToplineUpdateAfterEdit` wasn't clamping scroll position, `BuildFromText` couldn't read back segments it just created. The user knew what was broken. They just had to fix it.

Forty-nine hours later, they committed the fix. Not because the bugs were individually complex, but because v-edit's architecture demanded understanding how text editors actually work at the systems level. The workspace manages text through segments - chunks of a file loaded into memory or stored temporarily. When you insert text, you're not just moving bytes around. You're updating segment boundaries, adjusting file offsets, recalculating line counts, and maintaining a chain of segments where the cursor might be pointing anywhere. Delete three lines and suddenly topline needs recalculating. Load text from a vector and the segment chain has a tail node that cursegm_ points to instead of the data. Navigation fails because you're looking at an empty segment.

The fix was 155 lines across four files. Most of it was handling edge cases: what if the workspace is empty when you call `put_line`? What if you're inserting at EOF? What if you delete from the last line and need the fast path? Each test failure revealed another boundary condition in a segment-based buffer no LLM had seen during training. This is systems programming - the kind where you need to understand data structures, not just pattern match on similar code.

When we ran Terminus on this task with a 60-minute timeout, it fixed seven of the eight tests in 18 minutes. It found the cursegm_ bug. It understood scrolling boundaries. It got most of the way there. But `SegmentCatOperations` - a test about merging segments when concatenating - remained broken due to null pointer issues in the segment chain. The agent made 179 attempts, wrote debug programs to trace execution, switched from sed to Python for precise editing. Then it gave up, declaring the problem "too complex." The human took 49 hours. The AI took 18 minutes to get 87.5% of the way, then hit a wall. That gap is exactly what RL training needs to close.

---

## Technical Details

**The bugs:** Eight edge cases in segment-based buffer management
1. DeleteLines - Off-by-one in `delete_segments` line counting
2. ToplineUpdateAfterEdit - Scrolling boundary not clamped after edits  
3. BuildFromText - Temp file segments (created by `load_text`) return empty when read
4. SetCurrentSegmentNavigation - `cursegm_` points to tail segment instead of data
5. BreakSegmentVariations - Breaking segments at specific lines beyond temp data
6. SegmentDeleteOperations - Delete operations miscounting lines
7. ViewManagementComprehensive - Scroll clamping doesn't limit topline properly
8. ComplexEditWorkflow - Insert operations miscount lines in multi-step edits

**The fix requires:**
- Understanding segment-based buffer architecture (text split across memory chunks)
- Handling empty workspace special case in `breaksegm()`
- EOF insertion special case in `insert_contents()`  
- Last-line fast-path in `delete_contents()`
- Empty workspace and append-at-end cases in `put_line()`
- Fixing `cursegm_` initialization in `load_text()` to skip tail segments
- Total: 155 changes (105 adds, 50 dels) across 4 files, 92% directly fixing edge cases

**Verification:**
- Runs GTest suite with `--gtest_filter=WorkspaceTest.*`
- Verifies exit code 0 (all tests pass)
- Checks each of the 8 specific tests shows `[OK]` status
- Outcome-based: doesn't prescribe HOW to fix bugs, only that tests pass
- Ground truth also fixes `SegmentCatOperations` (not in the 8, but improved by same changes)

**Repository:** [sergev/v-edit](https://github.com/sergev/v-edit)  
**Broken:** commit `79390613` (Oct 28, 2025)
**Fixed:** commit `57bba22b` (Oct 30, 2025)
**Timeline:** 49 hours 12 minutes

**Build environment:**
- Ubuntu 24.04 with CMake 3.28+, GTest, ncurses
- C++17 compiler (g++ 13.3.0)
- Build requires patching CMakeLists.txt to disable `-Werror` (Linux has stricter sign-compare warnings than macOS)
- Standard systems programming stack, no exotic dependencies

**Why it's hard:**
This isn't "fix the obvious bug." It's "understand the architecture, then fix eight boundary conditions." Segment-based buffers are rare - most editors use simpler approaches. The cursegm_ bug is subtle: it points to the right location in the list, just not the right *kind* of node (tail vs data segment). Navigation works in common cases, fails at boundaries. These are the bugs that take humans days because you need to understand the whole system, not just pattern match. LLMs trained on typical editor code won't have seen this specific architecture.

**Agent results:**
- Oracle: 100% (reference solution fixes all tests including extras)
- Terminus: 0% (fixed 7/8 explicitly requested tests, broke SegmentCatOperations, gave up)
  - 179 episodes, 18 minutes
  - Found cursegm_ bug, understood scrolling, fixed most edge cases
  - Couldn't fix segment merging null pointer issue
  - Self-reported "architectural changes needed, beyond scope"

**Build time:** ~2 minutes (1min Docker build, <10sec cmake+make, <10sec tests)

**Difficulty rating:** Hard
- Requires systems programming knowledge (C++, data structures, buffer management)
- Multiple interdependent edge cases across different functions
- Agent needs to understand segment chain architecture, not just fix isolated bugs
- Human baseline: 49 hours (vs other qualified tasks like police sync: 55 minutes = 53x longer)