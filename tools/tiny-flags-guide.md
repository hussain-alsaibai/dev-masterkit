# tiny-flags Guide

## Repo
https://github.com/hussain-alsaibai/tiny-flags

## What It Does

Zero-dependency feature flags for Python. One file, no setup. Boolean,
percentage, and multivariate flags with deterministic SHA-256 bucketing.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_flags import Client,
gate, variant`. **There is no `Client` class.** Verified against upstream
`tiny_flags.py`:

```
__all__ = ['Flag', 'Flags', 'Rule', 'Operator', 'Context', 'Source', 'sources',
           'gate', 'variant']
```

The container is **`Flags`** (plural); `Flag` is a single flag, `Rule` an
operator-guarded condition, `Context` the evaluation context, and `Source` a
configuration backend. `gate` and `variant` are the evaluation functions.

## Key Features

- Boolean / percentage / multivariate flag types
- `Rule` with `Operator` conditions
- Deterministic SHA-256 bucketing (stable across processes and hosts)
- `Source` backends plus a `sources` helper for combining them

## Quick Start

```python
from tiny_flags import Flags, Context, gate, variant

flags = Flags()
flags.add("new_ingest", rollout=10.0)

if gate(flags, "new_ingest", Context(user_id="u-42")):
    ...

which = variant(flags, "new_ingest", Context(user_id="u-42"))
```

## When to Use

- Rolling out a behaviour to a percentage of users deterministically
- Gating an agent capability behind a flag without a config service
- When the same flag decision must be identical on every host

## Related

- `tools/tiny-feature-flag-guide.md` — `tiny-feature-flag`, a different repo with
  a `Flag` / `FlagStore` / `Context` / `Rule` API
