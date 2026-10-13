"""Tests for tiny_middleware. Run with pytest or ``python test_tiny_middleware.py``."""
from __future__ import annotations

import asyncio
import unittest

from tiny_middleware import Chain, Request, Response, request_id, cors


class TestRequest(unittest.TestCase):
    def test_default_construction(self):
        req = Request()
        self.assertEqual(req.method, "GET")
        self.assertEqual(req.path, "/")
        self.assertEqual(req.headers, {})
        self.assertEqual(req.ctx, {})

    def test_header_get_case_insensitive(self):
        req = Request(headers={"X-Foo": "bar", "AUTHORIZATION": "Bearer t"})
        self.assertEqual(req.header_get("x-foo"), "bar")
        self.assertEqual(req.header_get("Authorization"), "Bearer t")
        self.assertIsNone(req.header_get("missing"))
        self.assertEqual(req.header_get("missing", "x"), "x")


class TestResponse(unittest.TestCase):
    def test_default(self):
        r = Response()
        self.assertEqual(r.status, 200)
        self.assertIsNone(r.body)

    def test_with_status_returns_self(self):
        r = Response()
        self.assertIs(r.with_status(404), r)
        self.assertEqual(r.status, 404)

    def test_with_header_returns_self(self):
        r = Response()
        self.assertIs(r.with_header("x", "y"), r)
        self.assertEqual(r.headers["x"], "y")

    def test_json(self):
        r = Response.json(200, {"hello": "world"})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, '{"hello": "world"}')
        self.assertEqual(r.headers["content-type"], "application/json")

    def test_text(self):
        r = Response.text(404, "not found")
        self.assertEqual(r.status, 404)
        self.assertEqual(r.body, "not found")
        self.assertEqual(r.headers["content-type"], "text/plain; charset=utf-8")


class TestChainSync(unittest.TestCase):
    def test_passthrough(self):
        def hello(req):
            return Response(200, {"hello": "world"})
        chain = Chain([], handler=hello)
        r = chain(Request("GET", "/"))
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, {"hello": "world"})

    def test_single_middleware(self):
        def add_header(req, next):
            resp = next(req)
            resp.headers["x-trace"] = "abc"
            return resp
        def hello(req):
            return Response(200, "ok")
        chain = Chain([add_header], handler=hello)
        r = chain(Request())
        self.assertEqual(r.status, 200)
        self.assertEqual(r.headers["x-trace"], "abc")

    def test_chain_order(self):
        order = []
        def outer(req, next):
            order.append("outer-before")
            resp = next(req)
            order.append("outer-after")
            return resp
        def middle(req, next):
            order.append("middle-before")
            resp = next(req)
            order.append("middle-after")
            return resp
        def handler(req):
            order.append("handler")
            return Response(200, "ok")
        chain = Chain([outer, middle], handler=handler)
        chain(Request())
        self.assertEqual(order, ["outer-before", "middle-before", "handler", "middle-after", "outer-after"])

    def test_short_circuit(self):
        def gate(req, next):
            if req.header_get("authorization") != "Bearer secret":
                return Response(401, {"error": "unauthorized"})
            return next(req)
        def hello(req):
            return Response(200, "secret")
        chain = Chain([gate], handler=hello)
        r = chain(Request())
        self.assertEqual(r.status, 401)
        r = chain(Request(headers={"authorization": "Bearer secret"}))
        self.assertEqual(r.status, 200)

    def test_short_circuit_with_response_mutation(self):
        def cache(req, next):
            if req.path == "/cached":
                return Response(200, {"from": "cache"})
            return next(req)
        def hello(req):
            return Response(200, {"from": "handler"})
        chain = Chain([cache], handler=hello)
        self.assertEqual(chain(Request("GET", "/cached")).body, {"from": "cache"})
        self.assertEqual(chain(Request("GET", "/fresh")).body, {"from": "handler"})

    def test_use_appends(self):
        def a(req, next):
            resp = next(req)
            resp.headers["a"] = "1"
            return resp
        def b(req, next):
            resp = next(req)
            resp.headers["b"] = "1"
            return resp
        def h(req):
            return Response(200, "ok")
        chain = Chain([], handler=h).use(a).use(b)
        r = chain(Request())
        self.assertEqual(r.headers["a"], "1")
        self.assertEqual(r.headers["b"], "1")

    def test_no_next_called_uses_first_response(self):
        def short_circuit(req, next):
            return Response(204)  # never calls next
        def handler(req):
            return Response(200, "unreachable")
        chain = Chain([short_circuit], handler=handler)
        r = chain(Request())
        self.assertEqual(r.status, 204)


