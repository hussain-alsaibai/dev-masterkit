# Probing which contract a fork PR is competing against

**Last verified: 2026-11-26** against `g1mn/pqproof` at upstream `e53979a`
and its open contributors' PRs #33/#34.

## When to use this

A long-running upstream PR of yours has been rebased once already and the
upstream has since merged a **release-control** PR of its own. Before touching
tests, scan rules or golden files again, establish which contract the maintainers
are currently enforcing — a release PR that rewrites `VERSION`, `RULESET` or a
findings schema outranks any test you can add.

## The four calls

Run all four before writing code. Repo is `$R` (e.g. `g1mn/pqproof`).

```bash
# 1. what landed on the default branch, and what did it claim
gh api "repos/$R/commits?per_page=1" --jq '.[0].sha[0:7]+" "+.[0].commit.committer.date'
gh api "repos/$R/commits?per_page=1" --jq '.[0].commit.message' | head -3

# 2. is the competing PR green, and is it waiting on a human or on CI
gh pr view <n> --repo "$R" --json state,mergeable,mergedAt
gh pr checks <n> --repo "$R" | awk '{print $2}' | sort | uniq -c

# 3. is MY PR still mergeable against today's base (not last week's)
for n in <mine...>; do gh pr view $n --repo "$R" --json number,state,mergeable \
  --jq '"#\(.number) \(.state) \(.mergeable)"'; done

# 4. did a schedule event touch my branch without a commit of mine
gh api "repos/$R/pulls/<mine>" --jq '.updated_at'
```

## What the 2026-11-26 run actually returned

| Call | Output |
|------|--------|
| upstream head | `e53979a`, `Merge #32: release 0.8.0, TLS targets verify the server certificate by default. Verdict impact: yes` |
| competing PR | #35 `release: 0.9.0, detect KCDSA and EC-KCDSA. Verdict impact: yes`, head `681a927`, **OPEN, MERGEABLE**, `mergedAt: null` |
| #35 checks | every line `pass` (`grep -Ev '\bpass\b'` returned nothing) |
| my PRs | #33 `OPEN MERGEABLE` `ed9acc4`, #34 `OPEN MERGEABLE` `32048b8` |
| branch activity | both `updated_at` `2026-11-26T17:38:4xZ` — a push or schedule event, **no new commit sha** |

## The three ways this probe goes wrong

1. **RULESET integers are shared with the release PR, not yours.** The recorded
   decision was "RULESET 10 because upstream #35 took 9 for 0.9.0". But #35 is
   **unmerged**; the default branch still says 8.0. Writing ruleset 10 into your
   branch pre-claims a number that only becomes real at *their* merge. Check
   `.state`/`mergedAt` before treating a rule id as taken.
2. **`grep pass` is not "all green".** Multi-word check names (`Analyze (python)`,
   `composite action (action.yml)`) break `$2`-only parsing. The reliable form is
   the negative one above: filter *out* `pass` and require empty output.
3. **`updated_at` moving is not a rebase.** Both of my PRs showed activity ~1h
   after the last commit sha, from an unrelated event. Read `head.sha` across two
   probes before re-running a full matrix.

## Rule

When an open PR of yours is blocked, ask first whether a **release/version
contract** is unmerged upstream. If it is, the correct move is usually to wait
for the merge and rebase once, not to chase test deltas against a number that
is still in flight.
