# bounty-pat-write-access — When Your PAT Can't Open PRs

**Created:** 2026-07-31
**Last verified:** 2026-07-31
**Author:** OpenClaw / hussain-alsaibai
**Source:** Real GitHub fine-grained PAT behavior, July 2026

---

## The Problem

You have a PAT for `hussain-alsaibai`. The PAT can:
- ✅ Clone any public repo
- ✅ Push branches to your forks
- ✅ Read issues, PRs, commits
- ✅ View CI runs

But it **cannot**:
- ❌ Open PRs against the upstream (e.g., `arakoodev/EdgeChains`)
- ❌ Create PRs from fork → upstream
- ❌ Comment on upstream issues

The error is silent — `gh pr create` just fails or the web UI shows no "compare" button for the fork.

---

## Root Cause: Fine-Grained PAT Scope

**Fine-grained PATs (FG-PATs)** have repository-level permissions, not org-level.

If you generate a FG-PAT with access to:
- `hussain-alsaibai/dev-masterkit` ✅ (your repo)
- `hussain-alsaibai/EdgeChains` ✅ (your fork)

Then:
- `arakoodev/EdgeChains` (upstream) ❌ — your PAT has no permission there
- **You cannot create PRs to upstream from your fork**

Classic PAT tokens only had `repo` scope (full read/write to all repos you can access). FG-PATs are scoped per-repo.

---

## Detection Checklist

Before spending time on any bounty, verify PR access:

```bash
# 1. Try to create a draft PR (dry-run)
gh pr create --repo owner/upstream --title "test" --body "test" --draft 2>&1

# 2. Check if compare button appears on GitHub web UI
#    Fork the upstream → Your fork should show "contribute" button
#    If it shows "contribute" but PR fails silently → PAT scope issue

# 3. Check PAT permissions
gh auth status
gh api user/repos --jq '.[].permissions' | head -5
```

---

## The Three-Layer PR Access Model

| Layer | Token Type | Can Open PR to Upstream? |
|-------|-----------|--------------------------|
| **Fork → upstream** | FG-PAT with upstream permission | ✅ Yes |
| **Fork → upstream** | FG-PAT without upstream permission | ❌ No |
| **Fork → upstream** | Classic PAT with `repo` scope | ✅ Yes |
| **Branch on upstream** | Any token with push access | ✅ Yes |

For bounty work on external repos, you **must** have either:
1. Push access to the upstream (rare for open source)
2. A FG-PAT that explicitly grants `pull` + `push` + `merge` on the upstream repo (requires upstream owner to add you)
3. **Manual web UI PR** — you open it yourself in a browser session

---

## Workaround: Fork Branch Push

You can still:
1. Clone the upstream to a local branch
2. Implement the feature
3. Push to `hussain-alsaibai/upstream-name:feature/branch`
4. **Cannot** create the PR — need the Architect to do it via web UI

**Pattern observed (July 2026):**
- Palm2 (`EdgeChains#279`): Branch `palm2-pr` on `hussain-alsaibai/EdgeChains` ✅ pushed, PR ❌
- Qdrant (`EdgeChains#273`): Branch `feature/qdrant-vector-db` on `hussain-alsaibai/EdgeChains` ✅ pushed, PR ❌

Both implementations are complete. Both are stuck because the PAT scope doesn't include `arakoodev`.

---

## Alternative: GitHub Web UI (Manual)

If the PAT can't open the PR:

1. Go to `https://github.com/owner/upstream/compare`
2. Select your fork's branch from the dropdown
3. Fill in PR title + description
4. Submit manually

**This bypasses the PAT entirely** — your browser session has full access to both repos.

---

## Scanner Integration

The bounty scanner should flag this:

```
Repo: arakoodev/EdgeChains
Issue: #279
PAT Status: hussain-alsaibai PAT (pull-only on this repo)
PR Access: ❌ BLOCKED — FG-PAT lacks write permission
Recommendation: SKIP unless Architect opens PR manually
```

A PAT-blocked repo should score lower unless the implementation is trivial and the Architect commits to opening the PR.

---

## Related Prompts

- `already-merged-skip.md` — skip when already resolved upstream
- `bounty-saturation-pat-blocked-skip.md` — skip when PAT blocked AND saturated
- `bounty-saturation-resolved-not-skip.md` — implement anyway when mirror-shape differs
- `gitea-cross-fork-pr-blocker.md` — Gitea equivalent (different auth model)
