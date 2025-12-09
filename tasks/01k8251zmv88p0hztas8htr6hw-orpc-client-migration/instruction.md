Set up oRPC infrastructure and migrate Next.js components to type-safe oRPC client.

## Infrastructure to Create:

The codebase currently uses plain fetch() calls. You need to set up oRPC infrastructure:

1. **`src/lib/context.ts`** - oRPC context interface with session/user types
2. **`src/lib/procedures.ts`** - Public and protected procedure definitions with auth middleware
3. **`src/lib/router.ts`** - Router wrapping Discourse plugin (use top-level await)
4. **`src/pages/api/rpc/[[...rest]].ts`** - API route handler at `/api/rpc/*`
5. **`src/lib/orpc.ts`** - Client setup with RPCLink for frontend

Discourse plugin remote URL: `https://jlwaugh-14-neargov-discourse-plugin-discourse-plu-cfdfb7fa7-ze.zephyrcloud.app/remoteEntry.js`

## Components to Migrate:

Once infrastructure exists, migrate these 4 components from fetch() to oRPC client:

1. **`src/components/ConnectDiscourse.tsx`** - fetch to `/api/discourse/auth` → `client.discourse.getUserApiAuthUrl()`
2. **`src/components/PublishButton.tsx`** - fetch to `/api/discourse/posts/create` → `client.discourse.createPost()`
3. **`src/components/navigation.tsx`** - fetch to `/api/discourse/linkage` → `client.discourse.getLinkage()`
4. **`src/pages/profile.tsx`** - fetch to `/api/discourse/linkage` → `client.discourse.getLinkage()`

## Cleanup:

Delete old API route: `src/pages/api/discourse/[[...orpc]].ts`

## Example Transformation:

**Before:**
```typescript
const response = await fetch("/api/discourse/linkage/get", {
  method: "POST",
  body: JSON.stringify({ nearAccount: "..." })
})
const data = await response.json()
```

**After:**
```typescript
import { client } from '@/lib/orpc'
const data = await client.discourse.getLinkage({ nearAccount: "..." })
```

<environment_details>
# Visual Studio Code Visible Files
src/pages/api/screen.ts

# Visual Studio Code Open Tabs
.gitignore
src/lib/context.ts
src/pages/api/discourse/posts.ts
src/lib/router.ts
src/pages/rpc/[[...rest]]/route.ts
src/lib/orpc.ts
src/pages/api/rpc/[[...rest]].ts
src/pages/api/screen.ts
.env.example
.env
</environment_details>