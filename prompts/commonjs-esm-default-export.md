# A CommonJS Dependency Imported By Name From ESM Fails At Startup

**`import { X } from "cjs-pkg"` throws at startup, not at install.**

> Found 2026-10-25: `context-bridge` (launched 2026-06-20, 0 stars, 0 issues)
> could not start at all, because `src/server.js` and `src/indexer.js` both
> did `import { Database } from 'better-sqlite3'`. better-sqlite3 is
> CommonJS and exposes no `Database` named export — **its default export IS
> the constructor**. The package threw a `SyntaxError` on every invocation
> for four months. **Last verified:** 2026-10-25 — fixed, and the four MCP
> tools were exercised over stdio after the fix.

## The Error

```
SyntaxError: The requested module 'better-sqlite3' does not provide an
export named 'Database'
```

This is a **link-time** error, not a runtime one. The package fails to load
at all — before a single line of your own logic runs.

## Why It Is Invisible Until It Is Fatal

- `npm install` succeeds. The dependency is fine.
- `npm test` can even pass, if the tests never import the module.
- The failure appears only when the entry point is loaded.

**A package that cannot start is not "quiet".** It is broken, and the
symptom ("no stars, no issues, no activity") is indistinguishable from
"nobody wants it".

## The Fix

```js
// WRONG — CommonJS module, no named export
import { Database } from 'better-sqlite3';

// RIGHT — the default export is the constructor
import Database from 'better-sqlite3';

const db = new Database('index.db');
```

## How To Check The Real Export Shape

Do not read the README. Ask the module:

```js
import * as mod from 'better-sqlite3';
console.log(Object.keys(mod));            // ['default', ...] — no 'Database'
console.log(typeof mod.default);          // 'function' — this is the class
```

From CommonJS:

```js
const mod = require('better-sqlite3');
console.log(Object.keys(mod));            // may be [] — cjs interop detail
console.log(typeof mod);                   // 'function' — the module IS the class
```

**The rule: a named import is only valid if the name appears in the module's
export list. Check the list; do not assume the name.**

For a dual package (CommonJS + ESM builds, e.g. via `exports` in
package.json), the ESM entry may expose a default export while the CJS entry
exposes the bare function. Both facts are visible in the same
`Object.keys` check.

## The Generalisation

> **A named import is a claim about the module's export list. Verify it once
> at the module boundary, not once per call site.**

The same class of bug appears with:

- `import { connect } from "pg"` when the package exports a factory,
- `import { request } from "axios'` when it is a default export,
- `import { v4 } from "uuid'` where the export name changed between majors,
- Node builtins imported with a default (`import fs from "node:fs'`).

The cheap guard: **one module that centralises the import** and asserts the
shape once at startup.

```js
// db.js — the single place that knows the module's real shape
import Database from 'better-sqlite3';
if (typeof Database !== 'function') {
  throw new Error('better-sqlite3 default export is not the constructor');
}
export { Database };
```

Then every other file imports `{ Database }` from `./db.js` and the shape
is checked exactly once.

## The Real Lesson: A Monitoring Job That Counts Issues Never Finds This

`context-bridge` was monitored daily by a job that counted stars, issues, PRs
and comments. For 127 days it reported "0 issues, 0 PRs, dormant" — a
perfectly accurate report of a **product that could not execute a single
line of its own code**.

> **Counting activity measures engagement. Starting the product measures
> existence.** A monitor must include at least one check that the thing
> still runs.

The cheapest such check is a smoke invocation on every run:

```bash
node -e "import('./src/server.js').then(m => console.log('server loads'))"
```

See also `prompts/zero-result-indexer.md` (the same product's three other
P0 bugs) and `prompts/zero-tests-ran-is-a-failure.md` (a suite that never
imports the module proves nothing).
