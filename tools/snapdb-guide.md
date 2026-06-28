# SnapDB — Ultra-Lightweight In-Memory Database

## What This Tool Does

Pure Python in-memory database with zero dependencies. Memory-mapped storage,
hash indexes, WAL transactions, MongoDB-style DocumentStore API, ClickHouse-inspired
columnar engine, Prometheus-style metrics, and Change Data Capture.
1.2M reads/sec key-value, 7.5M rows/sec columnar aggregates.

## Installation

```bash
git clone https://github.com/hussain-alsaibai/snapdb.git
cd snapdb
pip install -e .
```

## Usage

### Basic Key-Value

```python
from snapdb import SnapDB

db = SnapDB("data.db")
db["key"] = "value"
print(db["key"])  # "value"
```

### Document Store (MongoDB-style)

```python
from snapdb import DocumentStore

docs = DocumentStore("docs.db")
user = docs.insert({"name": "Alice", "age": 30})
results = docs.find({"age": {"$gte": 25}})
```

### Query Engine

```python
results = docs.find({
    "$and": [
        {"status": "active"},
        {"age": {"$gte": 18, "$lte": 65}}
    ]
})
```

## Key Features

- Zero dependencies
- **Columnar engine** — `array.array` per-column storage, null masks, aggregates (sum/avg/min/max/count)
- **Metrics** — Prometheus-style QPS, latency histograms (p50/p95/p99), operation counters
- **CDC** — Change Data Capture with callbacks and file-based replay
- **Batch insert** — 5-10x speedup over single-row inserts
- Memory-mapped files (mmap)
- Hash indexes for O(1) lookups
- WAL transactions (durability)
- JSON/BSON serialization
- Thread-safe
- 1.2M reads/sec key-value, 7.5M rows/sec columnar aggregates

## Versions

| Version | Date | Features |
|---------|------|----------|
| v0.3.1 | 2026-06-28 | Batch insert optimization, pre-fetched column refs, null-skipping aggregates |
| v0.3.0 | 2026-06-28 | Columnar engine, metrics, CDC, 47/47 tests |
| v0.2.0 | 2026-06-25 | Query engine, DocumentStore, hash indexes, WAL |
| v0.1.0 | 2026-06-23 | Initial release, key-value API |

## Benchmarks (100K rows, 5 engines)

### INSERT (batch)
| Engine | ops/sec | Time |
|--------|---------|------|
| DuckDB (DataFrame) | 6.7M | 0.015s |
| Pure Dict | 1.1M | 0.089s |
| **SnapDB Col (batch)** | **656K** | **0.152s** |
| SQLite (batch) | 586K | 0.171s |
| SnapDB Row (batch) | 196K | 0.509s |

### AGGREGATE SUM
| Engine | rows/sec | Time |
|--------|----------|------|
| DuckDB | 96.3M | 0.001s |
| Pure Dict | 17.9M | 0.006s |
| SQLite | 10.9M | 0.009s |
| **SnapDB Col** | **7.5M** | **0.013s** |
| SnapDB Row | ~400K | 0.25s |

### MEMORY (50K rows)
| Engine | Memory | vs DuckDB |
|--------|--------|-----------|
| **SnapDB Row** | **0.6 MB** | **17x more efficient** |
| **SnapDB Col** | **1.5 MB** | **7x more efficient** |
| SQLite | 9.4 MB | 1.1x |
| DuckDB | 10.7 MB | baseline |
| Pure Dict | 16.8 MB | 0.6x |

## Last Verified: 2026-06-28
