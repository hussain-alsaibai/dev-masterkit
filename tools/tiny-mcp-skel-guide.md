# tiny-mcp-skel Guide

**tiny-mcp-skel** — Stdlib-only MCP server skeleton. ~150 LOC of executable code, one file, built from three tiny-* primitives (tiny-router blueprints for dispatch, tiny-validator for the McpServer schema, optional tiny-router-sse for streaming). Speaks the **2026-07-28** MCP revision.

- **Repo:** hussain-alsaibai/tiny-mcp-skel (local clone: `~/workspace/tiny-mcp-skel`)
- **Install:** `pip install tiny-mcp-skel` (pulls `tiny-router>=0.7.0`, `tiny-validator>=0.5.0`)
  - **The PyPI install line cannot work — checked 2026-10-26.** `tiny-validator` has
    **no PyPI project at all** (the JSON endpoint 404s), and `tiny-router`'s
    newest release on PyPI is **0.0.8**, while this package pins `>=0.7.0`.
    CI therefore installs its siblings **straight from GitHub**:

    ```yaml
    pip install "tiny-router @ git+https://github.com/hussain-alsaibai/tiny-router.git"
    pip install "tiny-validator @ git+https://github.com/hussain-alsaibai/tiny-validator.git"
    ```

    A hardcoded `/home/node` path in the test bootstrap was removed in the same
    commit — it made the suite pass on exactly one machine.
- **Size:** 605 lines total, ~150 executable; 0 external runtime deps beyond the two tiny-* siblings
- **Tests:** 43 passing (verified by run, 2026-10-24)
- **Last verified:** 2026-10-26 (43/43 by test run; `server/discover` handler confirmed against the vendored 2026-07-28 JSON Schema)

## Why This Exists

The 2026-07-28 MCP revision removed the `initialize` handshake, made MCP
stateless, and made `server/discover` mandatory. A server that only answers
`initialize` is not merely deprecated — it is **invisible** to a current
client. There is no negotiation fallback in the revision.

A live probe of 400 registry servers on 2026-10-24 found **73 of the 79** that
answered at all still speak only the legacy dialect. `tiny-mcp-skel` v0.2.0 is
our answer to that: a skeleton that starts on the current dialect rather than
one that has to be migrated later.

## The API

```python
from tiny_mcp_skel import make_server, run_stdio
from tiny_validator import Schema, String

server = make_server(name="echo-mcp", version="0.2.0", title="Echo MCP")

@server.tool(
    name="echo",
    description="Echo the input.",
    input_schema=Schema({"text": String()}),
)
def echo_handler(params):
    return {"text": params["text"]}

run_stdio(server)
```

Public surface (verified against `tiny_mcp_skel.py`, 2026-10-24):

| Symbol | Purpose |
|---|---|
| `make_server(...) -> McpSkelServer` | Build a server instance |
| `McpSkelServer.tool(...) / .manifest() / .list_tools() / .call_tool()` | Register tools, expose the manifest, dispatch |
| `McpSkelServer.discover(request_id) -> McpResponse` | The `server/discover` handler |
| `McpSkelServer.handle(request: McpRequest) -> McpResponse` | Single entry point for every method |
| `McpSkelServer.as_router() -> Router` | Drop the server into a tiny-router blueprint |
| `McpRequest` / `McpResponse` | Request/response envelopes |
| `McpCallError(code, message)` | Raised on tool dispatch failure |
| `run_stdio(server, *, input_stream=None, output_stream=None)` | stdio transport |

Methods actually implemented: `server/discover`, `tools/list`,
`tools/call`. `ping` was removed as a core method in the 2026-07-28
revision and is not implemented.

## The dialect details that matter

- `PROTOCOL_VERSION = "2026-07-28"`; `SUPPORTED_PROTOCOL_VERSIONS = ("2026-07-28",)`
- The protocol version is also read from the request's
  `_meta.io.modelcontextprotocol/protocolVersion`, so a client can pin a revision.
- **Every result carries the protocol version.** A result without it is not
  conformant with the current revision.
- `server/discover` is the entry point for up-front version negotiation — it
  returns supported versions, capabilities, and identity in one round trip.

## CI validates against the upstream schema

```
.github/workflows/ci.yml
```

runs the suite across Python 3.8-3.12, then runs a dedicated
`TestSchemaConformance` case that validates responses against
`tests/schema-2026-07-28.json` — the vendored upstream JSON Schema.

**This is the pattern worth copying.** The spec is the test oracle, and the
oracle is versioned into the repo, so a spec change shows up as a failing
test rather than as drift nobody notices. Compare
`prompts/readme-claims-must-be-runnable.md` — a doc that a test can drift
will drift.

## Status

The repo does not exist on GitHub yet — `GET /repos/hussain-alsaibai/tiny-mcp-skel`
returns **404** as of 2026-10-24. The local clone has README, LICENSE, CI, a
CHANGELOG, `llms.txt`, an example server, and a vendored schema, and the git
tree has zero committed junk (`__pycache__`/`.pyc`). Treat the install line
above as the intended distribution, not a live one.

## See Also

- `tools/tiny-mcp-audit-guide.md` — the auditor that flags a server speaking the legacy dialect
- `tools/tiny-mcp-server-guide.md` — the other one-file MCP framework in the family
- `prompts/mcp-manifest-trust-gate.md` — gating on manifest trust before connecting
- `reports/2026-10-24-mcp-dialect-migration.md` — the 400-server census behind this guide
