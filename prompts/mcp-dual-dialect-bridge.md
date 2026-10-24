---
name: mcp-dual-dialect-bridge
description: Migrate an MCP server to the 2026-07-28 spec revision by adding server/discover while keeping initialize as a compatibility shim, instead of cutting over. Trigger when a client reports a server as unreachable, when -32601 is returned for server/discover, or when auditing a manifest for protocol-version drift.
last_verified: 2026-10-24
---

# MCP Dual-Dialect Bridge

## Why

The 2026-07-28 MCP revision removed the `initialize` handshake, made MCP
stateless, and made `server/discover` **MUST**-implement. There is no
negotiation fallback. A current client calls `server/discover` and gets
`-32601` — the server is not deprecated, it is **invisible**.

The obvious response is a cutover: delete `initialize`, implement
`server/discover`, ship it. **The measured field data says that is wrong.**

A live probe of 400 registry servers (2026-10-24) found:

| Dialect | Count | Share |
|---|---|---|
| Legacy only — `initialize` works, `server/discover` returns -32601 | 73 | 92.4% |
| **Dual-dialect bridge** — both work | **6** | **7.6%** |
| Current only — `initialize` removed | **0** | **0%** |

**Not one server in the sample removed `initialize`.** Every server that
migrated did it by *adding* `server/discover` on top of the old handshake and
keeping both. The spec says the handshake is removed; the ecosystem is using
it as a compatibility shim, and that is the behaviour that actually works.

## Procedure

### 1. Measure before you migrate

Do not assume. Classify the population with two requests per server:

```python
# Modern probe: spec-shaped discovery request
POST <remote_url>
Mcp-Method: server/discover
Content-Type: application/json

{"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {}}

# Legacy probe: the old handshake
POST <remote_url>
{"jsonrpc": "2.0", "id": 1, "method": "initialize",
 "params": {"protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "probe", "version": "0"}}}
```

Classify:

- **modern** — `server/discover` returns a `supportedVersions` array
- **legacy** — `server/discover` returns -32601, `initialize` returns a `protocolVersion`
- **bridge** — both work
- **unclassified** — anything else (a -32602 means the request shape was wrong, not that the server is old)

### 2. Bridge, do not cut over

Keep `initialize` as a compatibility shim for one deprecation window. Add
`server/discover`. Answer both.

```
legacy client --> initialize        (works)
current client --> server/discover  (works)
```

A cutover breaks the legacy half of your users to satisfy a spec line, for a
compatibility path the field has not actually abandoned.

### 3. Report the version in every result

Every result carries the protocol version, and the request's
`_meta.io.modelcontextprotocol/protocolVersion` is honoured when present:

```python
PROTOCOL_VERSION = "2026-07-28"
SUPPORTED_PROTOCOL_VERSIONS = ("2026-07-28",)
META_PROTOCOL_VERSION = "io.modelcontextprotocol/protocolVersion"
```

A result without the version is not conformant with the current revision.

### 4. Validate against the upstream schema, vendored into the repo

```yaml
# .github/workflows/ci.yml
- name: Validate responses against the MCP JSON Schema
  run: python -m unittest tests.test_skeleton.TestSchemaConformance -v
```

Vendor the upstream JSON Schema (`schema/2026-07-28/schema.json`) into
`tests/`. The spec is the test oracle, and the oracle is versioned, so a spec
change becomes a failing test instead of drift nobody notices.

### 5. If you audit manifests, grade the bridge as INFO, not HIGH

If the server implements `server/discover` **and** keeps `initialize`, that
is the recommended pattern, not a finding. Flagging it would be flagging
correctness.

```
legacy server (unreachable)      bridge (recommended)
  [HIGH] MCP070  version '1.0'     [INFO] MCP071 initialize kept as a shim
  [HIGH] MCP071  initialize        grade A, does not block CI
  grade F, blocks CI
```

## What this looks like in code

Real example, `tiny-mcp-skel` v0.2.0 (605 lines, 43 tests passing):

```python
def handle(self, request: McpRequest) -> McpResponse:
    method = request.to_dict().get("method")
    if method == "server/discover":
        return self.discover(request.id)
    if method == "tools/list":
        ...
    if method == "tools/call":
        ...
    if method == "initialize":
        # Kept deliberately as a compatibility shim for one deprecation
        # window. See prompts/mcp-dual-dialect-bridge.md.
        ...
```

## Pitfalls

- **Do not "fix" the legacy handler by deleting it.** 92.4% of reachable
  servers still speak it; your clients may be legacy too.
- **Do not assume `protocolVersion: "1.0"` is old.** It is not a revision
  string in the date-based scheme at all — it is malformed. Flag it as
  malformed (MCP070), not as "a legacy version".
- **Do not trust a registry listing's declared version.** Probe it. One
  server in the sample advertised a pre-standardisation draft shape
  (`protocolVersions` + `compatibility` instead of `supportedVersions`).
- **The registry's own JSON Schema is at `2025-12-11`, one revision behind.**
  The registry's *metadata* schema lags the protocol spec. Do not treat the
  registry as the spec.

## Verification

- **Last verified:** 2026-10-24
- Census: 400 registry servers probed, 79 reachable, 73 legacy-only, 6
  bridges, 0 current-only.
- Shipped in `tiny-mcp-skel` v0.2.0 (43 tests) and `tiny-mcp-server`
  v0.2.0 (16 tests).
- Audited by `tiny-mcp-audit` v0.2.0 check group `protocol` (MCP070-MCP073),
  suite 84 tests.

## See Also

- `reports/2026-10-24-mcp-dialect-migration.md` — the full census
- `tools/tiny-mcp-skel-guide.md` — the shipped implementation
- `tools/tiny-mcp-audit-guide.md` — the auditor that grades the dialect
