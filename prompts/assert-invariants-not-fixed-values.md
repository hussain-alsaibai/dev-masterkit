# Assert Invariants, Not Fixed Values — Property-Based Testing for Tiny Libs

**A checklist for writing tests for a statistical or approximate algorithm.**

While building `tiny-hll` on 2026-10-23, three of my own test assertions
were wrong on the first run. All three asserted a **fixed expected value**
and failed because the property they assumed was false.

The fix was not to correct the constants. It was to rewrite the assertions to
test the **invariant** instead.

> Found 2026-10-23 while shipping tiny-hll v0.1.0 (25 tests passing).
> **Last verified:** 2026-10-23

## The Wrong Assumption

The failing assertions expected accuracy to improve **monotonically** with
precision:

```python
# WRONG — assumes larger precision => strictly smaller error, every time
def test_precision_monotonic():
    errs = [error_at(p) for p in (5, 6, 7, 8, 10, 14)]
    assert all(errs[i] > errs[i + 1] for i in range(len(errs) - 1))
```

That is false. Single-sample sketches of **identical items are perfectly
correlated** — every sketch at every precision sees the same collision
pattern, so more precision does not help when the sample itself is the
limiting factor. The estimator was fine. The test was wrong.

## The Fix — Average Over Independent Samples

```python
# RIGHT — asserts the invariant, averaged over independent item sets
def test_bias_under_tolerance():
    for p in (5, 6, 7, 8, 10, 14):
        estimates = [estimate(p, fresh_items(50_000)) for _ in range(12)]
        true = 50_000
        bias = abs(mean(estimates) - true) / true
        assert bias < 0.025, f"p={p} bias={bias:.3%}"

def test_spread_tracks_theory():
    for p in (5, 6, 7, 8, 10, 14):
        estimates = [estimate(p, fresh_items(50_000)) for _ in range(12)]
        measured = stdev(estimates) / mean(estimates)
        theoretical = 1.04 / sqrt(2 ** p)
        assert measured < theoretical * 1.6, f"p={p}"
```

The invariant is *unbiasedness within a tolerance* and *spread tracking
theory*. Both are properties of the estimator, not of one particular run.

## Why This Matters Beyond Statistics

A fixed-value assertion couples the test to the implementation. The moment
you change an internal constant — a hash seed, a correction threshold, a
bucket count — every fixed-value test breaks, and the breakage is noise: you
end up updating numbers to match the new output, which means **the test can
never catch a regression**. It only proves the code still does what it did
yesterday.

An invariant assertion couples the test to the **contract**. Changing the
implementation is fine as long as the contract holds; changing the contract
breaks the test, which is the point.

## The PyPI Numbers Behind the Practice

The 2026-10-23 trends report measured property-based testing as a fast-growing
category:

| Package | 30d downloads | Growth |
|---------|--------------:|-------:|
| hypothesis | 62.9M | +11.4% |
| pytest | 912.9M | +12.2% |
| nox | 4.4M | +10.5% |

`hypothesis` is growing at essentially the same rate as `pytest` itself
despite being a fraction of its size. Testing investment is rising, and a
meaningful slice of it is going into adversarial input generation rather
than more example cases.

The tiny-* standard is now property-based: **assert invariants, not fixed
expected values.** The tiny-hll suite caught three of its own wrong assumptions
that way.

## Procedure

1. **Write the contract first.** What must be true for every valid input?
   For HLL: the estimate is unbiased; the spread tracks `1.04/sqrt(m)`; the
   error rate decreases with precision.
2. **Express it as an inequality with a tolerance**, not an equality. A
   statistical component has no exact expected output.
3. **Use independent samples.** Correlated samples (same items, same seed)
   measure the data, not the estimator. Vary the items, vary the seed.
4. **Average enough times to see the distribution.** 12 independent sketches
   was enough to expose the correlation bug; 1 was not.
5. **Keep a fixture for the regression.** Once you find a case that broke your
   assumption, pin it as its own test with a comment saying what it protects.
6. **Keep one exact assertion where exactness is real.** `merge()` of two
   identical sketches must equal one sketch; a saved sketch must reload to an
   identical count; `memory_bytes` must be exactly `2**p`. Those are exact
   and should be tested exactly.

## The Balanced Form

| Property | Test style | Example |
|----------|-----------|---------|
| Statistical / approximate | invariant + tolerance | estimate within 2.5% of truth over 12 samples |
| Deterministic / exact | exact equality | `merge(a, a).count() == a.count()` |
| Structural | invariant over a family | `memory_bytes == 2**p` for every `p` in 5..14 |
| Error handling | must raise | `merge()` across precisions raises `ValueError` |

A suite that only has exact assertions is brittle. A suite that only has
tolerance assertions is vague. Use both.

## The Transferable Lesson

> **A test that fails when you change a constant is a change-detector, not a
> correctness test.** The value of a test is that it fails when the product
> is wrong. If you update the expected numbers to match new output, the test
> has stopped testing.
>
> The property-based framing is what surfaced three wrong assumptions during
> the tiny-hll build. Those bugs were in the *tests*, and they would have
> shipped as wrong expectations in the guide.
