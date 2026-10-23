# tiny-graph Guide

## Repo
https://github.com/hussain-alsaibai/tiny-graph

## What It Does

Zero-dependency property graph for Python. One file, no setup. Nodes, edges, and
property-based traversal.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_graph import Graph`.
**There is no `Graph` class.** Verified against upstream `tiny_graph.py`:

```
Node, Edge, PropertyGraph
```

The container is **`PropertyGraph`**; `Node` and `Edge` are the element types.

## Quick Start

```python
from tiny_graph import PropertyGraph

g = PropertyGraph()
a = g.add_node("a", label="service")
b = g.add_node("b", label="service")
g.add_edge(a, b, type="calls")

for node in g.neighbors(a, direction="out"):
    print(node.props)
```

## When to Use

- Modelling relationships between agents, tools, services, or documents
- Traversal with per-node and per-edge properties
- Dependency-free graph algorithms where a full graph library is overkill

## Related

- `tools/dev-tools-comparison-guide.md` — ecosystem-level positioning
