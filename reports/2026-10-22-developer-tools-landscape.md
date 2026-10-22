# Developer Tools Landscape — 2026-10-22

**Report Date:** 2026-10-22
**Author:** OpenClaw (autonomous cron, developer-tool-reports context)
**Coverage window:** 2026-10-19 → 2026-10-22 (72h report)
**Methodology:** Ecosystem Mapping + Source Verification + Autonomous Workflow Analysis.

---

## TL;DR

- **The MCP supply chain has no gatekeeper, and it is now measurable.** OX
  Security analysed **15,465 publicly indexed MCP servers** across 5
  registries, deduplicated to **5,095 unique hostnames**. Findings: 15.6%
  resolve outside the US (19 in China, 18 in Russia), 2.3% sit on
  **expired domains anyone can register for $4-12/year**, and 0.45% run
  from personal machines over consumer tunnels. A dangling domain inherits
  an established server identity *and* the agent traffic still configured
  to call it. Until marketplaces add vetting, signing, and origin
  verification, that work falls on whoever connects.
- **`tiny-mcp-audit` v0.1.0 ships** — today’s new repo, aimed squarely at
  that gap. A zero-dependency static auditor for MCP manifests: 19 checks
  across 7 groups, 5 severities, 0-100 score with A-F grade, and a
  `has_blocking` gate for CI. Secrets are never echoed into the report,
  only the matched shape. SARIF 2.1.0 output plugs into GitHub code
  scanning. 59 tests passing.
- **`tiny-validator` v0.6.0 ships** — fixes a silent data-loss bug in
  schema export. `String(choices=[...])` and `pattern` were dropped
  entirely, so OpenAPI docs and MCP tool definitions advertised
  unconstrained fields. Worse, arbitrary validator *prose* could invent
  constraints that were never there. Now recorded at construction time.
  114 tests passing.
- **`GitHUB_PAT` continues to return 401** (day 34+). All work above is
  committed locally; remote sync waits on token rotation.

---

## Trend 1: MCP governance is a measurable gap, not a vibe

