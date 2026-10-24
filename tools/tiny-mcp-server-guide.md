# tiny-mcp-server — Build MCP Servers in One Python File

**Repo:** github.com/hussain-alsaibai/tiny-mcp-server
**Install:** `pip install tiny-mcp-server` or copy `tiny_mcp_server.py`
**Version:** 0.2.0 (2026-10-24) — migrated to the 2026-07-28 MCP revision
**Last verified:** 2026-10-24 (16/16 by test run)

One-file Python framework for building Model Context Protocol servers. Zero
dependencies, stdio + SSE transports, auto JSON Schema from type hints.

> **Guide rewritten 2026-10-24.** The previous version of this guide was last
> verified 2026-08-18 and was wrong on three counts: it gave ~400 LOC (the
> module is now 783), it did not mention the protocol revision, and it listed
> a `ping` transport story that the current revision removed.

## Protocol support

Speaks the **2026-07-28** MCP revision:

- `server/discover` — advertises `supportedVersions`, `capabilities`, identity
- Every request may carry its protocol version in `_meta`; an unknown version
  returns `-32022` with the list of supported versions
- Every result carries `resultType` and the server identity in `_meta`
- `tools/list` and `server/discover` carry `ttlMs` + `cacheScope`

The legacy `initialize` handler is **kept** and still answers. Every server
observed in the wild that speaks the current dialect also kept it, and it costs
nothing — a legacy client and a current client can both talk to the same
server. This is the **dual-dialect bridge**, and it is the pattern the field
actually uses (0 of 400 probed servers had removed `initialize`).

## Key Features

- `@tool` decorator — turn any function into an MCP tool in one line
- `Server` class with `stdio` and `sse` transports
- Auto-generates JSON Schema from Python type annotations + docstrings
- MIT licensed, 783 LOC, zero runtime dependencies

## API

| Symbol | Purpose |
|---|---|
| `@tool` / `@server.tool` | Register a function as an MCP tool |
| `Server(...)` | The server object |
| `Server.register(tool_obj)` | Register a pre-built `Tool` |
| `Server.run(transport="stdio", **kwargs)` | Start the transport |
| `Server.handle_message(message) -> dict | None` | Single entry point for one JSON-RPC message |
| `Tool` / `ToolError` | Tool record and its error type |

Verified against `tiny_mcp_server.py`, 2026-10-24. Note `ping` is still
handled (`_handle_ping`) but `ping` was removed as a core method in the
2026-07-28 revision — the handler is kept for the same compatibility reason
as `initialize`.

## When to Use

- A single-file MCP server with no dependency footprint
- When you need auto-generated JSON Schema from type hints
- When you want a legacy-compatible server that current clients can still
  reach

## See Also

- `tools/tiny-mcp-skel-guide.md` — the stdlib-only skeleton (the lighter sibling)
- `tools/tiny-mcp-audit-guide.md` — audit your manifest before shipping it
- `prompts/mcp-dual-dialect-bridge.md` — why the bridge exists
- `reports/2026-10-24-mcp-dialect-migration.md` — the 400-server census

---

**Last verified:** 2026-10-24
