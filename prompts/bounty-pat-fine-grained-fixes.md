# Bounty PAT Fine-Grained Token Fix Procedure

**Created:** 2026-08-16
**Last verified:** 2026-08-24
**Author:** OpenClaw / hussain-alsaibai
**Source:** Resolved Qdrant EdgeChains bounty — arakoodev/EdgeChains#273

---

## Problem

GitHub fine-grained Personal Access Tokens (PATs) return:

```
403 Resource not accessible by personal access token
```

...when calling `POST /repos/:owner/:repo/pulls` on an external repo, even when the token has `pull_request: write` permission.

### Root Cause

A fine-grained PAT with `pull_request: write` **still requires the upstream repo to be explicitly listed** under "Repository access" in the token settings.

> **⚠️ Scope applies to ALL endpoints including Search API:** The `/search/issues` endpoint
> (used for competition counts — counting open PRs on a target repo) ALSO requires the repo to be
> explicitly added. Without it, competition counts return `403` even though `Contents` and
> `Pull requests` permissions are set. Add `Search: Read-only` scope AND add the repo to
> "Repository access" to get full competition data. Without it, GitHub rejects the action at the access-control layer — before permission checking.

This manifests on **every new external repo** until the token owner manually adds it.

---

## Fix Procedure

```
1. Open GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Select the token (e.g. hussain-alsaibai)
3. "Repository access" section → Click "Add repository" → search for the upstream repo
   (e.g. arakoodev/EdgeChains)
4. Click the repo to add it to the token's access list
5. Under "Repository permissions" → "Pull requests" → set to "Read and write"
6. Under "Repository permissions" → "Contents" → set to "Read and write" (needed for push + PR)
7. Save
8. Copy the new token value
9. Update wherever the token is stored:
   - /home/node/.openclaw/workspace/.env → GitHUB_PAT
   - Any other env vars or credentials stores
10. For active agent sessions, restart or re-fetch the token
```

## Verify the Fix

```bash
# Test PR creation via API
curl -X POST "https://api.github.com/repos/<owner>/<repo>/pulls" \
  -H "Authorization: token ${GitHUB_PAT}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "test",
    "head": "hussain-alsaibai:pr/test",
    "base": "main",
    "body": "test"
  }'

# Should return 201 Created (not 403)
```

## Workaround (When PAT Fix Not Available)

Use the GitHub **web compare URL** — this bypasses PAT scope and uses the browser session instead:

```
https://github.com/arakoodev/EdgeChains/compare/ts...hussain-alsaibai:pr/qdrant-273
```

Format: `https://github.com/<owner>/<repo>/compare/<base>...<fork>:<branch>`

GitHub will show a PR preview. If branches are mergeable, click "Create pull request".

---

## When This Happens

- Every new external repo that isn't pre-added to the token
- After token rotation
- After repo transfer or rename
- When using a freshly created fine-grained PAT

---

## Prevention Strategy

Create a single fine-grained PAT specifically for **bounty work** and pre-add all known high-target bounty repos:

| Repo | Status |
|------|--------|
| arakoodev/EdgeChains | Add now |
| opire-dev/bounty-farm | Add now |
| Other Algora-reachable repos | Add as encountered |

Set it as `GITHUB_BOUNTY_PAT` in `.env`, separate from `GITHUB_PAT`.

---

## Related Prompts

- `bounty-pat-write-access.md` — Original PAT scope limitation documentation
- `gitea-cross-fork-pr-blocker.md` — Similar issue for Gitea instances
- `external-bounty-clean-branch.md` — Clean branch preparation for PAT-blocked bounties
