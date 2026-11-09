# tiny-route-redact v0.2.0 — Framework-Agnostic Path Redaction That Fails Closed

> Framework-agnostic middleware that redacts credentials from route paths so logs, error reports, and observability spans never leak them. Single file, MIT.
> Last verified: 2026-11-09 | Version 0.2.0 | hussain-alsaibai/tiny-route-redact
> Verified by: fresh `--depth 1` clone of `main`; `pytest -q` -> **23 passed**; sealed-import
> negative control (see [Failure behaviour](#failure-behaviour)).

## Why It Exists

Most request paths are safe. Some are not:

```
GET /v1/users/550e8400-e29b-41d4-a716-446655440000/tokens/ghp_xx...xxxx
```

A path like that can carry a session UUID and a leaked token by accident. SOUL.md mandates "Private things stay private. Period." so we redact by default at the middleware layer.

`tiny-route-redact` is the smallest reliable way to keep credential-shaped path components (UUIDs, hex strings, base64url fragments, JWT fragments, AWS keys, GitHub PATs, Stripe keys, OpenAI keys, Google API keys) out of every log line and trace span that touches a request path — **without** pulling in a router. If you use `tiny-router`, see `tools/tiny-router-v0.7.3-guide.md` instead; if you use anything else (Django, FastAPI, Flask, aiohttp, bare WSGI/ASGI), this is the reference.

## Install

```bash
pip install tiny-secret-mask>=0.4.0
# tiny-route-redact itself is NOT on PyPI - see below
```

> **Not published to PyPI (verified 2026-11-09).** `https://pypi.org/pypi/tiny-route-redact/json`
> returns **HTTP 404**, and there are **0 GitHub releases**. The **GitHub repository does
> exist** (created 2026-11-09T06:49:34Z, MIT, `main`) — the 2026-11-03 note in this guide
> claiming "there is no GitHub repository under this name" was wrong and is corrected here.
> Install from source until a release exists:
>
> ```bash
> pip install git+https://github.com/hussain-alsaibai/tiny-route-redact.git
> ```

`tiny-secret-mask>=0.4.0` is also **404 on PyPI** as of 2026-11-09. In practice both come
from source, and the dependency must be importable — that is the whole point of 0.2.0.

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

Both lines above were executed against 0.2.0 on 2026-11-09, not transcribed.

## API

### `redact_path(path: str) -> str`

Returns the redacted path string. **Requires `tiny-secret-mask >= 0.4.0`** (for
`mask_route_path`). Raises `RedactionUnavailable` when it is missing — it does **not**
return the input unchanged.

### `redact_path_passthrough(path: str) -> str`

New in 0.2.0. An explicitly named no-op returning `path`. "Do not redact here" becomes a
visible decision in review instead of an accident of packaging.

### `route_redactor_middleware(get_response, *, stats=None, on_redact=None)`

WSGI-style middleware that rewrites request paths before the wrapped app sees them. Works with dict-style requests (`request["path"]`) and object-style requests (`request.path`).

- `stats: RedactionStats | None` — optional counter object.
- `on_redact: Callable[[str, str], None] | None` — optional callback invoked as `on_redact(original, redacted)` for every path that changed.

Building it raises `RedactionUnavailable` when redaction is unavailable — **at
construction, not on first request**. A middleware that refuses only under traffic passes
every startup probe and then serves unredacted paths in production.

### `route_redactor_asgi_middleware(app, *, stats=None)`

ASGI-style middleware that rewrites the `path` scope key. Returns a coroutine callable with the same signature as the wrapped app. Fails closed at construction, same as the WSGI form.

### `RedactionUnavailable`

Exported exception type (new in 0.2.0). Its message names both the install command and the
passthrough opt-out.

### `RedactionStats`

Lightweight counter object. Fields: `redactions: int`, `paths_seen: int`, `last_redacted_path: str | None`. `as_dict()` returns a JSON-serializable snapshot for `/metrics` endpoints.

## Failure behaviour

The 0.1.0 -> 0.2.0 change is breaking on purpose. 0.1.0 returned the path untouched when
`tiny_secret_mask` was missing, so a deployment logged full credentials while every call
site looked correct. Its docstring claimed "a warning is emitted once"; no warning was ever
emitted.

Proven 2026-11-09 with a **sealed import** — a `sys.meta_path` finder that raises
`ImportError` for anything named `tiny_secret_mask*`, before importing the module:

| call | result |
|---|---|
| `redact_path("/x")` | raises `RedactionUnavailable` |
| `redact_path_passthrough("/x")` | returns `/x` |
| `route_redactor_middleware(fn)` | raises `RedactionUnavailable` |
| `route_redactor_asgi_middleware(fn)` | raises `RedactionUnavailable` |

**How to run this control wrong, and how it lied to us.** The obvious version imports the
module first and monkeypatches `builtins.__import__` afterwards. It reports *"FAIL OPEN"* —
falsely. `_MASK = _resolve_mask()` is bound at **module import time**, so the patch happens
after the only resolution that matters. Sealing the import *before* the module loads is the
only version that tests what ships. **A negative control must control the moment the value
is bound, not the moment it is used.**

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

## Tests and CI

- **23 tests**, all passing on a fresh clone of `main` (2026-11-09).
- CHANGELOG records **5 tests for the failure modes, 4 of which fail against 0.1.0** — the
  fail-closed behaviour is load-bearing, not decorative.
- CI matrix **3.8-3.13** plus a job that proves redaction fails closed. First run was red on
  all six rows for a reason unrelated to the code: `python -m pytest` with pytest never
  installed. Fixed in `6b58e1f`; latest `main` run is green.

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
- `prompts/a-guard-that-fails-open-passes-every-happy-path-test.md` — the general rule this release enforces
