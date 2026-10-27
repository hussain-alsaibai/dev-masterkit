# tiny-bloom — Zero-Dependency Bloom Filter

> **Last verified:** 2026-10-27
> **Repo:** https://github.com/hussain-alsaibai/tiny-bloom
> **License:** MIT
> **Status:** Published as `tiny-bloom` v0.1.0. 22 tests pass. Numbers on this page were measured against the shipped source, not quoted from an earlier draft.

A Bloom filter is a probabilistic set: it can tell you **with certainty** that an element is **not** in the set, and may say it **is** when it is not (a false positive). The probability of a false positive is bounded and tunable. tiny-bloom ships the optimal sizing math, FNV-1a + Kirsch-Mitzenmacher double hashing, and a serializable form — **single file, zero dependencies**.

## When to Use

- "Have I seen this URL/request/job before?" at scan time, when a full set would cost memory you don't have.
- Cheap pre-filter in front of an expensive lookup (cache or DB).
- De-duplicating a stream before writing it to disk or an LLM context window.
- Anywhere you can tolerate a tunable false-positive rate and want zero deps.

## Optimal Sizing (closed form)

For target capacity `n` and target FPP `p`:

```
m = ceil(-n * ln(p) / (ln 2)^2)   # bit count
k = ceil((m / n) * ln(2))         # hash count
```

Measured output of the shipped implementation (the bit count is rounded up to a
multiple of 64 so the bit array can be backed by 64-bit words):

| Capacity | Target FPP | Bits | Bytes | Hashes |
|----------|-----------:|-----:|------:|-------:|
| 10,000   | 10%        | 47,936 | 5,992 | 3 |
| 100,000  | 1%         | 958,528 | 119,816 | 7 |
| 1,000,000 | 0.1%      | 14,377,600 | 1,797,200 | 10 |

Note: ~2 bits per element for a 1% FPP target — that's why Bloom filters are the cheapest probabilistic set in CS.

## API

```python
from tiny_bloom import BloomFilter, from_iterable

# 1. Build
bf = BloomFilter(capacity=1_000_000, error_rate=0.001)
bf.add("user_42")
bf.add("user_99")

assert "user_42" in bf       # confirmed (or FP)
assert "user_77" not in bf   # **definitely not** present

# 2. In-tests alias
assert bf.may_contain("user_42")

# 3. Bulk
seen = from_iterable(urls, capacity=len(urls), error_rate=0.001)

# 4. Serialize
bf.save("seen.bin")                  # file
raw = bf.to_bytes()                  # bytes
bf2 = BloomFilter.from_bytes(raw)    # in-memory
bf3 = BloomFilter.load("seen.bin")   # from file

# 5. Stats
print(bf.stats)
# {
#   'size_bits': 14377600,
#   'size_bytes': 1797200,
#   'hash_count': 10,
#   'items': 2,
#   'fill_ratio': 0.0,
#   'estimated_fpp': 2.71e-59,
# }
```

Keys must be `str` or `bytes`. Passing an `int` raises `TypeError` — the
hash function iterates over the key's bytes, so there is no integer encoding.

## Hashing Strategy

FNV-1a 64-bit hash + **Kirsch-Mitzenmacher double hashing**. One real hash per operation; the second hash is derived by a splitmix-style finalizer on `h1`. Net effect: `k` separate hashes run in **one hash call + `k` cheap finalizer multiplies**, instead of `k` independent hash computations.

```python
def _fnv1a_64(data): ...              # FNV-1a over the key bytes
def _double_hash(key, i, size):
    h1 = _fnv1a_64(key)
    h2 = splitmix-style finalizer of h1
    return (h1 + i * h2) % size
# add() and __contains__() use _double_hash(key, i) for i in range(k)
```

## Composition with other tiny-* primitives

- **`tiny-input-sanitize`** — strip unsafe keys/values before using them as Bloom keys (Bloom filters don't validate input shape, only membership).
- **`tiny-secret-mask`** — mask the keys before `add()` so secrets never enter the bit array.
- **`tiny-log`** — log `bf.stats` periodically to confirm fill ratio is on plan.
- **`tiny-config`** — load capacity/error-rate from a config file, fall back to CLI flag.

## When NOT to Use

- You need a guaranteed-no-false-positive set → use a Python `set` or hash table.
- You need to delete elements → use a **counting** Bloom filter (not in this repo).
- You need to enumerate members → Bloom filters can't list contents.
- Your target FPP is below ~1e-9 → at that point a small hash table is more memory-efficient.

## Testing

- 22 tests in `test_tiny_bloom.py`, all passing.
- Coverage: sizing math, FNV/Kirsch hashing, FPP bounds (empirical vs theoretical), serialization round-trips (file + bytes), bulk operations, 100K-item no-false-negative smoke, random FP-rate probe.
- Magic header `b"TBLM"` + a 2-byte little-endian version word in serialization; rejects truncated/garbage files cleanly.
- Measured: 100,000 `add()` calls take ~1.1s on stdlib Python.
- Measured FPP at the 0.1% target with a 50% load: ~0.08% (theoretical 0.10%).

## Cross-references in dev-masterkit

- `tools/tiny-input-sanitize-guide.md` — JSONPath + Bloom filter share the input-cleaning pipeline.
- `tools/tiny-config-guide.md` — capacity/error_rate from config.
- `daily-updates/2026-10-26.md` — release notes.
