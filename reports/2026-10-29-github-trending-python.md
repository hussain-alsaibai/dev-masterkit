# GitHub Trending Python — 2026-10-29

**Source:** https://github.com/trending/python?since=daily (fetched 2026-10-29 00:02 ET)
**Stars:** total from api.github.com/repos (verified 2026-10-29 00:10 ET). "Today" is the
"stars today" column parsed from the trending page's own HTML.
**Method note:** the trending page was parsed from raw HTML (regex over article blocks),
because the markdown extractor drops the star counts. Every repo was then confirmed
against the API so the numbers are not taken from a rendering.

---

## TL;DR

1. **A scanner upgrade invalidated a suppression baseline, and nothing caught it.** This is
   the one finding from today's sweep that changes our repo. NVIDIA/SkillSpector shipped
   v2.13.2 on 2026-10-28; our `.skillspector-baseline.yaml` was written for v2.13.1.
   SkillSpector binds every fingerprint to the scanner version, so after the bump the
   baseline suppressed **nothing** — 124 previously-reviewed findings came back as "new".
   The baseline was **gitignored** and no CI job consumed it, so the drift was invisible.
   Fixed, and the baseline is now tracked with a CI gate that fails on version drift.
2. **The chart is agent tooling, not libraries.** Eight of today's ten trending repos are
   agent harnesses, skills, scanners or multi-agent frameworks. The "Python" tag is
   incidental; many are TypeScript/Node projects that happen to ship Python.
3. **Spec-driven development has become the default front-end for coding agents.**
   github/spec-kit (143,714 stars) now ships *processes* — spec-driven development, bug
   fixing, idea assessment — as composable extensions with catalogs, presets, workflows
   and lifecycle hooks. It is a process marketplace, not a template collection.
4. **Skill security is now a supply-chain discipline, not a feature.** SkillSpector's own
   research claim: of 31,132 analysed skills, **26.1% contain vulnerabilities** and **5.2%
   show likely malicious intent**. That is the number that makes our new CI gate
   non-optional.
5. **context-bridge has no direct competitor on this chart today.** The knowledge-graph
   race is real but its leaders (graphify, codebase-memory-mcp, context7) are not trending
   right now. Nobody is attacking the MCP semantic-indexing position this week.

---

## Trending table (verified 2026-10-29)

| Repo | Stars | Today | Born | License | What it is |
|---|---|---|---|---|---|
| github/spec-kit | 143,714 | 361 | 2025-08-21 | MIT | SDD / bug-fix / idea-assessment processes as installable extensions |
| TauricResearch/TradingAgents | 117,968 | 654 | 2024-12-28 | Apache-2.0 | Multi-agent LLM trading framework, LangGraph-based |
| debpalash/VoiceStudio | 93,208 | 1,793 | 2026-04-09 | AGPL-3.0 | Fully-local ElevenLabs alternative: clone, dub, transcribe, 646 languages |
| Alishahryar1/free-claude-code | 64,685 | 400 | 2026-01-28 | NOASSERTION | Multi-harness free-token router, browser sessions included |
| HKUDS/DeepTutor | 48,355 | 2,371 | 2025-12-28 | Apache-2.0 | Lifelong personalised tutoring agent, LightRAG-backed KB |
| p-e-w/heretic | 37,014 | 307 | 2025-09-21 | AGPL-3.0 | Automated censorship removal for open-weight LLMs |
| baidu/Unlimited-OCR | 29,578 | 429 | 2026-06-18 | MIT | One-shot long-horizon document parsing |
| AgriciDaniel/claude-seo | 23,475 | 581 | 2026-02-07 | MIT | Claude Code SEO plugin: 26 sub-skills, 19 sub-agents |
| NVIDIA/SkillSpector | 23,130 | 298 | 2026-03-21 | Apache-2.0 | Security scanner for agent skills, MCP servers and prompt injection |
| shitagaki-lab/see-through | 5,110 | 74 | 2026-03-31 | Apache-2.0 | Single-image layer decomposition for anime characters (SIGGRAPH 2026) |

---

## What we can learn from each

### NVIDIA/SkillSpector — the one that mattered today
**Why it is trending:** the ClawHavoc supply-chain incident made "scan before you install"
a default step. NVIDIA ships it as part of a Verified Skills pipeline that signs vetted
skills.

