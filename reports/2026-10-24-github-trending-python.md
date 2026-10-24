# GitHub Trending Python — 2026-10-24

**Source:** https://github.com/trending/python?since=daily (fetched 2026-10-24 00:05 ET, raw HTML + unauthenticated api.github.com)
**Stars:** total from api.github.com/repos (verified 2026-10-24). **Today** = "stars today" column parsed from the trending page.
**Method note:** the unauthenticated core API still works (search capped at 10/min, core 60/h). Stargazer listing requires auth, so star *velocity* could not be independently verified — only the trending page's own "stars today" counter is trusted here.

---

## TL;DR

1. **graphify** (133,956*, +1,173 today) is the standout and the single most relevant to **context-bridge**. Same product category — codebase -> queryable knowledge graph — shipped as a multi-agent-host skill with a Python library underneath. 362 contributors, 2,498 PRs, PyPI `graphifyy` v0.9.95, 263 releases, 1,755,205 downloads/30d (+8.0%).
2. **The skill-as-distribution-format is now the norm.** graphify, book-to-skill, and Anthropic's own knowledge-work-plugins all distribute the same way: a SKILL.md in a per-host skills directory. All three explicitly support OpenClaw.
3. **book-to-skill** (35,897*, +143 today) applies a *document -> skill* compiler pattern we do not have.
4. **Anthropic/knowledge-work-plugins** (32,304*, +635 today) is official Anthropic plugin packaging with a connectors model — the reference for how a plugin declares external services.
5. **Most of today's trending stars are agent tooling, not libraries.** Six of the twelve are skills/agent workspaces. The "Python" language tag is incidental.

---

## Trending table (verified 2026-10-24)

| Repo | Stars | Today | Born | License | What it is |
|---|---|---|---|---|---|
| Graphify-Labs/graphify | 133,956 | 1,173 | 2026-04-03 | Apache-2.0 | Codebase+docs -> queryable knowledge graph, as an agent skill |
| luongnv89/claude-howto | 44,038 | 1,053 | 2025-11-07 | MIT | Visual guide to Claude Code with copy-paste templates |
| OpenBMB/VoxCPM | 40,329 | 150 | 2025-09-16 | Apache-2.0 | Tokenizer-free multilingual TTS / voice cloning (VoxCPM2) |
| virgiliojr94/book-to-skill | 35,897 | 143 | 2026-05-01 | MIT | Book/PDF/folder -> one Agent Skill, chapters loaded on demand |
| anthropics/knowledge-work-plugins | 32,304 | 635 | 2026-01-23 | Apache-2.0 | 18 official role plugin dirs (skills + connectors + commands + sub-agents) |
| onyx-dot-app/onyx | 32,932 | 86 | 2023-04-27 | NOASSERTION | Self-hosted enterprise RAG chat |
| baidu/Unlimited-OCR | 28,293 | 75 | 2026-06-18 | MIT | One-shot long-horizon OCR parsing |
| TauricResearch/TradingAgents | 113,437 | 485 | 2024-12-28 | Apache-2.0 | Multi-agent LLM trading framework |
| vllm-project/vllm | 95,260 | 108 | 2023-02-09 | Apache-2.0 | LLM serving engine |
| SnailSploit/Claude-Red | 8,579 | 226 | 2026-03-04 | MIT | 78 offensive-security SKILL.md files, 23 categories |
| Anil-matcha/open-duet | 6,116 | 68 | 2023-05-25 | Apache-2.0 | Self-hosted named AI coworkers w/ memory + routines + approval |
| Mailu/Mailu | 7,585 | 4 | — | MIT | Docker mail server (long tail, not really trending) |

---

## 1. graphify — the one that matters for context-bridge

**134k*, +1,173 today, 362 contributors, 2,498 PRs, Apache-2.0.**

### Architecture worth stealing
The pipeline is strictly staged, and **stages communicate through plain dicts and NetworkX graphs, not shared objects**:

    detect() -> extract() -> build() -> cluster() -> analyze.* -> report.generate() -> export.to_*

From `ARCHITECTURE.md` (v8 branch):
- `detect(root)` -> scan summary dict (files grouped by category)
- `extract(paths, *, root=None)` -> `{nodes, edges}` dict
- `build(extractions)` -> `nx.Graph`
- `cluster(G)` -> `{community_id: [node_id]}` — **does not mutate the graph**
- `analyze.py` is sibling functions (`god_nodes`, `surprising_connections`, `find_import_cycles`, `graph_diff`) — **no single `analyze()` entry point**
- `export.py` is one function per format: `to_json`, `to_html`, `to_obsidian`, `to_svg`, `to_graphml`, `to_cypher`, `to_canvas`

