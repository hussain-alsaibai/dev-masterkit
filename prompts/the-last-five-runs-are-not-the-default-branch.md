# The Last Five Runs Are Not The Default Branch

**A rule for any "how many repos are red?" scan.**

> Found 2026-11-06 (17:00 UTC health pass). The scan reported **42 of 173
> repos red**. Reading the runs showed **41 were false** and **0 real**
> failures. `snapdb` was green at 13:05:47 the same day and still counted red.
> **Last verified:** 2026-11-06 — after the fix, the formerly-wrong cases
> (`snapdb`, `reload`, `tiny-dist-audit`) all report GREEN and no repo is
> reported red without a failing latest run on its default branch.

## The Rule

> **"Is this repo red?" is a question about the newest run on the default
> branch. Not about the last five runs, and not about a branch you assumed.**

```bash
# ask the question the number claims to answer
gh run list --repo OWNER/REPO --branch "$DEFAULT" --limit 1 \
    --json conclusion,headBranch,createdAt
```

The scan did `run list --limit 5` and called any `failure` in that window
"failing". It never asked whether a **later success** existed. **A window scan
over-reports in proportion to how busy the fleet is** — the more active the
repository, the worse the news looks.

## The two sub-cases, both wrong for different reasons

| case | what the scan saw | reality |
|---|---|---|
| `snapdb` | a failure in the last 5 runs | success on `main` at 13:05:47 |
| `reload` | red on `main` | default branch is **`master`**, which is green |

`reload` is the subtler one: **the default branch is data, so read it from the
API (`defaultBranchRef.name`), never from habit.** `main` is a convention, not
a guarantee.

## A repo scanned mid-run is not a red repo

`tiny-dist-audit` was red at 13:07 and green at 13:08:30 — it was scanned while
*this* run was still pushing to it. A second pass a few minutes later is what
settles it. **Any scan that can observe the work it is complaining about needs
a settling window.**

## The fix

Filter completed runs to `headBranch == repo.defaultBranchRef.name` before
picking the latest; persist `default_branch` per repo so tomorrow's comparison
cannot silently pick a different one. Store `green/yellow/red` counts, not
just a total, so a 139-green claim cannot absorb 42 unknown states.

## The same run, second bug: a dead credential read as truth

The script did `GH_TOKEN = GH_TOKEN || GitHUB_PAT || ...`. `GitHUB_PAT` is a
dead token (HTTP 401); it silently shadowed the gh keyring. **A credential
fallback chain that always resolves is a chain that is never tested** — see
`prompts/a-dead-credential-named-in-a-prompt-fails-every-run.md`, the same
defect in a job prompt rather than a script.
