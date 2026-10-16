# 2026-10-16 — Developer Tool Trends: HTTP Correctness

**Theme:** the boring 90% that separates a working agent from a production-grade one.

## Trend 1 — Sliding windows close the boundary-burst hole

Fixed-window counters (e.g. "1000 req/min") are the most common rate-limiter in
production HTTP APIs and they are wrong: a client can fire 1000 requests in the
last second of one window and 1000 in the first second of the next, getting
2000 through in 2 seconds — twice the intended rate. This is the
**boundary-burst problem** and it is not theoretical, it is the failure mode
that gets you throttled by your upstream provider.

The fix is the **weighted sliding window** algorithm: track the previous
window's count and apply an overlap-fraction weight based on how far into the
current window we are.

    effective_count(now) = previous_count * overlap_fraction + current_count
    where overlap_fraction = 1 - (now - current_window_start) / window_seconds

This is the same algorithm used by nginx (the limit_req module) and by
Cloudflare's analytics pipeline. It is small, it is correct, and it has no
boundary-burst hole. **tiny-rate-window v0.1.0** ships a 613-LOC stdlib-only
implementation with 23 tests including a regression test for the 2000-in-2s
case.

**Practical guidance:**

- Use sliding windows for *hard* rate ceilings (per-user, per-tenant)
- Use token buckets when you need burst tolerance
- Use bulkheads when you need concurrency caps (not request-rate)
- The three are complementary, not competing

## Trend 2 — Hierarchical quotas need all-or-nothing acquire

A flat per-key token bucket is the wrong abstraction for multi-tenant SaaS.
Real workloads are nested: org -> team -> user, with budgets that must be
consistent up and down the tree. If `user:42` spends 200 RPM, the
`team:backend` bucket must drop to 1800 RPM and `org:acme` to 4800 RPM.

A flat limiter on `user:42` alone would let the team burn through 4000 RPM
total (200 x 20) — twice the team budget. This is how you get emergency Slack
messages at 3 AM.

The fix is a **tree of token buckets** with refill propagated through the
parent/child relationship, and **all-or-nothing acquire**: if any ancestor is
at zero, no node is decremented. Partial reservations are how you under-report
utilization and lose the diagnostic information that makes a post-mortem
possible.

**tiny-bucket-quota v0.1.0** ships exactly this, plus a `blocked_at` field in
the `QuotaDecision` that tells you *which* node hit zero. That single field
turns a 429 into actionable information: "team-level quota exceeded, escalate
to admin" vs "your personal quota is gone, slow down."

**Practical guidance:**

- Build quotas as trees, not flat maps
- Make acquire all-or-nothing across the path
- Always include a `blocked_at` diagnostic in the deny response
- Pair with a counter (per-node stats) for /metrics

## Trend 3 — RFC 9457 enforcement > dict literals

RFC 9457 (July 2023, "Problem Details for HTTP APIs") defines a single JSON
shape for *all* HTTP error responses. The shape is small and the spec is clear,
yet half-implementations are everywhere:

- Default `type` set to empty string instead of `about:blank`
- Wrong Content-Type (`application/json` instead of `application/problem+json`)
- Missing `status` mirror
- `errors` array shaped ad-hoc instead of per-spec
- No `instance` field

The reason this matters: clients (and AI agents) that consume your API need to
parse error bodies uniformly. The moment one endpoint emits a non-conformant
shape, every consumer has to special-case it. RFC 9457 is a 5-year-old spec
and the failure mode is still "we rolled our own error JSON."

**tiny-rfc9457 v0.1.0** ships a 558-LOC stdlib-only implementation that
enforces the spec (frozen dataclass, `as_dict()`/`as_json()` round-trip, an
exception registry that maps `ValueError` -> 400 validation / `KeyError` -> 400
missing-field / `PermissionError` -> 403 / `FileNotFoundError` -> 404 /
`NotImplementedError` -> 501). Drop it in front of any HTTP handler and every
error path gets spec-compliant JSON for free.

**Practical guidance:**

- For any new HTTP API, ship RFC 9457 from day one
- Centralize the renderer; do not let endpoint code construct error JSON
- Map your exception hierarchy once and let the renderer handle status/title/type
- Use the `errors` array for validation failures, not a custom shape
- Pair with `tiny-rate-window` / `tiny-bucket-quota` to emit 429s in the
  standard shape (clients can parse them without special-casing)

## Cross-ecosystem context

- **nginx `limit_req`** uses the same weighted-prev-window algorithm as
  tiny-rate-window
- **Cloudflare Workers rate-limiting** uses sliding windows + per-tenant
  hierarchies
- **Stripe API** uses RFC 9457-shaped errors (since 2024) for all 4xx responses
- **GitHub API** uses RFC 7807 (predecessor) errors, with `errors[]` for
  validation
- **OpenAI API** switched to RFC 9457 in 2025 for `/v1/*` errors

The trio (sliding-window + hierarchical quota + RFC 9457) is the boring 90%
that you ship in month 1 and never think about again. It is also the thing
that makes an agent look production-grade instead of a weekend hack.

## What this means for the tiny-* ecosystem

The family now spans 60 repos. The HTTP correctness cluster (rate-window +
bucket-quota + rfc9457) is the **fourth** themed cluster after:

1. Resilience: tiny-rate-limiter, tiny-bulkhead, tiny-circuit-breaker
2. Resilience: tiny-retry, tiny-backoff, tiny-timeout
3. Redaction: tiny-secret-mask (5 layers), tiny-headers-redact, tiny-route-redact
4. **HTTP correctness: tiny-rate-window, tiny-bucket-quota, tiny-rfc9457**

Each cluster is a small set of zero-dep primitives that solve a specific
slice of the production-readiness problem. The pattern is consistent: ~600 LOC,
stdlib-only, 20+ tests, README + llms.txt, MIT.

## Sources

- RFC 9457 (July 2023): https://www.rfc-editor.org/rfc/rfc9457
- nginx limit_req docs: https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
- Cloudflare Workers rate-limiting: https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/
- Stripe API errors: https://docs.stripe.com/error-codes
- GitHub REST API errors: https://docs.github.com/en/rest
