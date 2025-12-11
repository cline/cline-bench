# Migrating to Type-Safe oRPC Client

@jlwaugh was working on a NEAR governance application and needed to migrate from plain fetch() calls to a type-safe oRPC client. Their codebase had four React components making untyped HTTP requests to `/api/discourse/*` endpoints - string URLs, manual JSON parsing, no compile-time safety. They wanted to set up oRPC infrastructure and migrate everything to typed client calls.

The task spans both architecture and implementation. First, create the oRPC plumbing: context types, procedure definitions, a router wrapping the Discourse plugin, an API handler, and a client setup. Then systematically migrate ConnectDiscourse, PublishButton, navigation, and profile - replacing fetch() with typed `client.discourse.*` method calls. Each transformation is simple, but getting all the pieces working together requires understanding Next.js API routes, oRPC's type system, and plugin runtime integration.

The user completed this in a real Cline session on October 21, 2025, delivering PR #1 with 15 files changed. The migration introduced compile-time type safety where there was none before - misspell an endpoint and TypeScript catches it, pass wrong parameters and the compiler fails. This environment tests whether agents can build full-stack TypeScript infrastructure from requirements and ensure type correctness throughout. Terminus managed partial component migration but never completed. Cline created all infrastructure and migrated all components but had type errors in the router setup. Only agents that verify compilation after migration succeed. That's realistic TypeScript development - patterns plus type safety.

---

## Technical Details

**Infrastructure to create:**
- `src/lib/context.ts` - oRPC context interface
- `src/lib/procedures.ts` - Public/protected procedures with auth
- `src/lib/router.ts` - Router wrapping Discourse plugin (remote Module Federation)
- `src/pages/api/rpc/[[...rest]].ts` - Next.js API route handler
- `src/lib/orpc.ts` - Client setup with RPCLink

**Components to migrate:**
- `src/components/ConnectDiscourse.tsx` - Auth flow (getUserApiAuthUrl)
- `src/components/PublishButton.tsx` - Post creation (createPost)
- `src/components/navigation.tsx` - Linkage display (getLinkage)
- `src/pages/profile.tsx` - Linkage display (getLinkage)

**Cleanup:** Delete `src/pages/api/discourse/[[...orpc]].ts`

**Transformation example:**
```typescript
// Before - untyped fetch
const res = await fetch("/api/discourse/linkage/get", {
  method: "POST",
  body: JSON.stringify({ nearAccount })
})
const data = await res.json()

// After - type-safe oRPC
import { client } from '@/lib/orpc'
const data = await client.discourse.getLinkage({ nearAccount })
```

**Verification:**
- 5 structural tests (verify migration patterns)
- 1 TypeScript type check (`tsc --noEmit`)

**Repository:** [NEAR-DevHub/neardevhub-bos-web](https://github.com/NEAR-DevHub/neardevhub-bos-web)
**Broken:** fd3ea2506aa (Oct 20, 2025)
**Fixed:** PR #1 merge 1663f4e4 (Oct 21, 2025)

**Agent results:**
- Oracle: 100% (reference solution works)
- Terminus: 0% (partial migration, never finished)
- Cline: 83% (all migrations done, type errors remain)

**Build time:** ~3 minutes
