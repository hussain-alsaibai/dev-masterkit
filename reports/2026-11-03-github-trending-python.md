# GitHub Trending Python — 2026-11-03

**Source:** https://github.com/trending/python?since=daily (fetched 2026-11-03 23:02 ET)
**Stars:** total from api.github.com/repos (verified 2026-11-03 23:05 ET). "Today" is the
"stars today" column parsed from the trending page's own HTML, because the markdown
extractor drops it.
**Second signal:** every repo was checked for created_at vs pushed_at and total commit
count, because stars alone are a distribution signal, not an adoption signal.

---

## TL;DR

1. **The biggest mover is a scraping library, and it has a self-healing selector trick
   worth stealing.** Scrapling (+1,658 today) re-resolves broken CSS selectors by
   matching the element's position and sibling structure instead of trusting the
   selector. That is the same idea as context-bridge's symbol graph, applied to HTML.
2. **Soup ships the exact test we should copy: a CI-matrix-derived upper bound on
   `requires-python`.** We have the same class of bug in our own packages (below).
3. **A doc-drift bug in our own published repo: context-bridge's README advertises five
   MCP tools; the server implements four and advertises one.** `get_callers` does not
   exist. The README also claims "precomputed embeddings" and there are none.
4. **No contribution target is open.** All 11 of Soup's good-first-issues are claimed
   with active PRs and the maintainer runs a first-refusal period. Do not burn a
   chance here.

---

## The repos, ranked by what we can actually use

### 1. D4Vinci/Scrapling — 95,118 stars, +1,658 today, 1,785 commits, pushed 2026-11-03
The largest single-day mover on the page. Python web scraping: single request to
full crawl, Playwright + curl_cffi, `--impersonate 'chrome'`.

**What to steal: adaptive element tracking.** The README advertises "adaptive element
tracking, similar-element matching" and auto CSS/XPath selector generation. When a
site changes its class names, Scrapling re-finds the element by structural position
and similarity rather than by the dead selector. That is a real answer to the
selector-rot problem, and it is the same shape as what context-bridge tries to do for
code symbols.

**Relation:** direct fit for context-bridge. Our `relationships` table is created and
never populated (see below), and a structural-match fallback for FTS5 misses is the
missing half of `search_code`. Also worth a registry entry in `mcp-server-registry`
— it exposes an MCP server and is not in the catalog yet.

### 2. MakazhanAlpamys/Soup — 10,105 stars, +111 today, 2,479 commits, pushed 2026-11-03
Fine-tune and post-train LLMs from one YAML. Layer streaming trains an 8B model on a
4 GB laptop GPU. 215 open issues, 11 of them good-first-issues.

**What to steal: `tests/test_requires_python_bound.py`.** This is the best engineering
artifact in today's list. Soup's `pyproject.toml` says:

    # Upper-bounded on purpose (#358). CI tests 3.11 / 3.12 / 3.13 and nothing above;
    # 3.10 left with #1805 (end of life on 2026-10-01), when 3.13 joined.

and the test **derives the bound from the CI matrix** rather than hardcoding it, so
"widen the matrix and widen the bound must happen together" is enforced by the suite.
The docstring explains the failure mode: on 3.14+ pip resolves a torch wheel nobody
ran, and it is not a Soup error — it is a loader crash inside `c10.dll` / `libc10.so`
before any Soup code runs, so the user has nothing actionable.

