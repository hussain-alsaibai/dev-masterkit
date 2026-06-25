# SnapDB — Ultra-Lightweight In-Memory Database

## What This Tool Does

Pure Python in-memory database with zero dependencies. Memory-mapped storage,
hash indexes, WAL transactions, and MongoDB-style DocumentStore API.
1.2M reads/sec.

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
- Memory-mapped files (mmap)
- Hash indexes for O(1) lookups
- WAL transactions (durability)
- JSON/BSON serialization
- Thread-safe
- 1.2M reads/sec benchmarked

## Versions

| Version | Date | Features |
|---------|------|----------|
| v0.2.0 | 2026-06-25 | Query engine, DocumentStore, hash indexes, WAL |
| v0.1.0 | 2026-06-23 | Initial release, key-value API |

## Last Verified: 2026-06-25
