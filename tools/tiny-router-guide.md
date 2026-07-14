# tiny-router — Stdlib WSGI Routing

## Repo

https://github.com/hussain-alsaibai/tiny-router

## One-liner

Zero-dependency WSGI router for small Python services, agent callbacks, and
stdlib-only HTTP examples.

## When to Use

- You need Flask-like routing without Flask.
- You are building a tiny-* style service or example.
- You need a callback receiver with explicit operational boundaries.
- You want a small WSGI app that is easy to test with stdlib tooling.

## Agent Callback Receiver Pattern

The verified `examples/agent_callback_receiver.py` recipe includes:

- bearer-token authentication,
- request IDs for correlation,
- fixed-window rate limiting,
- TTL idempotency keys,
- JSON body validation,
- structured JSON logs,
- `/health`, `/ready`, and `/status` endpoints,
- focused tests for valid, duplicate, unauthorized, invalid, and throttled
  callback flows.

## Signed Callback Receiver Additions

The July 14 field note extends the callback pattern for providers that sign
requests. Verify the HMAC over the exact raw request body before parsing JSON,
reject timestamps outside a small tolerance, and deduplicate by delivery ID
with a TTL. Keep rejected callbacks deterministic: use 401 for missing or
invalid signatures, 409 for recognized replays, and 422 for structurally
invalid payloads. Pair the receiver with `/health`, `/ready`, and `/status`
endpoints so tunnel, DNS, and provider-retry failures are observable.

See [Signed Callback Receivers With tiny-router](https://github.com/hussain-alsaibai/tiny-router/blob/main/reports/2026-07-14-signed-callback-receivers.md)
for the verified field note.

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

## Operational Checklist

- Validate auth before parsing or acting on the body.
- Require a stable request or event ID for side-effecting callbacks.
- Store idempotency keys with a TTL.
- Return deterministic responses for duplicate delivery.
- Keep health checks free of side effects.
- Test the example as part of CI, not only the core router.

## Tests

- Core router tests: 15/15 passing.
- Callback receiver example tests: 11/11 passing.

## Last verified: 2026-07-14

- Repo: `hussain-alsaibai/tiny-router`
- Commit: `41ddb67` (field note; callback recipe remains at `902691d`)
- Verification: the signed-receiver guidance was recorded after reviewing the
  repo's callback receiver implementation and field report; no code changed in
  this documentation-only commit.
