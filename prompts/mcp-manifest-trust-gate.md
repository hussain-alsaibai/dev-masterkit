# MCP Manifest Trust Gate

**A pre-connection checklist for pointing an agent at a third-party MCP server.**

The manifest is the only artifact your agent reads before deciding to trust a
server. Today it is reviewed by nothing. This prompt is the gate.

> Grounded in the OX Security census of 15,465 indexed public MCP servers
> (5,095 unique hostnames, 2.3% on expired domains, 15.6% outside the US),
> reported by The Hacker News on 2026-10-22.
> **Last verified:** 2026-10-22

## When to Use

- Before adding an MCP server to an agent config.
- Before installing or forking one from a marketplace.
- When reviewing a PR that adds or edits a manifest.

## Step 1 — Read the manifest, not the README

```bash
mcp-audit ./server.json --format text
```

If the repo you are reviewing has `tiny-mcp-audit`, run it. If not, the
checklist below is the manual equivalent.

## Step 2 — Seven questions about the declaration

Answer all seven. Any "no" or "unclear" is a finding.

| # | Question | Why it matters |
|---|----------|----------------|
| 1 | Is `serverInfo.version` a floating tag or absent? | A floating version means the bytes behind the identity can change with no visible signal. Supply chain drift. |
| 2 | Does `env` forward any credential-shaped variable? | `AWS_SECRET_ACCESS_KEY`, `*_TOKEN`, `*_API_KEY` handed to a server is a credential handed to whoever operates it. |
| 3 | Is every non-stdio transport TLS? | Plaintext `http` SSE is a passive read of every request, including whatever credentials ride in it. |
| 4 | Does any resource URI reach the host filesystem or a sensitive path? | `file:///root/.ssh/id_rsa` as a *resource* is not a data source, it is a key. |
| 5 | Does any tool name imply execution, and is it documented? | `shell.exec` with a thin description is an undeclared capability. |
| 6 | Does every tool declare an `inputSchema`? | A tool with no schema accepts anything, including fields the author never validated. |
| 7 | Does any prompt contain instruction-override language? | Prompts are executable text. Override language inside a manifest is an injection surface, not documentation. |

## Step 3 — Reason about what the manifest cannot tell you

The manifest is a claim. Three things it never covers:

- **What the backend actually runs.** A remote server's behavior need not match
  its public repo. Code review tells you what was published, not what is served.
- **Who operates the host today.** The 2.3% dangling-domain finding is the sharp
  edge: trust was extended when it was legitimate, and the attack lands later,
  silently, with no reconfiguration and no error.
- **What the agent will do with it.** A read-only tool and a destructive tool can
  be declared identically. Only `annotations` (`readOnlyHint`,
  `destructiveHint`) distinguish them.

Marketplace star counts are not a security signal. None of the famous
fork-scam families from the July 2026 Opire flood had real stars.

## Step 4 — Apply the controls that actually hold

A clean manifest is the floor, not the ceiling:

1. **Pin by digest**, not by tag — removes question 1 entirely.
2. **Least-privilege credentials** — a scoped, short-lived token whose blast
   radius is one read-only replica.
3. **Egress allow-list** — the server's hostname, nothing else.
4. **Redact at runtime** — `tiny-secret-mask` for anything that will cross a
   log, a trace, or a chat surface after connect.
5. **Audit in CI** — `mcp-audit ./mcp/*.json --fail-on high --format sarif`
   so the gate does not depend on a human remembering to run it.

## Step 5 — Record the verdict

Write it down where the next reader will find it:

```
- Server: <owner>/<server> @ <pinned digest>
- Audited: <date> — score/grade from tiny-mcp-audit
- Credential scope: <what it can actually reach>
- Accepted risks: <explicit list, or none>
```

An unaudited manifest that is nonetheless in your config is an accepted risk
you did not write down. That is the failure mode this gate exists to prevent.

## Anti-Patterns

- Trusting the marketplace listing instead of the manifest.
- Treating a green README as a security signal.
- Auditing once at install and never in CI, so the next PR reopens the hole.
- Assuming a clean manifest means a safe server. It means a *legibly declared*
  one.
- Copying an audit result forward. Digests, transports, and env blocks all move.

## Related

- `tools/tiny-mcp-audit-guide.md` — the auditor this gate is built on
- `tools/tiny-mcp-server-guide.md` — writing manifests that pass this gate
- `prompts/silent-security-control-audit.md` — auditing controls that degrade to no-ops
- `reports/2026-10-22-developer-tools-landscape.md` — Trend 1, MCP governance
