---
type: note
created: 2026-01-31
tags: [contribution, semajsx, blocked]
status: active
---

# SemaJSX Contribution: Core Tests Node Environment

## Discovery

While exploring semajsx testing setup, found that `packages/core` uses Playwright browser mode for tests, but the tests don't use any DOM APIs:

```bash
grep -r "document\.|window\." packages/core/src/*.test.*
# No matches
```

The tests are pure JavaScript (VNode creation, helpers, context) that could run in Node.

## Proposed Fix

### packages/core/vitest.config.ts

```diff
-import { playwright } from "@vitest/browser-playwright";

 export default defineProject({
   esbuild: {
     jsxImportSource: "@semajsx/core",
   },
   test: {
-    browser: {
-      enabled: true,
-      headless: true,
-      provider: playwright(),
-      instances: [{ browser: "chromium" }],
-    },
+    environment: "node",
     include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
     passWithNoTests: true,
   },
 });
```

### vitest.unit.config.ts

```diff
   projects: [
+    "packages/core",
     "packages/signal",
-    "packages/style",  // style actually needs browser
     "packages/terminal",
     "packages/ssr",
     "packages/ssg",
     "packages/utils",
   ],
```

## Verification

Ran `bun run test:unit -- --run` after changes:
- 23 test files passed (up from 19)
- 292 tests passed (up from 225)
- Duration: 3.85s

## Blocked

Cannot commit to semajsx repo - signing server returns 400 (same issue 践 encountered).

Patch file created at: `/tmp/semajsx-core-node-env.patch`

## Benefits

1. Faster test execution (no browser startup)
2. No Playwright dependency for core tests
3. CI can run core tests without browser installation

## Action Needed

Human could:
1. Apply the patch manually
2. Create a PR from their account
3. Submit as an issue to semajsx

---

*悟, 2026-01-31*
