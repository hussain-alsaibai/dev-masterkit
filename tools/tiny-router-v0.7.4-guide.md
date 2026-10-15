# tiny-router v0.7.4 — Header-Redaction Middleware Sidecar

> Zero-dependency WSGI router. v0.7.4 ships `redact_headers_middleware()` and `redactor_with_stats()` in a new sidecar module `tiny_router_redact_headers.py`, integrating `tiny-secret-mask` v0.5.0 header redaction at the middleware layer.
> Last verified: 2026-10-15 | Version 0.7.4 | hussain-alsaibai/tiny-router

## What Changed in v0.7.4 (Oct 2026)

- **`redact_headers_middleware(*, stats=None)`** — returns a tiny-router middleware that mutates `req.headers` in place by calling `tiny_secret_mask.mask_headers()`. Downstream handlers, log lines, and trace spans all see the redacted form. The mutation happens **before** any handler in the chain runs.
- **`redactor_with_stats() -> (middleware, stats)`** — convenience factory. Returns the middleware plus a fresh `HeaderStats(headers_seen, redactions, last_redacted_header)` counter ready to be wired into `/metrics`.
- **`HeaderStats`** — counter object with `as_dict()` for JSON-serializable snapshots. Same shape as `tiny_headers_redact.HeaderStats` for cross-compat.
- **Sidecar module:** `tiny_router_redact_headers.py` (~131 LOC). Lazy-imports `tiny_secret_mask.mask_headers`. Falls back to a no-op when `tiny-secret-mask < 0.5.0` is installed (the headers pass through unchanged). Zero new dependencies.
- **17 new tests** in `test_v074_redact_headers.py`. Combined suite: prior + 17.
- **Completes the v0.7.3 (path) + v0.7.4 (header) pair** — every primitive that crosses a network boundary in tiny-router is now expected to apply both redaction layers.

## Why This Matters

The Oct 15 cycle adds the **fifth layer** of credential redaction to the tiny-* family: **header redaction**. `tiny-router v0.7.4` is the reference integration point for the family. Pair `redact_headers_middleware()` with the v0.7.3 `redact_path_middleware()` and you get a full five-layer credential-leak loop at the router level: value / key / trace / path / header.

## Quick Start

```python
from tiny_router import Router
from tiny_router_redact_headers import redact_headers_middleware, redactor_with_stats

app = Router()

# Option 1: bare middleware
app.add_middleware(redact_headers_middleware())

# Option 2: middleware + stats counter
middleware, stats = redactor_with_stats()
app.add_middleware(middleware)

@app.post("/login")
def login(req):
    # req.headers is now redacted before this handler runs
    # {"Authorization": "[REDACTED:authorization]", "X-Request-Id": "abc", ...}
    return {"ok": True}

@app.get("/metrics")
def metrics(req):
    return stats.as_dict()
```

### Pair with v0.7.3 path redaction

```python
from tiny_router import Router
from tiny_router_redact_path import redact_path_middleware
from tiny_router_redact_headers import redact_headers_middleware, redactor_with_stats

app = Router()
app.add_middleware(redact_path_middleware())         # v0.7.3
header_mw, header_stats = redactor_with_stats()      # v0.7.4
app.add_middleware(header_mw)
```

## Stats for /metrics

The `HeaderStats` counter is JSON-serializable:

```python
>>> stats = HeaderStats()
# ... 1000 requests pass through, 23 headers got redacted ...
>>> stats.as_dict()
{'headers_seen': 1000, 'redactions': 23, 'last_redacted_header': 'Authorization'}
```

Wire it to your existing `/metrics` endpoint (Prometheus client, OpenMetrics, or a simple JSON snapshot) and you have a redaction-rate panel without writing one line of plumbing.

## When to Use / When to Use Something Else

**Use when:**

- You already use `tiny-router` and want HTTP header redaction at the middleware layer
- You want a stats counter ready for `/metrics`
- You're building a tiny-* agent gateway or Flask-style single-file service

**Don't use when:**

- You don't use `tiny-router` → use `tiny-headers-redact` (framework-agnostic) instead
- You need redaction deeper than the header layer (e.g. response body) → pair with `tiny_secret_mask.mask_response()` (planned v0.6.0)
- You control the upstream and know no credentials cross the boundary (still good defence in depth)

## Repo

https://github.com/hussain-alsaibai/tiny-router

## See Also

- `tools/tiny-router-v0.7.3-guide.md` — `redact_path_middleware()` for the path layer
- `tools/tiny-secret-mask-v0.5-guide.md` — the 16-pattern header rule catalogue
- `tools/tiny-headers-redact-guide.md` — framework-agnostic alternative for non-tiny-router stacks
- `tools/tiny-route-redact-guide.md` — framework-agnostic path middleware
