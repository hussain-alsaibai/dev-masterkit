# tiny-mcp-audit Guide

**tiny-mcp-audit** — Zero-dependency static security audit for MCP server manifests. 23 checks across 8 groups, 5 severities, a 0-100 posture score with an A-F grade, and a CI-blocking gate. No network I/O, no sandbox, no imports of the audited code.

- **Repo:** hussain-alsaibai/tiny-mcp-audit (local clone: `~/workspace/tiny-mcp-audit`)
- **Install:** `pip install tiny-mcp-audit`
- **Size:** ~1 module, 0 runtime dependencies, Python 3.9+
- **Version:** 0.2.0 (2026-10-24) — added the `protocol` check group
- **Tests:** 84 passing
- **Last verified:** 2026-10-24 (84/84 by test run; `tiny-mcp-skel` and `tiny-mcp-server` audited clean by hand)

## Why This Exists

The manifest is the only artifact an agent reads *before* it decides to trust a
server. Nothing in the stack vets it. A census of 15,465 publicly indexed MCP
servers (OX Security, reported 2026-10-22) found 2.3% on expired domains
anyone can register for $4-12/year, 15.6% hosted outside the US, and 0.45%
reachable only through consumer tunnels on personal machines.

Code review does not close that gap: a remote MCP server runs backend code
that bears no relation to what its public repository shows. Marketplace star
counts are not a security signal either.

This audits the declaration, statically, before a client ever connects.

## Quick Start

```python
from tiny_mcp_audit import audit_file

report = audit_file("server.json")
print(report.score, report.grade)      # 0 F
print(report.has_blocking)            # True -> CI gate
for f in report.sorted_findings:
    print(f"[{f.severity.value}] {f.code} {f.location}: {f.message}")
    print(f"    fix: {f.remediation}")
```

```bash
mcp-audit server.json                       # text, human-readable
mcp-audit server.json --quiet               # one-line summary
mcp-audit server.json --format sarif        # GitHub code scanning
mcp-audit server.json --fail-on high        # exit 1 at HIGH or worse
mcp-audit *.json --checks transport,secrets # narrow the group set
```

## API

| Symbol | Purpose |
|--------|---------|
| `audit_file(path, checks=None)` | Audit a manifest on disk |
| `audit_json(text, checks=None)` | Audit a manifest already in memory |
| `audit_manifest(manifest, checks=None)` | Audit a parsed dict |
| `audit_many(paths, ...)` | Batch, one report per file |
| `CHECK_NAMES` | The 8 check groups |
| `Severity` | `critical / high / medium / low / info` |
| `Finding` | `.code .severity .message .location .evidence .remediation` |

`AuditReport` exposes `score` (0-100), `grade` (A-F), `has_blocking`
(any HIGH or worse — the default CI gate), `max_severity`, `summary`,
`to_json()`, `to_sarif()`.

## The 7 Check Groups

`identity, secrets, transport, resources, tools, prompts, annotations`

Verified finding codes (from auditing `examples/risky-manifest.json`,
2026-10-22 — score 0, grade F, 11 findings):

| Severity | Code | Fires on |
|----------|------|----------|
| critical | MCP031 | resource URI targets a sensitive host path (`file:///root/.ssh/id_rsa`) |
| critical | MCP041 | tool name implies arbitrary command execution and is undocumented |
| high | MCP002 | `serverInfo.version` is floating (`'latest'`) — supply-chain drift |
| high | MCP011 | manifest forwards a sensitive env var (`AWS_SECRET_ACCESS_KEY`) |
| high | MCP020 | transport `sse` uses plaintext http |
| high | MCP030 | resource exposes the host filesystem |
| high | MCP043 | tool declares no input schema |
| high | MCP050 | prompt contains instruction-override language |
| medium | MCP042 | tool has a missing or too-short description |
| low | MCP004 | manifest declares no capabilities |
| low | MCP060 | tool has no `annotations` (`readOnlyHint` / `destructiveHint`) |

The clean example scores 100 / grade A / 0 findings.

## Grading

