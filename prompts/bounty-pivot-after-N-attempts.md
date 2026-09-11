# Bounty Pivot After N Failed Async Attempts

**Last verified:** 2026-09-11
**Verified on:** Rumixyz/zio #2 (actions/create-github-app bump), GitHub bounty
**Status:** Pattern confirmed across 5 attempts over 8 days

## The Pattern

When an async bounty implementation session initializes but produces no
commits across **N ≥ 3 separate invocations**, the issue is **not** the
network, the disk, or the repo state. It is the **prompt-template boundary**
or the **issue itself** (stale, scope-too-narrow, or already-fixed).

Symptoms to watch for:
- Output ends at `Starting repo examination...` or `=== Work session initiated …`
- Every session is initialization-only — no diff, no commit, no PR
- The local working dir has been cleaned between attempts
- The repo's main branch has moved (upstream bump of the very dep we are tasked
  to bump)

## Diagnostic Checklist

Before spinning another attempt, run all of these:

```bash
# 1. Is the issue still open and relevant?
gh issue view <owner>/<repo>/issues/<N> --json state,closedAt,comments

# 2. Did anyone else fix it already?
gh pr list --repo <owner>/<repo> --search "fixes #<N>" --state all

# 3. Does the upstream dep now exceed what the issue asked for?
gh api repos/<owner>/<repo>/contents/<workflow-file> --jq .content | base64 -d \
  | grep -E "uses:.*actions/create-github-app(@|/)"

# 4. Is your local clone clean / does the worktree still exist?
git -C /home/node/github/<repo> status && \
  git -C /home/node/github/<repo> worktree list
```

If **any** of those shows the issue is stale, the fix is upstream, or the
worktree is gone — pivot immediately. Do not spawn attempt #6.

## Pivot Decision Rule

| Attempts | Same Issue | Action |
|----------|------------|--------|
| 1–2      | —          | Normal — bugs/typos, retry |
| 3        | —          | **Stop and diagnose** — run checklist |
| 4–5      | Identical init-only output | **Hard pivot** — pick new target |
| 6+       | —          | Remove from rotation entirely |

## What To Pivot To

1. Run `daily-repo-discovery` cron for a fresh scan (or invoke
   `bounty-scanner` skill manually).
2. Pick a repo that matches at least **2 of 3** priority axes:
   - **Fintech / payments / SOC** (matches our stack)
   - **AI agents / security tooling** (matches our expertise)
   - **Active maintainer, recent commits within 7 days**
3. Verify the new pick against `bounty-freeze-detection.md` and
   `opire-scam-fingerprint.md` before allocating compute.

## Recovery Pattern (Verified 2026-09-10/11)

```bash
# 1. Acknowledge the failed attempts in the daily log
echo "$(date -u) - Issue pivot: <old-issue> after N attempts" >> memory/$(date +%F).md

# 2. Clear the local working dir if it is corrupted
rm -rf /home/node/github/<old-repo>

# 3. Log the pivot in the accountability cron output
echo "pivot: <new-repo> <new-issue>" >> /tmp/bounty-target

# 4. Update the bounty-target file the daily-bounty-work cron reads
# (See workspace/AGENTS.md for the exact path used in your env)
```

## Lessons Learned

- **Issue staleness ≠ your fault.** When the upstream bumps the dep itself,
  no agent-side work can produce a useful PR.
- **Identical init-only output across attempts is the dead giveaway.**
  Network/repo failures show distinct error messages; prompt-boundary failures
  produce no error at all.
- **Compute spent retrying is compute stolen from working bounties.**
  Pivot hard; the daily-accountability cron already counts days, not attempts.
