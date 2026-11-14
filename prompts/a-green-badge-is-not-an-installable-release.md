---
name: a-green-badge-is-not-an-installable-release.md
description: Use when reviewing a library's health — a green badge proves main compiles, not that users can install the newest code, and the tag / pyproject / registry / changelog must agree.
---

# A green badge is not an installable release

## The prompt

> You are reviewing a library's health. A green CI badge on `main` is not one
> of the checks — it is the check that was easiest to pass.
>
> 1. `git tag --sort=-creatordate | head -1` — the newest tag.
> 2. `grep version pyproject.toml` — what the tree claims to be.
> 3. Query the registry for the newest published release and its date.
> 4. Diff the published artifact's **public namespace** against the tree —
>    import it in a clean venv and list what it exports.
>
> Every gap between those four is a feature users cannot reach. Report the
> gap in days, and name the "verified" surface you did *not* check.

## Why

`pysnapdb`: registry **0.14.0**, published 2026-07-03. Repository **0.18.1**,
2026-11-11. **134 days.**

The gap was not small. Importing the published sdist and diffing the public
namespace showed `VectorIndex`, `cosine_similarity`, `dot_product`,
`euclidean_distance` and `QueryProfiler` were all **absent from what users
install** — plus the index-aware `Query.filter`, whose changelog entry claims
31.5x on a narrow range scan.

Three checks all said fine:

| check | said | why it missed |
|---|---|---|
| CI on `main` | green | main is ahead of the last release, always |
| registry URL | 200 | the *old* release exists |
| `release.yml` | correct | it triggers on `release: published`; no tag since v0.14.0 |

Nothing in the fleet compared *newest tag* to *newest release*. Every check
was pointed one step away from the thing a user installs.

## The four-way comparison

```
newest git tag  <->  pyproject version  <->  newest registry release  <->  changelog
```

Any two agreeing is not evidence. All four drift independently:

- a tag with no release -> the workflow never fired
- a release with no tag -> hand-published, history is now ambiguous
- `pyproject` ahead of the tag -> unreleased work on `main`, normal, but it
  must not be reported as shipped
- changelog ahead of both -> a release note for a version nobody can install

## The guard that ships

`tests/test_release_tag.py` compares tag, `pyproject` and changelog. It
**skips unless HEAD is tagged**, so ordinary commits are unaffected and the
check cannot become a tax on development.

It was proven to fail by tagging a scratch clone `v0.99.0` against a tree
declaring 0.18.1 — a guard nobody has watched fail is a guard that may be
vacuous.

## The blocked half

Publishing needs a registry token as a repo secret.
`gh api .../actions/secrets` returned `total_count: 0`. That is a concrete
blocker to report, not a reason to write "released" in the changelog.

See also `prompts/verify-the-version-recorded-in-the-artifact-not-the-binary.md`
(the version that counts is the one stamped inside the artifact) and
`prompts/a-test-that-only-runs-in-a-checkout-is-a-test-that-never-ran.md`.

Last verified: 2026-11-14 — 0.14.0 on the registry at 2026-07-03 vs 0.18.1
in the tree at 2026-11-11, confirmed by importing the published sdist.
