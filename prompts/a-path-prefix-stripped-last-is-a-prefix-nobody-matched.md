---
name: a-path-prefix-stripped-last-is-a-prefix-nobody-matched.md
description: Use when a service is mounted under a sub-path (reverse proxy, base href, `--base-url`) and one prefix is stripped at the end of a request handler — every route that matched earlier saw the un-stripped path, and the strip only reaches the last handler in the chain.
---

# A path prefix stripped last is a prefix nobody matched

## The prompt

> Where in the handler is the prefix removed? If it is not the first thing,
> every branch above it compared a path that still carries the prefix — and the
> branch that "works" is the only one that survives to the strip.

## What happened

`blixvip/NullMotion` issue #57: an instance served under `/null/` should serve
the same site as `/`. In `test/server.test.js` every mounted route 404'd while
`/` worked.

The strip was the **last** statement in the request handler, after four things
had already been decided on the un-stripped path:

```js
// (abridged) the order as shipped
if (pathname === '/')            pathname = '/demo.html'
if (pathname === '/editor')      pathname = '/editor.html'
const ro = readOnly[pathname]                 // table lookup
if (pathname.startsWith(TEMPLATE_SRC)) ...    // template-source route
if (pathname.startsWith('/api/')) ...         // API guard
pathname = pathname.replace(/^\/null/, '') || '/'   // <- the strip
serveFile(pathname)
```

Only `serveFile` ever saw a stripped path. `/null/api/...` hit the API guard
with the prefix still attached, `/null/editor` missed the editor rewrite, and
`/null/` reached the file server as `/`— which then served the directory index,
i.e. the **template gallery** instead of the homepage.

**Second bug, same two lines:** `pathname = '/'` was assigned *after* the
`'/' -> '/demo.html'` rewrite, so normalising `/null` to `/` skipped the
homepage mapping entirely. Both `/null` and `/null/` now normalise to `/` at the
**top** of the handler, before the first comparison:

```js
const BASE = '/null'
if (pathname === BASE || pathname === BASE + '/') pathname = '/'
else if (pathname.startsWith(BASE + '/')) pathname = pathname.slice(BASE.length)
```

**Test:** `inherited /null/ path prefix is stripped before route matching`,
added to `test/server.test.js`. Proven to fail on `origin/main` and pass with
the fix. Suite **41 → 42 tests, 40 pass / 2 fail** — both failures pre-existing
and identical on the unmodified base commit (audio extraction), unrelated to
the change.

**Manual curl, all five routes:** `404 → 200` for `/null/`, `/null/api/...`,
`/null/editor`, `/null/<media>`, `/null/<template-src>`; `/null` and `/null/`
now return the same `<title>` as `/`.

## The rule

1. **A normalisation step belongs before the first decision that depends on
   it.** Strip, decode, case-fold, trailing-slash — all of it, at the top.
   Placement *is* the bug; the regex was correct.
2. **Grep for the second assignment to the same variable.** `pathname = '/'
   || pathname` hides an ordering dependency in an `||` chain that reads as
   defensive. Any later rewrite of that same value was bypassed.
3. **Test through the real router, not the helper that does the stripping.** A
   test on `stripPrefix()` passes whatever the handler order is. The regression
   drives `request(app)` and asserts the title/status, so it fails when the
   strip moves.
4. **Report pre-existing failures with their provenance.** "40 pass / 2 fail"
   is a claim; "the 2 also fail on the base commit, same names" is a proof the
   change did not cause them.
5. **A mounted-path bug has a route table, not a route.** Enumerate every
   branch above the strip (rewrite, allowlist lookup, static mount, API guard)
   and check each one under the prefix. The single failing route a reporter
   names is usually the last one in line.

---

**Last verified:** 2026-11-16 — PR `blixvip/NullMotion` #75 open; test proven to
fail on `origin/main`; suite 42 tests measured; all five routes curled from
404 to 200 in this session; `/null` and `/null/` titles compared against `/`.
