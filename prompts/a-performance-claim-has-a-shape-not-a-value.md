---
name: a-performance-claim-has-a-shape-not-a-value.md
description: Use when a repo advertises a speedup multiple — re-measure it across selectivities, because a scalar result describes one input shape, and the same code path is often slower than no optimisation outside it.
---

# A performance claim has a shape, not a value

## The prompt

> A README says "31.5× faster". Ask: faster than what, on how many rows, and
> what does the same measurement say one order of magnitude up? If the claim is
> a single number, the shape was never measured.

## What happened

`snapdb`'s README and changelog advertised a **31.5× speedup on a 50K-row
narrow range** for the v0.18.0 `RangeIndex` query planner. Re-measuring the
stated shape (~500 of 50,000 rows matched):

| rows matched | share | scan | index | speedup |
|---:|---:|---:|---:|---:|
| 30 | 0.1% | 24.7 ms | 0.15 ms | 169× |
| 505 | 1% | 25.7 ms | 0.97 ms | 26× |
| 2,505 | 5% | 25.4 ms | 4.6 ms | 5.5× |
| 10,005 | 20% | 27.3 ms | 19.3 ms | 1.4× |
| 20,005 | 40% | 31.7 ms | 29.7 ms | 1.1× |
| 40,005 | 80% | 37.8 ms | 35.7 ms | 1.1× |

The stated shape gives **26×**, not 31.5×; 31.5× is reachable near 0.4%
selectivity. The number ranges over three orders of magnitude across the
column's own domain.

**The worse finding is in the last row.** Measured generously at 80% the index
came in at **0.4×** — *slower than no index*. A user who added an index to speed
up a query made it slower, having read a README that promised 31.5×.

**Root cause:** index-served results cost one random row decode each
(`db.get(idx)`); a scan decodes sequentially. Below some touched-row fraction
the random decodes dominate. Nothing in the planner guarded that, so every
range plan was taken.

**Fix** (`snapdb` `6fd005a`): `execute()` estimates touched rows from the index
with two bisects and rejects the plan above 30% of the table; `explain()` now
reports the plan execution will actually use and the reason for rejection
(`Scan(filter=['age']) [index rejected: 62/100 rows]`). Verified: 244 passed,
9 skipped; **5 of 8 new tests fail against the unfixed file**.

## The rule

1. **A scalar speedup is a point on a curve, published as a property.** State
   the shape: rows, matched share, machine, and the crossover point. Either
   publish the table or publish the range.
2. **The claim must match the code path.** 31.5× in the export was measured at
   a selectivity the fix did not previously exist for. Re-measure after any
   change to the planner, and re-read the sentence that describes it.
3. **A guard that is not in the code is not in the claim.** If the optimisation
   needs a selectivity threshold to stay faster, that threshold is part of the
   feature; `explain()` must be able to say why the index was refused.
4. **Cost both paths in units you can compare.** Sequential decode vs N random
   decodes is an inequality, not a benchmark — write the inequality down, and
   the selectivity guard becomes derivable rather than tuned.

## How to measure it

```python
for share in (0.001, 0.01, 0.05, 0.2, 0.4, 0.8):
    n = int(rows * share)
    t_scan  = timeit(...)   # same predicate, index dropped
    t_index = timeit(...)   # same predicate, index used
    print(f"{n:7d} {share:6.1%} scan={t_scan:.2f}ms index={t_index:.2f}ms x{t_scan/t_index:.1f}")
```

Run both paths against the **same** data in the **same** process, and drop the
index by opening a second connection rather than deleting it — rebuilding costs
more than the measurement and changes page cache state.

## README as a test

`snapdb` has `tests/test_readme_consistency.py`, which executes the README's own
example. It caught a new example block within a minute of it being written.
Extend that pattern to numbers where the cost is low: a test that asserts the
published table is monotone, or that the claimed crossover fraction still
produces the claimed sign of the result, fails when the planner drifts.

---

**Last verified:** 2026-11-15 — table above measured in this session on the
workspace container; `snapdb` `6fd005a` merged, **244 passed / 9 skipped**, CI
green, 5 of 8 new tests proven to fail on the unfixed file. Prior claim (31.5×)
was published on 2026-11-05 and is now replaced by the measured table in both
`README.md` and `CHANGELOG.md`.
