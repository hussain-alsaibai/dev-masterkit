# tiny-route-redact v0.1.0 — Framework-Agnostic Path Redaction Middleware

> New repo. Framework-agnostic middleware that redacts credentials from route paths so logs, error reports, and observability spans never leak them. Single file, ~224 LOC, MIT, zero runtime dependencies.
> Last verified: 2026-10-14 | Version 0.1.0 | hussain-alsaibai/tiny-route-redact

## Why It Exists

Most request paths are safe. Some are not:

```
GET /v1/users/550e8400-e29b-41d4-a716-446655440000/tokens/ghp_xx...xxxx
```

A path like that can carry a session UUID and a leaked token by accident. SOUL.md mandates "Private things stay private. Period." so we redact by default at the middleware layer.

`tiny-route-redact` is the smallest reliable way to keep credential-shaped path components (UUIDs, hex strings, base64url fragments, JWT fragments, AWS keys, GitHub PATs, Stripe keys, OpenAI keys, Google API keys) out of every log line and trace span that touches a request path — **without** pulling in a router. If you use `tiny-router`, see `tools/tiny-router-v0.7.3-guide.md` instead; if you use anything else (Django, FastAPI, Flask, aiohttp, bare WSGI/ASGI), this is the reference.

## Install

```bash
pip install tiny-route-redact
# also requires tiny-secret-mask >= 0.4.0 (auto-installed)
```

## Quick Start

```python
from tiny_route_redact import route_redactor_middleware, RedactionStats

stats = RedactionStats()
app = route_redactor_middleware(my_app, stats=stats)
# Every request now has its path scrubbed before my_app sees it.
```

Standalone function:

```python
from tiny_route_redact import redact_path

>>> redact_path("/users/550e8400-e29b-41d4-a716-446655440000/profile")
'/users/[REDACTED:uuid]/profile'
>>> redact_path("/keys/AKIAIOSFODNN7EXAMPLE/active")
'/keys/[REDACTED:aws_access_key]/active'
```

## API

### `redact_path(path: str) -> str`

Returns the redacted path string. If `tiny-secret-mask >= 0.4.0` is not installed, the path is returned unchanged.

### `route_redactor_middleware(get_response, *, stats=None, on_redact=None)`

WSGI-style middleware that rewrites request paths before the wrapped app sees them. Works with dict-style requests (`request["path"]`) and object-style requests (`request.path`).

- `stats: RedactionStats | None` — optional counter object.
- `on_redact: Callable[[str, str], None] | None` — optional callback invoked as `on_redact(original, redacted)` for every path that changed.

### `route_redactor_asgi_middleware(app, *, stats=None)`

ASGI-style middleware that rewrites the `path` scope key. Returns a coroutine callable with the same signature as the wrapped app.

### `RedactionStats`

Lightweight counter object. Fields: `redactions: int`, `paths_seen: int`, `last_redacted_path: str | None`. `as_dict()` returns a JSON-serializable snapshot for `/metrics` endpoints.

## What Gets Redacted

`tiny-route-redact` delegates the rule set to `tiny-secret-mask` v0.4.0+. The default catalogue covers:

| Rule | Severity | Example |
|------|----------|---------|
| `uuid` | low | `550e8400-e29b-41d4-a716-446655440000` |
| `hex_32` / `hex_64` | low / medium | `deadbeef...` / `0123...cdef` |
| `base64url_24` | low | long base64url fragments |
| `jwt_header` / `jwt_payload` | high | `eyJhbGciOiJIUzI1NiJ9` / `eyJzdWIiOiIxMjM0In0` |
| `aws_access_key` / `aws_secret_key` | critical | `AKIAIOSFODNN7EXAMPLE` / 40-char base64 |
| `github_pat` | critical | `ghp_xxx...xxx` |
| `stripe_live` | critical | `sk_live_xxx...xxx` |
| `openai_key` | critical | `sk-xxx...xxx` |
| `google_api_key` | critical | `AIzaSyAxxx...xxx` |

Custom rules via the underlying `tiny_secret_mask.RoutePathRedactor` constructor.

## When to Use / When to Use Something Else

**Use when:**

- You don't use `tiny-router` (Django, FastAPI, Flask, aiohttp, bare WSGI/ASGI)
- You want a single import that gives you WSGI + ASGI middlewares + a stats counter
- You need framework-agnostic redaction for a polyglot stack

**Don't use when:**

- You use `tiny-router` → `tiny_router_redact_path.redact_path_middleware()` is the family-native choice and is 1 import lighter
- You only need the standalone function → `from tiny_secret_mask import mask_route_path` (no extra package)
- You need to redact the response body too → pair with `tiny_secret_mask.mask_response()`

## Repo

https://github.com/hussain-alsaibai/tiny-route-redact

## See Also

- `tools/tiny-secret-mask-v0.4-guide.md` — the rule catalogue
- `tools/tiny-router-v0.7.3-guide.md` — the `tiny-router`-native alternative
