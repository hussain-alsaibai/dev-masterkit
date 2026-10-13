# tiny-middleware

> Zero-dependency composable middleware chain for Python handlers.

Compose sync or async handler callables with a list of middleware
functions. Each middleware receives the request and a `next` callable;
calling `next()` runs the rest of the chain. A middleware can decide
not to call `next` (e.g. to short-circuit with a cached response, a
fallback, or an auth failure).

## Install

```bash
pip install tiny-middleware
```

## Quick start

```python
from tiny_middleware import Chain, Request, Response, request_id, cors

def auth(req, next):
    if req.header_get("authorization") != "Bearer secret":
        return Response(401, {"error": "unauthorized"})
    return next(req)

def hello(req):
    return Response.json(200, {"hello": "world"})

chain = Chain([request_id(), cors(), auth], handler=hello)

resp = chain(Request("GET", "/", headers={"authorization": "Bearer secret"}))
assert resp.status == 200
```

## Sync and async

The chain auto-detects whether a middleware or handler is async and
switches the whole chain to async if any callable is async. Mixing
sync middleware into an async chain is supported but discouraged —
the sync middleware runs in an executor and the rest of the chain
runs around it, which is rarely what you want. Keep chains
all-sync or all-async.

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
resp = asyncio.run(chain(Request(headers={"authorization": "Bearer t"})))
```

## Built-in middleware

- `request_id(header="x-request-id")` — assign / echo a request id.
- `cors(origins=("*",), methods="GET, POST, ...")` — CORS headers +
  short-circuit on `OPTIONS` preflight.

## Short-circuit

A middleware that does not call `next` wins immediately. Useful for:

- Caching (`if cache.has(req.path): return cached_response`)
- Auth (`if not authorized: return 401`)
- Rate-limit rejection (`return 429`)
- CORS preflight (return 204 directly)

## Order matters

The middleware list is outer-to-inner. `[auth, logging, rate_limit]`
runs `auth` first, then `logging`, then `rate_limit`, then the handler.
`auth` is the *outermost*; an unauthorized request never reaches
`logging` or `rate_limit`.

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

## License

MIT
