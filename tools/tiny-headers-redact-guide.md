# tiny-headers-redact v0.1.0 — Framework-Agnostic Header-Redaction Middleware

> NEW REPO. Framework-agnostic HTTP header redaction middleware. Single file ~200 LOC, MIT, zero runtime deps. Wraps `tiny-secret-mask` v0.5.1 `mask_headers()` and exposes WSGI + ASGI adapters plus a `HeaderStats` counter.
> Last verified: 2026-10-15 | Version 0.1.0 | hussain-alsaibai/tiny-headers-redact

## What's in v0.1.0 (Oct 2026)

A brand-new repo, the framework-agnostic standalone answer to "I want header redaction but I don't use `tiny-router`."

- **`redact_headers(headers) -> dict`** — convenience wrapper. Returns a NEW dict with credential-bearing header values replaced. Equivalent to `tiny_secret_mask.mask_headers(headers)`.
- **`header_redactor_middleware(get_response, *, stats=None)`** — WSGI-style middleware that rewrites request headers before the wrapped app sees them. Compatible with `tiny-router`, FastAPI (via WSGI bridge), Django, and any other WSGI stack.
- **`header_redactor_asgi_middleware(app, *, stats=None)`** — ASGI-style middleware that rewrites the `headers` scope key. Returns a coroutine callable. Compatible with FastAPI, Starlette, Quart, Sanic, and any other ASGI stack.
- **`HeaderStats`** — counter object (`headers_seen`, `redactions`, `last_redacted_header`) with `as_dict()`. Same shape as `tiny_router_redact_headers.HeaderStats` for cross-compat.
- **25 tests** in `tests/test_tiny_headers_redact.py`. Suite passes locally.
- **Single file, ~200 LOC.** MIT-licensed, no third-party runtime deps. `tiny-secret-mask >= 0.5.0` is **required for redaction to work** - if absent, tiny-secret-mask v0.5.1+ raises a `RuntimeWarning` and the middleware passes headers through **unredacted**. Do not ship without it.
- > **Amended 2026-10-21.** This guide previously described the no-op as intended ("the middleware no-ops when not installed"). It was a packaging defect: `tiny_secret_mask_v050` was never listed in `py-modules`, so header redaction never ran in any install. Fixed in tiny-secret-mask v0.5.1. **Last verified 2026-10-21.**

## Quick Start

```python
# Standalone (no framework)
from tiny_headers_redact import redact_headers

incoming = {
    "Authorization": "Bearer eyJhbG....",
    "X-API-Key": "sk_live_...",
    "X-Request-Id": "abc-123",
}

redact_headers(incoming)
# {
#     "Authorization": "[REDACTED:authorization]",
#     "X-API-Key": "[REDACTED:x_api_key]",
#     "X-Request-Id": "abc-123",
# }
```

### WSGI middleware

```python
from tiny_headers_redact import header_redactor_middleware, HeaderStats

stats = HeaderStats()

def my_app(environ, start_response):
    # environ['HTTP_AUTHORIZATION'] is already redacted
    ...

app = header_redactor_middleware(my_app, stats=stats)
```

### ASGI middleware

```python
from tiny_headers_redact import header_redactor_asgi_middleware, HeaderStats

stats = HeaderStats()

async def my_app(scope, receive, send):
    # scope['headers'] is already redacted
    ...

app = header_redactor_asgi_middleware(my_app, stats=stats)
```

### FastAPI integration

```python
from fastapi import FastAPI
from tiny_headers_redact import header_redactor_asgi_middleware, HeaderStats

app = FastAPI()
stats = HeaderStats()
app.add_middleware(type("HeaderRedactorMiddleware", (), {
    "__call__": lambda self, scope, receive, send: header_redactor_asgi_middleware(app, stats=stats)(scope, receive, send)
}))
```

## Stats for /metrics

The `HeaderStats` counter is JSON-serializable:

```python
>>> stats = HeaderStats()
# ... 1000 requests pass through, 23 headers got redacted ...
>>> stats.as_dict()
{'headers_seen': 1000, 'redactions': 23, 'last_redacted_header': 'Authorization'}
```

The shape matches `tiny_router_redact_headers.HeaderStats` exactly, so a single `/metrics` endpoint can read both stats and emit a unified redaction-rate panel.

## When to Use / When to Use Something Else

**Use when:**

- You don't use `tiny-router` and want a zero-dep WSGI/ASGI middleware
- You want to wrap a legacy framework (Django, FastAPI, Starlette, raw WSGI/ASGI)
- You want a stable, minimal repo that depends only on `tiny-secret-mask`

**Don't use when:**

- You already use `tiny-router` → use `tiny_router_redact_headers` (already in the router, no extra import)
- You only need the rule catalogue and not the middleware → import `tiny_secret_mask.mask_headers` directly
- You need body redaction (planned v0.6.0 layer) — wait for the next `tiny_secret_mask` cycle

## Repo

https://github.com/hussain-alsaibai/tiny-headers-redact

## See Also

- `tools/tiny-secret-mask-v0.5-guide.md` — the 16-pattern header rule catalogue
- `tools/tiny-router-v0.7.4-guide.md` — `redact_headers_middleware()` if you use `tiny-router`
- `tools/tiny-route-redact-guide.md` — framework-agnostic path middleware (sister repo, same shape)
- `reports/2026-10-15-developer-tools-landscape.md` — full trend report on the five-layer credential-leak loop
