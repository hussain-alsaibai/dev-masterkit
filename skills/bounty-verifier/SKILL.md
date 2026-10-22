---
name: bounty-verifier
description: Two-stage bounty issue verification — hard filters + behavioral signals — to refuse scam/fork issues before picking them. Last verified: 2026-10-22.
---

# Bounty Verifier

> **Last verified:** 2026-10-22
> Born from the July 1, 2026 Opire scam flood (18/18 issues from 10 throwaway-account fork repos).
> Re-checked 2026-07-08 and again 2026-10-22 — see the dated sections below.
> See: [`bounty-scanner`](../bounty-scanner/SKILL.md) for the upstream scanner; this skill is the verification gate.

## When to Use

- Before picking **any** bounty issue, especially from aggregator platforms (Algora, Opire)
- When an issue looks "too good" (high reward + easy task + new repo)
- Whenever the upstream scanner returns N issues and you must pick 0–1 to ship

## The Two-Stage Pattern

### Stage 1 — Hard Filters (fast, boolean)

Reject the issue if **any** of:

| Filter | Value | Why |
|--------|-------|-----|
| `repo_stars` | `< 50` | Most scams are sub-50 stars; legitimate programs almost never are |
| `repo_age_days` | `< 90` | Throwaway accounts create repo, post fake bounty, vanish |
| `is_fork` | `true` | Scammers fork legitimate projects to inherit credibility |
| `creator_login` | in known-scam list | Cross-reference maintained blacklist |
| `creator_created_at` | `< 30 days ago` | Account age correlates with throwaway behavior |
| `collaborators` | `≤ 1` | Real OSS repos have multiple maintainers |

**Cost:** 2–3 GitHub API calls per issue (`/repos/{o}/{r}` + `/users/{login}`).
**Throughput:** ~100 issues/min on a single token.

### Stage 2 — Behavioral Signals (slower, score-based)

Score 0–10; reject if `< 6`:

| Signal | Weight | What "passes" looks like |
|--------|--------|--------------------------|
| Commit cadence | 0–3 | ≥1 commit / week across the last 90 days, from ≥2 different authors |
| README quality | 0–2 | Non-template: has project description, install, usage, license sections |
| Test/CI present | 0–2 | `tests/` or `__tests__/` directory exists, OR `.github/workflows/` has CI |
| Issue history | 0–2 | ≥10 real issues with non-bot comments in the last 6 months |
| Org affiliation | 0–1 | Repo is under a recognized org (e.g. `apache/`, `cli/`) — bonus, not required |

**Cost:** ~5–8 GitHub API calls per repo (paginated commit list + issue search + workflow list).
**Throughput:** ~20 repos/min.

## Output Shape

For each candidate issue, produce a verdict:

```json
{
  "issue_id": 12345,
  "repo": "owner/name",
  "creator_login": "user",
  "hard_filters": "PASS",
  "behavioral_score": 8,
  "verdict": "PICK",
  "reason": "Active repo, real CI, multiple maintainers, legit-looking issue"
}
```

Or `verdict: "REJECT"` with `reason` citing which stage tripped.

## Anti-Patterns to Watch

These are the actual signals from July 1, 2026:

1. **Fork of a famous project** (Vault, ClickHouse, Traefik, Gitea, Casbin, Apache-Pulsar, VictoriaMetrics, APISIX, spf13-cobra, GORM) — clone the name, post a fake bounty, collect "winners" who never get paid
2. **Throwaway creator account** — `thaohuynh14zc`, `elnahomenick123`, `quachminh11` (names look auto-generated)
3. **No tests, no CI, no real description** — just a `README.md` with the fork source's name
4. **Single collaborator, single commit** — "Initial commit" + the bounty issue
5. **Reward denominated in a token, not USD** — easier to fake, no platform escrow

### July 8, 2026 Re-check

The same hard filters still held during the July 8 daily scan:

- 29 issues contained dollar markers; 27 contained explicit dollar amounts
- 27/27 payout-looking issues were rejected
- Dominant triggers: `young_repo`, `no_stars`, `inorganic_forks`
- Common targets impersonated by fork repos: cobra, helm, mysql, go-redis, grpc-go, echo, gocron, zap, VictoriaMetrics
- Creator names again looked auto-generated or low-reputation (`qxrtjdggj653`, `Markp1598M`, `MariauqmpsA333`)

Do not relax the star/age/fork filters just because the issue includes a plausible USD amount.

## 2026-10-22 Re-check — the filters are correct, the scorer bypassed them

Stage 1 and Stage 2 both held up today. What failed was upstream of them: the
scorer fed them bad data and awarded points for it.

**Three defects found on a 348-issue scan:**

1. **`no_stars` fired on a 429-star repo.** The star lookup is
   unauthenticated and throttled, so it returns 0 on rate limit and the
   scorer reads that as "zero stars" — which is exactly the signal the
   filter is supposed to trust. **A signal the scorer cannot read must not
   be treated as a signal that failed.** Fail closed: no data means
   unverifiable, not clean.
2. **`competing_prs=0` on an issue with 5+ real PRs.** That is 25 unearned
   points on the #1 pick — the competition factor was the largest single
   term in the score and it was pure fiction.
3. **Ranks 2, 3 and 4 were all scam-shaped**, despite Stage 1 existing:
   `Kristywvs22/gin`, `RoseMark45/echo`, `Tylerx3udv/go-github` — every one
   created 2026-07, zero pushes after creation, not forks, zero stars.
   All three cleared the star gate because the gate read zero for a
   throttled reason.

**The #1 pick was real:** `arakoodev/EdgeChains` — 429 stars, 253 forks,
created 2023, pushed 2026-10-20.

**Procedure change.** Enforce a min-stars and min-age gate **before**
scoring rather than after, and make the star lookup fail closed. Then verify
the top pick by hand against `api.github.com` directly, every run, even
when the scanner says PASS. Verified: all 348 issues scanned, 168 filtered,
10 rejected as scam.

**Last verified: 2026-10-22.**

## Procedure

1. Run `bounty-scanner` (or equivalent) to get a candidate list
2. For each candidate: execute Stage 1 (2–3 API calls)
3. For Stage 1 survivors: execute Stage 2 (5–8 API calls)
4. Pick at most 1 issue with `verdict: PICK`
5. If zero survive, **report the drought** rather than relax the filter

## Quick-Reference (one-liner shell check)

```bash
# Stage 1 fast-reject on Opire issue URL
gh api repos/{owner}/{repo} --jq '.stargazers_count, .created_at, .fork, .size' | \
  awk -F, 'NR==1{if($1<50)exit 1} NR==2{days=(now-mktime(substr($1,1,10)))/86400; if(days<90)exit 2}'
```

## Related

- `bounty-scanner` — Upstream issue discovery (Algora + Opire + verified repos)
- `repo-creator` — Once you've picked, this scaffolds the fix repo
- `memory/2026-07-01.md` — July 1 bounty work log (the trigger for this skill)
- `memory/2026-07-08.md` — July 8 re-check: 27/27 payout-looking issues rejected by hard filters

---

**Maintainer:** OpenClaw 🦞
**Status:** Active — preventing scam picks since 2026-07-01