That is exactly our AGENTS.md rule ("Python version support is a claim you have to
test") expressed as an executable test. **Action: port this file into
dev-masterkit as a reusable check for all our `tiny-*` packages.**

**Also steal: the refusal-message discipline.** Six of the eleven good-first-issues are
"the error message reads wrong" (RST double backticks in one message, "require" for
one flag, a refusal that names two of four tasks, a refusal that names a different
install target than the docs). Soup treats a wrong error message as a bug worth
labeling. That matches our own "a security library must not fail quietly" rule.

**Contribution status: none available.** Every one of the 11 good-first-issues carries
a `claimed` label, has a named author, and has an open PR. The maintainer's protocol
is a first-refusal period — a claim is only released after a stated deadline with no
PR. #2223 shows the check-in: "a friendly check-in, as we do with any claim that has
had no pull request for about a week (we confirmed it on 2026-10-27)."

### 3. jordan-gibbs/hyperresearch — 4,373 stars, +23 today, 132 commits, pushed 2026-11-01
Turns Claude Code / Codex into a deep research agent. A tier-adaptive 16-step pipeline
that writes into a persistent searchable vault. Ships a `.codex-plugin/plugin.json`
and a `skills/deep-research/SKILL.md`.

**What to steal: the MCP tool vocabulary.** Its MCP server exposes 12+ tools over a
SQLite vault: `search_notes`, `read_note`, `read_many`, `list_notes`,
`get_backlinks`, `get_hubs`, `vault_status`, `lint_vault`, `check_source`,
`list_sources`, `fetch_url`, `create_note`. Two of those are ideas we do not have:
**`get_backlinks`** (what references this note) and **`lint_vault`** (a self-check
over the vault's own integrity). `lint_vault` is our doc-drift scanner applied to a
knowledge base instead of a README.

**Also: the step-skill layout.** One `SKILL.md` per pipeline step (`hyperresearch-1-decompose.md`
through `hyperresearch-16-readability-audit.md`), plus a Stop hook that prevents the
agent from skipping steps. That is the shape our dev-masterkit skills want.

**Relation:** high. Our `tiny-agentskills` is one Python file; hyperresearch shows the
per-step decomposition we would need. And `get_backlinks` is the missing half of our
never-populated `relationships` table.

### 4. FlashML-org/FreeToken — 16,520 stars, +608 today, 205 commits, pushed 2026-11-04
Edge-native MoE serving: run 290B+ models on a gaming PC. **Explicitly lists OpenClaw**
among the coding agents it serves over an Anthropic/OpenAI-compatible API.

**What to steal: semantic-aware caching.** "Semantic anchor checkpoints for recurrent
state and KV caches, allowing agentic context edits (tool calls, thinking blocks) to
avoid redundant context recomputation." That is our **context-bridge** problem stated in
inference-engine language: when the agent edits its context, the cached work should
survive. Also: runtime VRAM re-allocation between expert caches and KV memory without
a restart.

**Relation:** relevant to `tiny-prompt-cache`. Worth a read when we next touch cache
invalidation — 467 open issues, 0 good-first-issues, so not a contribution target.

### 5. blader/humanizer — 64,476 stars, +407 today, 103 commits, pushed 2026-10-28
An agent skill that strips signs of AI-generated writing. Ships `.claude-plugin`,
`.cursor-plugin`, `.github/workflows/validate.yml`, and `.github/ISSUE_TEMPLATE/`
with `new-pattern.yml` and `rewrite-problem.yml`.

**Why it is trending:** it is a skill, and the skills niche is saturated (confirmed in
our own 2026-11-03 daily update: 33 of our 37 Python packages have never been
published to PyPI and the 4 that were get single-digit monthly downloads). The niche is
crowded and distribution, not usage, is what moves these numbers.

**Caution, per the standing rule:** 103 commits against 64,476 stars is a distribution
signal, not adoption. The `stargazers` endpoint returns 404 so star timestamps cannot
be dated. `pushed_at` is 2026-10-28, so it is not a dead repo — but do not report the
star count as traction.

**Relation to us: we already do this.** `dev-masterkit/skills/human-actor` covers
writing GitHub comments that read like a real developer. humanizer does the same job
for prose, not for PR bodies. No gap; no action.

### 6. calesthio/OpenMontage — 76,048 stars, +814 today, 501 commits, pushed 2026-11-03
Agentic video production: 12 pipelines, 100+ tools, 700+ agent skill and
production-knowledge files.

**What to steal: the 700-file production-knowledge corpus.** This is the largest
example of "skills as a knowledge base" on the page. Worth reading for how it splits
a huge domain into per-stage skill files rather than one giant prompt.

### 7. p-e-w/heretic — 38,904 stars, +701 today, 230 commits, pushed 2026-11-03
Training-free local model modification: remove censorship, suppress slop, reduce
sycophancy. Runs on a gaming PC, no training.

**What to steal: the technique.** Logit-space steering without retraining. Directly
relevant to our `tiny-llm-router` work if we ever want per-provider behaviour tuning
without a fine-tune budget. It is also the same goal as the "suppress slop, reduce
sycophancy" half of `heretic`, which is a personality concern, not a capability one.

### 8. aminblg/SimpleEnglish — 4,205 stars, +61 today, pushed 2026-10-05
Agent skill that makes LLMs write docs in ASD-STE100 Simplified Technical English.

**What to steal: the multi-host plugin layout.** It ships `.agents/plugins/`,
`.claude-plugin/`, `.codex-plugin/` (with `hooks.json`), and an `evals/` directory
with `check_numbers.py`, `pressure-tests.md`, `reply_scenarios.json`, and a
`results/RESULTS.md` — including a `WHY-USELESS-2026-09-02.md` that documents a
version that did not work. **Having a file that records why an approach was abandoned
is a practice we do not have anywhere.** Same multi-host layout as humanizer.

### 9. shiyu-coder/Kronos — 46,578 stars, +503 today, 76 commits, last push 2026-04-13
A foundation model for the language of financial markets.

**Caution:** 503 stars today but **no commit since 2026-04-13** and only 76 commits
total. This is the clearest distribution-not-adoption case on the page. Not a
contribution target either — the repo is effectively archived.

### 10. kornia/kornia — 12,314 stars, +272 today, 4,758 commits, pushed 2026-11-03
Geometric computer vision for spatial AI. The only repo on this page with a long
commit history proportional to its star count — a real, actively maintained library
rather than a spike. Worth a look for our vision/media work.

---

## Our own defects found while researching

These came out of comparing the trending repos against our own code, and both are
confirmed by reading the source, not inferred.

### A. context-bridge README advertises five tools; the server implements four - FIXED
Published README tool table: `search_code`, `get_symbol`, `get_dependencies`,
**`get_callers`**, `summarize_module`.

Actual state in the published `src/server.js`:
- `tools/list` advertises **only `search_code`** — the other three implemented tools
  are invisible to any MCP client that discovers tools by listing them.
- The dispatch switch implements `search_code`, `get_symbol`, `get_dependencies`,
  `summarize_module`. **`get_callers` is not implemented at all.**
- The `relationships` table is created and **never populated** — zero rows, and there
  is no `INSERT INTO relationships` anywhere in the source. `get_callers` is exactly
  the tool that needs it.

So the README describes a graph feature that does not exist. The existing test asserts
only that `tools/list` advertises `search_code`, which is why this survived.

**Fixed in v0.2.2 (pushed 2026-11-03).** The README tool table now lists the four
real tools, `tools/list` advertises all four with input schemas, and
`test/readme-consistency.test.js` parses the README and fails if it documents a
tool the server does not implement and advertise. The test was verified to fail
against the unfixed code first. A third defect surfaced while fixing this one:
`get_dependencies` returned `imports: []` for `import { a } from "./x"`, because
the pattern only matched a bare specifier directly after the keyword. That is
fixed too, with a regression test verified against the unfixed code.

### B. context-bridge claims "FTS5 + precomputed embeddings"; there are no embeddings - FIXED
README line 21: "Sub-millisecond Queries — FTS5 + precomputed embeddings". The
SQLite schema has `files`, `symbols`, `relationships`, and the FTS5 virtual tables
`file_search` and `symbol_search`. **There is no embeddings table, no vector column,
and no embedding code.** The word "embed" does not appear in `src/` at all.

The related claim "Semantic Code Search — Query code with natural language" is also
overstated: `search_code` passes the query straight to FTS5 `MATCH`, and FTS5 is a
keyword engine. Verified directly:

    'index file'            -> 0 hits
    'how do we index files' -> 0 hits
    'index*'                -> 1 hit

Natural-language phrasing does not match. It needs an `OR` of tokens or a prefix
wildcard. The tool description in `tools/list` is honest ("FTS5 query string"); it is
the README that overclaims.

**Fixed in v0.2.2.** The README now says "Fast Code Search" and "SQLite FTS5",
documents the actual query syntax, and the tool table describes `search_code` as a
keyword query. A test asserts the Features and MCP Tools sections make no
embedding or natural-language claim.

### C. Six of our `tiny-*` packages declare `requires-python = ">=3.8"` with no CI
Packages with `>=3.8` and **no CI workflow at all**:
`tiny-agentskills`, `tiny-bloom`, `tiny-chain`, `tiny-checkpoint`, `tiny-context`,
`tiny-diff`, `tiny-evaluator`, `tiny-llm-router`, `tiny-memory`,
`tiny-rate-limiter`, `tiny-repl`, `tiny-retry`, `tiny-semver`, `tiny-sentinel`,
plus more.

The version claim is untested in exactly the way AGENTS.md warns about — and for
`tiny-semver` we already know the pattern (no LICENSE, no CI, never indexed).
Soup's `test_requires_python_bound.py` is the fix: derive the bound from the matrix
and fail when they drift.

### D. `mcp-server-registry` has no entry for Scrapling
Scrapling exposes an MCP server (`mcp`, `mcp-server` are in its topics) and is not
in our catalog of 28 servers. It also has 2 good-first-issues and a real one open
now: "Cookie strings with spaces or quotes in a value silently lose cookies (uncurl,
extract --cookies)".

---

## Recommended actions, in order

1. ~~**Fix context-bridge's README**~~ - **done, v0.2.2 pushed 2026-11-03.**
   Removed `get_callers` from the tool table, dropped the embeddings and
   natural-language claims, and made `tools/list` advertise all four real tools.
   Added `test/readme-consistency.test.js`, which parses the README and fails on
   drift - verified to fail against the unfixed code first. Also fixed the
   `get_dependencies` import regex, which missed `import { a } from "./x"`.
   Still open: the `relationships` table is created and never populated, and
   `get_callers` could now be implemented on top of it.
2. **Port Soup's `test_requires_python_bound.py`** into dev-masterkit as a reusable
   check, and run it across all `tiny-*` packages. Fix the six+ packages with
   `>=3.8` and no CI.
3. **Adopt hyperresearch's `lint_vault` and `get_backlinks` ideas** for
   context-bridge: a self-check that the README matches the server, and a real
   relationship graph that `get_callers` can query.
4. **Add Scrapling to `mcp-server-registry`**, and consider its adaptive element
   tracking as the fallback for FTS5 misses.
5. **Do not** file a PR on Soup — all 11 good-first-issues are claimed with live PRs
   and the maintainer enforces a first-refusal period.

## Method note

The trending page was parsed from raw HTML (regex over `<article class="Box-row">`
blocks) because the markdown extractor drops the star counts. Every repo was then
confirmed against `api.github.com/repos` for total stars, forks, `created_at`,
`pushed_at`, and commit count. Star deltas were cross-checked against the API
rather than taken from a rendering. The `stargazers` endpoint returns 404 for every
repo tested, so star timestamps cannot be dated — `created_at` vs `pushed_at` was
used as the second signal instead, and that is what flagged Kronos and humanizer.
