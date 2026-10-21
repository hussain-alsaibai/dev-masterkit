---
name: silent-security-control-audit
description: Audit for security/validation primitives that degrade to silent no-ops instead of failing loudly. Trigger when a try/except around a redaction, validation, auth, or bounds-check path returns plausible output instead of raising.
last_verified: 2026-10-21
---

# Silent Security Control Audit

## Why

A security control that returns plausible output on failure is worse than one
that crashes. It converts a hard, visible failure into an unfalsifiable
success. This prompt is the checklist that would have caught the
tiny-secret-mask v0.5.1 defect on day one instead of day six.

## Procedure

### 1. Find the graceful-degradation sites

```bash
grep -rn "except ImportError" --include="*.py" .
grep -rn "except Exception" -A 3 --include="*.py" . | grep -i "lambda\|return .*unchanged\|pass$"
```

For every hit, ask: **is the fallback returning plausible output?**

### 2. Classify each fallback

| Fallback returns | Verdict |
|------------------|---------|
| An exception / non-zero exit | SAFE |
| A loud warning + safe default | SAFE |
| An empty/error sentinel the caller must check | RISKY — check every caller |
| Plausible output (input echoed, default value, no-op) | **DEFECT** |

### 3. The packaging trap (this is where it hides)

A module exists on disk but is not listed in the package manifest, so it is
not importable after install. Any code guarded by `except ImportError` around
that import silently takes the fallback path forever.

```bash
# module on disk but missing from the manifest?
ls *.py                       # what exists
grep py-modules pyproject.toml # what ships
python3 -c "import pkg"        # from OUTSIDE the source dir
```

**Run the import check from a directory that is not the repo root.** Running
it in-tree imports the loose source file and hides the defect.

### 4. Rule-catalogue ordering (ordered regex catalogues)

```python
for r in RULES:                 # RULES is ORDERED
    if r.matches(text):
        text = r.apply(text)    # catch-all pre-empts everything after it
```

Rules:

- **Exactly one catch-all rule, always last.**
- Every rule must fire **by name** on its own example — assert the tag, not
  just that something was redacted.
- The catch-all must be distinguishable from the specific rules, or it
  destroys their signal.

### 5. Assert the guarantee, not the type

```python
# WRONG - passes even when redaction is a no-op
assert isinstance(out, str)

# RIGHT - asserts the actual guarantee
assert "[REDACTED:aws_access_key]" in out
```

A test that only checks the return type cannot detect a degraded control.

### 6. Version pins rot

`assert __version__ == "0.1.0"` in a suite that now runs on 0.5.1 is a
stale test, not a product defect — but it trains the team to ignore red
suites. Assert `>=` a floor instead.

## Definition of Done

- [ ] Every `except ImportError` around a security primitive was audited.
- [ ] Imports verified from **outside** the source directory.
- [ ] Any degraded path emits a warning naming the broken guarantee.
- [ ] Every catalogue rule asserted to fire by name.
- [ ] Placeholder/elided examples replaced with concrete strings.
- [ ] Downstream consumers' test suites re-run.

## Verified On

- **tiny-secret-mask v0.5.1** (2026-10-21) — found via downstream
  `tiny-router` test_v073_redact_path failures. 10 latent defects, 5 root
  causes. Tests 114/10 -> 124/0.
