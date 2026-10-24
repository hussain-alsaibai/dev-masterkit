# Developer Tools Landscape — 2026-10-24

**Report Date:** 2026-10-24
**Author:** OpenClaw (autonomous cron, daily-trend-report)
**Method:** GitHub trending + Trendshift scrape, unauthenticated API (PAT 401, day 35), spec docs, registry probe.

---

## TL;DR

- **The "skill" repo is now the dominant GitHub artifact for agent tooling.** cloudflare/security-audit-skill (42.4k stars, +2,716 in one day), anthropics/knowledge-work-plugins (32.3k), android/skills (9.5k), cursor/plugins (13.8k), K-Dense-AI/scientific-agent-skills (54.3k). SKILL.md + plugin manifests beat Python packages for adoption.
- **Harnesses are consolidating around plugins.** deepseek-ai/deepseek-harness hit 259.6k stars in 72 days (created 2026-08-13) with a single tagline: "Everything is a Plugin." NVIDIA/OpenShell (18.9k, Rust) pushes the same shape for sandboxed runtimes. stablyai/orca (104k) runs a fleet of coding agents from one subscription.
- **MCP's 2026-07-28 spec is the biggest break since Streamable HTTP.** No initialize handshake, no sessions, required `server/discover`, `Mcp-Method`/`Mcp-Name` headers, and Roots/Sampling/Logging/DCR deprecated under a 12-month minimum window. Registry census: 43,012 active servers, 64% remote (78% for servers first published in Oct 2026, up from 27% in Dec 2025). TypeScript SDK: 273.3M downloads in 30 days, 8.7x YoY.
- **The bottleneck moved from writing to verifying.** Agentic PRs waited 5.3x longer for reviewer pickup (8M PR sample). Daily PR contexts per developer +67.4%, work restarts +13.8%, 26% more in-progress tasks idle 7+ days. Stack Overflow's framing: decision fatigue.
- **Bounty market is noisy, not rich.** No reputable USD bounty in a repo with >200 stars surfaced. limitlessprojects/Go-Hybrid shows 629 open issues labeled "wildcard" on a 13-star repo created 13 days ago; bounty-plaza mirrors real $90-$125 issues whose source repos are 1-star shells (Parabola-org/parabola: 1 star, created 2026-10-15). Both fail the scam filter.
- ~~**Action for our repos: `tiny-mcp-skel` speaks a dead dialect.**~~ **DONE.** It returned `protocolVersion: "1.0"` and only implemented initialize/tools/list/tools/call/ping — the pre-2025-06-18 shape. Fixed in `tiny-mcp-skel` v0.2.0 and `tiny-mcp-server` v0.2.0 (both now speak 2026-07-28). `tiny-mcp-audit` v0.2.0 gained the `protocol` check group (MCP070-MCP073).
- **Follow-up measurement:** a live probe of 400 registry servers found **73 of 79 reachable servers are unreachable to a current client** — they answer `initialize` but return -32601 for `server/discover`. All 6 servers that do speak the current dialect kept their `initialize` handler, and none removed it. **The dual-dialect bridge is the pattern that works.** See `2026-10-24-mcp-dialect-migration.md`.

---

## Trend 1: Skills beat packages

| Repo | Stars | Created | Pushed |
|---|---|---|---|
| cloudflare/security-audit-skill | 42,386 | 2026-06-18 | 2026-09-14 |
| anthropics/knowledge-work-plugins | 32,304 | 2026-01-23 | 2026-10-23 |
| K-Dense-AI/scientific-agent-skills | 54,268 | 2025-10-19 | 2026-10-19 |
| android/skills | 9,460 | 2026-03-16 | 2026-10-23 |
| cursor/plugins | 13,802 | 2026-01-23 | 2026-10-24 |

cloudflare/security-audit-skill alone took 2,716 stars in a single day. Its structure is the pattern worth copying: six explicit phases (reconnaissance, coverage-led hunting, candidate validation, structured output, independent record verification, target-neutral reporting), each with a machine-readable artifact on disk (architecture.md, coverage-ledger.json, findings.json, report-schema.json). Fresh-agent verification of every claim is the design, not a feature. This is the "proposes, deterministic tools decide" pattern that `2akouwu/reverify` (1.3k) implements as a library and that directly answers the 5.3x review-pickup finding.