class TestChainAsync(unittest.TestCase):
    def test_async_handler(self):
        async def hello(req):
            return Response(200, {"hello": "async"})
        chain = Chain([], handler=hello)
        result = chain(Request())
        # run returns awaitable when handler is async
        self.assertTrue(asyncio.iscoroutine(result))
        r = asyncio.run(result)
        self.assertEqual(r.status, 200)
        self.assertEqual(r.body, {"hello": "async"})

    def test_async_middleware_with_async_handler(self):
        async def auth(req, next):
            if req.header_get("authorization") != "Bearer t":
                return Response(401, {"error": "no"})
            return await next(req)
        async def hello(req):
            return Response(200, "ok")
        chain = Chain([auth], handler=hello)
        r1 = asyncio.run(chain(Request()))
        self.assertEqual(r1.status, 401)
        r2 = asyncio.run(chain(Request(headers={"authorization": "Bearer t"})))
        self.assertEqual(r2.status, 200)

    def test_async_middleware_chain_order(self):
        order = []
        async def outer(req, next):
            order.append("o-before")
            r = await next(req)
            order.append("o-after")
            return r
        async def middle(req, next):
            order.append("m-before")
            r = await next(req)
            order.append("m-after")
            return r
        async def h(req):
            order.append("h")
            return Response(200, "ok")
        chain = Chain([outer, middle], handler=h)
        asyncio.run(chain(Request()))
        self.assertEqual(order, ["o-before", "m-before", "h", "m-after", "o-after"])


class TestBuiltins(unittest.TestCase):
    def test_request_id_generates(self):
        chain = Chain([request_id()], handler=lambda r: Response(200))
        req = Request()
        r = chain(req)
        self.assertIn("request_id", req.ctx)
        self.assertIn("x-request-id", r.headers)
        self.assertEqual(req.ctx["request_id"], r.headers["x-request-id"])

    def test_request_id_echoes(self):
        chain = Chain([request_id()], handler=lambda r: Response(200))
        req = Request(headers={"x-request-id": "abc-123"})
        r = chain(req)
        self.assertEqual(req.ctx["request_id"], "abc-123")
        self.assertEqual(r.headers["x-request-id"], "abc-123")

    def test_cors_preflight(self):
        chain = Chain([cors()], handler=lambda r: Response(200, "x"))
        r = chain(Request("OPTIONS", "/"))
        self.assertEqual(r.status, 204)
        self.assertEqual(r.headers["access-control-allow-origin"], "*")
        self.assertIn("OPTIONS", r.headers["access-control-allow-methods"])

    def test_cors_adds_header_to_normal_response(self):
        chain = Chain([cors(origins=["https://x.com"])], handler=lambda r: Response(200, "x"))
        r = chain(Request("GET", "/"))
        self.assertEqual(r.status, 200)
        self.assertEqual(r.headers["access-control-allow-origin"], "https://x.com")


class TestIntegration(unittest.TestCase):
    def test_typical_web_stack(self):
        # Realistic stack: request_id -> cors -> auth -> handler
        def auth(req, next):
            if req.header_get("authorization") != "Bearer secret":
                return Response(401, {"error": "unauthorized"})
            return next(req)
        def handler(req):
            return Response.json(200, {"user": "alice", "request_id": req.ctx["request_id"]})
        chain = Chain([request_id(), cors(), auth], handler=handler)

        # Unauthorized
        r1 = chain(Request("GET", "/api/me"))
        self.assertEqual(r1.status, 401)
        self.assertIn("x-request-id", r1.headers)
        self.assertIn("access-control-allow-origin", r1.headers)

        # Authorized
        r2 = chain(Request("GET", "/api/me", headers={"authorization": "Bearer secret"}))
        self.assertEqual(r2.status, 200)
        import json
        body = json.loads(r2.body)
        self.assertEqual(body["user"], "alice")
        # request_id is freshly generated per request; just make sure it
        # is a non-empty string echoed back to the response
        self.assertTrue(body["request_id"])
        self.assertEqual(r2.headers["x-request-id"], body["request_id"])

    def test_preflight_short_circuits_before_auth(self):
        def auth(req, next):
            return Response(401)  # would block everything
        def handler(req):
            return Response(200, "never")
        chain = Chain([cors(), auth], handler=handler)
        r = chain(Request("OPTIONS", "/"))
        # CORS preflight short-circuits with 204, auth never runs
        self.assertEqual(r.status, 204)


if __name__ == "__main__":
    unittest.main()
