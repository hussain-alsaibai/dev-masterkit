# tiny-router v0.7.3 — Path-Redaction Middleware Sidecar

> Zero-dependency WSGI router. v0.7.3 ships `redact_path_middleware()` and `redactor_with_stats()` in a new sidecar module `tiny_router_redact_path.py`, integrating `tiny-secret-mask` v0.4.0 path redaction at the middleware layer.
> Last verified: 2026-10-14 | Version 0.7.3 | hussain-alsaibai/tiny-router

## What Changed in v0.7.3 (Oct 2026)

- **`redact_path_middleware(*, stats=None, on_redact=None)`** — returns a tiny-router middleware that mutates `req.path` in place so downstream handlers, log lines, and trace spans all see the redacted form. The mutation happens **before** any handler in the chain runs.
- **`redactor_with_stats() -> (middleware, stats)`** — convenience factory. Returns the middleware plus a fresh `RedactionStats(paths_seen, redactions, last_redacted_path)` counter ready to be wired into `/metrics`.
- **`RedactionStats`** — counter object with `as_dict()` for JSON-serializable snapshots.
- **Sidecar module:** `tiny_router_redact_path.py` (~132 LOC). Lazy-imports `tiny_secret_mask.mask_route_path`. Falls back to a no-op when `tiny-secret-mask < 0.4.0` is installed (the path passes through unchanged). Zero new dependencies.
- **15 new tests** in `test_v073_redact_path.py`. Combined suite: prior + 15.

## Why This Matters

The Oct 14 cycle adds a third layer of credential redaction to the tiny-* family: **path-component redaction**. `tiny-router v0.7.3` is the reference integration point for the family. Pair `redact_path_middleware()` with the existing v0.4.0 trace-context redaction in `tiny-secret-mask` and you get a full four-layer credential-leak loop at the router level: value / key / trace / path.

## Quick Start

```python
from tiny_router import Router
from tiny_router_redact_path import redact_path_middleware, redactor_with_stats

app = Router()

# Option 1: bare middleware
app.add_middleware(redact_path_middleware())

# Option 2: middleware + stats counter
middleware, stats = redactor_with_stats()
app.add_middleware(middleware)

@app.get("/users/<user_id>")
def get_user(req, user_id):
    # req.path is now "/users/[REDACTED:uuid]" if user_id is UUID-shaped
    return {"user_id": user_id, "path": req.path}

@app.get("/metrics")
def metrics(req):
    return stats.as_dict()
```

## Stats for /metrics

The `RedactionStats` counter is JSON-serializable:

```python
>>> stats = RedactionStats()
# ... 1000 requests pass through, 12 paths got redacted ...
>>> stats.as_dict()
{'paths_seen': 1000, 'redactions': 12, 'last_redacted_path': '/users/[REDACTED:uuid]/profile'}
```

Wire it to your existing `/metrics` endpoint (Prometheus client, OpenMetrics, or a simple JSON snapshot) and you have a redaction-rate panel without writing one line of plumbing.

## When to Use / When to Use Something Else

**Use when:**

- You already use `tiny-router` and want path redaction at the middleware layer
- You want a stats counter ready for `/metrics`
- You're building a tiny-* agent gateway or Flask-style single-file service

**Don't use when:**

- You don't use `tiny-router` → use `tiny-route-redact` (framework-agnostic) instead
- You need redaction deeper than the path layer (e.g. response body) → pair with `tiny_secret_mask.mask_response()`
- You control the path generation end-to-end and never put credentials in it

## Repo

https://github.com/hussain-alsaibai/tiny-router

## See Also

- `tools/tiny-router-v0.5-guide.md` — v0.5.0 (openapi_endpoint + jwt_refresh_pair + jwt_refresh_exchange)
- `tools/tiny-secret-mask-v0.4-guide.md` — the rule catalogue (12 patterns, severity levels)
- `tools/tiny-route-redact-guide.md` — framework-agnostic alternative for non-tiny-router stacks
