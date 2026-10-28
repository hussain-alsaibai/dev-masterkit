# tiny-semantic-cache Guide

> Vector-similarity cache with BM25 + cosine scoring, auto-threshold detection, TTL, and LRU eviction. ~452 LOC. Zero dependencies.

**Repo:** https://github.com/hussain-alsaibai/tiny-semantic-cache
**Last Verified:** 2026-10-28 - **20 tests passing** (measured by run against
the upstream clone). The package had **no CI** until 2026-10-28; adding it
found a defect that made the library's central function unusable.

## The `cosine_similarity` Defect (fixed 2026-10-28)

`cosine_similarity()` raised **`NameError` on every call**:

```python
# BROKEN - `x` is not in this generator
norm_b = math.sqrt(sum(x * y for y in b))

# CORRECT
norm_b = math.sqrt(sum(y * y for y in b))
```

This is the similarity function the whole package is built on, so **every
semantic lookup was broken**. It shipped because the package had a test suite
and **no CI workflow** - nothing executed the tests on every change.

Three further test defects were fixed in the same pass: two tests called
`llm(prompt)` when the library calls `call_fn()` with no arguments, and two
referenced a bare `cache` name that does not exist in the fixture.

Packaging was fixed too - the wheel shipped **no importable module**, because
`[tool.setuptools.packages.find]` with `include = ["tiny_semantic_cache*"]`
finds nothing (a single module is not a package). It now uses
`[tool.setuptools] py-modules = ["tiny_semantic_cache"]`.

Also note: the PyPI name `tiny-semantic-cache` is **free** (verified
2026-10-28), but the package is not published there yet.

## Quick Start

```python
from tiny_semantic_cache import SemanticCache

cache = SemanticCache(
    similarity_threshold=0.75,
    max_size=1000,
    ttl=3600
)

# Store
cache.set("fetch_user_data", {"user_id": 42}, result)

# Retrieve (query doesn't need exact match)
hit = cache.get("fetch_user_data", {"user_id": 42})
```

## Key Features

- BM25 + cosine similarity scoring
- Auto-threshold: dynamically learns best threshold from hit distribution
- TTL + LRU eviction
- JSON-serializable keys and results
- Zero dependencies (Python stdlib only)

## When to Use

- AI agent pipelines that repeat semantically similar queries
- RAG systems with near-duplicate retrieval calls
- API response caching where exact key matching is too strict