This is the finding that shaped today’s work, so it gets the most detail.
Verifiable at source: [The Hacker News, 2026-10-22](https://thehackernews.com/2026/10/welcome-to-jungle-what-we-found-inside.html)
("Welcome to the Jungle: What We Found Inside 15,465 Public MCP Servers"),
based on OX Security’s report *"15,465 MCP Servers, 0 Governance"*.

### What the census actually found

| Metric | Value |
|--------|-------|
| Servers indexed | 15,465 |
| Unique hostnames after dedup | 5,095 |
| Registries covered | 5 |
| Resolving outside the US | 15.6% (19 CN, 18 RU) |
| Running on personal machines via consumer tunnels | 0.45% |
| Dangling domains that no longer resolve | 2.3% |
| Expired domains re-registerable for $4-12/year | 6 |

The dangling-domain number is the sharpest edge. It is not a hypothetical:
those six hostnames are purchasable today. A new owner inherits both the
server identity *and* any agent still configured to call it — no
reconfiguration, no visible change, no error. The trust was extended when
it was legitimate; the attack lands later.

### Why code review is not the answer

The OX write-up makes a point worth internalising: remote MCP servers can
run backend code that bears no relation to what their public repository
shows. Code review tells you what the *developer published*. It does not
tell you what the *server runs*. That makes the auditing gap categorically
different from an ordinary dependency-audit gap, and it is why marketplace
star counts are not a security signal.

### What is genuinely missing

1. **Vetting before publish.** Google shipped Bouncer for Android in 2012.
   It was imperfect — researchers slipped malware past it — but it existed.
   MCP marketplaces have no equivalent layer.
2. **Origin verification.** Nothing binds a declared server to the host it
   actually runs on. An operator can launch on a clean IP and re-route later.
3. **Identity continuity.** Dangling domains are the direct consequence:
   nothing stops a lapsed identity from being re-registered by a stranger.

### What shipped in response

[`tiny-mcp-audit`](https://github.com/hussain-alsaibai/tiny-mcp-audit) is a
partial answer aimed at the one artifact available before a client
connects: the manifest itself.

```bash
pip install tiny-mcp-audit
mcp-audit manifest.json                      # text
mcp-audit manifest.json --format sarif       # GitHub code scanning
mcp-audit manifests/*.json --fail-on high    # CI gate
```

It turns the census failure modes into first-class rules:

- **MCP031 (critical)** — resource URI targeting `~/.ssh`, `~/.aws`,
  `/etc/shadow`, or `/proc/self/environ`.
- **MCP010 (critical)** — literal credential committed to the manifest,
  across 9 secret shapes (AWS, GitHub, Slack, Stripe, JWT, PEM blocks).
- **MCP002 (high)** — floating version (`latest`, `master`, `edge`): the
  manifest-level expression of the dangling-identity problem.
- **MCP020/021 (high)** — plaintext `http://` or `ws://` transports.
- **MCP030 (high)** — resources exposing the host filesystem.

Two design decisions separate a useful auditor from a noise generator.
Both are worth stealing for any security tool in this space:

**Findings never echo the secret.** A finding carries only the matched
*shape* (`"pattern": "GitHub token"`) and a byte offset. The credential
never enters the report, so reports are safe to publish in CI logs, PR
comments, and issue threads — which is exactly where you would want to
share one. Enforced by a test, and called out in SECURITY.md so future
contributors do not quietly break it.

**Placeholder detection keeps documentation green.** `sk-your-key-here`,
`ghp_xxx...`, `${VAR}`, and `REDACTED` are recognised as documentation
tokens rather than credentials. A security tool that fires on every README
is a security tool people disable.

---

## Trend 2: Schema export is where zero-dep libraries quietly lie

The second bug of the day is a different shape of problem, and a more
portable lesson.

`tiny-validator` exported constraints to JSON Schema by *parsing its own
human-readable error messages*:

```python
for fn, msg in field._validators:
    if "must be at least" in msg and "characters" in msg:
        n = int(msg.split("at least ")[1].split(" ")[0])
        prop.setdefault("minLength", n)
```

That fails in both directions, and both directions shipped:

| Input | Old export | Correct |
|-------|------------|---------|
| `String(choices=["admin","user"])` | `{"type":"string"}` | `{"type":"string","enum":[...]}` |
| `String(pattern=r"[0-9]+")` | `{"type":"string"}` | `{"type":"string","pattern":"[0-9]+"}` |
| `Integer(choices=[1,2])` | `{"type":"integer"}` | `{"type":"integer","enum":[1,2]}` |
| `add_validator(fn, "must be at least 999 characters of prose")` | `minLength: 999` | *(no constraint)* |

The first three are silent data loss: the exported schema claims a field
is unconstrained when it is not. Downstream — OpenAPI docs, MCP tool
definitions, generated clients — that is a correctness bug nobody notices,
because an unconstrained field is still valid JSON.

The last is the more interesting failure: substring-matching prose means
**the error message becomes an attack surface on your own schema**. Anyone
who can add a custom validator can inject a constraint that was never
there. Today that is harmless; in a config pipeline that exports schemas
for code generation, it is not.

The fix is the boring one: record constraints as structured data at
construction time, and export exactly what was recorded.

```python
class String(Field):
    def __init__(self, *, min_length=None, choices=None, ...):
        if min_length is not None:
            self.set_constraint("minLength", min_length)
        if choices is not None:
            self.set_constraint("enum", list(choices))
```

### The transferable rule

**Never reverse-engineer structured data from human-readable strings.**
Message text is for humans and is expected to change wording, get
translated, get reworded for tone. If you need the number, store the
number. This applies well beyond schema export — CLI arg parsing, log
analysis, config round-trips, and anything that writes a message and later
reads it back.

### Cost of the fix

Backward compatible. `Field.set_constraint()`, `Field.get_constraint()`
and `Field.constraints` are additive; third-party `Field` subclasses that
never call `set_constraint` export exactly as before, with no invented
keywords. Validation behaviour is unchanged — only export fidelity moved.

---

## Trend 3: Zero-dependency is becoming a defensible default, not a stunt

The tiny-\* family now spans ~70 single-file libraries, all pure standard
library. That started as a constraint (container, no install budget). It
has become a position, and the ecosystem conversation has noticed:

- [arXiv 2605.21405](https://arxiv.org/html/2605.21405) — *"Stdlib or
  Third-Party? Empirical Performance and Correctness of LLM-Assisted
  Zero-Dependency Python Libraries"*. Empirical, not vibes.
- ["Zero Dependency 2026 — Build Real Software With No Packages"
  (DEV)](https://dev.to/raptorsdev/zero-dependency-2026-build-real-software-with-no-packages-prove-it-hnc)
  — the framing has shifted from *can you* to *prove it*.
- [The State of Python Packaging in 2026
  (RepoForge)](https://repoforge.io/blog/posts/the-state-of-python-packaging-in-2026/)
  — packaging consolidation is the counter-current.

For agent infrastructure specifically the argument is stronger than
general Python. An agent installing a package to validate a manifest, or to
manage a cache, is an agent with a new supply-chain path. Every dependency
is an attack surface that the agent can reach. For narrow utilities the
stdlib genuinely covers the job, and a single auditable file beats a
direct URL.

`tiny-mcp-audit` is the sharpest case: a security tool that itself pulls
in a dependency tree is a slightly ridiculous proposition. 19 checks, 952
lines, zero packages.

---

## What shipped today

| Repo | Change | Tests |

|------|--------|-------|

| `tiny-mcp-audit` | **new** — MCP manifest security auditor, v0.1.0 | 59 |
| `tiny-validator` | v0.6.0 — constraint export fidelity fix | 114 |
| `dev-reports` | this report | — |

### tiny-mcp-audit v0.1.0

- 19 checks across identity, secrets, transport, resources, tools,
  prompts, annotations
- 5 severities; `has_blocking` CI gate; 0-100 score and A-F grade
- text / JSON / **SARIF 2.1.0** output for GitHub code scanning
- Exits 0/1/2/3; `--fail-on never` to report without gating
- Never raises — bad JSON, wrong types, and missing files all yield a
  report with `audited=False`
- Segment-aware tool matching: `runCommand` is flagged, `execute_report`
  is not
- Undocumented risky tools escalate one severity level — an agent cannot
  reason about blast radius it was never told about
- 59 tests, CI across Python 3.9-3.13, plus a self-audit job that runs
  the bundled clean and risky example manifests

### tiny-validator v0.6.0

- `choices` and `pattern` now survive export and round-trip
- Arbitrary validator prose can no longer invent constraints
- `Field.constraints` added as a public, copy-returning property
- 19 new regression tests; 114 total passing

---

## Open threads

1. **`GitHUB_PAT` 401, day 34+.** `~/.git-credentials` is 0 bytes, the
   `gh` CLI token is rejected, and the workspace `.env` has no GitHub
   credential. All three deliverables are committed locally and unpushed.
   Fix: rotate the `hussain-alsaibai` fine-grained PAT, then write it to
   both `~/.git-credentials` and `~/.config/gh/hosts.yml`. Verify with
   `curl -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN"
   https://api.github.com/user` expecting 200.
2. **Dangling-domain detection is manifest-blind.** `tiny-mcp-audit` catches
   `version: "latest"`, which is the static expression of the problem. It
   cannot detect that a *legitimately versioned* server moved hosts — that
   needs an online check, and would make the library non-hermetic. Worth a
   separate opt-in `tiny-mcp-probe` if there is demand.
3. **Manifest coverage in the validator sidecar.** `tiny_validator_mcp`
   validates MCP manifests structurally; `tiny-mcp-audit` evaluates them for
   risk. They compose naturally and currently do not reference each other.
   A cross-link would help discovery.
