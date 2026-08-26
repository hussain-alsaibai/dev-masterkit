# tiny-tool-registry — Zero-Dependency Dynamic Tool Registry

**Repo:** https://github.com/hussain-alsaibai/tiny-tool-registry
**Install:** `pip install tiny-tool-registry`
**Last verified:** 2026-08-24

---

## What It Does

Zero-dependency dynamic tool registry with versioning, discovery, and hot-reload for AI agents. Register tools at runtime, version them, discover by capability, and reload without restart.

## Quick Start

```python
from tiny_tool_registry import ToolRegistry

registry = ToolRegistry()

@registry.register(version="1.0.0")
def summarize(text: str) -> str:
    return text[:100]

# Discover all tools
for tool in registry.list_tools():
    print(tool.name, tool.version)

# Hot-reload
registry.reload()
```

## When to Use

- AI agents that need dynamic tool registration
- Systems requiring plugin-style extensibility without imports
- Tool versioning and capability discovery
- Live code updates without restart

## See Also

- `tiny-checkpoint` — crash recovery + state snapshots
- `tiny-state` — state machine patterns
