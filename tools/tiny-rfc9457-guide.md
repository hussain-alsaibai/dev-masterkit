# tiny-rfc9457 v0.1.0 — RFC 9457 Problem Details Renderer

**Last verified:** 2026-10-16
**Repo:** https://github.com/hussain-alsaibai/tiny-rfc9457
**License:** MIT • **Deps:** zero (stdlib only) • **LOC:** 558 (lib) + 216 (tests) • **Tests:** 21/21

## What is RFC 9457?

RFC 9457 (July 2023, "Problem Details for HTTP APIs") is the successor to RFC 7807. It defines a single JSON shape for **all** HTTP error responses, so clients parse error bodies uniformly instead of reverse-engineering each API's contract.

A Problem Details document:

    {
      "type": "https://example.com/probs/rate-limit",
      "title": "Rate limit exceeded",
      "status": 429,
      "detail": "1000 requests per 60s; you sent 1001",
      "instance": "/requests/abc-123",
      "errors": [{"name": "limit", "reason": "exceeded"}]
    }

Content-Type: application/problem+json. XML path (application/problem+xml) supported but rarely used.

## Why this, not just a dict?

The spec is small but *particular*. Common half-implementations:
- Wrong default type (must be about:blank, not empty string)
- Wrong Content-Type
- Missing status mirror
- errors shape ad-hoc instead of the spec's array-of-objects

tiny-rfc9457 enforces the spec, round-trips cleanly with both content types, and converts Python exceptions to Problems via a registry.

## Public API

- Problem — frozen dataclass. as_dict(), as_json(), as_content_type(). Optional errors: list[SubProblem] for nested sub-problems.
- problem_response(status, ...) — turn any HTTP status into a (status, headers, body) triple ready for Flask/FastAPI/WSGI/ASGI.
- from_exception(exc, *, instance=None) -> Problem — convert via registered exception->Problem mappers.
- ProblemType — typed URI constants for the common cases (rate-limit, validation, not-found, unauthorized, conflict, internal). Extensible.
- SubProblem — typed nested sub-problem (name, reason, optional value).
- parse(payload: str|bytes) -> Problem — round-trip from a wire payload.

## Quick start

    from tiny_rfc9457 import Problem, ProblemType, problem_response, from_exception

    # Construct manually
    p = Problem(
        type=ProblemType.RATE_LIMIT,
        title="Rate limit exceeded",
        status=429,
        detail="1000 req/60s; you sent 1001",
        instance="/requests/abc-123",
    )
    status, headers, body = problem_response(p)
    # (429, {"Content-Type": "application/problem+json"}, b'...')

    # From an exception
    try:
        do_thing()
    except ValidationError as e:
        p = from_exception(e, instance=request.path)
        return problem_response(p)

## Built-in exception mappers

- ValueError -> 400 validation
- KeyError -> 400 validation (name=<missing key>)
- PermissionError -> 403 unauthorized
- FileNotFoundError -> 404 not-found
- NotImplementedError -> 501 not-implemented

Extend with from_exception.registry.register(MyExc, lambda e: Problem(...)) or by subclassing _ExceptionRegistry.

## When to use

- Any HTTP API where clients should parse errors uniformly
- Replacing per-endpoint ad-hoc error JSON shapes
- Pairing with tiny-rate-window / tiny-bucket-quota to emit 429s in the standard shape
- AI agent tool surfaces — agents can read Problem Details deterministically

## When NOT to use

- Internal-only RPCs where you control both ends and a custom shape is fine
- You need i18n on the human-readable fields (do it in the renderer layer above)

## Test highlights (21/21)

Default type=about:blank, as_dict()/as_json() round-trip, as_content_type() is application/problem+json, problem_response() triple correctness, from_exception() for all 5 built-ins, custom registry extension, nested errors array shape, parse() JSON path, parse() bad payload raises informative error, status mirror invariant, XML path smoke.
