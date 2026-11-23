---
title: A missing optional dependency must skip, not abort collection
date: 2026-11-23
tags: [testing, ci, packaging, optional-dependencies]
---

# A missing optional dependency must skip, not abort collection

## The shape

A test file guards its optional-dependency tests like this:

```python
import tiny_secret_mask  # optional sidecar

def test_redaction():
    ...
```

On a machine **with** the sidecar, every test runs. On a machine **without** it,
pytest reports:

```
ERROR tests/test_v074_redact_headers.py - ModuleNotFoundError: No module named 'tiny_secret_mask'
1 error in 0.42s
```

That single line hides **every dependency-independent test in the file**. It is
not a skip. A skip is a statement about one test; a collection error is a
statement about the whole module, and it reports the same way whether the file
holds one optional test or sixteen independent ones.

## Why it survives review

The developer's machine has the sidecar. CI's default job may also install it,
because something else in the requirements file needs it. So the abort path is
only exercised where nobody looks — a fresh consumer install, a minimal CI
image, a contributor's first checkout.

`tiny-router` 0.9.4 shipped exactly this. `test_v074_redact_headers.py` did a
bare module-scope import, and on a machine without the extra the suite reported
**1 collection error** instead of **16 skipped**, taking the whole file's
coverage with it. Measured in this container:

```
tiny-router @ fa3c96a (0.9.4), no tiny_secret_mask installed
196 passed, 26 skipped
```

The 26 skips are the honest count; the pre-fix run was a single ERROR line.

## The two fixes, and why the first is not enough

**Fix 1 — resolve at call time, not import time.**

```python
def _have_sidecar():
    try:
        import tiny_secret_mask  # noqa: F401
    except ImportError:
        return False
    return True

HAVE_SIDECAR = _have_sidecar()  # evaluated when the module loads, not at parse
```

or, cleaner, `pytest.importorskip("tiny_secret_mask")` inside a fixture. Either
way the decision happens where a missing import can be turned into a skip.

**Fix 2 — a CI job that runs the suite with the dependency deliberately absent
and asserts it is really absent.**

```yaml
- name: suite without optional sidecar
  run: |
    python -c "import importlib.util as u; assert u.find_spec('tiny_secret_mask') is None"
    pytest -q
```

The first line is the load-bearing one. A "no-extras" job that silently has the
extras installed passes trivially and proves nothing — it is a green check over
an untested path. `assert find_spec(...) is None` fails loudly if the isolation
was never achieved.

## The rule

> **An optional dependency must degrade to a skip, and the absence must be
> asserted before the suite that depends on it runs.** A `try/except ImportError`
> at module scope is only half the fix — the CI job that would have caught the
> abort has to be unable to accidentally install the dependency.

## Where else to look

The four signal queries from the 2026-11-23 trend scan, all live:

- `is:issue is:open "ModuleNotFoundError" created:>2026-11-16` — **501** issues.
- `is:issue is:open "optional dependency"` — steady stream, mostly "clear error
  message" asks.
- `is:issue is:open "zero-dependency" created:>2026-11-16` — **1,793** issues,
  including two against the same pair of repos for *live* numpy imports under a
  zero-dep claim. A zero-dep README is checkable and therefore gets audited.

Repos in our own tree that import sidecars lazily: `tiny-log`, `tiny-config`,
`fast-cache`. Apply the skip-path CI job to each; it is the only thing that
keeps a `try/except ImportError` honest over months.

## Last verified

2026-11-23 — `tiny-router` @ `fa3c96a` (0.9.4): suite run in this container with
`tiny_secret_mask` confirmed absent, **196 passed / 26 skipped**; sidecar
absence checked with `python -c "import tiny_secret_mask"` →
`ModuleNotFoundError`.
