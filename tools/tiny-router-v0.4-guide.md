# tiny-router v0.4.0 — Async + Dependency Injection + Structured Errors

> Zero-dependency WSGI router. v0.4.0 force-push aligns GitHub main with local v0.3.0 unreleased features.
> Last verified: 2026-09-11 | Version 0.4.0 | hussain-alsaibai/tiny-router

## What Changed in v0.4.0 (Sep 2026)

This is a **force-push realignment** — GitHub main was lagging at v0.1.0 while local work had reached v0.3.0 (commit `f522543`). v0.4.0 collapses all unreleased features plus the Sep refactor into a single aligned release.

- Async handler support (`inspect.iscoroutine()` detect-and-dispatch)
- FastAPI-style `Depends()` dependency injection — recursive, per-request cached
- `HTTPError(status, message)` exception class — structured error responses
- `AsyncResponse` wrapper for explicit async I/O handlers
- 503 status mapping for service-unavailable paths
- README + tiny_router.py + test_router.py + LICENSE refreshed on main

## Repo

https://github.com/hussain-alsaibai/tiny-router

## When to Use

- Flask-like routing without Flask
- Stdlib-only agent callback receivers
- Tiny-* style services or examples

## See Also

- `tools/tiny-router-guide.md` — base guide (kept in sync)