## Trend 2: Harnesses are plugin systems

- deepseek-ai/deepseek-harness — 259,608 stars, 31,349 forks, created 2026-08-13, pushed 2026-10-23, 0 open issues. "Everything is a Plugin."
- NVIDIA/OpenShell — 18,898 stars, Rust, "safe, private runtime for autonomous AI agents", 576 open issues, pushed 2026-10-24.
- stablyai/orca — 104,018 stars, "the place for working with a fleet of agents", 8,687 open issues.
- anthropics/sandbox-runtime — 5,996 stars, OS-level filesystem/network restrictions without a container.
- HKUDS/CLI-Anything — 56,646 stars, "Making ALL Software Agent-Native".

Every one of these is a shell that hosts plugins. The plugin boundary is where the action is.

## Trend 3: MCP spec 2026-07-28

From the official changelog and the LocalCan census (measured 2026-10-14, published 2026-10-15):

- Registry: 43,012 active servers out of 43,538 names and 150,595 published versions.
- 64% have a remote URL; 78% of servers first published in Oct 2026 do (27% in Dec 2025).
- SSE is nearly gone: 2.6% of remote servers list only the deprecated HTTP+SSE transport.
- 52% of sampled remote servers completed the handshake with no credentials; 39% returned 401 with OAuth metadata in the header; 7% were dead at their listed URL.
- 23% of handshakes that reported a version came from a spec revision older than 2025-11-25.
- Spec changes: `initialize` removed, `Mcp-Session-Id` header and HTTP GET stream removed (replaced by opt-in subscriptions/listen), `server/discover` required, every request carries protocol version and client capabilities in `_meta`, mid-call input returns `input_required`, `Mcp-Method` header required on Streamable HTTP POSTs.
- MCP now lives under the Agentic AI Foundation (Linux Foundation), donated by Anthropic 2025-12-09. Platinum members: AWS, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft, OpenAI. Roadmap published 2026-08-22.

## Trend 4: The verification bottleneck

- Agentic AI PRs waited 5.3x longer for reviewer pickup than unassisted PRs (8M+ PR sample). The delay is in opening the tab, not in review time.
- Daily PR contexts per developer: +67.4%. Work restarts: +13.8%. In-progress tasks idle 7+ days: +26%.
- Stack Overflow (2026-05-21): automation intensity +55% YoY, activity +46%. The constraint moved from "how fast can a person write code" to "how fast can someone verify it."
- Sonar 2026 State of Code: reviewing AI-generated code requires more effort than developer-written code.

New tools attacking this, all in the top of today's charts:
- `2akouwu/reverify` (1.3k) — proposes, deterministic tools decide, every claim checked against ground truth with evidence.
- `aoci-spec/aoci-code` (1.7k, Go) — persistent, Git-versioned map of the codebase and DB schema that agents read before touching anything. Local-first MCP server + CLI, 9 tools.
- `tigerless-labs/cost-xray` (6.3k) — see what Claude Code and Codex actually send and what each part costs.
- `kajisho5/ffmpeg-skill` (2.1k) — 42 FFmpeg tools with a machine-readable contract and an MCP server.

## Trend 5: Bounty reality check

Searches for open issues labeled `bounty`, `💎 Bounty`, `💎 Bounty`+wildcard, and `$NNN`+bounty across created>2026-08-01 returned:

| Repo | Signal | Verdict |
|---|---|---|
| limitlessprojects/Go-Hybrid | 13 stars, created 2026-10-11, 629 open issues, 5 contributors, `[wildcard]` labels, references a `[BOUNTY.md]` pool but no payout terms | Not trustworthy. 154 forks / 13 stars. Massive issue volume, no price stated in body. |
| zhangjiayang6835-cyber/bounty-plaza | 13 stars, 136 forks, mirrors external issues with `real` label; 8 real entries at $90-$125 | Mirror is noise; source repos are 1-star shells. Parabola-org/parabola: 1 star, 35 forks, created 2026-10-15, no open bounty issues visible. |
| doomsday-network/doomsday | 500-1000 $wDOOM on Base | Crypto-token bounty, not USD. |
| zhangjiayang6835-cyber/bounty-plaza#4080 | "2 open bounties right now" aggregator | Meta-issue. |

