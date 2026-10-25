# "Indexed 0 Files" Is Not an Empty Repo — It Is a Broken Matcher

**A zero result from an indexer is a defect report, not a measurement.**

> Found 2026-10-25 in `context-bridge`: three separate P0 bugs made the indexer
> report **0 files, 0 symbols** on every run, for four months. The repo was
> monitored daily and reported "dormant, 0 issues" — because a broken indexer
> and an empty repo look identical from the outside. **Last verified:**
> 2026-10-25 — fixed and re-verified end to end (init → index → search → all
> four MCP tools over stdio).

## Bug 1: The Glob Matcher Never Matched The Default Pattern

The default include pattern is:

```
**/*.{js,ts,jsx,tsx,py,rs,go,java,rb,php}
```

The matcher handled only `*`. Converting that pattern to a regular
expression with a naive `.*` yields a pattern that requires a literal `{js,ts,...}`
brace sequence — which no filename contains. **Every file was excluded.**

The bug is invisible in the code and total in effect: a matcher that matches
nothing is exactly as quiet as a matcher that works.

The fix is a real glob-to-regex translation supporting `**`, `*`, `?`, and
brace expansion:

```js
function globToRegExp(pattern) {
  // expand {a,b,c} -> (a|b|c)
  let re = pattern.replace(/\{([^}]+)\}/g, (_, inner) =>
    '(' + inner.split(',').map(s => s.trim()).join('|') + ')');
  // ** -> any path segments, * -> any chars but '/', ? -> one char
  re = re.replace(/\*\*/g, '\u0000')
         .replace(/\*/g, '[^/]*')
         .replace(/\u0000/g, '.*')
         .replace(/\?/g, '[^/]');
  return new RegExp('^' + re + '$');
}
```

**Test the matcher against the pattern you actually ship**, not against a
pattern you invented for the test:

```js
const re = globToRegExp('**/*.{js,ts,py}');
assert(re.test('src/server.js'));      // TRUE — and this is the whole point
assert(re.test('a/b/c/main.py'));      // TRUE — ** spans directories
assert(re.test('README.md'));          // FALSE
assert(!re.test('node_modules/x.js')); // FALSE only via an explicit exclude
```

## Bug 2: The Swallowed Foreign Key Violation

Re-indexing used `INSERT OR REPLACE INTO files`. In SQLite, `REPLACE`
**deletes** the conflicting row and inserts a new one — which breaks the
`symbols -> files` foreign key the moment that file already has symbols.

The error was caught and discarded:

```js
try {
  db.prepare('INSERT OR REPLACE INTO files ...').run(...);
} catch (e) {
  // swallowed
}
```

Result: **the first index run worked, and every run after it produced 0
files.** The catch block hid a real error, and the visible symptom pointed
somewhere else entirely.

The fix is the correct write order — upsert the parent, clear the children,
insert the children:

```js
db.prepare(`INSERT INTO files (path, hash, ...) VALUES (?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET hash = excluded.hash, ...`)
  .run(path, hash, mtime);
db.prepare('DELETE FROM symbols WHERE file_id = ?').run(fileId);
// then insert the symbols for this file
```

## The Rule About catch

> **A catch block that discards an error is a decision to be blind in exactly
> one place.** If the code cannot proceed without the data, the error must be
> logged and counted, and the run must report that it skipped rows.

```js
let skipped = 0;
try { ... } catch (e) { skipped += 1; log.warn('row skipped', e); }
// ...at the end:
if (skipped) console.warn(`indexed ${n} files, ${skipped} rows skipped`);
```

A skipped row that is counted is a fact. A skipped row that is swallowed is
a mystery.

## Bug 3: The Startup Import (covered separately)

The third P0 — `import { Database } from 'better-sqlite3'` — is a startup
crash, documented in `prompts/commonjs-esm-default-export.md`.

## The Pattern Across The Three

| # | Bug | Visible symptom | Real cause |
|---|-----|-----------------|------------|
| 1 | Glob matcher handles only `*` | 0 files indexed | default pattern matched nothing |
| 2 | `INSERT OR REPLACE` + swallowed FK error | 2nd+ run indexes 0 files | row delete broke the FK |
| 3 | Named import of a CommonJS default | package does not start | wrong export shape |

**All three produced the same class of output: a number that looked like a
measurement and was actually a failure.**

## The Rule

> **A count of zero is a claim that must be proven, not a result that can be
> trusted.** If the answer is "nothing found", the system must prove that the
> search space was non-empty.

Two cheap assertions catch most of this class:

```js
// 1. the matcher must match the shipped default pattern
assert(globToRegExp(DEFAULT_INCLUDE).test('src/index.js'));

// 2. an index run over a known-non-empty directory must return > 0
const files = await index('testdata/known-good');
assert(files.length > 0, 'indexer returned 0 for a known-good directory');
```

A fixture directory with known contents turns "0" from a silent outcome into
a loud one.

## The Meta-Lesson: Monitoring Engagement Is Not Monitoring Existence

`context-bridge` was checked daily by a job that counted stars, issues, PRs,
comments and pushes. For 127 days it said "dormant". It was **broken the
whole time** — it could not start, and its indexer could not find a file.

> **A monitor that only counts engagement cannot detect a product that
> cannot run.** Add one check that executes the thing: start the server,
> index a fixture, call one tool. One smoke call per run is cheaper than a
> day of looking at zero-issue dashboards.

See also `prompts/commonjs-esm-default-export.md`, 
`prompts/fail-closed-on-unavailable-data.md` (absence of data is not a pass),
`prompts/zero-tests-ran-is-a-failure.md` (a green suite can also be a lie).
