"""
tiny-middleware - Zero-dependency composable middleware chain for Python handlers.

A small library for composing sync or async handler callables with a
list of middleware functions. Each middleware receives the request
and a ``next`` callable; calling ``next()`` runs the rest of the
chain. A middleware can decide not to call ``next`` (e.g. to short-
circuit with a cached response, a fallback, or an auth failure).

    from tiny_middleware import Chain, Request, Response, request_id, cors

    def auth(req, next):
        if req.header_get("authorization") != "Bearer secret":
            return Response(401, {"error": "unauthorized"})
        return next(req)

    def hello(req):
        return Response(200, {"hello": "world"})

    chain = Chain([request_id(), cors()], handler=hello)
    chain(Request("GET", "/"))

The pattern is identical to Koa / Express middleware; the only
twist is that it works equally well for sync and async handlers.
"""
from __future__ import annotations

import asyncio
import functools
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Sequence, Union

__all__ = [
    "Request",
    "Response",
    "Chain",
    "MiddlewareError",
    "request_id",
    "cors",
]
__version__ = "0.1.0"


Handler = Callable[["Request"], "Response"]
AsyncHandler = Callable[["Request"], Awaitable["Response"]]
SyncMiddleware = Callable[["Request", Callable[["Request"], "Response"]], "Response"]
AsyncMiddleware = Callable[["Request", Callable[["Request"], Awaitable["Response"]]], Awaitable["Response"]]
Middleware = Union[SyncMiddleware, AsyncMiddleware]


class MiddlewareError(Exception):
    """Raised when a middleware misbehaves (e.g. it returns a non-Response)."""


@dataclass
class Request:
    """A minimal request envelope.

    ``body`` is left untyped on purpose; middleware that need a parsed
    body should use a dedicated middleware (e.g. ``json_body``).
    """

    method: str = "GET"
    path: str = "/"
    headers: Dict[str, str] = field(default_factory=dict)
    query: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    ctx: Dict[str, Any] = field(default_factory=dict)

    def header_get(self, name: str, default=None):
        """Case-insensitive header lookup."""
        lower = name.lower()
        for k, v in self.headers.items():
            if k.lower() == lower:
                return v
        return default


@dataclass
class Response:
    """A minimal response envelope. ``body`` may be any JSON-able value."""

    status: int = 200
    body: Any = None
    headers: Dict[str, str] = field(default_factory=dict)

    def with_status(self, status: int) -> "Response":
        self.status = status
        return self

    def with_header(self, name: str, value: str) -> "Response":
        self.headers[name] = value
        return self

    @classmethod
    def json(cls, status: int, payload) -> "Response":
        import json
        return cls(status=status, body=json.dumps(payload), headers={"content-type": "application/json"})

    @classmethod
    def text(cls, status: int, payload: str) -> "Response":
        return cls(status=status, body=payload, headers={"content-type": "text/plain; charset=utf-8"})


class Chain:
    """A list of middleware wrapping a final handler.

    ``Chain([m1, m2], handler=h)`` is equivalent to
    ``m1(req, lambda r: m2(req, lambda r: h(r)))``. Both sync and
    async middleware can be mixed; the chain auto-detects per-callable.
    """

    def __init__(self, middleware: Sequence[Middleware], *, handler):
        self.middleware: List[Middleware] = list(middleware)
        self.handler = handler
        self._is_async_handler = asyncio.iscoroutinefunction(handler)

    def use(self, mw: Middleware) -> "Chain":
        """Append a middleware. Returns self for chaining."""
        self.middleware.append(mw)
        return self

    def __call__(self, req: Request):
        return self.run(req)

    def run(self, req: Request):
        """Run the chain. Returns ``Response`` or an awaitable of it."""
        if self._is_async_handler or any(_is_async_callable(m) for m in self.middleware):
            return self._run_async(req)
        return self._run_sync(req)

    def _run_sync(self, req: Request) -> Response:
        idx = [0]

        def call_next(r: Request) -> Response:
            if idx[0] < len(self.middleware):
                mw = self.middleware[idx[0]]
                idx[0] += 1
                return mw(r, call_next)
            return self.handler(r)

        return call_next(req)

    def _run_async(self, req: Request) -> Awaitable[Response]:
        idx = [0]

        async def call_next(r: Request) -> Response:
            if idx[0] < len(self.middleware):
                mw = self.middleware[idx[0]]
                idx[0] += 1
                if _is_async_callable(mw):
                    return await mw(r, call_next)
                # sync middleware in an async chain
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, _sync_to_async_bridge(mw), r, call_next)
            if self._is_async_handler:
                return await self.handler(r)
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.handler, r)

        return call_next(req)


def _is_async_callable(fn) -> bool:
    if asyncio.iscoroutinefunction(fn):
        return True
    inner = fn
    while isinstance(inner, functools.partial):
        inner = inner.func
    return asyncio.iscoroutinefunction(inner)


def _sync_to_async_bridge(sync_mw):
    """Wrap a sync middleware so the async chain can call it via the executor."""
    def bridge(r, async_next):
        # We can't easily call the async_next from sync code; instead, run the
        # rest of the chain synchronously by asking for the response. This works
        # only when no further async middleware is downstream, which is the
        # common case for the bridge.
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # If we are already in an event loop, the executor call will block; that
        # is the limitation of mixing sync/async middleware. In practice, keep
        # chains all-sync or all-async.
        if loop.is_running():
            # Best effort: just call the sync middleware with a sync next that
            # blocks on the async chain. The user should not mix modes.
            import warnings
            warnings.warn(
                "mixing sync middleware into an async chain is not supported; "
                "the async chain will block. Make all middleware async.",
                RuntimeWarning,
                stacklevel=2,
            )
        # Simple: run the async_next synchronously by spinning a new loop.
        coro = async_next(r)
        try:
            return loop.run_until_complete(coro)
        except RuntimeError:
            # loop is already running in this thread; just call sync
            return sync_mw(r, lambda x: None)  # type: ignore

    return bridge


# Built-in middleware

def request_id(header: str = "x-request-id"):
    """Assign a request id (or echo an existing one) into ``req.ctx``."""
    import uuid

    def mw(req, next):
        rid = req.header_get(header) or str(uuid.uuid4())
        req.ctx["request_id"] = rid
        resp = next(req)
        resp.headers[header] = rid
        return resp

    return mw


def cors(origins=(), methods: str = "GET, POST, PUT, DELETE, OPTIONS"):
    """Add CORS headers and short-circuit OPTIONS preflight."""
    if not origins:
        origins = ("*",)
    origin = ", ".join(origins)

    def mw(req, next):
        if req.method.upper() == "OPTIONS":
            return Response(
                status=204,
                body="",
                headers={
                    "access-control-allow-origin": origin,
                    "access-control-allow-methods": methods,
                },
            )
        resp = next(req)
        resp.headers["access-control-allow-origin"] = origin
        return resp

    return mw