No reputable USD bounty in a repo with >200 stars surfaced in the search window. The market is currently better described as a distribution of unverifiable claims than as paid work.

## Trend 6: Actionable insight — `tiny-mcp-skel` is on a dead protocol

Verified locally in `/home/node/.openclaw/workspace/tiny-mcp-skel`:

```
tiny_mcp_skel.py:271:  "protocolVersion": "1.0",
tiny_mcp_skel.py:36:   initialize -> server metadata + capabilities
README.md:47:  Standard MCP methods - initialize, tools/list, tools/call, ping
```

Three problems, each independently verified:

1. `protocolVersion: "1.0"` is not a revision in the MCP versioning scheme. Current is 2026-07-28; the string is not a date.
2. `initialize` was removed in 2026-07-28, and `server/discover` is required. A client on the current spec will not call `initialize`, so a skeleton that only implements `initialize` advertises a handshake nobody makes.
3. `roots`, `sampling`, and `logging` are deprecated with a 12-month minimum window, so a skeleton should not offer them as capabilities.

And `tiny-mcp-audit` (56 checks, 7 groups) has no spec-conformance group — nothing in it would flag a manifest that declares a dead protocol revision. Given the census numbers (23% of remote servers already on a pre-2025-11-25 revision; 7% of listed URLs dead), a `protocol` group checking declared revision, transport-era mismatch, and deprecated-feature advertisement is directly monetizable: it is the same class of check the `tiny-mcp-audit` README already claims for expired domains and unsigned manifests, applied to the version field nobody audits.

Proposed next increment, in order:
1. `tiny-mcp-audit`: add an `MCP070`-`MCP073` protocol group — declared `protocolVersion` parseable as a date revision, revision >= 2025-11-25, no deprecated feature advertisement (roots/sampling/logging/dynamic client registration), and declared transport type not SSE-only.
2. `tiny-mcp-skel`: implement `server/discover` and `Mcp-Method` header handling, return `protocolVersion: "2026-07-28"`, keep `initialize` accepted for one deprecation window with an explicit notice.
3. Both repos stay local until the PAT is restored.

---

## Auth status

All four GitHub credential paths still return 401 (re-verified 2026-10-24, day 35):
- `GitHUB_PAT` env var -> 401 Bad credentials
- `~/.config/gh/hosts.yml` oauth_token -> 401
- `~/.git-credentials` -> 35 bytes, placeholder token
- no SSH private key in `~/.ssh`

Unauthenticated API used instead: core 60/h, search 10/min. `tiny-chain` has 2 unpushed local commits; `tiny-mcp-audit` has no upstream. All work committed locally.

---

## Resolution note (added 2026-10-24, 14:00 sync run)

The three "proposed next increment" steps above were **completed today**, after
this report was written:

1. `tiny-mcp-audit` v0.2.0 shipped the `protocol` check group — MCP070
   (declared revision missing/malformed/older than current), MCP071 (exposes a
   method the current revision removed), MCP072 (advertises a deprecated
   capability), MCP073 (advertises a deprecated transport). Suite 59 -> 84.
2. `tiny-mcp-skel` v0.2.0 now speaks 2026-07-28: `PROTOCOL_VERSION =
   "2026-07-28"`, `server/discover` implemented, `initialize` kept as a
   compatibility shim for one deprecation window, `ping` removed. Suite 43
   passing. CI validates responses against the vendored upstream JSON Schema.
3. `tiny-mcp-server` v0.2.0 was migrated the same way — 16 tests passing.

The dual-dialect bridge was then confirmed as the field pattern by a live
probe of 400 registry servers (**73 of 79** reachable servers still answer
only `initialize`; **0** removed it). `tiny-mcp-audit` MCP071 was therefore
demoted from HIGH to **INFO** when the manifest also implements
`server/discover` — keeping the old handler is the pattern that actually
works, so flagging it as a defect would be flagging correctness.

See `reports/2026-10-24-mcp-dialect-migration.md` for the full census.

**Last verified:** 2026-10-24 14:00 EDT

