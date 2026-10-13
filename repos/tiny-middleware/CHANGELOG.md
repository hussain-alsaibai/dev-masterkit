# Changelog

All notable changes to `tiny-middleware` are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-10-13

### Added
- `Request` and `Response` dataclasses with `header_get` and JSON/text helpers.
- `Chain` class with auto-detection of sync/async middleware.
- `request_id()` built-in middleware (assign or echo `x-request-id`).
- `cors()` built-in middleware (headers + preflight short-circuit).
- 23 unit tests covering sync, async, short-circuit, built-ins, integration.