Two details worth copying verbatim:

1. **The doc is drift-proofed by a test.** "Signatures below are the real ones — `tests/test_architecture_doc.py` imports every symbol named here, so this table cannot drift from the code." That is the exact failure mode we hit on 2026-10-23, when **35 of 90 dev-masterkit guides had drifted** from upstream. graphify solved it with a test instead of a periodic audit. We should do the same.
2. **Edge confidence is typed, not a float.** Every edge carries `confidence: "EXTRACTED" | "INFERRED" | "AMBIGUOUS"` plus a `relation` label (`calls|imports|uses`). The README sells this as "honest about what it found vs guessed." A float would be a lie dressed as a number.

### The claim that needs checking before we copy it
README says "71.5x fewer tokens per query vs reading the raw files." `BENCHMARKS.md` (last updated **2026-07-05**, 3.5 months stale) claims LOCOMO recall@10 of 0.497 vs BM25 0.362 and mem0 0.048, QA accuracy 45.3%, and "zero LLM credits to build the graph." It states its own harness is its own, with competing systems run as adapters inside it. Single-harness, self-adjudicated, with a blind second judge at 90.6% agreement — better than most, but not independent. Treat the ratios as a hypothesis to reproduce, not a fact.

### Relation to context-bridge — a direct competitor
context-bridge today: **0*, last push 2026-06-20, MIT**, npm package `context-bridge`, MCP server over SQLite + FTS5 + precomputed embeddings, tools `search_code`/`get_symbol`/`get_dependencies`/`get_callers`/`summarize_module`, file-watcher auto-indexing, "sub-millisecond queries," zero cloud.

