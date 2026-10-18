# 2026-10-18 — Developer Tools Landscape

**Theme:** Query engine + cache stampede protection + RFC 9535 — three small primitives
that close three production holes that every in-memory store eventually reinvents badly.

**Last verified:** 2026-10-18

---

## 1. Index-aware query planning is the cheap next step for any in-memory store

`snapdb` v0.18.0 ships a planner that walks HashIndex (equality) and RangeIndex
(gt/gte/lt/lte) before falling back to a linear scan. 31.5x speedup on a 50K-row narrow
range scan (500 matches), no API change for callers, and the new `Query.explain()`
returns the chosen plan so reviewers can confirm the index actually got picked.

**Cross-ecosystem context:** SQLite, DuckDB, and Postgres all ship cost-based planners.
Python in-memory stores (pickleDB, tinydb, pickled) ship none. The pattern is the same:
walk the available indexes by operator, pick the most selective, fall back to scan. The
`Query.explain()` return shape (a plain dataclass) is the cheapest way to make the
planner observable — without introspection the planner is a black box and the next
contributor can't tune it.

**When to ship your own:** you've crossed ~10K rows and the same query is hitting the
linear scan path. Verify with `Query.explain()` (returns `linear` not `hash_index` /
`range_index`) — if so, add the missing index type before reaching for a bigger store.

---

## 2. Single-flight caching is the universal cache-stampede fix

`fast-cache` v0.7.2 ships `SingleFlightCache` — per-key `threading.Event` so N
concurrent misses share one factory call (different keys still run in parallel).
`SingleFlightStats` exposes `loads / shared / waiters / peak_waiters` so the cache
itself reports how often the stampede protection actually fired.

**Cross-ecosystem context:** Go's `singleflight` package (since 2014), Java's
`LoadingCache.get(key, loader)` (Guava, since 2010), Redis's `SETNX` + Lua scripts.
The Python stdlib has had no equivalent until now. The pattern: one dict
(key → in-flight `Event`), one `threading.Lock` only around the dict insert, factory
called once per in-flight key, all waiters wake on `Event.set()`.

**Invariant that's easy to get wrong:** if the factory raises, the in-flight slot MUST
be cleared (and the `Event` set), otherwise every future caller for that key hangs
forever waiting on a dead `Event`. This is the same class of bug as the v0.7.1 CRDT
slot bug in the same repo — "fail fast, free the slot" is the family-wide invariant.

**When to ship your own:** any cache whose factory hits a slow backend (DB, HTTP, RPC)
and whose keys are popular enough to attract concurrent misses. Verify by looking at
`SingleFlightStats.shared` — if it's >0 under steady-state load, the protection is
actually firing.

---

## 3. RFC 9535 finally gives JSON the query semantics 0.7.x Goessner users hand-roll

`tiny-jsonpath` v0.1.0 is a ~830-LOC stdlib-only RFC 9535 (JSONPath 1.0) parser.
Supports root, members, indexing, slicing (all 8 forms), wildcard, recursive descent,
unions, filter expressions with &&/||/=~, with caret-pointed `JSONPathError` messages.

**Cross-ecosystem context:** IETF finalized JSONPath as RFC 9535 in 2024. Goessner's
0.7.x draft (circa 2007) is what `jsonpath`, `jsonpath-ng`, and most hand-rolled queries
still use. The two diverge in three places users care about: filter expressions
(`[?(@.x > 5)]`), recursive descent (`..name`), and union selectors
(`[a, b, c]`). RFC 9535 makes all three first-class syntax; Goessner makes them script
expressions that need a separate evaluator.

**When to ship your own:** any code path that takes a JSON query string from a caller
and slices a document by it. The cost of `pip install jsonpath-ng` is small but the
dependency surface is not — `tiny-jsonpath` is stdlib-only and runs anywhere CPython
runs. Pair with `tiny-input-sanitize` (`jsonpath` context) for safe querying of
untrusted queries.

**When NOT to ship your own:** >10k docs/sec (use `python-jsonpath-rfc9535` with its
compiled cache), or cross-doc comparisons (`$..book[?(@.price < $.max)]`), or Goessner
script expressions (`$.store.book[(@.length-1)]`) — out of scope for this subset.

---

## Shipped this cycle

- `snapdb` v0.18.0 — index-aware query planning (HashIndex + RangeIndex), Query.between(),
  Query.explain(). 33 new tests, 213/213 pass.
- `fast-cache` v0.7.2 — SingleFlightCache + SingleFlightStats. 15 new tests, 74/74 pass.
- `tiny-jsonpath` v0.1.0 — RFC 9535 parser, stdlib-only, ~830 LOC. 49/49 tests pass.

## Family-wide patterns observed

- **Sidecar modules for non-breaking feature drops** — `fast_cache_v072.py` continues
  the pattern set by `fast_cache_v071.py` (Oct 12). Same invariants: `from __future__
  import annotations` header, `__version__ = "X.Y.Z"`, no `__init__` re-exports,
  separate test file (`test_v072_additions.py`), `### Added` CHANGELOG entry.
- **Counter objects as the universal metrics export** — `SingleFlightStats` follows the
  same pattern as `HeaderStats`, `RedactionStats`, `LimiterStats`. Three or four
  fields with `as_dict()` for /metrics.
- **Planner introspection > planner obscurity** — both `Query.explain()` and
  `SingleFlightStats` let reviewers see what the optimization actually did. The
  pattern is small but worth documenting: any primitive that picks a strategy should
  ship a way to ask "what strategy did you pick?"
- **Stdlib-only is the family default** — `tiny-jsonpath` is the 21st tiny-* repo with
  zero deps. `snapdb` and `fast-cache` are too. The dependency surface of the
  ecosystem is essentially zero — everything runs on whatever Python version you
  already have.

## Adjacent projects to watch

- `python-jsonpath-rfc9535` — alternative RFC 9535 implementation with a compiled cache.
  Use this if `tiny-jsonpath` becomes a throughput bottleneck (>10k docs/sec).
- `jsonpath-rfc9535` (Rust core, Python bindings) — the fastest option but pulls a
  Rust toolchain into your build. Worth it for hot paths.
- `pickleDB` — small in-memory dict store. No index-aware planning yet. The `snapdb`
  v0.18.0 pattern is a clean drop-in if they want to ship it.
- `cachetools` — alternative in-memory caching. Has `LRUCache`/`TTLCache` but no
  `SingleFlightCache` primitive yet.

## References

- RFC 9535 — https://www.rfc-editor.org/rfc/rfc9535.html (JSONPath 1.0)
- Go's singleflight — https://pkg.go.dev/sync/singleflight
- Guava LoadingCache — https://guava.dev/releases/19.0/api/docs/com/google/common/cache/LoadingCache.html
- snapdb repo — https://github.com/hussain-alsaibai/snapdb
- fast-cache repo — https://github.com/hussain-alsaibai/fast-cache
- tiny-jsonpath repo — https://github.com/hussain-alsaibai/tiny-jsonpath