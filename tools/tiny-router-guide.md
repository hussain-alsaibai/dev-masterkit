# tiny-router — Stdlib WSGI Routing

> Zero-dependency WSGI router for small Python services, agent callbacks, and stdlib-only HTTP examples.
> Last verified: 2026-08-17 | Version 0.3.0 | hussain-alsaibai/tiny-router

## What Changed in v0.3.0 (Aug 2026)

- **Async handler support** — `async def` route handlers are automatically detected and awaited (`inspect.iscoroutine()` detect-and-dispatch)
- **FastAPI-style `Depends()`** dependency injection — recursive dependency resolution, per-request caching, zero deps
- **`HTTPError` exception** — raise `HTTPError(status, message)` for structured error responses; 503 status maps to service unavailable
- **`AsyncResponse`** — explicit async response wrapper for handlers that need async I/O

## Repo

https://github.com/hussain-alsaibai/tiny-router

## When to Use

- You need Flask-like routing without Flask.
- You are building a tiny-* style service or example.
- You need a callback receiver with explicit operational boundaries.
- You want a small WSGI app that is easy to test with stdlib tooling.

## Minimal Shape

```python
from tiny_router import Router, Response

app = Router()

@app.get("/health")
def health(request):
    return {"ok": True}

@app.post("/callback")
def callback(request):
    payload = request.json()
    return Response.json({"accepted": True, "id": payload["id"]}, status=202)
```

## Async Handlers (v0.3.0)

```python
from tiny_router import Router

app = Router()

@app.get("/slow")
async def slow_handler(request):
    result = await fetch_data_from_external_api()
    return {"data": result}
```

Handlers are automatically detected via `inspect.iscoroutine()` and awaited — no changes to the router API needed.

## Dependency Injection with `Depends()` (v0.3.0)

```python
from tiny_router import Router, Depends, HTTPError

app = Router()

def get_db():
    return DatabaseConnection()

def get_user(dep_db=Depends(get_db)):
    user = dep_db.current_user
    if not user:
        raise HTTPError(401, "Unauthorized")
    return user

@app.get("/profile")
def profile(request, user=Depends(get_user)):
    return {"id": user.id, "name": user.name}
```

Features:
- **Recursive resolution** — dependencies can themselves `Depends()` on other dependencies
- **Per-request caching** — each dependency is resolved once per request, then cached
- **Zero deps** — pure Python, no third-party DI framework

## HTTPError Exception (v0.3.0)

```python
from tiny_router import HTTPError

@app.get("/status")
def status_check(request):
    upstream = check_service_health()
    if not upstream:
        raise HTTPError(503, "Upstream service unavailable")
    return {"status": "ok"}
```

Maps to standard HTTP status codes in the response. Catch with a global error handler:

```python
@app.error_handler
def handle_error(request, error):
    if isinstance(error, HTTPError):
        return Response.json({"error": error.message}, status=error.status)
    return Response.json({"error": "Internal server error"}, status=500)
```

## Agent Callback Receiver Pattern

The verified `examples/agent_callback_receiver.py` recipe includes:
- bearer-token authentication
- request IDs for correlation
- fixed-window rate limiting
- TTL idempotency keys
- JSON body validation
- structured JSON logs
- `/health`, `/ready`, and `/status` endpoints
- focused tests for valid, duplicate, unauthorized, invalid, and throttled callback flows

## Signed Callback Receiver (field note 2026-07-14)

Extend the callback pattern for signing providers. Verify the HMAC over the exact raw request body before parsing JSON, reject timestamps outside a small tolerance, and deduplicate by delivery ID with a TTL. Pair with `/health`, `/ready`, and `/status` endpoints for observable health.

See [Signed Callback Receivers With tiny-router](https://github.com/hussain-alsaibai/tiny-router/blob/main/reports/2026-07-14-signed-callback-receivers.md)

## Performance

~76K req/s on commodity hardware.

## Tests

- Core router tests: **61/61 passing** (v0.3.0 — added TestAsyncHandlers + TestDepends)
- Callback receiver example tests: 11/11 passing

## Last verified: 2026-08-17

- Repo: `hussain-alsaibai/tiny-router`
- Commit: `f522543` (v0.3.0)
- Verification: 61/61 tests passing, async + Depends features verified

## Ecosystem

Part of the `tiny-*` zero-dependency ecosystem. See also:
- [tiny-context](tiny-context-guide.md) — LLM context window manager (v0.1.0, new)
- [tiny-log](tiny-log-guide.md) — Structured logging
- [tiny-chain](tiny-chain-guide.md) — Streaming LLM processor
