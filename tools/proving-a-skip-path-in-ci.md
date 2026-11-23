# Proving a skip path in CI

**Last verified:** 2026-11-23 — `tiny-router` 0.9.4 (`fa3c96a`), suite run with
the optional sidecar confirmed absent (196 passed / 26 skipped).

## Why this guide exists

A package with optional dependencies has two configurations, and only one of them
is exercised by default. The other one — the minimal install — is where bugs
ship, because that is where a `try/except ImportError` decides whether the module
aborts, skips, or silently no-ops.

The failure this guide prevents, seen live in `tiny-router` 0.9.4: a
module-scope `import tiny_secret_mask` turned **16 skips** into **1 collection
error**, hiding every dependency-independent test in the file.

## The three-part pattern

### 1. Resolve availability where you can skip

```python
import pytest

@pytest.fixture(scope="module")
def masker():
    return pytest.importorskip("tiny_secret_mask")
```

`importorskip` converts absence into a per-test skip. A module-scope `try/except
ImportError` that sets a boolean works too, but the boolean is frozen at import
time — if the dependency is installed later in the same process, the flag lies.

### 2. Assert the absence before running the suite

```bash
python -c "import importlib.util as u, sys; sys.exit(0 if u.find_spec('tiny_secret_mask') is None else 1)"
pytest -q
```

Without this line the job is theater: any transitive dependency, any image with
extras preinstalled, and the "minimal" job quietly runs the same path as the
default job. The assertion is what makes the job about the absent case.

### 3. Assert an exact skip count, not "green"

```bash
pytest -q | tee /tmp/out.txt
grep -qE "passed" /tmp/out.txt && ! grep -qE "^(ERROR|[0-9]+ error)" /tmp/out.txt
```

An exit code of 0 from a run that collected zero tests is also green. Where the
count matters, assert it: `--tb=no -q` plus a grep for `skipped` is enough to
distinguish "26 skipped" from "0 collected".

## When the dependency is genuinely required

If the package cannot work at all without the sidecar, the import is not
optional and should be a hard dependency. The tell is whether the *package's*
public API works without it — in `tiny-router` the redaction middleware needs
the masker, but the router does not, so the suite must still collect.

## Applying it here

Candidate repos in this tree, all with lazy sidecar imports:

| Repo | Sidecar | Action |
|---|---|---|
| `tiny-log` | none today | add the job when the first optional dep lands |
| `tiny-config` | none today | same |
| `fast-cache` | none today | same |
| `tiny-router` | `tiny-secret-mask` | **done** — job landed in 0.9.4 |

## Related

- `prompts/a-missing-optional-dependency-aborts-collection.md`
- `skills/ci-that-actually-runs/SKILL.md`
- `skills/runtime-reliability/SKILL.md`
