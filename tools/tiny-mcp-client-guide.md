# tiny-mcp-client — Zero-Dependency MCP Client (stdio + SSE/HTTP)

**Repo:** github.com/hussain-alsaibai/tiny-mcp-client
**Install:** pip install tiny-mcp-client

> **Not published (verified 2026-11-03).** `pip install tiny-mcp-client` fails - the
> name returns **HTTP 404** on the PyPI JSON API. Install from the
> repository instead:
>
> ```bash
> pip install git+https://github.com/hussain-alsaibai/tiny-mcp-client.git
> ```
**Last verified:** 2026-11-07 — fresh clone of `main`, `pytest -q` -> **40 passed**.

Connect to any MCP server (Claude Desktop, Cursor, custom). Stdio subprocess or SSE/HTTP transport. Auto-introspection of tools/resources/prompts. CLI included.

## Capability negotiation (added 2026-11-07)

A missing capability in the `initialize` result means *not implemented*, not
*not yet asked*. The client used to parse `capabilities` and then ignore it, so
calling `tools/list` on a server that never advertised `tools` surfaced as an
opaque `-32601 Method not found` — a transport-shaped error for a
contract-shaped defect.

```python
from tiny_mcp_client import Client, MCPCapabilityError

client = Client(...)
client.capabilities            # exactly what initialize advertised (dict)
client.supports("tools")       # bool, no exception
client.list_tools()            # raises MCPCapabilityError if "tools" absent
try:
    client.list_tools()
except MCPCapabilityError as exc:
    exc.capability, exc.method, exc.code   # "tools", "tools/list", -32601
except MCPError:                            # unchanged: still one hierarchy
    ...
```

| surface | behaviour |
|---|---|
| `capabilities` | `{}` before `initialize`, the advertised dict after |
| `supports(name)` | `False` for absent, `False` for a non-dict `capabilities` payload |
| `list_tools()` / `call_tool()` | `MCPCapabilityError` when the capability is absent |
| `MCPCapabilityError` | subclasses `MCPError`, code `-32601`, carries `.capability` / `.method` |

**The guard fails open, so a positive-only suite cannot see it.** Deleting
`_require()` leaves every happy-path test green. Proved by mutation: stub the
guard out and 5 of 40 tests fail; restore it and 40 pass. One of the seven new
tests is a positive control, so the guard cannot be satisfied by blocking
everything.

**A malformed `capabilities` is an absent one.** A server that sends
`"capabilities": "tools"` (a string) advertised nothing; treating it as a
container raises `TypeError` from inside a property, which is a crash where a
named error belongs.

**The server side is still open.** `tiny-mcp-server` implements
`tools/list` and `tools/call` unconditionally: a request for
`resources/list` returns `-32601 method not found` rather than `initialize`
never having advertised `resources`. Measured 2026-11-07 against a fresh clone
(`16 passed`). Two parsers disagreeing about the same document is the same
defect class.
