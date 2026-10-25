# context-bridge: three P0 bugs that made the product unusable since launch

**Date:** 2026-10-25
**Repo:** `hussain-alsaibai/context-bridge` (v0.1.0, launched 2026-06-20)
**Commits:** `90a3d8f` (initial) → `2cc4ee9` (the three fixes) → `f52d478`
(search_code highlight fix)
**Last verified:** 2026-10-25 — `npm test` → **4 tests, 4 pass** (verified by
run, 1027 ms)

## Why this report exists

A monitoring job that counted stars, issues, PRs and comments reported
`context-bridge` as **"dormant, 0 issues, 0 PRs, last push Jun 20"** — for
127 days.

Every one of those numbers was accurate. The repo was **broken the whole
time**: it could not start, and its indexer could not find a single file.

> **Counting activity measures engagement. Starting the product measures
> existence.** A monitor that only counts engagement cannot detect a product
> that cannot run.

## The three P0 bugs

### P0-1 — Named import of a CommonJS default (startup crash)

```js
// src/server.js, src/indexer.js
import { Database } from 'better-sqlite3';   // SyntaxError
```

better-sqlite3 is CommonJS and exposes **no `Database` named export** — its
default export **is** the constructor.

```js
import Database from 'better-sqlite3';       // correct
```

**Symptom:** the package threw on every invocation for 127 days. Nothing in
the repo could run. A link-time error, so it failed before any of the
project's own logic executed.

### P0-2 — The glob matcher never matched the default include pattern

The default include pattern is:

```
**/*.{js,ts,jsx,tsx,py,rs,go,java,rb,php}
```

The matcher handled only `*`. Converting that to a regex naively produces
something that requires a literal `{js,ts,...}` brace sequence, which no
filename contains. **Every file was excluded.**

**Symptom:** every run reported `Indexed 0 files, 0 symbols`.

**Fix:** a real `globToRegExp` with `**`, `*`, `?` and brace expansion.

### P0-3 — `INSERT OR REPLACE` broke a foreign key, and the error was swallowed

Re-indexing used `INSERT OR REPLACE INTO files`. In SQLite, `REPLACE`
**deletes** the conflicting row and inserts a new one — which breaks the
`symbols -> files` foreign key the moment that file already has symbols.

```js
try {
  db.prepare('INSERT OR REPLACE INTO files ...').run(...);
} catch (e) {
  // swallowed — the error never reached a log
}
```

**Symptom:** the **first** index run worked; the **second and every later
run** produced 0 files. The failure looked like a data problem and pointed
nowhere near the cause.

**Fix:** upsert the file row, clear that file's symbols, then insert the new
ones.

## The table that matters

| # | Bug | Visible symptom | Real cause | Loud? |
|---|-----|-----------------|------------|-------|
| 1 | Wrong export shape | package does not start | CommonJS default import | yes (throws) |
| 2 | Glob handles only `*` | `Indexed 0 files` | default pattern matched nothing | **no** |
| 3 | REPLACE + swallowed FK | 2nd+ run indexes 0 files | row delete broke the FK | **no** |

Two of the three produced **no error at all**. They produced a number that
looked like a measurement.

## Verification (all by run, 2026-10-25)

- `init` → `index` → **2 files, 2 symbols**
- `search` returns the expected hit
- **all four MCP tools exercised over stdio**: `search_code`, `get_symbol`,
  `get_dependencies`, `summarize_module`
- an unknown tool returns an **error object**, not a crash
- DB integrity check: **ok**; no symbol duplication across repeated index runs
- exclude patterns verified: `node_modules`, `dist`, `*.test.js` all skipped

```
$ npm test
✔ indexes files with the default brace-expanded include pattern
✔ re-indexing an existing database does not lose files
✔ the server starts and handles an MCP request over stdio
✔ excluded directories are not indexed
ℹ tests 4   ℹ pass 4   ℹ fail 0
```

## The regression suite proves itself

`test/context-bridge.test.js` was written to be **verified against the
original code**, not just against the fix:

1. the suite **FAILS** against the pre-fix code,
2. the suite **PASSES** against the fixed code.

The check was performed by reverting a copy of the fix and running the
suite against it. **A test that passes both ways proves nothing.**

## Two other fixes shipped the same day

### The README told users to install someone else's package

```bash
npm install -g context-bridge     # installs memo-cn's Electron package
```

npm `context-bridge` is owned by `memo-cn` (i@memo.cool), an unrelated
Electron/JS inter-context bridge, last published 2023-12-17. We had never
published to npm.

**Fix:** clone + install, with a note. Recommended publish name:
`@alsaibai/context-bridge` (scope exists, package free).

### The native build was blocked on a clean install

`package.json` gained:

```json
"allowScripts": { "better-sqlite3": true }
```

so `better-sqlite3`'s native build is not skipped. A clean install was
verified afterwards.

## What generalises

1. **A CommonJS dependency imported by name from ESM fails at startup, not at
   install.** Check `Object.keys(module)` and the default export's shape.
2. **`catch {}` around an insert hides FK violations.** Log and count skipped
   rows instead.
3. **A glob matcher must be tested against the pattern you ship**, not a
   pattern invented for the test.
4. **A zero count must be proven, not assumed.** One fixture directory with
   known contents turns a silent zero into a loud failure.
5. **A monitor needs one execution check per run.** Counting stars is not
   the same as knowing the software still starts.

## Still unpublished

Both commits are local only as of this report — the GitHub credential outage
(see `reports/2026-10-25-credential-recovery.md`) had not yet been resolved
at the time of writing.

See also `prompts/commonjs-esm-default-export.md`,
`prompts/zero-result-indexer.md`,
`prompts/npm-name-ownership-before-install.md`.
