# Changelog

All notable changes to tiny-headers-redact are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed - a missing dependency is loud, not a silent no-op
- `redact_headers()` **raises `RuntimeError`** when `tiny_secret_mask >= 0.5.0`
  cannot be imported. 0.1.0 returned a shallow copy, so a caller believed the
  headers were scrubbed while the credential passed through untouched.
- `redact_headers_passthrough(headers) -> dict` is the explicit opt-out. A
  no-op now has to be spelled.
- **Default behaviour change for callers without the sidecar:** 0.1.0 worked
  (by doing nothing); this raises. That is intentional and is a security fix.

### Fixed
- `redact_headers.__doc__` still documented the 0.1.0 fallback ("falls back to
  a shallow copy") while the code raised. The docstring is now the behaviour.

### Known issue
- The middleware path (`header_redactor_middleware`,
  `header_redactor_asgi_middleware`) calls `redact_headers()` and therefore
  raises on the first request when the sidecar is absent, rather than at
  import time. Not fixed here: it needs a decision between raising at
  construction and documenting the crash-on-first-request.

## [0.1.0] - 2026-10-15

### Added
- **Initial release.** Framework-agnostic middleware that redacts
  credentials from HTTP headers.
- `redact_headers(headers) -> dict` - returns a NEW dict with credential-
  bearing header values replaced. **Superseded in [Unreleased]:** 0.1.0 fell
  back to a shallow copy when `tiny-secret-mask >= 0.5.0` was not installed;
  that silent no-op is the defect that made the fallback unsafe.
- `header_redactor_middleware(get_response)` - WSGI-style middleware that
  rewrites request headers before the wrapped app sees them.
- `header_redactor_asgi_middleware(app)` - ASGI-style middleware that
  rewrites the `headers` scope key.
- `HeaderStats` - counter object (`headers_seen`, `redactions`,
  `last_redacted_header`) for `/metrics` endpoints.
- Default rule set covers 16 patterns: Authorization, Proxy-Authorization,
  Cookie, Set-Cookie, X-API-Key, X-Auth-Token, X-CSRF-Token, X-Hub-Signature,
  X-Hub-Signature-256, X-Hub-Token, Stripe-Signature, X-GitHub-Token,
  X-Slack-Token, X-Shopify-Access-Token, X-AWS-Signature, X-AWS-Security-Token.
- 19 tests in `tests/test_tiny_headers_redact.py`. All pass.
- MIT license, single file, ~200 LOC.

### Notes
- The default rule set is owned by `tiny-secret-mask` v0.5.0+, NOT by
  this package. Adding a new header rule is a one-PR change to
  `tiny_secret_mask.HEADER_REDACT_RULES`, not this file.
- This package is the header-redaction equivalent of `tiny-route-redact`
  (path redaction). Together they form the credential-leak loop at the
  HTTP boundary.
- For framework-native integration, use the sidecar modules:
  - `tiny_router_redact_headers` for tiny-router v0.7.x.
  - `fastapi-header-redact` adapters (not yet published).
  - `django-header-redact` adapters (not yet published).