The overlap is total on the problem statement ("persistent semantic knowledge graph of your codebase… sub-millisecond latency, eliminating the need to re-read files every session" vs graphify's "queryable knowledge graph… local deterministic AST parsing, every edge explained, no vector store"). graphify = Python + NetworkX + tree-sitter + Leiden clustering. context-bridge = TypeScript + SQLite FTS5.

**Three real wins context-bridge has today:**
- graphify needs a **model** to extract non-code semantics (PDFs, images, configs via Claude vision). context-bridge is fully local and deterministic.
- context-bridge's FTS5 + precomputed embeddings gives genuinely sub-millisecond queries. graphify's path is a graph traversal.
- context-bridge is a **plain MCP server**; graphify is primarily a **skill** with a library inside. An MCP server is the more composable primitive.

**Two things graphify has that we lack:**
- **Exports**: JSON, HTML, Obsidian, SVG, GraphML, Cypher, Canvas, plus a `--wiki` mode emitting one Markdown article per community. A knowledge graph whose only output is an MCP tool call is much less useful to a human.
- **Edge provenance and typed confidence**, plus `graph_diff(G_old, G_new)` — a diff of the graph across two runs. That is directly a "what changed since the last session" primitive.

**Actionable:** do not rebuild. (a) graphify already supports `graphify install --platform claw` for OpenClaw, and our skills live in `~/.openclaw/workspace/skills/` — test it. (b) Port the **edge-confidence enum** and **`graph_diff`** into context-bridge. (c) Add an export layer. (d) Consider tree-sitter for Python instead of regex/LSP.

**Also:** graphify supports **OpenClaw natively** and ships on PyPI as `graphifyy` (263 releases, 1.75M downloads/30d, +8.0%) — a dependency candidate for our own repos, not just a reference. Risk: it duplicates context-bridge's mission inside our own workspace.

---

## 2. book-to-skill — the document -> skill compiler

**35,897*, +143 today, MIT.**

Two halves, and the split is the idea:
- **Deterministic Python extractor** -> `full_text.txt` + `metadata.json` (pages, words, tokens, chapters, ToC). Parsers for pdf/epub/docx/html/rtf/calibre/text, plus `sanitize.py` stripping invisible and zero-width Unicode.
- **Spec-driven agent generator** -> the agent follows SKILL.md to produce `SKILL.md` + `chapters/*.md` + `glossary.md` + `patterns.md` + `cheatsheet.md`.

**Design principles, quoted from their architecture doc:**
1. "Extract structure, not summaries — named frameworks, decision rules, anti-patterns; never raw passages."
2. "Compile-time over runtime — pay navigation/structuring once; at query time load only the relevant chapter."
3. "On-demand chapters — SKILL.md stays small; chapter files cost tokens only when asked."

Their Step 2.6: "REPL-style probing for large books (grep/sed, no full re-reads)" — same idea as our own verified-docs approach.

**Result shape:** SKILL.md ~4,000 tokens; each chapter ~1,000; glossary ~1,500; patterns ~2,000; cheatsheet ~1,000. Claimed 24x-51x token reduction vs dumping the book into context, measured on real books.

**Relation to dev-masterkit:** we have 135 tool guides, each hand-written against upstream. book-to-skill is a *different* job — turning a body of prose into a queryable, on-demand-loaded skill. We do not have that. The **glossary/patterns/cheatsheet** triple is a better guide structure than our current per-guide shape: one guide with three on-demand indexes loads better than three separate files.

**Also relevant:** it writes to **`~/.agents/skills/`** as a cross-agent root and handles the OpenClaw case precisely (default state dir -> `~/.openclaw/skills/`; a non-default `OPENCLAW_STATE_DIR` -> the active state's `skills/` root; it does **not** infer arbitrary `skills.load.extraDirs`). That is a precise description of our own loader behavior — worth cross-checking against ours.

---

## 3. anthropics/knowledge-work-plugins — official plugin packaging

**32,304*, +635 today, Apache-2.0, 18 role dirs, 137 open issues.**

The connector model is the interesting part. Each plugin directory contains:
- `.claude-plugin/plugin.json` — `{name, version, description, author}` (productivity is at v1.3.1)
- `.mcp.json` — the MCP server wiring
- `CONNECTORS.md` — declares which external services the plugin talks to
- `skills/` — subdirectories per skill, each a SKILL.md
- `README.md`, `LICENSE`

productivity bundles connectors for Slack, Notion, Asana, Linear, Jira, Monday, ClickUp, Microsoft 365; sales adds HubSpot, Close, Clay, ZoomInfo, Fireflies; customer-support adds Intercom, Guru. The `.mcp.json` is where the actual server is declared.

**Relation to dev-masterkit:** we have 39 skills with no packaging manifest, no version, and no connector declaration. Anthropic's structure is the obvious model for making our skills installable and self-describing: a plugin.json equivalent per skill, a CONNECTORS.md for skills that touch external APIs (github, notion, youtube, browser), and per-skill versioning so a stale skill is identifiable. Our daily-updates already track counts (Skills 39) but not versions.

**Also:** `partner-built/` and `cowork-plugin-management/` show Anthropic is designing for third-party plugin authors — the format is meant to be a marketplace standard, not a vendor format.

---

## 4. open-duet — memory architecture worth copying

**6,116*, +68 today, Apache-2.0, only 6 open issues (healthy).**

Not a library — a self-hosted workspace of named AI coworkers. The design detail worth taking is the **memory layout** (from `docs/MEMORY.md`):

    <workspace>/agents/<agent id>/
    ├── MEMORY.md          loads into every turn (first 200 lines / 24 KB)
    └── memory/
        ├── <topic>.md     one subject each; never loaded whole
        ├── archive.md      older entries moved out to make room
        └── log/2026-10-23.md   one line per finished turn; never loaded

The journal and proposals live **outside** the agent's folder, deliberately: "an agent with file tools works in its own folder, and a record it could rewrite would not be a record." Correct threat model — the agent can edit anything it can write, so tamper-evident state must live where it has no write path.

**Relation to our AGENTS.md / memory/ layout:** ours is nearly identical already (MEMORY.md + memory/YYYY-MM-DD.md). What we lack: (a) the **topic file** tier (one subject per file, never loaded whole) — the difference between a 24KB MEMORY.md and a 24KB MEMORY.md you actually need; (b) the **archive** tier; (c) the **write-isolated journal**; (d) the hard 200-line / 24KB cap with the first-N rule, which we state but do not enforce.

Also relevant: approval modes — "Ask first, Accept edits, or Plan only" — plus routines that run on a schedule or on external trigger, and per-agent isolated Docker computers. We have none of the three in OpenClaw.

---

## 5. Claude-Red — skill-as-attack-surface-library

**8,579*, +226 today, MIT, 78 skills across 23 categories.** Each attack surface (SQLi, shellcode, EDR evasion, ADCS abuse) is one SKILL.md priming expert methodology. The value is the *cataloguing* discipline: 78 individually-thin skills that collectively map a domain, in a consistent format.

**Relation to dev-masterkit:** we have `skills/security-audit` and `skills/security-sentinel`. Claude-Red is a better-shaped version of the same idea — one skill per attack surface rather than two broad ones. The taxonomy is reusable as a checklist for our security skill. Not a farm: 58 watchers, 32 open issues, pushed 2026-10-12, MIT.

---

## 6. The rest — noted, not actionable

- **TradingAgents** (113,437*, +485 today) — multi-agent LLM trading framework. Architecturally interesting (analyst/researcher/risk/trader roles, shared memory, reflection loop) and directly relevant to the Architect's fintech work, but a domain application, not a reusable pattern. Worth a read if the trading project resumes.
- **claude-howto** (44,038*, +1,053 today, 25 contributors) — visual guide with copy-paste templates. The **+1,053 from a 25-person contributor base** is a distribution play, not engineering. Useful as a template-format reference for our guides; nothing to install.
- **VoxCPM2** (40,329*, +150) — tokenizer-free TTS with voice cloning, Apache-2.0. Candidate for replacing ElevenLabs in the TTS path if it fits the container's GPU budget. Not urgent.
- **Unlimited-OCR** (28,293*, +75, born 2026-06-18) — one-shot long-horizon OCR, Baidu. Relevant only if we process scanned documents; book-to-skill already covers PDF->text with a local extractor.
- **vllm** (95,260*, +108) — permanent fixture of the Python trending page, not news. 9,371 open issues.
- **onyx** (32,932*, +86) — enterprise RAG chat, noassertion license. Skip; we have the RAG pieces we need.
- **Mailu** — 4 stars today, long tail, not trending.

---

## Cross-cutting conclusion: the distribution format changed

Every top agent-tooling repo distributes the same way: a SKILL.md dropped into a **per-host skills directory**, with a per-host install command:

| Repo | Install | Per-host dirs |
|---|---|---|
| graphify | `graphify install --platform <x>` | 20+ platforms incl. `--platform claw` (OpenClaw) |
| book-to-skill | `/book-to-skill <path>` | `~/.agents/skills/` + `~/.openclaw/skills/` + `~/.claude/skills/` |
| knowledge-work-plugins | plugin marketplace | `.claude-plugin/` + `.mcp.json` |
| Claude-Red | drop in SKILL.md | Claude skills dir |

**The 20-platform install matrix in graphify is the real news.** A tool that installs itself into 20+ agent hosts is solving distribution, not functionality. OpenClaw is on that list (`--platform claw`). We have no equivalent — our skills are hand-copied into the workspace.

**Concrete proposal:** add a `plugin.json` layer to dev-masterkit mirroring Anthropic's `.claude-plugin/plugin.json` + `.mcp.json` + `CONNECTORS.md` triple, plus a `dev-masterkit install --platform claw` that **symlinks** (not copies) skills into `~/.openclaw/workspace/skills/`. Symlink matters: the local checkout stays the single source of truth, which is how the 2026-10-23 audit found 35 drifted guides in the first place.

---

## Verification notes

- Star counts, creation dates, license, topics, open-issue counts: `api.github.com/repos/<owner>/<repo>`, unauthenticated, fetched 2026-10-24 ~00:05 ET.
- "Stars today": parsed from the raw trending HTML (the markdown extractor dropped the numbers for repos whose first entry had no star block).
- PyPI: `pypi.org/pypi/graphifyy/json` (v0.9.95, 263 releases) and `pypistats.org/api/packages/graphifyy/overall` (1,755,205 downloads/30d, +8.0% vs prior 30d).
- Contributor/PR counts: `api.github.com/repos/<repo>/contributors?per_page=1` and `/pulls?per_page=1`, read from the `Link: rel="last"` header (graphify: 362 contributors, 2,498 PRs).
- Architecture claims: `raw.githubusercontent.com/Graphify-Labs/graphify/v8/ARCHITECTURE.md` and `/v8/BENCHMARKS.md`; `raw.githubusercontent.com/virgiliojr94/book-to-skill/master/docs/architecture.md`; `raw.githubusercontent.com/Anil-matcha/open-duet/main/docs/MEMORY.md`.
- **Not verified:** individual stargazer timestamps (the `/stargazers` endpoint requires auth). Star velocity is the trending page's own counter, unaudited.
- **Stale:** graphify `BENCHMARKS.md` is dated 2026-07-05. Its numbers are 3.5 months old and were produced by the project's own harness.
