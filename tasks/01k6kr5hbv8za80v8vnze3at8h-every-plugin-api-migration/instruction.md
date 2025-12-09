# Current Work: Migration to New every-plugin Runtime API

## What Was Being Worked On

The user requested updates to migrate the telegram plugin tests and efizzybusybot example to use the new simpler runtime API that was recently documented.

### Previous Context: Documentation Updates (Completed)
Earlier in the conversation, I successfully integrated new DevEx features into the every-plugin documentation:

1. **Added `EveryPlugin.Infer` type helper** to `apps/docs/content/docs/runtime/index.mdx` and `apps/docs/content/docs/runtime/patterns.mdx`
2. **Added `createLocalPluginRuntime` documentation** showing local plugin development patterns
3. **Completely rewrote** `apps/docs/content/docs/testing/index.mdx` to use `createLocalPluginRuntime` instead of deprecated `createTestPluginRuntime`
4. **Updated** `apps/docs/content/docs/index.mdx` with new "Plugins Can Be Sophisticated" section
5. **Verified** no mentions of `createTestPluginRuntime` remain in docs

### Current Focus: Code Migration

User's exact request: "I need to update the telegram plugin. Look here: 'plugins/telegram-source/src/index.ts' and all of its tests need to use the new simpler runtime interface and simple vitest (no effect/vitest)"

Then expanded to: "And then also, what are list of changes to 'examples/efizzybusybot/main.ts' and all of it's services?"

## Key Technical Concepts

### New Runtime API Pattern

**OLD (Effect-based):**
```typescript
const { runtime, PluginService } = createPluginRuntime<Bindings>({...});

const program = Effect.gen(function* () {
  const pluginService = yield* PluginService;
  const { client } = yield* pluginService.usePlugin("plugin-id", config);
  // use client
});

await Effect.runPromise(program.pipe(Effect.provide(runtime)));
```

**NEW (Simple async/await):**
```typescript
const runtime = createPluginRuntime<Bindings>({...});

const { client } = await runtime.usePlugin("plugin-id", config);
// use client directly
```

### Test Pattern Changes

**OLD (@effect/vitest):**
```typescript
import { expect, it } from "@effect/vitest";

it.effect("test name", () =>
  Effect.gen(function* () {
    const pluginService = yield* PluginService;
    const { client } = yield* pluginService.usePlugin(...);
    // test logic with yield*
  }).pipe(Effect.provide(runtime), Effect.timeout("10 seconds"))
);
```

**NEW (simple vitest):**
```typescript
import { expect, it } from "vitest";

it("test name", async () => {
  const { client } = await runtime.usePlugin(...);
  // test logic with await
}, { timeout: 10000 });
```

### Stream Processing Changes

**OLD (Effect.Stream):**
```typescript
const stream = Stream.fromAsyncIterable(streamResult, error => error);
const collected = yield* stream.pipe(Stream.take(3), Stream.runCollect);
```

**NEW (for-await loops):**
```typescript
const collected = [];
let count = 0;
for await (const item of streamResult) {
  collected.push(item);
  if (++count >= 3) break;
}
```

### Important: Effect Services Stay the Same

The migration ONLY affects how you use the plugin runtime. Effect.Service patterns remain unchanged:
- All services in `examples/efizzybusybot/services/` keep their `Effect.Service` pattern
- Worker functions using `Effect.gen()` with services stay the same
- Only the plugin runtime usage changes

## Relevant Files Examined

### Telegram Plugin
1. **`plugins/telegram-source/src/index.ts`** - Plugin implementation (already uses new API correctly)
2. **`plugins/telegram-source/src/schemas/index.ts`** - Contract definitions
3. **`plugins/telegram-source/src/__tests__/unit/message-logic.test.ts`** (257 lines) - Needs updating
4. **`plugins/telegram-source/src/__tests__/integration/polling-integration.test.ts`** (130 lines) - Needs updating
5. **`plugins/telegram-source/src/__tests__/integration/webhook-integration.test.ts`** (245 lines) - Needs updating
6. **`plugins/telegram-source/package.json`** - Has `@effect/vitest` dependency to remove

### efizzybusybot Example
1. **`examples/efizzybusybot/main.ts`** - Main entry point using Effect-based runtime (needs updating)
2. **`examples/efizzybusybot/worker.ts`** - Worker functions (NO changes needed - uses Effect services correctly)
3. **`examples/efizzybusybot/services/*.ts`** - All 7 service files (NO changes needed - Effect.Service pattern is correct)

## Pending Tasks and Next Steps

User's exact instruction: "Let's make these changes! Write and maintain a full TODO list, and then let's knock it out. Please give me any uninstall command, or any changes like that. You do the rest."

### Complete TODO List

**Phase 1: Telegram Plugin Tests**
- [ ] Remove `@effect/vitest` from `plugins/telegram-source/package.json` (command: `cd plugins/telegram-source && bun remove @effect/vitest`)
- [ ] Update `plugins/telegram-source/src/__tests__/unit/message-logic.test.ts`:
  - Replace `import { expect, it } from "@effect/vitest"` with `import { expect, it } from "vitest"`
  - Change all `it.effect()` to `it()` with async
  - Replace `Effect.gen(function* () {...})` with `async () => {...}`
  - Replace `yield*` with `await`
  - Replace `yield* PluginService` → `const { client } = await runtime.usePlugin(...)`
  - Replace Effect.Stream usage with for-await loops
  - Replace `.pipe(Effect.provide(runtime), Effect.timeout("10 seconds"))` with `, { timeout: 10000 }`
  
- [ ] Update `plugins/telegram-source/src/__tests__/integration/polling-integration.test.ts` with same pattern
- [ ] Update `plugins/telegram-source/src/__tests__/integration/webhook-integration.test.ts` with same pattern

**Phase 2: efizzybusybot**
- [ ] Update `examples/efizzybusybot/main.ts`:
  - Change `const { runtime, PluginService } = createPluginRuntime(...)` to `const runtime = createPluginRuntime(...)`
  - Replace `Effect.gen()` with `async function` for main program
  - Replace `yield* PluginService; yield* pluginService.usePlugin(...)` with `await runtime.usePlugin(...)`
  - Keep Effect service layer composition unchanged
  - Stream processing can stay with Effect.Stream or convert to for-await

**Phase 3: Verification**
- [ ] Run telegram plugin tests: `cd plugins/telegram-source && bun test`
- [ ] Verify efizzybusybot still works (if environment allows)

### Uninstall Command Provided
```bash
cd plugins/telegram-source && bun remove @effect/vitest
```

### Current Status
User attempted to execute the uninstall command but it was denied. Need to continue with the manual file updates instead, starting with the test files.

### Next Immediate Steps
1. Start with `plugins/telegram-source/src/__tests__/unit/message-logic.test.ts` - rewrite to use simple vitest
2. Then proceed to the two integration test files
3. Finally update `examples/efizzybusybot/main.ts`
4. Manually remove `@effect/vitest` from package.json if needed
