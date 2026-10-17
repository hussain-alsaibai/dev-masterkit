# tiny-cors v0.1.0 — RFC 9110 / Fetch CORS Middleware

**Last verified:** 2026-10-17
**Repo:** https://github.com/hussain-alsaibai/tiny-cors
**License:** MIT • **Deps:** zero (stdlib only) • **LOC:** 425 (lib) + ~600 (tests) • **Tests:** 23/23

## What it solves

CORS is a small spec with a long tail of ways to get it wrong. The two failure modes that ship to production over and over:

1. `Access-Control-Allow-Origin: *` together with `Access-Control-Allow-Credentials: true` — the spec explicitly forbids this, and browsers reject the response.
2. Missing `Vary: Origin` on cached responses — causes the wrong response (origin A’s headers) to be served to origin B.

`tiny-cors` handles both correctly, plus the boring 90% (preflight caching, method/header/expose-header allow lists, max-age) in ~425 lines of stdlib-only Python.

## Public API

- `CorsConfig` — configuration dataclass
  - `allow_origins: set[str]` — exact origins, or `{"*"}` for any
  - `allow_origin_regex: Optional[str]` — e.g. `r"^https://[a-z]+\.example\.com$"` for subdomain matching
  - `allow_methods: set[str]` — default `{"GET", "POST", "OPTIONS"}`
  - `allow_headers: set[str]` — default empty
  - `expose_headers: set[str]` — default empty
  - `allow_credentials: bool` — default `False`
  - `max_age: int` — preflight cache TTL, seconds (default 600, max from spec is 86400)
  - `vary_origin: bool` — default `True`
  - `preflight_cache_size: int` — default 1024 entries
- `CorsMiddleware` — WSGI middleware wrapper
- `cors_middleware(app, config)` / `make_cors_middleware(app, config)` — factories
- `ASGI_CorsMiddleware` — ASGI middleware wrapper
- `tiny_router_middleware(config)` — returns a `tiny-router`-compatible middleware function
- `PreflightCache` — internal preflight cache with TTL

## Quick start (WSGI)

    from tiny_cors import cors_middleware, CorsConfig

    config = CorsConfig(
        allow_origins={"https://example.com", "https://app.example.com"},
        allow_methods={"GET", "POST", "OPTIONS", "PUT", "DELETE"},
        allow_headers={"Content-Type", "Authorization"},
        expose_headers={"X-Request-Id"},
        max_age=3600,
        allow_credentials=True,
    )

    app = cors_middleware(my_wsgi_app, config)

## Quick start (ASGI / FastAPI)

    from tiny_cors import ASGI_CorsMiddleware, CorsConfig

    config = CorsConfig(allow_origins={"https://app.example.com"}, allow_credentials=True)
    app = ASGI_CorsMiddleware(my_asgi_app, config)

    # Or with FastAPI/Starlette:
    from fastapi import FastAPI
    fastapi_app = FastAPI()
    wrapped = ASGI_CorsMiddleware(fastapi_app, config)

## Quick start (tiny-router)

    from tiny_router import TinyRouter
    from tiny_cors import tiny_router_middleware, CorsConfig

    router = TinyRouter()
    config = CorsConfig(allow_origins={"*"})

    # Global (applies to every route)
    router.use(tiny_router_middleware(config))

    # Per-route
    router.route("/api", handler).middleware(tiny_router_middleware(config))

## The wildcard+credentials trap (and how tiny-cors handles it)

RFC 9110 §3.2.2 forbids `Access-Control-Allow-Origin: *` together with `Access-Control-Allow-Credentials: true`. Browsers reject the response. The library auto-handles this: when `allow_credentials=True` and the request origin matches, the response sends the **specific** origin instead of `*`.

    # This is what the library does under the hood:
    if config.allow_credentials and matched_origin and matched_origin != "*":
        response.headers["Access-Control-Allow-Origin"] = matched_origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"  # only safe when no credentials

If you set `allow_origins={"*"}` AND `allow_credentials=True` you are asking for an impossible response; the library will fail loudly rather than silently produce a broken response.

## Vary: Origin (so caches do the right thing)

When `vary_origin=True` (the default), every response gets `Vary: Origin` so a downstream cache knows the response varies by the request’s `Origin` header. Without this, a single cached response can be served to the wrong origin.

## Preflight caching

The library caches preflight (OPTIONS) responses per `(origin, path)` tuple, respecting `Access-Control-Max-Age`. Default cache holds 1024 entries with TTL eviction. Cache invalidation is time-based; you can flush it via `app.cors.preflight_cache.clear()` (where `app` is the `CorsMiddleware` instance) if you need to force a refresh.

## When to use

- Any WSGI/ASGI service that is consumed by a browser from a different origin
- Multi-tenant apps where each tenant has its own subdomain (`allow_origin_regex`)
- Services behind a gateway that needs the preflight cache to reduce origin OPTIONS traffic

## When NOT to use

- Server-to-server RPC where the browser is not involved — CORS is a browser-only concern
- A public read-only API served from the same origin as the page (no CORS needed)
- You need CSP, HSTS, COEP/COOP, or other security headers — CORS is orthogonal; layer separately

## Test highlights (23/23)

Wildcard vs exact origin, wildcard+credentials rejection, regex subdomain matching, Vary: Origin on every response, preflight cache hit + TTL expiry, max-age cap at spec maximum, all 6 CORS response headers, ASGI+WSGI parity, tiny-router integration helper, `CorsConfig` immutability, `expose_headers` reflected on actual responses.
