# External Bounty Clean Branch Prompt

Use this prompt when bounty work exists in a local/fork branch but the final
handoff needs a clean branch containing only the issue-specific commits.

## Prompt

You are preparing a clean fork branch for an upstream bounty PR.

Build the branch from the upstream target branch, not from a dirty or historical
work branch:

- fetch the upstream target branch and create a new topic branch from it,
- identify only the commits that implement the selected issue,
- cherry-pick those commits in order,
- resolve conflicts without carrying unrelated package, lockfile, build-cache,
  or generated-output changes,
- run the project build and the focused tests that prove the issue behavior,
- push the branch to the fork under a descriptive issue-specific name,
- attempt PR creation only after the branch is pushed and verified,
- if PR creation is blocked by permissions, record the exact branch URL, test
  commands, and API error for a human handoff.

Prefer this over reusing a stale shared bounty branch. A clean branch makes the
review surface obvious and keeps parked work ready for manual PR creation when
fine-grained PAT permissions block automation.

## Verification Checklist

- Target branch was refreshed from upstream before branching.
- Topic branch name references the issue or feature.
- Only issue-specific commits were cherry-picked.
- Build command passes.
- Focused test command passes.
- Fork branch URL is recorded.
- PR-blocking permission errors are copied exactly.

## Last verified: 2026-07-17

- Repo: `hussain-alsaibai/EdgeChains`
- Upstream issue: `arakoodev/EdgeChains#290`
- Clean branch: `fix/issue-290`
- Verification:
  - `npm run build`
  - `npm test -- --run src/ai/src/tests/awsComprehend.test.ts`
- Result: branch pushed to `https://github.com/hussain-alsaibai/EdgeChains/tree/fix/issue-290`
- Blocker: GitHub PR creation failed with `403 Resource not accessible by
  personal access token`; the branch is ready for manual PR creation or a PAT
  scope fix.
