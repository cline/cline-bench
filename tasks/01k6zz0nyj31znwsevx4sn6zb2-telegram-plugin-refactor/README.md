# Telegram Plugin Architectural Refactoring

@elliotBraem was building a plugin system for the NEAR ecosystem. They had a working telegram plugin, but all 367 lines of business logic lived in a single `index.ts` file - bot initialization, error handling, webhook setup, polling logic, stream processing, message sending, everything tangled together. The project had a template showing the clean pattern: separate contract definition from business logic, business logic from orchestration. Three files doing three jobs. The user's request was direct: "I want to restructure 'plugins/telegram/src' so it follows this same, index contract service flow."

This is architectural refactoring at its core. Not changing what the code does, but how it's organized. Not fixing bugs, but enforcing patterns for maintainability. The user spent an hour with the AI iterating through the transformation - 93 messages of back-and-forth. The work required understanding the template pattern, identifying which code belonged where, extracting 10 discrete methods into a TelegramService class, creating a proper contract with orpc router definitions, and refactoring the orchestration layer to use them. Two minutes after the task completed, they committed the result to GitHub.

---

## Technical Details

**The Request:** "Restructure plugins/telegram/src to follow the template's index/contract/service flow"

**What This Means:**
- Extract business logic from index.ts into TelegramService class
- Move contract definitions from schemas/index.ts to contract.ts
- Refactor index.ts to orchestration layer (create service, implement contract, wire together)
- Follow exact pattern shown in plugins/_template/src

**The Transformation:**
- **Broken state:** Single file (367 lines) with everything inline in createPlugin
- **Fixed state:** Three files with clean separation:
  - `contract.ts`: API definition using orpc router (webhook/listen/sendMessage routes)
  - `service.ts`: TelegramService class with 10 business logic methods
  - `index.ts`: Orchestration using createPlugin, instantiates service, implements contract

**Verification (7 tests):**
1. Required files exist (contract.ts, service.ts, index.ts)
2. Contract exports orpc router with required routes
3. Service exports TelegramService class with business logic
4. Index imports both contract and service (architectural separation)
5. Index uses createPlugin pattern (regression test)
6. Service instantiated in initialize (pattern correctly applied)
7. Project compiles with TypeScript (behavioral verification)

**Test Design Philosophy:**
Tests 1-4, 6 verify the architectural pattern the user explicitly requested. Test 5 ensures no regressions (plugin still works). Test 7 ensures code compiles. Structural tests justified here because user requested specific architectural structure, not just "make it better." This is about enforcing patterns, not solving ambiguous problems.

**Repository:** [near-everything/every-plugin](https://github.com/near-everything/every-plugin)  
**Broken:** commit `fa16847` (Oct 7, 2025, 1:30 PM)  
**Fixed:** commit `0f98ec19d1` (Oct 7, 2025, 7:33 PM - 2 minutes after task completion)

**Build Environment:**
- Ubuntu 24.04 with Node.js 20 and Bun
- Monorepo with turbo build system
- Standard TypeScript compilation
- No external services or secrets required

**Why It's Hard:**
The user explicitly showed the pattern - it's right there in the template. But transforming 367 lines of working code into a new architecture without breaking functionality requires:
1. Understanding which code is "contract" vs "service" vs "orchestration"
2. Extracting methods while preserving scope and dependencies
3. Threading context through the new structure (bot, queue, config)
4. Updating all the call sites to use the new pattern
5. Ensuring nothing breaks in the process

Terminus understood the pattern but couldn't execute the systematic extraction. The gap between "I see what good looks like" and "I can transform this code into that pattern" is where current agents struggle.

**Agent Results:**
- Oracle: 100% (7/7 tests, 0.40s execution, reference solution perfect)
- Terminus: 0% (5/7 tests failed - examined pattern thoroughly but never created files)

**Task Duration:** ~1 hour (original user session: 6:30 PM - 7:31 PM with 93 messages)

**Build Time:** ~3-4 minutes total (Docker build 10min first time, solution 2s, tests 0.4s)