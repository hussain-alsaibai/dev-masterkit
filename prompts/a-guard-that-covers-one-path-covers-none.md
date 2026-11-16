---
title: A guard that covers one path covers none
date: 2026-11-16
tags: [performance, query-planner, verification]
source: snapdb 0.18.2 (commit c57aeb3), 2026-11-16
last_verified: 2026-11-16
---

# A guard that covers one path covers none

A selectivity guard was added to a query engine and wired into `execute()`. `count()`,
`sum()`, `avg()`, `min()` and `max()` kept calling the raw planner. The guard was correct,
tested, documented — and bypassed by four of five entry points.

## What it cost

Measured on the same predicate, before the fix:

| query | `execute()` | `count()` / `sum()` / `avg()` / `min()` / `max()` |
|---|---|---|
| range matching **1%** of rows | 1.1 ms (index) | **37 ms** (full scan) |
| range matching **62%** of rows | scan | scan **plus** a 162K-element candidate set |

A selective `count()` was ~34× slower than `len(execute())` on the same predicate, and it
scanned a table whose index already named the matching rows. A *wide* aggregation scanned
**and** materialised the plan that `explain()` had just reported as rejected — 162K
elements built in 706 ms, paid again by each of four aggregations.

## The fix, and the part that matters more than the fix

The predicate moved into a single helper (`_plan_or_scan()`) used by every path. The
durable part is the regression test:

> **A regression test asserts that exactly two call sites may reach the raw planner.**

A test that only checks each consumer's behaviour drifts: the next consumer added has no
reason to know the guard exists. Counting the call sites turns "everyone opted in" into a
property the suite enforces, and a new bypass fails the build instead of the benchmark.

## The second bug hides where the index is fastest

While writing the regression test: `min(first, *rest)` lowers to `min(first)` when `rest`
is empty, and `min` of a number is not iterable — so `min()`/`max()` raised `TypeError` on
a **one-row** result. One row is the *common* case for a selective indexed query, so the
defect sat exactly where the performance work had just made queries land.

**Rule:** when you speed up a path, the inputs that path now serves change shape. Newly
fast means newly common. Re-test the degenerate cases (0 rows, 1 row) at the same time;
they were rare only because the path was slow.

## Checklist

- [ ] Guard lives in one place, called by every entry point
- [ ] A test asserts the count of call sites that bypass it
- [ ] Benchmarked selective **and** wide on each entry point, not just the main one
- [ ] Degenerate cardinalities (0, 1) tested on the newly fast path
