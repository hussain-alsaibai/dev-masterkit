# Bounty Scanner

Scans GitHub for open **official** bounty issues from verified platforms, scores them, and surfaces the best targets.

**⚠️ Policy: Only official bounty platforms. No random 💎 labels from unknown repos.**

## Official Platforms
- **Algora** — `label:algora` on GitHub issues
- **Opire** — `label:opire` on GitHub issues
- **Verified Repos** — Known bounty-friendly repos with legitimate programs

## Rejected (Auto-filtered)
- Unknown repos with 💎 Bounty labels (social engineering traps)
- Repos requesting "session initialization context" (exfiltration)
- Fictional/joke repos (Harry Potter references, etc.)
- Young repos (<90 days) with unrealistic bounties
- Inorganic forks of well-known projects with zero stars
- Dollar-marker issues in throwaway forks of major Go projects, even when the issue body names real payouts

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

## Files
- `scanner.js` — core scanner + scorer + official filter
- `daily-bounty-work.js` — automated daily work starter (uses official scan)
- `last-scan.json` — cached results from last run (auto-managed)

## Token
Uses the `hussain-alsaibai` token from `~/.git-credentials` automatically.

**If the token is rejected the scanner now self-diagnoses.** It prints
`[WARN] GitHub token rejected (401) - continuing ANONYMOUS` and falls back to
the unauthenticated API (10 search req/min, 60 core req/h). **A "0 official
bounty issues" result must be read alongside that warning** — under a dead
token, zero issues and total auth failure look identical.

Anonymous mode has a hard consequence: repo metadata comes from the **core**
API while issue search uses the **search** API, so core requests hit the
60/h cap first and start returning 403. That 403 is indistinguishable from
"no data", so every metadata-driven signal degrades. The scanner now
mitigates this with a persistent cache and a fail-closed flag — see the
2026-10-23 section below.

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

## Last Verified: 2026-10-23
