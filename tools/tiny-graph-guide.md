# tiny-graph Guide

**Repo:** [hussain-alsaibai/tiny-graph](https://github.com/hussain-alsaibai/tiny-graph)  
**Size:** ~450 LOC | **Deps:** 0 (stdlib-only) | **Last verified:** 2026-07-24

> Zero-dependency, stdlib-only in-memory property graph for Python.

## What it does

An in-memory property graph implementation using only Python's standard library. Nodes and edges support arbitrary properties, and the graph provides traversal and query operations.

## When to use

- **Knowledge graphs** for AI agent context — build a graph of facts, traverse to find related entities
- **Relationship mapping** — social graphs, dependency graphs, entity linking
- **Graph-based reasoning** — path finding, reachability queries, property-based filtering
- **Lightweight graph DB replacement** — when you don't want to deploy Neo4j

## Key patterns

```python
from tiny_graph import Graph

g = Graph()
g.add_node("Alice", role="engineer", team="backend")
g.add_node("Bob", role="manager")
g.add_edge("Alice", "Bob", type="reports_to")
g.add_edge("Alice", "Charlie", type="collaborates_with")

# Traverse
for node in g.neighbors("Alice", edge_type="reports_to"):
    print(node)
```

## Related

- `tiny-memory` — agent memory that could use a graph backend for structured knowledge
- `tiny-chain` — LLM chain that can extract graph relationships from text
- `tiny-embed` — embeddings that can augment graph similarity searches
