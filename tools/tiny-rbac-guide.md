# tiny-rbac — Zero-Dependency RBAC/ABAC Policy Engine

**Created:** 2026-07-29 by @hussain-alsaibai
**Last verified:** 2026-07-29
**License:** MIT | **Dependencies:** 0 (Python stdlib only)
**Repo:** https://github.com/hussain-alsaibai/tiny-rbac
**PyPI:** `pip install tiny-rbac`

## Overview

Single-file, zero-dependency authorization library supporting Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC) with a **deny-overrides** evaluation model. JSON policies, glob resource matching, and role inheritance built in.

## Key Features

- **RBAC** — Role hierarchies with `add_role(parents=...)` inheritance
- **ABAC** — Attribute conditions (`time < "09:00"`, `sensitivity == "high"`, etc.)
- **Deny-overrides** — Any deny policy match blocks access, even if allow matches too
- **Glob resource patterns** — `documents/*`, `api/**/users`, etc.
- **JSON import/export** — Serialize entire policy set for persistence or distribution
- **Zero deps** — Pure Python stdlib, single file, MIT licensed

## Quick Usage

```python
from tiny_rbac import PolicyEngine

engine = PolicyEngine()
engine.add_role("editor")
engine.add_role("viewer", parents=["editor"])

engine.grant("admin", "*", "*")
engine.grant("editor", "write", "documents/*")
engine.grant("viewer", "read", "*")

engine.is_allowed("editor", "write", "documents/report.pdf")  # True
engine.is_allowed("viewer", "write", "documents/report.pdf")  # False
```

## AI Agent Integration

Designed for tool-level authorization in agent frameworks. Use to scope which tools/actions an agent identity can invoke:

```python
engine.grant("code-agent", "call", "tools/git/*")
engine.grant("data-agent", "call", "tools/db/read/*")
engine.grant("admin-agent", "call", "tools/*")
```

## Deny-Overrides Safety

If a deny policy matches AND an allow policy matches, **deny wins**. This is the safest model for security-critical agent tool access.

## When To Use

- AI agents need scoped tool permissions
- Multi-tenant API authorization
- Need policy-as-code that serializes to JSON
- Want zero-dependency, auditable single-file authz

## See Also

- [tiny-policy](https://github.com/hussain-alsaibai/tiny-policy) — ABAC-only policy engine (lighter, no RBAC)
- [tiny-agent](https://github.com/hussain-alsaibai/tiny-agent) — Agent framework that integrates with tiny-rbac
