---
name: git-pr-workflow
description: "Cherry-pick workflow for opening PRs against external repos with fine-grained PATs. Last verified: 2026-08-15."
---

# Git PR Workflow for External Repos

## Adding Upstream Remote & Cherry-Picking

```bash
# 1. Add upstream as remote
git remote add upstream https://github.com/arakoodev/EdgeChains.git

# 2. Fetch latest upstream
git fetch upstream

# 3. Create fresh branch from upstream target (not from fork!)
git checkout -b pr/my-feature upstream/ts

# 4. Cherry-pick relevant commits
git cherry-pick <commit-sha-1> <commit-sha-2>

# 5. Drop build artifacts
git rm --cached tsconfig.tsbuildinfo
echo "tsconfig.tsbuildinfo" >> .gitignore
git add .gitignore && git commit --amend --no-edit

# 6. Push to fork
git push -u origin pr/my-feature
```

## Opening the PR

### Via API (requires PAT with repo access)
```bash
curl -X POST https://api.github.com/repos/owner/repo/pulls \
  -H "Authorization: token ${GitHUB_PAT}" \
  -H "Content-Type: application/json" \
  -d @/tmp/pr_payload.json
```

### Via Web Compare URL (bypasses PAT scope)
```
https://github.com/owner/repo/compare/base...fork:branch
```

## Fine-Grained PAT: External Repo Access

Fine-grained PATs require **explicit repository access** for each external repo.

**Error:** `403 Resource not accessible by personal access token` on PR creation API.

**Fix:**
1. GitHub → Settings → Developer settings → Fine-grained tokens
2. Under "Repository access", add the external repo (e.g. `arakoodev/EdgeChains`)
3. Set Permissions → Contents: **Read and write** + Pull requests: **Read and write**
4. Save and copy new token

## Cherry-Pick Multi-Commit

```bash
# Get commits from a branch
git log --oneline feature-branch -10

# Cherry-pick range
git cherry-pick <oldest-sha>..<newest-sha>

# Abort if conflicts
git cherry-pick --abort
```

## Dropping Build Artifacts

```bash
# Remove cached build artifact from staging
git rm --cached tsconfig.tsbuildinfo

# Or from the last commit
git rm --cached dist/*.js
git rm --cached coverage/.coverage

# Amend without changing commit message
git commit --amend --no-edit
```
