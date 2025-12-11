# Migrating to Promise-Based Runtime APIs

@elliotBraem just finished implementing a cleaner, simpler API for their plugin framework. The new approach replaced Effect-based dependency injection with straightforward async/await. Documentation was updated. The API was ready.

But the codebase still used the old patterns everywhere. Three test files (600+ lines) imported from `@effect/vitest`, wrapped everything in `Effect.gen(function* ...)`, and piped through `Effect.provide(runtime)`. The main application destructured `PluginService` and threaded it through yields. The user asked Cline to migrate everything systematically.

The work seemed straightforward - apply transformation patterns to move from old API to new. But after making changes, the user hit test errors. Then type errors in the core package. The reality of API migration isn't just syntax changes - it's debugging until everything compiles and works. The user had to iterate: transform the requested files, try to build, hit compilation errors from deeper in the codebase, fix those too. Eventually everything worked.

This environment teaches that complete skill. Agents must apply the transformation patterns correctly (7 structural tests verify this) AND debug until the code compiles (1 behavioral test catches this). Terminus got stuck in exploration. Cline transformed the requested files but left compilation broken. Only agents that iterate to working state - like the real user had to - succeed. That's realistic software engineering, not pattern-matching exercises.

---

## Technical Details

**Files to migrate:**
- `plugins/telegram-source/src/__tests__/unit/message-logic.test.ts` (257 lines)
- `plugins/telegram-source/src/__tests__/integration/polling-integration.test.ts` (130 lines)
- `plugins/telegram-source/src/__tests__/integration/webhook-integration.test.ts` (245 lines)
- `examples/efizzybusybot/main.ts` (main application)
- `plugins/telegram-source/package.json` (remove @effect/vitest)

**Transformation patterns:**
- Imports: `@effect/vitest` → `vitest`
- Test syntax: `it.effect()` → `it()` with async
- Async: `Effect.gen/yield*` → `async/await`
- Streams: `Stream.pipe()` → `for-await` loops
- Runtime: `PluginService` injection → `runtime.usePlugin()` directly
- Timeouts: `Effect.timeout("10s")` → `{ timeout: 10000 }`

**Validation:**
- 7 structural tests (verify patterns applied)
- 1 compilation test (verify it works)
- Oracle: 100% (8/8 tests)
- Terminus: 0% (exploration only, never executed)
- Cline: 75-88% (transforms correctly, compilation struggles)

**Why it's hard:**
Starting code has pre-existing type errors in `packages/core/`. User's quote: "Ok nevermind. Only thing we still have to do is fix these test errors." Agents must debug beyond the requested changes to reach working state. Tests intentional failing compilation - realistic requirement, not just pattern-checking.

**Build time:** ~11 minutes (Docker setup + solution + tests)