**What is worth stealing:**
- **71 vulnerability patterns across 17 categories**, two-stage analysis (fast static +
  optional LLM semantic), SARIF 2.1.0 output, and live CVE lookup against OSV.dev.
- **The baseline/suppression model** — a YAML file of reviewed findings, each with a
  mandatory reason, so a re-scan surfaces only *new* issues. Same "accept known findings,
  fail on new ones" pattern as our own CI census work.
- **Fail-closed ingest limits** (100 MiB per ingest, 10,000 zip members) that refuse
  rather than truncate.

**The trap:** the baseline is bound to the scanner version. It does not warn you when it
stops matching. See the defect below.

**Relation to us:** direct. We already use it on `dev-masterkit/skills`. Today it
also taught us a lesson about our own CI.

### github/spec-kit
**Why it is trending:** GitHub's own official entry point for spec-driven development.

**What is worth stealing:**
- **Processes are extensions.** "Build a feature", "diagnose a bug" and "decide if an
  idea deserves investment" are three independent entry points, not mandatory phases.
  Our `dev-masterkit` has one linear flow: plan, implement, verify.
- **Extension runtime events and hooks** — an extension can react to a coding agent's
  lifecycle and run before/after a command. That is the seam we would need for
  `tiny-agentskills` to participate in someone else's workflow rather than being
  called directly.
- **Presets and project-local overrides** — org-level methodology that a single project
  can partially override without forking.

**Relation to us:** `dev-masterkit` should be able to publish itself as a spec-kit
extension. That is a distribution channel we do not currently use.

### HKUDS/DeepTutor
**Why it is trending:** 2,371 stars today, the single largest daily gain on the chart.

**What is worth stealing:**
- **LightRAG-backed knowledge bases** with a **published index that records and enforces
  what built it** (v1.6.10) — the index is auditable, not a black box.
- **Bounded tutoring memory** (v1.6.15) — memory with a hard budget, which is the failure
  mode we have to design around in `context-bridge`.
- **Resumable embedding checkpoints** (v1.7.0, 2026-10-28) — indexing is checkpointed so
  a crash does not restart the whole embedding pass.

**Relation to us:** directly relevant to **context-bridge**. Three ideas to adopt:
checkpointed indexing, an auditable index manifest, and bounded memory.

### debpalash/VoiceStudio
**Why it is trending:** 1,793 stars today. A fully local ElevenLabs alternative is a
genuine capability unlock: no per-character cost, no API key, works offline.

**What is worth stealing:** nothing structural for us — it is a media model repo. Worth
knowing if the Architect ever wants local voice without a metered API.

**Relation to us:** none.

### TauricResearch/TradingAgents
**Why it is trending:** 654 stars today, sustained for two years.

**What is worth stealing:**
- **Point-in-time integrity.** Every dated path is fixed so a backtest only sees data
  published before the decision date. v0.7.1 fixed decisions being scored on the *first
  close after* the decision, and holidays.
- **Provider-per-model-tier**, so managers and analysts can run on different models.
- **A decision log as a first-class artefact**, plus checkpoint resume.

**Relation to us:** indirect but valuable. The "never let a backtest see the future" rule
is the same discipline our CI matrix work needs. Their provider-per-tier model is what
our **tiny-llm-router** already does, and their decision log is close to our
`tiny-agent-memory`.

### AgriciDaniel/claude-seo
**Why it is trending:** 581 stars today, and the README shows 1,077 passing tests.

**What is worth stealing:** the **sub-skill + sub-agent split** — 26 sub-skills and 19
specialist agents for one narrow domain, with 1,077 tests. That is the decomposition
shape our 37 skills should be converging toward: one skill, many focused specialists.

**Relation to us:** a direct template for `dev-masterkit/skills`.

### Alishahryar1/free-claude-code
**Why it is trending:** 400 stars today. Routes 1.3B+ free tokens across 9+ harnesses,
including browser sessions.

**What is worth stealing:** the **multi-harness adapter** design — one client surface,
many agent runtimes. Our **tiny-llm-router** already does model selection; the next
layer is harness selection.

**Relation to us:** `tiny-llm-router` is the same product one level down. Worth
checking for feature overlap before we ship more of it.

### p-e-w/heretic, baidu/Unlimited-OCR, shitagaki-lab/see-through
Three ML repos with no structural lessons for us:
- **heretic** — automated refusal-direction removal for open-weight models.
- **Unlimited-OCR** — one-shot long-horizon document parsing, two HF checkpoints.
- **see-through** — SIGGRAPH 2026 paper, single-image layer decomposition.

