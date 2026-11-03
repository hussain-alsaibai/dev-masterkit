# tiny-mesh — Zero-Dependency Service Mesh Proxy (circuit breaker + retries + rate limit)

**Repo:** github.com/hussain-alsaibai/tiny-mesh
**Install:** `pip install httpx` && `pip install git+https://github.com/hussain-alsaibai/tiny-mesh.git`
**Last verified:** 2026-11-03 - `tiny-mesh` is **not published on PyPI** (the name returns HTTP 404), so the bare `pip install tiny-mesh` fails. The GitHub URL is the working install.
**Content last verified:** 2026-08-14

Circuit breaker, retry with exponential backoff, weighted round-robin load balancing, token-bucket rate limiting, health checks, stats endpoint. No sidecar, no YAML. ~1 external dep (httpx).
