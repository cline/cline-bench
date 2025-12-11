# Axios Error Handling in React Query

A Norwegian developer (@klogt-as) building an HTTP interception library hit a subtle bug. Their axios adapter worked perfectly for direct axios calls - intercept a request, return an error, axios throws the error as expected. But wrap the same code in React Query's async context and everything broke. React Query expected thrown errors but got normal responses. The error handling chain silently failed.

The user debugged this over several hours, adding three new tests that exposed the problem: `intercept.reject()` with 404 status wasn't throwing AxiosError objects, just returning error responses. In React Query's promise-based queries, errors must be thrown to trigger error boundaries and retry logic. Without proper error throwing, the library appeared to work but silently broke integrations.

The fix required understanding axios's validateStatus mechanism - checking if status codes fall outside the 2xx range and explicitly throwing AxiosError for those cases. The user added validateStatus logic to the axios adapter, wrote comprehensive tests covering React Query contexts and various status codes (400, 401, 500), and verified error message extraction worked correctly. The fix was surgical but the testing was thorough - 135 lines of new tests ensuring the bug wouldn't resurface.

This environment uses the user's own test suite as verification. The broken state has 15 tests in adapters.test.ts. The fixed state has 18 (three new ones for this bug). Our test just runs `vitest` and checks all 50 tests pass. No need to rewrite verification when the user already did it. Agents must understand the async error handling issue, implement validateStatus logic correctly, and ensure the repository's tests pass. That's the whistle blowing - real tests from real development.

---

## Technical Details

**The bug:** axios adapter returns error responses instead of throwing AxiosError objects

**The fix location:** `src/adapters/axios.ts` - Add validateStatus logic around line 285-287

**What needs to happen:**
```typescript
// Check if status is non-2xx
if (status < 200 || status >= 300) {
  // Throw AxiosError with custom message extraction
  throw makeAxiosError(...)
}
// Return normal response for 2xx
return axiosResponse
```

**User's new tests (in fixed commit):**
- Verify reject() with 404 throws AxiosError (not returns response)
- Verify reject() works in React Query context with custom error messages
- Verify reject() with various codes (400, 401, 500) throws correctly

**Verification:**
- Test 1: Build succeeds (TypeScript compiles, dist files generated)
- Test 2: Agent touched test file (added tests)
- Test 3: Agent's tests pass on agent's code
- Test 4: User's ground truth tests pass (fetched from fixed commit)
- Test 5: Agent's tests fail on broken state (meta-test - tests actually detect bug)

**Repository:** [klogt-as/intercept](https://github.com/klogt-as/intercept)
**Broken:** 2fe4969 (before fix)
**Fixed:** 052106281 (after fix with new tests)

**Why it's excellent:**
Tests real-world async error handling patterns, uses actual repository tests as verification (no artificial checks), requires understanding both axios internals and React Query behavior, bug is subtle but impactful.

**Agent results:**
- Oracle: 100% (5/5 tests, reference solution works)
- Terminus: 100% (5/5 tests, FIRST TERMINUS SUCCESS!)
- 41 episodes, 7 minutes, correctly implemented validateStatus

**Build time:** ~2 minutes (pnpm install + vitest + build)
