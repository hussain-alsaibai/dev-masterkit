# tiny-semantic-cache Guide

> Vector-similarity cache with BM25 + cosine scoring, auto-threshold detection, TTL, and LRU eviction. ~452 LOC. Zero dependencies.

**Repo:** https://github.com/hussain-alsaibai/tiny-semantic-cache
**Last Verified:** 2026-08-31

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
