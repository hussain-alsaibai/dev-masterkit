# tiny-secret-mask v0.4.0 — Path-Component Redaction

> Stdlib-only secret redaction gets a path-component layer. v0.4.0 ships `mask_route_path(path)`, a 12-pattern `PATH_REDACT_RULES` catalogue, and a composable `RoutePathRedactor` engine.
> Last verified: 2026-10-14 | Version 0.4.0 | hussain-alsaibai/tiny-secret-mask

## What Changed in v0.4.0 (Oct 2026)

- **`mask_route_path(path: str) -> str`** — one-line function that redacts credential-shaped path components: UUIDs, hex strings, base64url fragments, JWT fragments, AWS keys, GitHub PATs, Stripe keys, OpenAI keys, Google API keys.
- **`RoutePathRedactor(rules=None, on_redact=None)`** — composable engine. Pass a custom rule list or a callback that fires with `(original_component, redacted_component)` for every match.
- **`MaskRoutePathRule(name, pattern, severity)`** — rule shape with `severity: "low" | "medium" | "high" | "critical"`. The default catalogue covers 12 patterns.
- **`PATH_REDACT_RULES`** — the default catalogue. Lazy-imported, overridable per-call.
- **Sidecar module:** `tiny_secret_mask_v040.py` (~254 LOC). The main `tiny_secret_mask.py` re-exports the new names. Zero new dependencies. `from __future__ import annotations` header. Idempotent on a second pass (the `[REDACTED:<name>]` placeholder is shorter than the threshold for any rule).
- **19 new tests** in `tests/test_v040_additions.py`. Suite: 23 → 55 (plus 16 from v0.2.0, plus 19 from v0.3.0 = 55 total).

## Why This Matters

Most request paths are safe. Some are not:

```
GET /v1/users/550e8400-e29b-41d4-a716-446655440000/tokens/ghp_xx...xxxx
```

A path like that can carry a session UUID and a leaked token by accident. v0.4.0 closes the path layer of the four-layer credential-leak loop:

| Layer | What it protects | Reference |
|-------|------------------|-----------|
| Value | The credential itself (Bearer, JWT, AWS key) | `tiny_secret_mask.mask_string` (v0.1.0) |
| Key | The field name (`password`, `token`, `api_key`) | `tiny_secret_mask.mask_dict` (v0.2.0) |
| Trace | W3C `tracestate` vendor entries | `tiny_secret_mask.mask_trace_context` (v0.3.0) |
| Path | URL path component (UUID, JWT, AWS key) | `tiny_secret_mask.mask_route_path` (v0.4.0) |

## Quick Start

```python
from tiny_secret_mask import mask_route_path   # re-exported at the top level

>>> mask_route_path("/users/550e8400-e29b-41d4-a716-446655440000/profile")
'/users/[REDACTED:uuid]/profile'

>>> mask_route_path("/keys/AKIAIOSFODNN7EXAMPLE/active")
'/keys/[REDACTED:aws_access_key]/active'

>>> mask_route_path("/oauth/eyJhbGciOiJIUzI1NiJ9.payload.signature/callback")
'/oauth/[REDACTED:jwt_fragment].payload.signature/callback'
```

## Custom Rules

```python
from tiny_secret_mask import RoutePathRedactor, MaskRoutePathRule
import re

redactor = RoutePathRedactor(rules=[
    MaskRoutePathRule(
        name="internal_id",
        pattern=re.compile(r"\bINT-\d{6}\b"),
        severity="low",
    ),
], on_redact=lambda original, redacted: log.info("redacted %s", name))

>>> redactor("/orders/INT-442109/details")
'/orders/[REDACTED:internal_id]/details'
```

## Coverage Matrix

| Rule | Severity | Example |
|------|----------|---------|
| `uuid` | low | `550e8400-e29b-41d4-a716-446655440000` |
| `hex_32` | low | `deadbeef0123456789abcdef01234567` |
| `hex_64` | medium | `0123...cdef` (64 hex chars, SHA-256-shaped) |
| `base64url_24` | low | `abcdefghijklmnopqrstuvwx` (≥24 b64url chars) |
| `jwt_header` | high | `eyJhbGciOiJIUzI1NiJ9` |
| `jwt_payload` | high | `eyJzdWIiOiIxMjM0In0` |
| `aws_access_key` | critical | `AKIAIOSFODNN7EXAMPLE` |
| `aws_secret_key` | critical | 40-char base64 |
| `github_pat` | critical | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `stripe_live` | critical | `sk_live_xxxxxxxxxxxxxxxxxxxxx` |
| `openai_key` | critical | `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `google_api_key` | critical | `AIzaSyAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

## Drop-in Patterns for the tiny-* Ecosystem

- **`tiny-router`** — register `redact_path_middleware()` (ships in `tiny_router_redact_path.py`) so `req.path` is rewritten before any handler or log formatter sees it.
- **`tiny-log`** — feed path strings through `mask_route_path()` before formatting, in case a logger holds the raw path.
- **`tiny-trace-otel`** — span attributes that include the path are scrubbed via `mask_route_path()` before export.
- **`tiny-route-redact` (new repo)** — framework-agnostic wrapper. The reference consumer for v0.4.0.

## When to Use / When Not to Use

**Use when:**

- You log request paths to disk, error sinks, or observability backends
- Your handler chain can pass through credentials in the URL (e.g. legacy webhook callbacks, OAuth callback paths)
- You want a four-layer credential-leak loop (value / key / trace / path)

**Don't use when:**

- The path is purely numeric (`/v1/orders/12345`) — a 5-digit order number doesn't trip any rule
- You control the path generation end-to-end and never put credentials in it
- You're already redacting at the value layer and never log the path

## Repo

https://github.com/hussain-alsaibai/tiny-secret-mask

## See Also

- `tools/tiny-secret-mask-guide.md` — v0.1.0 base guide (value redaction, dict redaction, pluggable rules)
- `tools/tiny-router-v0.7.3-guide.md` — pair with `redact_path_middleware()` for the middleware layer
- `tools/tiny-route-redact-guide.md` — framework-agnostic wrapper for non-tiny-router stacks
