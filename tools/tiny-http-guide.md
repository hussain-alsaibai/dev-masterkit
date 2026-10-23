# tiny-http — Zero-Dependency HTTP Client

## Repo
https://github.com/hussain-alsaibai/tiny-http

## What It Does

Zero-dependency HTTP **client** for Python. One file, no setup. Convenience
functions plus a `Client` class with retries and rate limiting.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented a **server** API —
`from tiny_http import serve, json_response`, route decorators, and
`serve(host=..., port=...)`. **None of that exists.** Verified against upstream
`tiny_http.py`:

```
__all__ = ['Client', 'Request', 'Response', 'get', 'post', 'put', 'delete', 'patch']
```

Top-level names: `Client`, `Request`, `Response`, `RetryConfig`, `RateLimiter`,
`get`, `post`, `put`, `delete`, `patch`.

`tiny-http` is a **client**. For a server, use `tiny-router`
(`tools/tiny-router-guide.md`).

## Key Features

- Module-level `get` / `post` / `put` / `delete` / `patch` helpers
- `Client` — connection reuse, `RetryConfig`, `RateLimiter`
- `Request` / `Response` value objects
- Pure stdlib: `urllib`, `http.client`, `json`

## Quick Start

```python
from tiny_http import get, post

resp = get("https://api.example.com/health")
print(resp.status, resp.body)

resp = post("https://api.example.com/echo", json={"hello": "world"})
```

`get(url, **kwargs)` returns a `tiny_http.Response`.

## When to Use

- A dependency-free HTTP client for agents and cron jobs
- When `requests` is too heavy but `urllib` is too manual
- Needing retries and rate limiting without a third-party dependency

## Related

- `tools/tiny-router-guide.md` — the server counterpart
- `tools/tiny-retry-guide.md` — retry + circuit breaker as a separate primitive
