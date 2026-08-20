---
name: tiny-mcp-registry
description: "Zero-dependency MCP server discovery and health checker. Last verified: 2026-08-20."
---

# tiny-mcp-registry Guide

> Zero-dependency MCP server discovery and health checker. MIT.
> GitHub: https://github.com/hussain-alsaibai/tiny-mcp-registry

## What It Does

`tiny-mcp-registry` manages the lifecycle of MCP servers on your machine — tracks installed servers, their commands/args/env vars, and whether they are currently operational.

## Features

- **Persistent Registry** — store server commands, args, and environment variables
- **Health Checks** — verify servers are responsive before long agent runs
- **Zero Dependencies** — pure Python, no external libraries
- **Agent-Ready** — clean API for agents to discover their own capabilities
- **Single-file** — MIT license

## Use Cases

- Track all installed MCP servers across projects
- Health-check before starting agent runs
- Self-discovery for agent tool registries
- Backup/restore MCP server configs

## Quick Start

```python
from tiny_mcp_registry import TinyMCPRegistry

reg = TinyMCPRegistry()

# Register a new server
reg.register(
    name="github-mcp",
    command="npx",
    args=["@modelcontextprotocol/server-github"],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": "..."}
)

# Check health
if reg.check_health("github-mcp"):
    print("GitHub MCP is ready!")

# List all
for s in reg.list_servers():
    print(f"{s['name']}: {s['status']}")
```

## Install

```bash
pip install tiny-mcp-registry
```

## Related Tools

- `tiny-mcp-server` — build your own MCP server in one file
- `tiny-mcp-observability` — tracing/metrics for MCP pipelines
- `mcp-server-registry-guide` — curated catalog of MCP servers by category
