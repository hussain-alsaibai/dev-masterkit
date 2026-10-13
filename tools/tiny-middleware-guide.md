# tiny-middleware Guide

> Zero-dependency composable middleware chain for Python handlers. ~245 LOC, 23 tests, stdlib-only.

**Repo:** github.com/hussain-alsaibai/tiny-middleware
**Version:** 0.1.0 (2026-10-13)
**Author:** OpenClaw (autonomous cron, developer-tool-reports context)
**Status:** ✅ Initial release — 23/23 tests passing; auto-detects sync/async per callable; pairs with `tiny-router`.

---

## What is it?

`tiny-middleware` is a single-file Python library (~245 LOC) that composes sync or async handler callables with a list of middleware functions. Each middleware receives the request and a `next` callable; calling `next()` runs the rest of the chain. A middleware can decide not to call `next` (short-circuit).

```python
from tiny_middleware import Chain, Request, Response, request_id, cors

def auth(req, next):
    if req.header_get("authorization") != "Bearer secret":
        return Response(401, {"error": "unauthorized"})
    return next(req)

def hello(req):
    return Response.json(200, {"hello": "world"})

chain = Chain([request_id(), cors(), auth], handler=hello)

resp = chain(Request("GET", "/", headers={"authorization": "Bearer ***"}))
assert resp.status == 200
```

## Why does it exist?

Middleware chains are not new. What is new is the **auto-detection**: most Python middleware libraries force you to choose sync-only or async-only up front, and the rest of the library follows that choice. `tiny-middleware` lets each callable declare its own mode — a sync `auth` middleware and an async `db_query` handler can coexist as long as the chain is all-async (the async path wins).

## Sync and async

The chain auto-detects whether a middleware or handler is async and switches the whole chain to async if any callable is async. Mixing sync middleware into an async chain is supported but discouraged — the sync middleware runs in an executor and the rest of the chain runs around it, which is rarely what you want. Keep chains all-sync or all-async.

```python
import asyncio
from tiny_middleware import Chain, Request, Response

async def auth(req, next):
    if req.header_get("authorization") != "Bearer t":
        return Response(401)
    return await next(req)

async def hello(req):
    return Response.json(200, {"hello": "async"})

chain = Chain([auth], handler=hello)
resp = asyncio.run(chain(Request(headers={"authorization": "Bearer ***"})))
```

## Built-in middleware

- `request_id(header="x-request-id")` — assign or echo a request id. Echoes the inbound header if present; otherwise generates a new UUID. The id is stored on `req.ctx`.
- `cors(origins=("*",), methods="GET, POST, ...", headers="Content-Type, Authorization, X-Request-ID")` — CORS headers on every response + short-circuit on `OPTIONS` preflight.

## Short-circuit

A middleware that does not call `next` wins immediately. Useful for:

- **Caching:** `if cache.has(req.path): return cached_response`
- **Auth:** `if not authorized: return 401`
- **Rate-limit rejection:** `return 429`
- **CORS preflight:** return 204 directly

```python
def rate_limit(req, next):
    if ip_is_hot(req):
        return Response(429, {"error": "slow down"})
    return next(req)
```

## Order matters

The middleware list is outer-to-inner. `[auth, logging, rate_limit]` runs `auth` first, then `logging`, then `rate_limit`, then the handler. `auth` is the *outermost*; an unauthorized request never reaches `logging` or `rate_limit`.

## Composition with `tiny-router`

```python
from tiny_router import Router
from tiny_middleware import Chain, Request, Response, request_id, cors

router = Router()

@router.get("/hello")
def hello(req):
    return Response.json(200, {"hello": "world"})

def dispatch(req):
    return router.dispatch(req.method, req.path, req)

app = Chain([request_id(), cors()], handler=dispatch)
```

## API

### `Request(method, path, *, headers=None, query=None, body=None, ctx=None)`

- `method` — HTTP method (string).
- `path` — URL path (string).
- `headers` — dict of header name → value.
- `query` — dict of query-string params.
- `body` — request body (any).
- `ctx` — per-request scratch space (a dict).

Helper: `req.header_get(name, default=None)`.

### `Response(status, body, *, headers=None)`

- `status` — HTTP status code (int).
- `body` — response body (any).
- `headers` — dict of header name → value.

Helpers: `Response.json(status, payload)` and `Response.text(status, text)`.

### `Chain(middleware, *, handler)`

- `middleware` — list of middleware callables.
- `handler` — the terminal callable.

Methods:

- `use(mw)` — append a middleware.
- `__call__(req)` — run the chain synchronously.
- `__call__(req)` from async context — run asynchronously if any middleware is async.

## When to use it

✅ Use `tiny-middleware` when:

- You have a small web framework or routing layer and want Koa/Express-style composition.
- You want sync and async callables to coexist in the same chain.
- You want a single in-process chain with no external service.

❌ Don't use it when:

- You need a full ASGI/WSGI server (this is a composition primitive, not a server).
- You need middleware ordering based on request attributes (the list is static; use a router for per-route middleware).
- You need streaming responses (the chain returns a single `Response`).

## License

MIT. Single file, zero dependencies.

**Last verified:** 2026-10-13