`score = max(0, 100 - sum(severity_rank * 8))` across findings.
Grades: A >= 90, B >= 75, C >= 60, D >= 40, else F.

The score is a posture summary, not a risk calculation. `has_blocking` is the
signal to gate CI on — a single critical finding is a stop, regardless of how
many low-severity findings sit alongside it.

## Design Rule: Never Echo the Secret

Findings carry the matched *shape* (`AWS_SECRET_ACCESS_KEY`, `id_rsa`) and
never the matched value. That property is asserted by a test and documented in
the repo's SECURITY.md, because it is what makes an audit report safe to publish
in a PR comment or a CI artifact.

If you add a rule that would print a matched value, you have broken the
contract, not added a feature.

## CI Integration

```yaml
- run: pip install tiny-mcp-audit
- run: mcp-audit ./mcp/*.json --fail-on high --format sarif > mcp-audit.sarif
```

Exit code is 1 at or above `--fail-on`. SARIF 2.1.0 output maps findings onto
GitHub code scanning without a translation step.

## Protocol conformance (added v0.2.0, 2026-10-24)

The 2026-07-28 MCP revision removed the `initialize` handshake, made MCP
stateless, and made `server/discover` **MUST**-implement. A live probe of 400
registry servers found **73 of the 79** reachable servers still answer only
`initialize` — they are invisible to a current client, which calls
`server/discover` and gets `-32601`.

The new `protocol` group closes the version-field gap:

| Code | Severity | What it flags |
|---|---|---|
| MCP070 | high | protocol version missing, malformed, or older than the current revision |
| MCP071 | high / info | server exposes a method the current revision removed |
| MCP072 | medium | server advertises a deprecated capability (roots / sampling / logging) |
| MCP073 | medium | server advertises a deprecated transport (HTTP+SSE) |

The revision is read from `protocolVersion`, `protocol_version`, `specVersion`,
`discover.protocolVersions` and `_meta`, so it works against both a raw
manifest and a captured `server/discover` response.

### MCP071 is demoted to INFO when the server bridges

**Every one of the 6 servers that speak the current dialect also kept its
legacy `initialize` handler. None removed it.** Keeping the old handler as a
compatibility shim is the pattern that actually works in the field, so MCP071
drops from HIGH to **INFO** when the manifest also implements
`server/discover`:

```
legacy server (unreachable)      bridge (recommended)
  [HIGH] MCP070  version '1.0'     [INFO] MCP071 initialize kept as a shim
  [HIGH] MCP071  initialize        grade A, does not block CI
  grade F, blocks CI
```

Without `server/discover` the finding stays HIGH, because such a server is
unreachable to current clients. Verified by hand: `tiny-mcp-skel` and
`tiny-mcp-server` now audit clean (grade A, non-blocking); a legacy-only
server still audits to grade F and blocks CI.

See `prompts/mcp-dual-dialect-bridge.md` and
`reports/2026-10-24-mcp-dialect-migration.md`.


## When to Use

- Before an agent connects to a third-party MCP server.
- In CI, over every manifest in the repo, gating on HIGH.
- When auditing a marketplace entry before you install or fork it.
- As a pre-review pass: run it first, then read what it flagged.

## When NOT to Use

- It audits the *declaration*, not the running server. It cannot see what the
  backend actually does.
- It is not a substitute for pinning by digest, least-privilege credentials,
  or egress allow-lists. Those are the controls that matter after connect.
- It is not a substitute for a code review of a server you are about to vendor.

## Status

The repo does not exist on GitHub yet — `GET /repos/hussain-alsaibai/tiny-mcp-audit`
returns **404** as of 2026-10-24. Local clone and passing tests only. Treat the
install line above as the intended distribution, not a live one.

## See Also

- `tools/tiny-mcp-skel-guide.md` — the stdlib-only skeleton that speaks the current dialect
- `tools/tiny-mcp-server-guide.md` — building the server this audits
- `tools/tiny-mcp-client-guide.md` — the consumer side
- `tools/tiny-secret-mask-guide.md` — runtime redaction, for what leaks after connect
- `prompts/mcp-dual-dialect-bridge.md` — the migration procedure behind the protocol group
