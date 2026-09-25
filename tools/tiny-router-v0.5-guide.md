# tiny-router v0.5.0 — OpenAPI Endpoint + JWT Refresh Pair/Exchange

> Zero-dependency WSGI router. v0.5.0 adds a built-in `/openapi.json` endpoint and a complete JWT refresh-token pair/exchange flow.
> Last verified: 2026-09-25 | Version 0.5.0 | hussain-alsaibai/tiny-router

## What Changed in v0.5.0 (Sep 2026)

- **`openapi_endpoint(router)`** — registers a built-in `GET /openapi.json` route that serves `openapi_spec()` as JSON with `Cache-Control: no-store`. One-line OpenAPI delivery for any `tiny-router` app.
- **`jwt_refresh_pair(access, refresh, *, secret, access_ttl_seconds=900, refresh_ttl_seconds=2_592_000)`** — mint a paired access + refresh JWT. Caller-supplied `iat`/`exp` are overwritten; refresh token carries `typ=refresh` automatically so an attacker can't smuggle eternal access tokens via refresh.
- **`jwt_refresh_exchange(refresh_token, *, secret, audience=None, issuer=None, leeway=0)`** — verify a refresh token, enforce `typ=refresh`, and mint a fresh access token whose claims are the refresh token's claims minus `typ`.
- New test suite `test_tiny_router_v050.py` (15 tests). Combined suite **101/101 passing**.

## Why This Matters

The refresh pair/exchange flow is the standard pattern for short-lived access tokens + long-lived refresh tokens. `tiny-router` now has it built-in without depending on `pyjwt` or `authlib`. Combined with the v0.4.0 `jwt_middleware()`, this means the entire auth surface (verify access, mint pair, exchange refresh, serve OpenAPI) is zero-dep.

## Quick Start

```python
from tiny_router import Router, openapi_endpoint
from tiny_router import jwt_refresh_pair, jwt_refresh_exchange

app = Router()

@app.post("/login")
def login(req):
    # ... verify credentials, build user claims ...
    access, refresh = jwt_refresh_pair(
        access={"sub": user_id, "scope": "read"},
        refresh={"sub": user_id},
        secret=SECRET,
    )
    return {"access_token": access, "refresh_token": refresh}

@app.post("/refresh")
def refresh(req):
    new_access = jwt_refresh_exchange(
        req.body["refresh_token"], secret=SECRET
    )
    return {"access_token": new_access}

openapi_endpoint(app)  # GET /openapi.json now live
```

## When to Use

- Auth flows that need both access + refresh tokens without `pyjwt`
- Tiny-* agent gateways that want OpenAPI discovery
- Single-file Flask-style services that need production auth patterns

## Repo

https://github.com/hussain-alsaibai/tiny-router

## See Also

- `tools/tiny-router-v0.4-guide.md` — v0.4.0 (JWT middleware + request-id + OpenAPI export)
- `tools/tiny-router-guide.md` — base router guide
- `tools/tiny-secret-mask-guide.md` — pair with `mask_response()` for safe error returns
