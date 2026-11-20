# An Unclaimed Issue Is Not an Unfixed Issue

**Last verified:** 2026-11-20

## The prompt

> You found a real bug, the issue is open, unassigned, `comments: 0`, and no
> PR in the open list has a matching title. Before you write the fix:
>
> **1. Read the issue's timeline, not just its fields.** An `assignee: null`
> issue with zero comments can still carry a `cross-referenced` event. That is
> a PR, and GitHub does not put it in `assignee`.
>
> **2. Check the PR's file list, not its title.** The linked PR was called
> `fix: validate option offsets in order schemas` — exactly the fix. A title
> search with your own keywords would have found it; the *field* search would
> not.
>
> **3. Compare against upstream `main`, not your clone.** `gh api
> repos/<org>/<repo>/contents/<path>?ref=main`, because a local clone may be
> sitting on someone else's branch.
>
> **If a PR exists and is unmerged for months, the ticket is not open — it is
> contested.** That is a different decision, not a green light.

## What happened

The 2026-11-20 discovery run recorded `marketcalls/openalgo` issue #1820 as a
clean pick: `assignee: null`, `comments: 0`, "no matching open PR", and a fix
that was two lines plus one import. All of that was measured, and all of it was
true as far as it went.

Two things it did not measure:

```
gh api repos/marketcalls/openalgo/issues/1820/timeline
  -> labeled x5, cross-referenced #1873

gh api repos/marketcalls/openalgo/pulls/1873/files
  -> .github/workflows/ci.yml
     restx_api/schemas.py              <- the fix
     test/test_order_schema_validation.py
```

PR #1873, open since August, `updated 2026-09-05`, last commit
`2026-08-25 test: cover multi-order offset validation`, **107 additions**. It is
the same fix, with tests. It is not merged, but it exists and its author is
still attached to it.

## Why this one is easy to get wrong

Three independent readings all pointed the same way, and all three were
recorded from the same wrong surface:

- `assignee: null` — GitHub puts reviewers, not authors, here once a PR links.
- `comments: 0` — an automated link posts a timeline event, not a comment.
- `pulls?state=open` title search — the PR's title used "offsets" and mine
  used "offset validator"; substring matching would have saved it, and a
  reviewer would not have.

The bug itself was completely real, which is what makes this dangerous. Verified
upstream:

```
gh api repos/marketcalls/openalgo/contents/restx_api/schemas.py?ref=main
  227:    offset = fields.Str(required=True)   <- no validator
  262:    offset = fields.Str(required=True)   <- no validator

restx_api/data_schemas.py:23 validate_option_offset  <- correct, and unused here
```

`validate_option_offset` accepts ATM / ITM1-50 / OTM1-50 and is applied in
`data_schemas.py:147`. It is simply never wired into the two order schemas, so
`offset="BOGUS"` reaches the live order path. **A correct validator that is not
called looks identical to a validator that does not exist.** The red-then-green
test proved that in nine failures.

## The cost of not checking

Writing the fix here costs an hour and produces a PR that conflicts with #1873,
or duplicates it, on a repo with 402 open issues where a maintainer has to
reconcile two attempts at the same two lines. The bug was real; the *slot* was
not free.

## The checks, in order

```
gh api repos/<org>/<repo>/issues/<n> --jq '{state,assignee,comments}'
gh api repos/<org>/<repo>/issues/<n>/timeline --jq '.[] | select(.event=="cross-referenced") | .source.issue.number'
gh api repos/<org>/<repo>/pulls/<pr>/files --jq '.[].filename'
gh api "repos/<org>/<repo>/pulls?state=open&per_page=100" --jq '.[] | "\(.number) \(.title)"'
```

Field checks say whether anyone *claimed* it. The timeline and file list say
whether anyone *worked* it. Only the second question decides whether the work
is yours.
