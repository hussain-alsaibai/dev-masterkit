# A test that constructs the response cannot validate it

**Discovered:** 2026-11-18, across four independent Python HTTP servers in one ecosystem
(`tiny-router`, `tiny-metrics`, `tiny-webhook`, `tiny-agent-service`)
**Last verified:** 2026-11-18 — each defect was reproduced over a raw TCP socket before
the fix; the fix's test file was then executed in this session:
`test_v092_wire_bodyless.py` **7 passed** (`repos/tiny-router`), `tiny-metrics` **36
passed**, `test_tiny_webhook.py` **27 passed / 4 skipped**, `tiny-agent-service` **21
passed / 2 skipped**. Each fix's new tests were observed failing on the pre-fix file
(3/7, 4/4, 5/6, 4/4).

## The claim

A green test suite says nothing about a property the suite never observes. Framing is one
of those properties: it exists **only in the bytes that leave the process**, and every
layer between the handler and the socket — the WSGI shim, the test client, the helper that
builds the response — is a place where it can be wrong while every assertion passes.

Four single-file servers, written at different times by the same hand, all had it. All
four suites were green.

| repo | defect | what a client saw |
|---|---|---|
| `tiny-router` | `_run` wrote `response.body` for every status and method | 204 carried a `content-type`; HEAD wrote the 6 bytes it declared as length |
| `tiny-metrics` | only `do_GET` was implemented | `HEAD /metrics` → **501** |
| `tiny-webhook` | `_respond` sent no `Content-Length`; `int()` outside `try` | every reply unframed; `Content-Length: abc` → **no response at all** |
| `tiny-agent-service` | the same two, copied from `tiny-webhook` | same, plus a header error reported as "invalid JSON" |

In all four the **status code was always correct**. `assert resp.status == 204` passed. The
defect lived in the ten lines between "I have a Response" and "I have put bytes on the
wire".

## Why each suite was green

Three different shims, one cause:

1. **A hand-rolled WSGI adapter.** `tiny-router`'s tests route through `_wsgi_call`, which
   turns a `Response` into `(status, headers, body)`. No socket, so framing is unobservable.
2. **`http.client` on the happy path.** `tiny-metrics` used `HTTPConnection` — and only
   GET. The transport was exercised, but only along the path that happened to be right.
   Its four endpoint behaviours were three-quarters tested, missing exactly the broken one.
3. **Calling the handler directly.** `tiny-webhook` and `tiny-agent-service` assert on the
   dict a handler returns. There is no transport at all.

## The rule

> **A test that constructs the response cannot validate it. Framing, status-line
> correctness, and body suppression are properties of the wire. Assert on the wire.**

The whole class is caught by one round-trip assertion, because it is written in terms of
the response itself rather than a constant:

```python
assert headers["content-length"] == str(len(body))
```

True of any correct server; false of one that omitted the header, miscounted it, or wrote a
body it did not declare.

## The 40-line fixture that catches it

Start the real server on port 0, connect with a raw socket, write the request by hand, read
to EOF, split on `\r\n\r\n`, and count the body yourself:

```python
sock = socket.create_connection(("127.0.0.1", port), timeout=5)
sock.sendall(f"{method} {path} HTTP/1.1\r\nHost: localhost\r\n"
             f"{headers}Connection: close\r\n\r\n".encode() + body)
raw = b""
while chunk := sock.recv(65536):
    raw += chunk
head, _, body = raw.partition(b"\r\n\r\n")
```

Only after that do you assert on the status line. `test_v092_wire_bodyless.py` is this
fixture, seven times.

## The four failure modes, ordered by cost

### 1. No `Content-Length` on a keep-alive connection
The most expensive, because HTTP/1.0 hides it. `BaseHTTPRequestHandler` defaults to 1.0,
so the body is framed by EOF and curl, `http.client`, and the test suite all agree it
works. Put a proxy in front that speaks 1.1 upstream and reuses connections, and the body
has no boundary: the proxy either waits for a length that never arrives, or reads the next
`HTTP/1.0 200 OK` as body bytes and hands the application corrupted JSON **intermittently**.
"It works in dev" and "it works with curl" are both true and both useless.

### 2. A body after a status that must not carry one
204 and 304 (RFC 9110 §15.3.5, §6.4.1) desynchronise the connection unconditionally, even
at HTTP/1.0. HEAD is the expensive one, because it looks free: route it through GET and
forget to drop the body, and the headers are correct while the payload is written and
discarded by every client that reads it.

### 3. A client-controlled header that produces **no response**
```python
content_length = int(self.headers.get("Content-Length", 0))   # outside any try
```
`Content-Length: abc` raises `ValueError`; `handle_one_request` logs a traceback and sends
**nothing**. The caller sees a timeout, not a 400. On a webhook endpoint that is a permanent
wedge: the provider retries the same malformed request, gets the same silence, and backs
off — the queue for that endpoint never drains and the only signal is a timeout graph. A
400 costs one line and ends the conversation correctly.

### 4. 501 for the method the health probe uses
`tiny-metrics` answered `HEAD /metrics` with `501 Unsupported method`. Prometheus scrapes
with GET, so the suite tested GET. Uptime checkers, mesh sidecars, and cloud load balancers
all send HEAD — to every one of them, a reproducing endpoint that 501s reads as an unhealthy
backend, and the instance leaves rotation. Three lines to fix; an unexplained half-capacity
incident not to.

## Prove the test fails on the old code

Before committing, `git show HEAD:<file> > /tmp/old.py`, run the new tests against it, and
count the failures you predicted:

| repo | new tests | fail on pre-fix file |
|---|---|---|
| `tiny-router` | 7 | 3 |
| `tiny-metrics` | 4 | 4 |
| `tiny-webhook` | 6 | 5 |
| `tiny-agent-service` | 4 | 4 |

A regression test never observed failing is indistinguishable from one that asserts `True`.
See `prompts/a-red-test-must-fail-on-the-assertion.md` for the same failure by a different
route.

## When one server has it, grep the neighbours

All four were found by one search:

```bash
grep -rln "send_header\|Content-Length" --include=*.py .
```

The fourth had byte-identical code because `_json_resp` was copied from `tiny-webhook` when
the repo was created. **Copy-paste is how a defect becomes a convention.**

## The one deliberate non-change

`tiny-router` still does **not** route HEAD to a GET handler: HEAD is registered explicitly,
so 404 is the correct answer there. A test now pins that, so adding a fallback later is a
visible decision rather than an accident.

## Related

- `tools/asserting-on-the-wire-not-the-object.md` — the fixture, parameterised
- `skills/http-framing-audit/` — the four-repo sweep
- `prompts/a-red-test-must-fail-on-the-assertion.md`
- `prompts/a-guard-that-covers-one-path-covers-none.md` — the GET-only test is that rule
  applied to methods
