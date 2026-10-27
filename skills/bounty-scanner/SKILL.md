---
name: bounty-scanner
description: Scan GitHub for official cash bounty and non-cash contributor-task issues, score them 0-100, and auto-reject scam patterns before ranking targets. Use when hunting for paid or mergeable open-source issues to work on, or when checking whether the bounty market is real or saturated.
---

# Bounty Scanner

Scans GitHub for open **official** bounty issues from verified platforms, scores them, and surfaces the best targets.

**⚠️ Policy: Only official bounty platforms. No random 💎 labels from unknown repos.**

## Official Platforms
- **Algora** — `label:algora` on GitHub issues
- **Opire** — `label:opire` on GitHub issues
- **Verified Repos** — Known bounty-friendly repos with legitimate programs
- **Contributor Tasks** — non-cash bounties: an issue in an established repo
  whose body is a spec and whose labels are `good first issue` / `help wanted`

## Rejected (Auto-filtered)
- Unknown repos with 💎 Bounty labels (social engineering traps)
- Repos requesting "session initialization context" (exfiltration)
- Fictional/joke repos (Harry Potter references, etc.)
- Young repos (<90 days) with unrealistic bounties
- Inorganic forks of well-known projects with zero stars
- Dollar-marker issues in throwaway forks of major Go projects, even when the issue body names real payouts
- Repos with <5 stars (fork farms) — demoted below trustworthy picks
- **Bounties already contested by 3+ open PRs** — a "first merged PR takes the
  payout" bounty with 10 rival PRs is effectively closed (added 2026-10-24)
- **Issues that already have an assignee** — added 2026-10-25. See below.

## Scoring (0–100)
| Factor | Max | Logic |
|--------|-----|-------|
| Payout | 40 | $1 = ~0.02 pts, capped at 40 |
| Competition | 25 | 25 pts with 0 open PRs, -10 per existing PR |
| Stack affinity | 20 | Go/JS/PHP/Python = high; Ruby/Java = medium |
| Spec clarity | 10 | Has acceptance criteria, examples, active comments |
| Freshness | 5 | Updated <7d = 5pts, <30d = 3pts, older = 1pt |

## Usage
```bash
# Official bounties only (default)
node scanner.js scan-official

# Legacy: all bounties (not recommended — high scam rate)
node scanner.js scan-all

# Print formatted Telegram report from last scan
node scanner.js report

# Output top 5 as JSON (for cron)
node scanner.js top
```

## An assigned issue is a taken issue (2026-10-25)

The 07:03 scan that day selected `pipeshub-ai#4063`. A maintainer had already
assigned it to `louisss1016`, with an open PR behind it. The issue said
"Comment here to claim it. One assignee." Nothing in the scanner or in
`daily-bounty-work.js` looked at the assignee, so a task somebody else was
already doing scored as available and the work would have started on it.

Closed, awarded, PR-contested, star-count and scam were all checked. The one
signal that actually decides whether a task is still open was not. **This is
the same bug class as the four failures above — a signal that was never read,
not a signal that was read and misjudged.**

The fix is cheap because the search API returns `assignees` on every issue
object, so the check costs no extra request:

- `scanner.js` rejects any issue with an assignee, flagged `already_assigned`.
  The singular `assignee` field is honoured too.
- `daily-bounty-work.js` re-checks, because it is the component that decides
  what work actually starts.

Regression test:

```bash
node test-assigned-issues.js   # 11 checks, all must pass
```

**Generalisation:** when picking work in a repo that hands tasks out one at a
time, the assignee is the claim. Check it before the PR count — one open PR
on an assigned issue is somebody's finished work, not a contest.

## A dead credential is read as "no market" (fixed 2026-10-27)

This is the fifth occurrence of the same bug class, and the most expensive
one, because it disabled the entire pipeline rather than one check.

`getToken()` used to return the FIRST credential it found:

```js
if (process.env.GITHUB_TOKEN) return process.env.GITHUB_TOKEN;
if (process.env.GitHUB_PAT) return process.env.GitHUB_PAT;   // <- DEAD
```

On this box `GitHUB_PAT` holds a **dead** fine-grained token (93 chars,
`github_pat_...`, HTTP 401 in every auth style) while the **working** classic
token (40 chars, `ghp_...`) lives in `~/.git-credentials` and in
`gh auth token`. The early return meant the working credential was never
reached.