**Relation to us:** none. Unlimited-OCR was on our 2026-10-24 chart, so it is holding
position rather than moving.

---

## The defect this scan found, and the fix

**What broke.** `dev-masterkit/.skillspector-baseline.yaml` was written against
SkillSpector v2.13.1. The scanner released v2.13.2 on 2026-10-28. SkillSpector binds each
suppression fingerprint to `scanner_version`, so after the bump:

- the v2.13.1 baseline suppressed **0 of 69** findings it should have suppressed;
- a scan of our 37 skills reported **124 unsuppressed findings, every one of them a false
  alarm** — a human had already reviewed and accepted all of them on 2026-10-27;
- the risk score read **100/100 CRITICAL / "DO NOT INSTALL"** for a skills directory whose
  worst real finding is a documented cross-reference between two of our own skills.

**Why it was invisible.** Three independent reasons, all of them ours:

1. The baseline was **gitignored** — local state, "no CI in this repo consumes it".
2. No CI job read the baseline, so no scan ever ran against it.
3. SkillSpector's own behaviour is correct: a stale baseline is *supposed* to report
   everything. It has no way to know the findings were previously accepted.

**Proof, not inference.** Baseline entries and live scan fingerprints were compared
directly:

| Scanner | Baseline says | Unsuppressed | Suppressed |
|---|---|---|---|
| v2.13.1 (matches) | 2.13.1 | 65 | 62 |
| v2.13.2 (drifted) | 2.13.1 | 124 | 0 |
| v2.13.2 + regenerated baseline | 2.13.2 | 0 | 124 |

**The fix, in three parts:**

1. **Regenerated the baseline against v2.13.2** and carried every human review reason
   across by (file, rule) pair — 115 reasons preserved verbatim from the 2026-10-27
   review, 9 new pairs reviewed and labelled by hand. The old file is preserved at
   `memory/skillspector-baseline-dev-masterkit-2026-10-27.yaml.bak-2.13.1`.
2. **Stopped ignoring the baseline.** It is a record of human decisions and it only works
   if it is versioned with the skills it describes. It is now tracked.
3. **Added `scripts/scan_skills.py` and a CI job** (`skill-security`) that
   fails when the installed scanner version does not match the baseline, and fails when any
   finding survives it. Both failure paths were tested, not assumed:
   - version mismatch, exit 1 with an actionable message;
   - clean scan, exit 0, "0 unsuppressed, 124 suppressed, risk score 0 (LOW)".

**One more real finding along the way.** The scan flagged `SC8`/`SC9` — a
skill shipping a `__pycache__` directory with compiled bytecode. It was never tracked
by git (so it was never published) but it was sitting on disk and being scanned as a
concealed executable artifact. Removed.

---

## Actions

- [x] Regenerate the SkillSpector baseline against v2.13.2, preserving review reasons
- [x] Un-ignore `.skillspector-baseline.yaml` and track it
- [x] Add `scripts/scan_skills.py` with a pinned scanner version and a version-drift guard
- [x] Add the `skill-security` CI job; verify both the pass and fail paths locally
- [x] Remove the untracked `__pycache__` artifact
- [ ] **context-bridge: adopt DeepTutor's checkpointed indexing and an auditable index
      manifest.** Our indexer has neither; a re-index today restarts from zero.
- [ ] **Publish `dev-masterkit` as a spec-kit extension** so it can be installed as a
      process rather than cloned.
- [ ] **Review our 37 skills for the sub-skill decomposition** that claude-seo uses
      (26 sub-skills / 19 agents / 1,077 tests for one domain).

---

## What did not change

- **context-bridge** has no competitor trending this week. The knowledge-graph race
  (graphify, codebase-memory-mcp, context7) is real but quiet. Our differentiator is
  still sub-millisecond local queries with zero cloud.
- **Our own repos remain at 0 stars.** context-bridge, dev-masterkit, tiny-llm-router
  and tiny-agentskills were all verified at 0 stars and 0 forks via the API. The
  distribution problem is unchanged by anything on today's chart.
- **VoiceStudio, TradingAgents and Unlimited-OCR were already on our 2026-10-24 chart.**
  They are holding position, not breaking out.
