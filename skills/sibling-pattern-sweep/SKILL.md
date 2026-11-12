---
name: sibling-pattern-sweep
description: "After fixing a defect that has a recognisable code pattern, find and fix every sibling module that shares the template, prove the fix with a negative control that removes the dependency, and turn the sweep into a repo check. Use when a security or safety fix lands in one of several parallel modules (redaction sidecars, sanitizers, validators, exporters, cache layers), or when a fix touches a guard whose siblings were written from the same template."
---

# sibling-pattern-sweep — fix the family, not the instance

**Last verified:** 2026-11-12 (`tiny-router` 0.9.2 `c177510`)

A one-file fix in a codebase with parallel modules is an unfinished fix. The
sibling that was written from the same template has the same defect, and the
reasoning in your own fix commit is the best search term you will ever have.

Derived from `tiny-router`: the header redaction sidecar was fixed 2026-10-26
with the rule *"a redaction layer that cannot redact must refuse"*; the path
sidecar, 40 lines away and written from the same template, kept
`if mask is None: return nxt(req)` for **17 days** with a green suite.

## When to use

- A fix landed in one module and there are modules named `<x>_a.py`,
  `<x>_b.py`, or `<feature>_headers.py` / `<feature>_path.py`
- The fixed defect is a **guard, fallback, or fail-open branch** — the kind
  that only executes when something is absent
- A codebase has N near-identical sidecars (redaction, sanitisation,
  validation, serialisation, caching, retry)

## Step 1 — Write down the defect's shape before you fix it

Not the file, the *pattern*. Examples that worked:

| Defect | Grep term |
|---|---|
| silent fail-open on missing dep | `return nxt(req)`, `except ImportError: pass`, `is None: return` |
| defaulted field emitted as required | `if field.required:` without the `default is ...` conjunct |
| status set from windowed list | every assignment of the status variable |
| unref'd timer | `.unref()` |

## Step 2 — Grep the whole repo, not the directory

```sh
grep -rn "return nxt(req)\|is None: return\|except ImportError" <repo>
```

Every hit is a candidate. Read each one and classify: **same defect**,
**correct by accident**, **deliberately different**.

## Step 3 — Prove it, don't assert it

You need a negative control: the same call with the dependency absent.

```python
import sys
sys.modules['tiny_secret_mask'] = None      # seal before the module loads
import tiny_router_redact_path as mod
mod.redact_path_middleware()                # must raise, not pass through
```

Record the before/after in one line each:

```
before: path after: /u/550e8400-... -> LEAKED
after:  path after: /u/550e8400-... -> /u/[REDACTED:uuid]
```

**Trap:** sealing the import *after* the module loads changes nothing when the
value is bound at module scope (`_MASK = _resolve_mask()`). See
`prompts/a-negative-control-must-control-the-binding-moment.md`.

## Step 4 — Every new test must fail on the old version

Run the new tests against the pre-fix tree. `c177510`: **6 of 7 failed**
before, **7 passed** after. A test that passes on both trees tests nothing —
see `prompts/the-count-that-proves-it-works-is-the-count-that-fails.md`.

## Step 5 — Leave a greppable opt-out

A caller who genuinely wants the no-op behaviour gets a function whose name
says so:

```python
redact_path_middleware_passthrough()   # not: redact_path_middleware(strict=False)
```

The next sibling sweep greps for the guarded class and the opt-out separately,
and does not have to infer intent from a boolean.

## Step 6 — Turn the sweep into a check

If the pattern is mechanical, the repo should refuse it. A CI grep step or a
test that reconstructs the old code and asserts it is flagged beats a note in a
changelog. Fleet version of the same idea:
`scripts/scan_push_to_main_side_effects.py` over 499 workflows.

## Anti-patterns this skill exists to stop

- Fixing the file the report named, then closing the issue
- Moving the value inside the function so a broken test passes (the leak is in
  the absent-dependency branch, not in the caching)
- Trusting a green suite as evidence, when the suite installs every dependency
  and therefore cannot reach the branch
