# tiny-mcp-gateway — MCP Proxy & Router

**Created:** 2026-08-04
**Last verified:** 2026-08-04
**Author:** OpenClaw / hussain-alsaibai
**Repo:** https://github.com/hussain-alsaibai/tiny-mcp-gateway
**License:** MIT | **LOC:** ~580 | **Tests:** 24 passing | **Deps:** 0

## What It Does

Zero-dependency MCP proxy/gateway server. Aggregate multiple MCP servers behind one endpoint, route by tool prefix, enforce auth + rate limits.

## When to Use

- Connecting multiple MCP servers behind a single agent
- Routing MCP tools by prefix across backends
- Adding auth/rate-limiting layer to existing MCP servers

## Key Features

- Register multiple MCP backends (HTTP/SSE or stdio subprocess)
- Route by tool prefix (e.g. `github/*` → GitHub MCP)
- Default backend fallback
- API key authentication
- Per-key rate limiting
- Priority-based routing

## Quick Start

```python
from tiny_mcp_gateway import MCPGateway, Backend

gw = MCPGateway(port=8080)
gw.add_backend(Backend(name="github", url="https://api.github.com/mcp"))
gw.route_tool("github/", "github", priority=10)
gw.set_default_backend("github")
gw.add_api_key(label="my-agent", rate_limit=100)
gw.run()
```

## Integration

- **tiny-agent** — MCP server endpoint for the reasoning loop
- **tiny-mcp-client** — Connect to external MCP servers
- **tiny-rate-limiter** — Per-key rate limiting enforcement
