We have a bug that needs to be fixed in this HTTP interception library:

**Bug Report:**
"I see the problem now. It looks like intercept.reject() is not working as expected with the axios adapter in a React Query context - even though it works fine for direct axios calls (see the 'handles axios error responses with reject()' test that passes)."

**Context:**
- This is a TypeScript library (@klogt/intercept) for HTTP request interception/mocking
- The library supports multiple adapters: axios and fetch
- The axios adapter (`src/adapters/axios.ts`) is not properly handling rejected requests when used with React Query/TanStack Query
- Direct axios calls work fine, but when wrapped in React Query's error handling, the behavior is incorrect
- The test "handles axios error responses with reject()" passes, but it doesn't cover the React Query use case

**Expected behavior:**
When using `intercept.reject()` with a non-2xx status code (like 404, 500, etc.), the axios adapter should:
1. Throw an AxiosError (not return a normal response)
2. Extract and use custom error messages from the response body (like `response.data.message`)
3. Work correctly in async contexts like React Query's query functions

**Current problem:**
The axios adapter is returning error responses as normal successful responses instead of throwing AxiosError objects. This breaks error handling in React Query and similar libraries that expect errors to be thrown.

Please fix the axios adapter to properly handle rejected requests by implementing axios's `validateStatus` logic and throwing appropriate AxiosError objects for non-2xx status codes.

<environment_details>
# Visual Studio Code Visible Files
src/adapters/adapters.test.ts

# Visual Studio Code Open Tabs
package.json
CHANGELOG.md
src/adapters/adapters.test.ts
src/adapters/axios.ts
src/adapters/types.ts

# Current Working Directory (/app) Files
.gitignore
biome.json
CHANGELOG.md
knip.json
LICENSE
package.json
pnpm-lock.yaml
README.md
tsconfig.json
tsdown.config.ts
vitest.config.ts
dist/
src/
src/index.ts
src/adapters/
src/adapters/adapters.test.ts
src/adapters/axios.ts
src/adapters/fetch.ts
src/adapters/types.ts
src/api/
src/api/intercept.test.ts
src/api/intercept.ts
src/core/
src/core/constants.ts
src/core/log.ts
src/core/server.ts
src/core/store.ts
src/core/types.ts
src/core/utils.ts
src/http/
src/http/response.ts
</environment_details>
