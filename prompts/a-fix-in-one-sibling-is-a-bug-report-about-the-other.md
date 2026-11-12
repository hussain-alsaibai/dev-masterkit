# A fix in one sibling is a bug report about the other

**Added:** 2026-11-12
**Last verified:** 2026-11-12 (`tiny-router` 0.9.2 `c177510`, path sidecar reproduced leaking on 0.9.1, fixed and CI green 7/7)
**Class:** security / refactoring hygiene
**Cost of not knowing:** credential-bearing URL paths forwarded verbatim by a middleware the operator believed was scrubbing them

## The shape

Two modules, forty lines apart, written on the same day from the same template:

```
tiny_router_redact_headers.py   # fixed 2026-10-26: raises RedactionUnavailable
tiny_router_redact_path.py      # untouched, still: return nxt(req)
```

The 2026-10-26 fix named the exact class of defect — *"a redaction layer that
cannot redact must refuse"* — and applied it to the header sidecar. The path
sidecar had the identical body and was never opened.

The bug it left live:

```python
if mask is None:
    return nxt(req)          # serve the request, forward the credential
```

A deployment that installed `redact_path_middleware()` without
`tiny_secret_mask` on the path believed URL segments were scrubbed. They were
not. Nothing raised, nothing logged, and the test suite was **green for
seventeen days** because every test had the dependency installed.

## How it was proven, not asserted

Run the same middleware construction with `tiny_secret_mask` off `sys.path` —
before and after:

```
path after: /u/550e8400-e29b-41d4-a716-446655440000 -> LEAKED
path after: /u/550e8400-e29b-41d4-a716-446655440000 -> /u/[REDACTED:uuid]
```

An unredacted path with no exception is the whole finding. Six of the seven
new regression tests fail on 0.9.1 and seven pass on 0.9.2.

## The rule

**When you fix a pattern, grep every sibling module for the pattern in the same
commit.** The fix commit's own reasoning is the best grep term you will ever
have — here it was `return nxt(req)`:

```sh
grep -rn "return nxt(req)\|is None: return\|except ImportError" <repo>
```

A sibling module that shares a template shares the defect. The one you fixed is
evidence the other one is wrong, not evidence the family is clean.

## Why the suite cannot find it

A unit test exercises the code path with the dependency present, because the
package's own CI installs everything in `install_requires`. The absent-dependency
branch is only reachable by removing the dependency — so the test that finds it
is not a better assertion, it is a different environment.

**Third rule:** for every optional import, run the module once with the import
failing *before* writing a test. The question is not "does it work?" but "what
does it do when the dependency is absent?" — and the answer must be an exception
or a function whose name says passthrough (`redact_path_middleware_passthrough`),
never a silent fallback.

## Near-miss to record

The obvious fix — move `_MASK` inside the closure so it resolves per call —
would have made a passing test and changed nothing about the leak, because the
guard has to fire at **construction**, not at request time. The leak is in the
absent-dependency branch, not in the caching.
