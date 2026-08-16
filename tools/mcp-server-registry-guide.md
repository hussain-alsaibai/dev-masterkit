# Tool Guide: mcp-server-registry

> **Last verified:** 2026-08-16
> **Repo:** https://github.com/hussain-alsaibai/mcp-server-registry
> **License:** MIT

## What it is

Curated catalog of Model Context Protocol (MCP) servers organized by category. TL;DR table with top pick + runner-up per category for quick decision-making.

## When to use

- Selecting an MCP server for a specific integration (GitHub, DB, Web, Slack, etc.)
- Evaluating MCP options when building agent tool registries
- Quick lookup for MCP server capabilities

## Quick reference

| Category | Top Pick | Runner Up |
|----------|----------|-----------|
| GitHub | `github-mcp-server` | `mcp-github` |
| Filesystem | `filesystem-mcp` | stdio-fs |
| Database | `postgres-mcp` | `sqlite-mcp` |
| Web | `fetch-mcp` | `brave-search-mcp` |
| Slack | `slack-mcp` | — |
| Notion | `notion-mcp` | — |
| AWS | `aws-mcp` | — |

## Related tools

- `tiny-mcp` — build your own MCP server in one file
- `tiny-mcp-gateway` — aggregate and route multiple MCP servers
- `tiny-mcp-observability` — tracing/metrics for MCP pipelines
- `mcp-duckgo` skill — DuckDuckGo search MCP integration
