# tiny-mcp-server — Build MCP Servers in One Python File

**Repo:** github.com/hussain-alsaibai/tiny-mcp-server
**Install:** `pip install tiny-mcp-server` or copy `tiny_mcp_server.py`
**Last verified:** 2026-08-18

One-file Python framework for building Model Context Protocol servers. Zero dependencies, stdio + SSE transports, auto JSON Schema from type hints.

## Key Features

- `@tool` decorator — turn any function into an MCP tool in one line
- `Server` class with `stdio` and `sse` transports
- Auto-generates JSON Schema from Python type annotations + docstrings
- MIT licensed, ~400 LOC
