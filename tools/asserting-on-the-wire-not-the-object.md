# Asserting on the wire, not the object

**Verified:** 2026-11-18 — the fixture below is the shape used by
`repos/tiny-router/test_v092_wire_bodyless.py` (7 passed), and the equivalent table-driven
version in `repos/tiny-metrics` (36 passed). All four repos it was applied to are at their
fixed versions on `main` and were re-run in this session.

## When to use this

- A server's test suite calls the handler directly, or goes through a WSGI/ASGI adapter.
- You are auditing a response-path change (a new status code, HEAD support, compression,
  redirects).
- A health probe, proxy, or load balancer in front of the service disagrees with the tests.

## Step 1 — Find every server that could have the defect

```bash
grep -rln "send_header\|Content-Length\|write(body" --include=*.py . | sort
```

A copied helper is the usual reason two repos share a defect. Fix the search, not the file.

## Step 2 — Before changing code, be a client

```python
import socket, threading
from http.server import HTTPServer

def wire_request(server, method, path, body=b"", headers=""):
    """Start the real server on an ephemeral port, speak HTTP/1.1 by hand."""
    srv = HTTPServer(("127.0.0.1", 0), server.handler)
    t = threading.Thread(target=srv.handle_request, daemon=True)
    t.start()
    sock = socket.create_connection(("127.0.0.1", srv.server_port), timeout=5)
    sock.sendall((f"{method} {path} HTTP/1.1\r\nHost: localhost\r\n{headers}"
                  "Connection: close\r\n\r\n").encode() + body)
    raw = b""
    while chunk := sock.recv(65536):
        raw += chunk
    sock.close(); srv.server_close(); t.join(timeout=2)
    head, _, resp_body = raw.partition(b"\r\n\r\n")
    lines = head.decode("latin-1").split("\r\n")
    status = int(lines[0].split()[1])
    hdrs = {k.strip().lower(): v.strip()
            for k, _, v in (l.partition(":") for l in lines[1:]) if k}
    return status, hdrs, resp_body
```

Three properties matter and all three are free:

- `Connection: close` keeps the read-from-EOF loop finite.
- `partition(b"\r\n\r\n")` is the only correct split — a body may contain the sequence.
- `srv.handle_request()` handles exactly one request, so no teardown races.

## Step 3 — Assert properties, not constants

```python
def test_every_response_is_framed(server):
    for method, path, expected in [("GET",  "/x", 200),
                                   ("HEAD", "/x", 200),
                                   ("GET",  "/nope", 404),
                                   ("HEAD", "/nope", 404)]:
        status, hdrs, body = wire_request(server, method, path)
        assert status == expected, (method, path, status)
        assert hdrs["content-length"] == str(len(body)), (method, path, hdrs)
```

The second assertion is the invariant; the first is the test case. Keep both, because a
wrong status with correct framing and a correct status with no framing are different bugs.

### The bodyless table

| status / method | body | `content-length` |
|---|---|---|
| 204, 304 | must be empty | `0` or absent — never the GET length |
| HEAD | must be empty | **the length GET would send** |
| any other | as computed | `str(len(body))` |

HEAD is the row people get wrong in both directions.

## Step 4 — Cover every method and status the server can emit

The `tiny-metrics` suite used `HTTPConnection` and only ever sent GET, so the one method
that 501'd was the one it never sent. Drive the table from the router's own registration
list where you can:

```python
for route in APP.routes:            # or a literal list of the endpoints
    for method in route.methods:
        ...
```

A table of four is cheap. Deriving it is cheaper than remembering to extend it.

## Step 5 — Prove the new tests fail on the old code

```bash
git show HEAD:tiny_router.py > /tmp/old_router.py
cp -n tiny_router.py /tmp/new_router.py && cp /tmp/old_router.py tiny_router.py
python3 -m pytest test_v092_wire_bodyless.py -q   # expect N failures, count them
cp /tmp/new_router.py tiny_router.py
```

Record the pair (`new tests`, `fail on old`). A number you did not observe is not evidence.

## Traps

- **A "200 OK" from `http.client` is not proof of framing.** HTTP/1.0 and connection-close
  framing hide a missing `Content-Length` completely.
- **`curl` hides it too**, for the same reason, and `curl -I` only sends HEAD — which is the
  request most likely to hit a 501 and least likely to be in the suite.
- **A WSGI adapter is a response *constructor*.** It normalises exactly the layer under
  test and will happily accept a body for a 204.
- **`BaseHTTPRequestHandler` swallows handler exceptions** inside `handle_one_request` and
  replies with silence. A `ValueError` on a client-supplied header therefore reads as a
  timeout in the client and as a traceback on the server, and a test that calls the handler
  directly sees neither.
- **The suite going from 27 to 33 passing is not the signal.** The signal is the count that
  failed on the pre-fix file.
