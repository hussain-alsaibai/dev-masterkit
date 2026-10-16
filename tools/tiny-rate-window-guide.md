# tiny-rate-window v0.1.0 — Sliding-Window Rate Limiter

**Last verified:** 2026-10-16
**Repo:** https://github.com/hussain-alsaibai/tiny-rate-window
**License:** MIT • **Deps:** zero (stdlib only) • **LOC:** 613 (lib) + 256 (tests) • **Tests:** 23/23

## Why a sliding window?

Fixed-window counters (e.g. "1000 req/min") suffer the **boundary-burst problem**: a client can fire 1000 in the last second of one window and 1000 in the first second of the next, getting 2000 through in 2 seconds — twice the rate.

Token buckets solve this but require tuning of burst + refill. Great for steady workloads, awkward when you need a *hard* ceiling.

tiny-rate-window implements the **weighted sliding window** algorithm:

    effective_count(now) = previous_count * overlap_fraction + current_count
    where overlap_fraction = 1 - (now - current_window_start) / window_seconds

The previous window still "counts for" a fraction of its requests until they age out. Smooth ceiling, no boundary-burst hole.

## Public API

- SlidingWindowLimiter(limit, window_seconds, *, clock=time.monotonic) — main limiter
  - try_acquire(key, *, cost=1, now=None) -> Decision — atomic reservation
  - peek(key, *, now=None) -> Decision — non-mutating check (for /metrics)
  - reset(key=None) — drop one key's history or all
  - stats() -> LimiterStats — hits, misses, hits_per_key, peak_count
- Decision — allowed, remaining, retry_after_s, limit, window_seconds
- http_headers(decision) -> dict — turn a Decision into standard X-RateLimit-* headers

## Quick start

    from tiny_rate_window import SlidingWindowLimiter, http_headers

    limiter = SlidingWindowLimiter(limit=100, window_seconds=60)

    def handler(req):
        d = limiter.try_acquire(req.user_id)
        if not d.allowed:
            return 429, http_headers(d), b"rate limited"
        return 200, http_headers(d), b"ok"

## When to use

- HTTP API rate limiting where you want a *hard* ceiling per key
- Per-user / per-tenant request budgets
- Agent pipelines where you need to bound calls across windows

## When NOT to use

- You need burst tolerance -> tiny-bucket-quota
- You need hierarchical (org -> team -> user) -> tiny-bucket-quota
- You only need concurrency cap (not request-rate) -> tiny-bulkhead

## Thread-safety

Single threading.Lock per limiter. For high contention, shard by key prefix and run multiple limiters in front of a router.

## Pairs with

- tiny-router (middleware) — wire try_acquire() into a route
- tiny-bucket-quota — orthogonal budget tracker
- tiny-rfc9457 — emit 429 as RFC 9457 Problem Details

## Test highlights (23/23)

Weighted prev-window fraction, boundary-burst prevention (2000 in 2s rejected), peek() non-mutation, reset() semantics, http_headers() standard fields, thread-safety smoke, stats() accuracy, custom clock injection, cost > 1 multi-slot, key isolation.