The scanner noticed the 401 and degraded to ANONYMOUS (60 req/hr) - correct
behaviour for a genuinely dead token. But then the repo-metadata fetch failed
for every candidate past the 60th, `detectScam()` read the missing repo as
0 stars, and the farm gate dropped all 15 real picks:

```
[GATE] WARNING: no trustworthy pick survived - market is all farms
```

The market was not all farms. **The metadata was unreadable**, and unreadable
was read as zero stars, and zero stars was read as scam. That is the
fail-open bug the section below warns about, one level up:

| what was true | what was read | consequence |
|---|---|---|
| token 401 | no credential | anonymous, 60 req/hr |
| metadata unreachable | 0 stars | farm_flagged_no_stars |
| 15 good candidates | 0 trustworthy picks | no work started |

**The fix:** collect ALL candidates, validate each one, use the first that
authenticates.

- `scanner.js` - `tokenCandidates()` + `getToken()` now validate in order.
  `tokenIsValid()` caches per token (a single global boolean would have
  cached the dead token's verdict and applied it to the working one).
- `reverify.js` - `resolveToken()` does the same for the live pre-flight gate.

**Generalisation:** a credential lookup must never trust *order*. Order is
not evidence of validity. Validate, then use.

**Second rule:** a scan that reports zero trustworthy picks must say WHY it
has zero metadata, not just zero picks. "market is all farms" is a claim
about the world; "repo metadata was unreachable, so stars were unknown" is a
claim about the run. Only the second one is actionable.

## The pre-flight gate is now wired in (2026-10-27)

`reverify.js` was written on 2026-10-26 and tested (9 pass / 2 fail), but the
two failing checks were the integration ones: `daily-bounty-work.js` neither
required the module nor called it. The gate existed and was not in the path.

It is now in the path: the worker requires the module, `main()` is async, and
every candidate that passes the scan-level checks is re-verified against the
LIVE API before work starts. A candidate that is assigned, closed, contested
or unreadable is skipped and the loop moves on.

Verified live against the real API:

```
pipeshub-ai/pipeshub-ai#4753 -> rejected: assigned since the scan to wanjinhao1
pipeshub-ai/pipeshub-ai#4754 -> rejected: assigned since the scan to one-ansh
```

Those are exactly the two issues yesterday's scan surfaced as clean picks.

## Fail-Closed Rules (learned the hard way)

**Never treat unavailable data as a pass.** This scanner has shipped three
bugs of the same shape: a `catch(() => null)` fed into a trust decision, and
the null read as "clean":

| Date | Signal | Read as | Reality |
|------|--------|---------|---------|
| 2026-10-23 | repo metadata fetch failed | no stars | 1-star fork farms |
| 2026-10-23 | model-cost tracker read SQLite | zero usage | 74.2M tokens/day |
| 2026-10-24 | PR competition search failed | zero competition | 25 open PRs |

Rules that follow from it:
- **Competition is measured in its own phase**, over the top 30 candidates
  only, so the request count stays bounded.
- **The HTML path is the source of truth when the API is exhausted.** An
  issue page embeds its linked PRs; that needs no API quota. Both sources are
  used and the **higher** count wins.
- **An unmeasurable count is `COMPETITION_UNKNOWN` (-1)**, never 0. It scores
  as maximum competition, and `daily-bounty-work.js` refuses to start work on
  it.
- **The dead `scoreIssue()` helper was deleted**, not left in place. A
  landmine containing the exact expression that broke the scanner is how the
  bug comes back.

Run the regression tests after touching the scorer:

```bash
node test-competition.js   # 12 checks, all must pass
```

## Contributor tasks: bounties that pay no cash (added 2026-10-24)

The label sweep above only finds CASH bounties. A large class of real,
mergeable work uses no cash convention at all: an issue in an established repo
whose body is a spec ("### Files", "### What to change", "### How to verify",
"### Out of scope") and whose labels are `good first issue` / `help wanted`.

On 2026-10-24 this blind spot cost a full day. The scanner ranked a 0-star
fork farm first and rejected every legitimate candidate, while
`pipeshub-ai/pipeshub-ai#4531` — 3.8k stars, a spec with pinned test
vectors, zero competing PRs — was invisible to it.

They are found by body shape, not by label, because there is no label that
marks them:

- `CONTRIBUTOR_TASK_QUERIES` — the search queries. `"How to verify"` is the
  high-signal marker; it cuts 462k bare `good first issue` issues down to
  ~1.6k real specs, which is what makes the sweep affordable on an anonymous
  quota.
- `looksLikeContributorTask()` — requires a verification step AND a scope
  section AND a minimum body length, so a vague "please fix this" never
  qualifies.
- `contributorTaskPayout()` — returns a **non-cash marker**, not a dollar
  amount. A task pays no cash, so inventing a dollar value would be a lie.
- `specQuality()` — stands in for the payout score. A task that names the
  file, the line, the expected values and the verification command is work
  that can be done without guessing.
- `CONTRIBUTOR_TASK_MIN_STARS` (500) — with no cash to anchor the value,
  the repo's reputation is the only trust signal. Far stricter than the
  5-star floor for cash bounties.

The `payout === 0` skip in the scorer is the trap here. A contributor task
prices at 0 because it pays no cash, and treating that 0 as "not a bounty"
dropped every one of them before it could be scored. The rule is now
`payout === 0 && !task`.

Run the regression tests after touching this logic:

```bash
node test-contributor-tasks.js   # 43 checks, all must pass
```

## The quota-death bug: "unmeasured" read as "malicious" (fixed 2026-10-24, late)

The contributor-task sweep collected **300** issues and the scanner scored
**zero** of them. The 08:32 scan rejected 231 of its 250 candidates as
"Scam detected" and every survivor was a 0-star fork farm.

Nothing malicious was detected. Three defects stacked:

1. **Repo metadata died on the core quota.** The anonymous core API allows
   60 requests/hour. The sweep spends that on the first 60 candidates; every
   fetch after returns `null`. `detectScam()` reads a missing repo as
   0 stars, and `fetchRepo()` returning `null` is fatal - a fork farm and a
   3.8k-star repo are indistinguishable once the metadata is gone.
   **Fix:** `parseRepoHtml()` reads the star/fork/created fields out of the
   repo's HTML page, which has no rate limit. `fetchRepo()` falls back to it
   when the API is unavailable, and records `_source: 'html'` so a report can
   be honest about which path produced the number.

2. **Absent metadata counted as two flags, not one.** The `no_stars` check
   fired on a missing repo (absent = 0 stars) *and* the `unverified_repo`
   check fired, giving two flags = a hard scam reject. Unmeasured is not
   malicious. **Fix:** the `no_stars` signal is suppressed when the repo
   object is absent, leaving exactly one flag.

3. **The shape filter was a heading whitelist.** It required the exact trio
   "How to verify" + "Files/What to change" + "Steps/Acceptance criteria".
   Real maintainers write "## Acceptance criteria", "## Done when",
   "## How to check the change", "## Scoped task", "## Goal", "## Scope".
   282 of the 300 collected issues were legitimate specs thrown away.
   **Fix:** all of those heading variants are accepted; the vague-issue
   rejections still hold.

A fourth defect sat behind the third: the contributor-task star floor only
rejected when the star count was a **number** below 500, so a task in a repo
whose metadata was unavailable skipped the check entirely and passed. That is
fail-open, so it is now `unmeasurable_stars_for_contributor_task` - rejected.

The sweep also reads **3 pages** per query, not one. `"How to verify"` matches
1,581 issues; sorting by `created desc` means page 1 holds only the newest
100, so 1,481 real specs were invisible.

**The general lesson, now the fourth occurrence of this bug class:** every
one of these was *unavailable data read as a pass*. The competition check,
the repo-metadata check and the model-cost tracker had all done it before.
Any new trust signal must ask "what does this code do when the value is
missing?" and the answer has to be *reject*, never *accept*.

## Finding bounties the label sweep misses

GitHub search cannot wildcard a numeric label prefix, so `$XX` labels are
searched one literal at a time (`DOLLAR_LABELS` in `scanner.js`). Projects
using this convention: JHipster (`$100`, `$500`), bcgov, kodadot, Quantacms.
Projects using a bare `bounty` label state the payout in the issue body —
that amount is parsed too, because the label alone prices the issue at 0.

Each literal label costs one search request and anonymous search is 10/min,
so the sweep is paced at 7s per label.

## Repo Metadata Cache

`repo-cache.json` (7-day TTL) caches **successful** repo metadata lookups only,
so a transient rate limit cannot poison it, and a failed live fetch returns
stale data rather than `null`. Currently holds 29 verified repo records.

## Scam Detection Patterns
| Pattern | Description |
|---------|-------------|
| Session info extraction | Requests for OpenClaw runtime data, session context |
| Fictional content | Harry Potter, made-up repos, non-existent projects |
| Inorganic forks | Forks of popular repos with zero stars, no activity |
| Young repos | <90 days old with unrealistic bounty amounts |
| Same operators | Repeat offenders with multiple fake repos |
| Go-project fork wave | Fake "Fix:" issues in forks of cobra, helm, mysql, go-redis, grpc-go, echo, gocron, zap, VictoriaMetrics |
| **Mirror-repo aggregator + stub fork** | `Vikingr2023/awesome-agent-bounties` mirrors real issues onto near-empty stub repos (only `README.md` + `main.go` with `fmt.Println`). Every top-5 candidate was a stub. Auto-block the aggregator and any repo it references. |
| **File-existence gate** | Before selecting any bounty, verify at least one file mentioned in the issue actually exists in the repo. Flag repos with <3 source files as likely scams. |

## Recent Verification Notes

- **2026-07-08:** Daily bounty scan found 29 issues with dollar markers and 27 with explicit dollar amounts. All 27 payout-looking issues were rejected by the existing hard filters: `young_repo`, `no_stars`, and `inorganic_forks`. No bounty work started.
- **2026-07-12:** Daily bounty run scanned 200 official issues and 327 bounty-labeled issues. Top 7 candidates all hit `competition = 0/25`, surfacing a saturation-floor masking pattern: the algorithm has its saturation-cap hit floor on every candidate, so ranking no longer separates "popular but still worth doing" from "popular and operationally blocked." Follow-up proposed: surface issues with 0 open PRs even at lower scores, OR attach a `saturated_warning` flag so humans can override intelligently.
- **2026-07-14:** Daily bounty run scanned 336 official issues; 240 filtered by anti-scam heuristics. Top 5 candidates all saturated or out-of-skill-stack. The saturation-floor masking pattern recurred (top candidates converged to the same score), confirming it as a stable scanner calibration debt rather than a one-off. Decision: skip per `prompts/bounty-saturation-pat-blocked-skip.md`. No code committed, no PR API calls. Existing parked branches remain parked: `hussain-alsaibai/EdgeChains:ts @ d0ceb72a` (Qdrant) and `hussain-alsaibai/gitea:feat/commit-inline-comments-4898 @ c50dffec5a`.
- **2026-07-15:** Daily bounty run scanned 336 total issues, 334 with dollar markers, and rejected 241 through the anti-scam / hard-filter path. Top 9 were unchanged in shape from the prior saturated queue: implemented Qdrant and Gitea branches still parked, non-implemented top candidates had at least 3 open PRs or were out-of-stack, and a fresh PR probe still returned `403 Resource not accessible by personal access token`. Decision: skip per `prompts/bounty-saturation-pat-blocked-skip.md`. No new fork, no new commits, no PR API calls.
- **2026-07-25:** Daily bounty run scanned top 5 candidates — all from `Vikingr2023/awesome-agent-bounties` aggregator, all pointing to stub repos. Example: `MurphyThomas87/go-redis` — only `README.md` + `main.go` (`fmt.Println("Hello, Bounty Hunter!")`), no `pubsub.go`, no actual Redis code. Created ~2026-07-12, single commit. 2 users already claimed (code-cannot-be-blank, Zubi-fix). Same pattern across all 5: young_repo + zero implementation. Verdict: NOT WORKABLE. Added `Vikingr2023/awesome-agent-bounties` + stub-fork pattern to scam blocklist. Added file-existence gate recommendation. No valid bounty found today.
- **2026-08-24:** Parallel batch scoring fix applied. Sequential forEach loop (250 issues × 3 API calls) was hanging indefinitely. Replaced with `pMap(items, fn, 10)` using native `https.get` + `Promise.all`. Runtime: ~25s (vs. hanging). Also fixed: `httpGet` helper was NOT passing token to `https.get` — competition search (`/search/issues`) returned 401s for all candidates. Token injection confirmed broken for parallel code path. Competition counts still show 0 due to GitHub fine-grained PAT requiring explicit repo addition for search API (not just repo read endpoints). Scanner healthy, no actionable bounty found today.

The scanner's `top N` output is not actionable when every candidate bottoms
out at the same competition score. The saturation-floor masking pattern is
now confirmed across three daily runs (2026-07-12, 2026-07-14, and
2026-07-15).
When this pattern appears:

1. Record it in this file's "Recent Verification Notes" with date and
   top-N score distribution.
2. Do NOT force an implementation to make the day look productive.
   Follow `prompts/bounty-saturation-pat-blocked-skip.md` instead.
3. The pending scanner fix is either (a) surface zero-open-PR candidates
   even at lower raw scores, or (b) attach an explicit `saturated_warning`
   flag so the human caller can decide whether to override.

## 2026-10-23 Verification Notes

- **The anti-scam filters were correct; the signal path into them was
  broken.** A 348-issue scan surfaced 20 picks and all 20 carried
  `no_stars`; 18 were 1-star forks with $10 labels. The root cause was
  `httpGet('.../repos/X').catch(() => null)` returning `null` on a 403
  rate-limit, so `detectScam()` received `repo || {}` — an empty object
  that produces exactly one flag instead of two, and therefore passed the
  `>= 2 flags = reject` rule.
- **Fixes:** persistent `repo-cache.json` (successful fetches only, 7-day
  TTL, stale-on-failure), an `unverified_repo` red flag for missing
  metadata, fork:star ratio compared against `stars` instead of
  `watchers_count`, and a `MIN_STARS=5` selection gate that demotes rather
  than hard-rejects. `stars` and `repo_age_days` are now on each record.
- **Measured:** rejections 161 -> 241, surfaces 20 -> 9, and the #1 pick
  (`javelin-anticheat/py-workedtask`, 1 star, 51 forks, born and abandoned
  the same day) was rejected. Every survivor was a 0-1 star fork farm aged
  93-99 days. `[GATE] WARNING: no repo met 5 stars - market is likely all
  farms` was emitted.
- **Auth:** all four credential paths return HTTP 401; `~/.git-credentials`
  is 0 bytes; no SSH key. The scanner self-diagnoses and continues
  anonymously rather than returning zero issues silently.
- **Verification:** `node --check scanner.js` plus a 4-case unit test
  (known scam -> scam, real 429-star repo -> clean, unavailable metadata ->
  scam, known fork farm -> scam). Backup at
  `scanner.js.bak-20261023-070714`.
- **EdgeChains #290 was deliberately not started.** `arakoodev/EdgeChains`
  is genuine (429 stars, org bounty posted by `sandys`) and was the only
  non-farm candidate, but it is dead: 75 PRs mention Comprehend and at least
  5 target #290 alone on an issue with 95 comments.

## 2026-10-24 Verification Notes

### The fail-closed family, now four occurrences

| Date | Signal | Read as | Reality |
|------|--------|---------|---------|
| 2026-10-23 | repo metadata fetch failed | no stars | 1-star fork farms |
| 2026-10-23 | model-cost tracker read SQLite | zero usage | 74.2M tokens/day |
| 2026-10-24 | PR competition search failed | zero competition | 25 open PRs |
| 2026-10-24 | repo metadata died on the core quota | 0 stars = 1 flag | 231 of 250 rejected as scam |

The general rule, and it has now cost a day twice: **never treat unavailable
data as a pass.** Any new trust signal must ask "what does this code do when
the value is missing?" and the answer has to be *reject*, never *accept*.
See `prompts/fail-closed-on-unavailable-data.md`.

Rules that follow:
- **Competition is measured in its own phase**, over the top 30 candidates
  only, so the request count stays bounded.
- **The HTML path is the source of truth when the API is exhausted.** An
  issue page embeds its linked PRs; that needs no API quota. Both sources are
  used and the **higher** count wins.
- **An unmeasurable count is `COMPETITION_UNKNOWN` (-1)**, never 0. It scores
  as maximum competition, and `daily-bounty-work.js` refuses to start work
  on it.
- **The dead `scoreIssue()` helper was deleted**, not left in place. A
  landmine containing the exact expression that broke the scanner is how the
  bug comes back.

Run `node test-competition.js` (12 checks) after touching the scorer.

### Contributor tasks: bounties that pay no cash

The label sweep above only finds **cash** bounties. A large class of real,
mergeable work uses no cash convention at all: an issue in an established repo
whose body is a spec ("### Files", "### What to change", "### How to verify",
"### Out of scope") and whose labels are `good first issue` / `help wanted`.

On 2026-10-24 this blind spot cost a full day. The scanner ranked a 0-star
fork farm first and rejected every legitimate candidate, while
`pipeshub-ai/pipeshub-ai#4531` — 3.8k stars, a spec with pinned test
vectors, zero competing PRs — was invisible to it.

They are found by **body shape, not by label**, because no label marks them:

- `CONTRIBUTOR_TASK_QUERIES` — the search queries. `"How to verify"` is the
  high-signal marker; it cuts 462k bare `good first issue` issues down to
  ~1.6k real specs, which is what makes the sweep affordable on an anonymous
  quota.
- `looksLikeContributorTask()` — requires a verification step AND a scope
  section AND a minimum body length, so a vague "please fix this" never
  qualifies.
- `contributorTaskPayout()` — returns a **non-cash marker**, not a dollar
  amount. A task pays no cash, so inventing a dollar value would be a lie.
- `specQuality()` — stands in for the payout score. A task that names the
  file, the line, the expected values and the verification command is work
  that can be done without guessing.
- `CONTRIBUTOR_TASK_MIN_STARS` (500) — with no cash to anchor the value, the
  repo's reputation is the only trust signal. Far stricter than the 5-star
  floor for cash bounties.

**The trap:** the `payout === 0` skip in the scorer. A contributor task prices
at 0 because it pays no cash, and treating that 0 as "not a bounty" dropped
every one of them before it could be scored. The rule is now
`payout === 0 && !task`.

Run `node test-contributor-tasks.js` (43 checks) after touching this logic.

### The quota-death bug: "unmeasured" read as "malicious"

The contributor-task sweep collected **300** issues and the scanner scored
**zero** of them. The 08:32 scan rejected 231 of its 250 candidates as
"Scam detected" and every survivor was a 0-star fork farm. Nothing malicious
was detected. Three defects stacked:

1. **Repo metadata died on the core quota.** The anonymous core API allows
   60 requests/hour. The sweep spends that on the first 60 candidates; every
   fetch after returns `null`. `detectScam()` reads a missing repo as 0 stars,
   and a fork farm and a 3.8k-star repo become indistinguishable.
   **Fix:** `parseRepoHtml()` reads the star/fork/created fields out of the
   repo's HTML page, which has no rate limit. `fetchRepo()` falls back to it
   and records `_source: 'html'` so a report can be honest about which path
   produced the number.
2. **Absent metadata counted as two flags, not one.** The `no_stars` check
   fired on a missing repo *and* the `unverified_repo` check fired, giving
   two flags = a hard scam reject. Unmeasured is not malicious.
   **Fix:** the `no_stars` signal is suppressed when the repo object is absent,
   leaving exactly one flag.
3. **The shape filter was a heading whitelist.** It required the exact trio
   "How to verify" + "Files/What to change" + "Steps/Acceptance criteria".
   Real maintainers write "## Acceptance criteria", "## Done when",
   "## How to check the change", "## Scoped task", "## Goal", "## Scope".
   **282 of the 300 collected issues** were legitimate specs thrown away.
   **Fix:** all of those heading variants are accepted; the vague-issue
   rejections still hold.

A fourth defect sat behind the third: the contributor-task star floor only
rejected when the star count was a **number** below 500, so a task in a repo
whose metadata was unavailable skipped the check entirely and passed. That is
fail-open, so it is now `unmeasurable_stars_for_contributor_task` — rejected.

The sweep also reads **3 pages** per query, not one. `"How to verify"` matches
1,581 issues; sorting by `created desc` means page 1 holds only the newest
100, so 1,481 real specs were invisible.

## Files
- `scanner.js` — core scanner + scorer + official filter
- `daily-bounty-work.js` — automated daily work starter (uses official scan)
- `reverify.js` — live pre-flight gate (assignee / closed / competing PR)
- `extract-fn.js` — literal-aware source extractor used by the test harnesses
- `last-scan.json` — cached results from last run (auto-managed)
- `repo-cache.json` — repo metadata cache, 7-day TTL (scam detection)
- `competition-cache.json` — open-PR counts, 6-hour TTL
- `fixtures/iss62.html` — real captured issue page for the competition tests
- `fixtures/farm-gate-2026-10-24.json` — the 14-farm-pick shortlist
- `test-competition.js` — regression tests for the fail-closed logic
- `test-contributor-tasks.js` — regression tests for contributor-task detection
- `test-assigned-issues.js` — regression tests for the assigned-issue gate
- `test-reverify.js` — regression tests for the pre-flight gate
- `test_gate.js` — regression tests for the farm-filter gate

### All five suites pass (2026-10-27)

```bash
node test_gate.js             # 7 passed, 0 failed
node test-competition.js       # ALL TESTS PASSED
node test-contributor-tasks.js # ALL TESTS PASSED
node test-assigned-issues.js   # 11 passed, 0 failed
node test-reverify.js          # 11 passed, 0 failed
```

The two suites that used to be red are now green, and the reasons were both
in the harness, not the logic:

- `test-competition.js` aborted with `unterminated function: parseLinkedPRs`
  because its naive brace counter counted the escaped `{` inside the regex
  `/"linkedPullRequests":\{"nodes":\[\]/` as a block delimiter. The error
  fired before a single assertion, so 12 checks had been silently disabled
  since 2026-10-25. It now uses `extract-fn.js`, which tracks literals.
  The fixture also moved from volatile `/tmp/iss62.html` to
  `fixtures/iss62.html`, and a missing fixture is now a FAILURE rather than a
  SKIP.
- `test_gate.js` read the LIVE `last-scan.json`, which every scan rewrites, so
  it asserted the shape of one historical result. It now reads the pinned
  `fixtures/farm-gate-2026-10-24.json`.

## Token
Credentials are resolved by **validating candidates, not by order**:
`GITHUB_TOKEN`, `GitHUB_PAT`, `GH_TOKEN`, `~/.git-credentials` (both
`user:token@` and bare `token@` forms), then `gh auth token`. The first one
that authenticates is used. Do not reintroduce a first-match-wins lookup —
see the dead-credential section above.

## Last Verified: 2026-10-27

All five regression suites pass on the current tree:

| suite | result |
|---|---|
| `node test_gate.js` | 7 passed, 0 failed |
| `node test-competition.js` | ALL TESTS PASSED |
| `node test-contributor-tasks.js` | ALL TESTS PASSED |
| `node test-assigned-issues.js` | 11 passed, 0 failed |
| `node test-reverify.js` | 11 passed, 0 failed |

Verified by run on 2026-10-27. The two suites that used to be red are now
green, and both reasons were in the harness, not the logic:

- `test-competition.js` aborted with `unterminated function: parseLinkedPRs`
because its naive brace counter counted the escaped `{` inside the regex
as a block delimiter. The error fired before a single assertion, so 12 checks
had been **silently disabled since 2026-10-25**. It now uses `extract-fn.js`,
which tracks literals. The fixture also moved from volatile `/tmp/iss62.html`
to `fixtures/iss62.html`, and a missing fixture is now a **FAILURE** rather
than a SKIP.
- `test_gate.js` read the **LIVE** `last-scan.json`, which every scan
rewrites, so it asserted the shape of one historical result. It now reads
the pinned `fixtures/farm-gate-2026-10-24.json`.

**A test that cannot fail is worse than no test.** A harness that aborts
before its first assertion reports a syntax error, which reads like a broken
implementation. It was not broken. It was not running.

The credential fix was verified against the live API: `GitHUB_PAT` returns
HTTP 401 and `gh auth token` returns HTTP 200 on the same host, at the same
moment. A post-fix scan returned a real 50 USD target
(`caley-io/marketing#1`) instead of an empty shortlist.
