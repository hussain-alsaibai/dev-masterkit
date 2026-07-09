# Gitea cross-fork PR blocker — fine-grained PAT `pull`-only scope

## What this solves

When you've implemented a feature on a fork branch (`you/feature-x`) and want
to open a PR against an upstream repo (e.g. `go-gitea/gitea`, `mem0ai/mem0`,
or any third-party GitHub project), a **fine-grained PAT scoped `pull`-only
on the upstream repo will block you at PR creation**, even though
`gh repo clone` and `git push` to your own fork both work fine.

## Symptoms

- `gh pr create --repo go-gitea/gitea` → `403 Resource not accessible by integration`
- `gh api POST /repos/go-gitea/gitea/pulls` → same `403`
- `git push hussain-alsaibai:feat/x` → **succeeds** (your fork, your PAT)
- `git fetch go-gitea` → **succeeds** (read-only is fine)
- Everything looks correct, but the cross-fork PR endpoint rejects the token

## Why it happens

GitHub's PR-creation API needs at least `Triage` (or higher) write access
**on the upstream repo**. The bot's fine-grained PAT typically has:
- `Contents: read & write` on its own repos ✅ (so `git push` works)
- `Pull requests: read & write` on its own repos ✅
- `Pull requests: read-only` on the upstream repo ❌ — this is the blocker

`pull` < `triage` < `push` < `maintain` < `admin`. The fine-grained PAT
screen literally does not expose a "create PR on someone else's repo" scope
that doesn't also grant full `push`.

## Workarounds

### A. Hand off the PR to a human maintainer (cleanest)

Write the PR body to `pr_body.md` and the exact `gh pr create` command to
a handoff doc. The Architect opens the PR with their own token, then you
take over once it lands.

```sh
cd ~/github/<upstream>          # or fresh clone
gh pr create \
  --repo <owner>/<repo> \
  --head <your-fork-user>:<branch> \
  --base main \
  --title "<conventional title>" \
  --body-file pr_body.md
```

Document everything in `gitea-pr-handoff.md` or equivalent so the next
session / the Architect doesn't have to re-derive the design decisions.

### B. Open the PR via GitHub's web UI fallback

`gh pr create --web` opens a prefilled browser tab. Same token applies, but
the URL is constructed client-side, and the human can confirm with one
click. Same auth scope needed underneath.

### C. Lower the scope requirement (rare)

Some upstreams allow PRs from forks via GitHub Actions workflows
(`pull_request_target` + secrets). That's an upstream policy decision, not
something the fork owner can fix.

## Don't do this

- **Don't broaden your PAT scope to `push` on every repo.** That's the
  default a lot of old tutorials suggest, and it's a security regression
  for a bot identity.
- **Don't use the legacy classic PAT for cross-fork PRs.** Classic PATs
  bypass the fine-grained scope model entirely — same blast radius.
- **Don't keep retrying with the same token hoping for a different result.**
  The 403 is deterministic; the only fix is a different credential with
  the right scope.

## What to actually do in dev-masterkit / OpenClaw

1. Implement the feature on a branch in your fork. Push it.
2. Write the PR body, title, and design summary to files in the workspace
   (so a handoff is durable).
3. Record a clear `*-pr-handoff.md` doc with:
   - exact `gh pr create` command
   - branch name + head SHA
   - PR body file path
   - brief "what I did and why"
4. Tell the Architect via the cron summary that a manual PR-open is needed.
5. Move on; the branch is preserved until someone with the right token
   opens the PR.

## Last verified

- 2026-07-09 — `go-gitea/gitea` PR #4898 branch `feat/commit-inline-comments-4898`,
  SHA `c50dffec5a` ready in `hussain-alsaibai/gitea`; cross-fork PR blocked
  by PAT scope; handoff doc at
  `~/.openclaw/workspace/gitea-pr-handoff.md`.