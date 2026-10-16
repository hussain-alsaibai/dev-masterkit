# tiny-bucket-quota v0.1.0 — Hierarchical Token-Bucket Quota Allocator

**Last verified:** 2026-10-16
**Repo:** https://github.com/hussain-alsaibai/tiny-bucket-quota
**License:** MIT • **Deps:** zero (stdlib only) • **LOC:** 623 (lib) + 250 (tests) • **Tests:** 23/23

## Why hierarchical?

A flat per-key bucket handles one dimension (one API key, 1000 RPM). Real workloads are **nested**:

    org:acme (5000 RPM)
    ├── team:backend (2000 RPM)
    │   ├── user:42 (200 RPM)
    │   └── user:43 (200 RPM)
    └── team:frontend (3000 RPM)
        ├── user:alice (500 RPM)
        └── user:bob   (500 RPM)

When user:42 spends 200 RPM, the team:backend bucket must drop to 1800 RPM and org:acme to 4800 RPM. That's the *hierarchical invariant*.

A flat limiter on user:42 alone would let the team burn 4000 RPM total (200 × 20) — twice the team budget.

tiny-bucket-quota implements exactly that: a tree of token buckets that share state through parent/child, with refill propagated automatically.

## Public API

- QuotaTree() — the tree
  - add(parent, child, *, limit, window_seconds, refill_rate=None) — register a node (root uses parent=None)
  - try_acquire(path, *, cost=1, now=None) -> QuotaDecision — walk the path; all ancestors must have capacity
  - peek(path, *, now=None) -> QuotaDecision — non-mutating check
  - reset(path=None) — drop one subtree or all
  - stats() -> QuotaStats — flat counters per node
- QuotaDecision — allowed, **blocked_at** (the path that hit zero), remaining_by_path
- acquire_or_raise(tree, path, *, cost=1) — convenience; raises QuotaExceeded if denied
- QuotaExceeded — carries the QuotaDecision for diagnostics

## Quick start

    from tiny_bucket_quota import QuotaTree, QuotaExceeded, acquire_or_raise

    q = QuotaTree()
    q.add(None, "org:acme", limit=5000, window_seconds=60)
    q.add("org:acme", "team:backend", limit=2000, window_seconds=60)
    q.add("team:backend", "user:42", limit=200, window_seconds=60)

    try:
        acquire_or_raise(q, ["org:acme", "team:backend", "user:42"])
    except QuotaExceeded as e:
        print("blocked at", e.decision.blocked_at)  # tells you WHICH node hit zero

blocked_at is the killer feature: a flat limiter just says "denied", this one tells you whether user:42 or team:backend or org:acme is the bottleneck — so your 429 response can say "team-level quota exceeded, escalate to admin" vs "your personal quota is gone, slow down."

## When to use

- Multi-tenant SaaS with org -> team -> user budgets
- API gateways enforcing nested SLAs
- AI agent platforms where per-org spend must not exceed contracts

## When NOT to use

- You only have a flat per-key budget -> tiny-rate-limiter or tiny-rate-window
- You only cap concurrent in-flight (not rate) -> tiny-bulkhead
- You need a percentage rollout -> tiny-feature-flag

## All-or-nothing acquire

try_acquire reserves all ancestors atomically: if user:42 has slots but team:backend does not, **no node is decremented**. This prevents partial reservations that would under-report utilization.

## Test highlights (23/23)

Root-only acquire, three-level path, all-or-nothing on parent zero, refill propagation, blocked_at accuracy at each level, reset(subtree) only clears descendants, stats() per-node, thread-safety smoke, custom clock, cost > 1 multi-token.
