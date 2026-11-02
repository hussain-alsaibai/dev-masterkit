# Check The Repo Before You Recommend The Bounty

**A selection rule for any agent that picks work from a public issue tracker.**

> Found 2026-11-02. A `label:bounty` search for the last week returned two
> repositories posting the **same** 'Bounty Seguro (250 dollars)' template
> against `starlette` forks. A `label:opire` search resolved to 1-star forks
> of `kafka-go`, `minio` and `chi` with plausible titles and no funding.
> **Last verified:** 2026-11-02 - the credibility check below was run against
> each candidate with the GitHub API.

## The Rule

> **A bounty label is a claim about the repository. A repository is a claim
> about the work. Check the repository before you recommend the work.**

## The One Command That Answers It

```bash
gh api repos/OWNER/NAME \
  --jq '[.stargazers_count,.forks_count,.fork,(.parent.full_name//"-")]|@tsv'
```

Four facts in one call:

| field | what it tells you |
|---|---|
| `stargazers_count` | whether anyone uses this repository |
| `forks_count` | how many people took a copy |
| `fork` | **is this a fork of the upstream it claims to pay for?** |
| `parent.full_name` | which upstream it forked from |

**The `fork` field is the one that matters.** A fork of `starlette` posting a
250-dollar bounty on `starlette` is not a bounty. It is a template.

## The Pattern To Recognise

| signal | value | reading |
|---|---|---|
| stars | 0-1 | nobody has looked at it |
| forks | 13 | 13 copies of a template |
| owner name | `zhangjiayang6835-cyber` | random, unrelated to the project |
| issue count | 1,409 open | template spam, not a project |
| body | identical 'Bounty Seguro' text | copy-pasted across repos |

Two repositories in one search result, **the same template**, both against
forks. That is not a coincidence and it is not a market.

## The Other Failure: A Label That Resolves To Nothing

The `opire` label resolved to 74 results, and **every one** was the same
family: a random-named owner with the upstream library's name in the repo name
(`SimsChad12/go-redis`, `BernhardPierno25/kafka-go`, `CurtFigone19/pgx`,
`TrudieMasenheimer3/prometheus`, `KentonMaverick47/cobra`), each with a
`score: 1`. Plausible titles, no funding.

**And the funding itself was unverifiable:** the aggregator's public bounties
list API returned an **empty item list** to unauthenticated callers, and its
per-repo shield endpoint served HTML rather than JSON. A market you cannot
read is not a market you can report on.

## The Honest Conclusion Is Often 'No Cash'

The one credible target found that week was explicitly a **zero-bounty** task
- merge credit only, no cash. The right output for that scan was:

> Cash bounties in this niche are currently thin. The better-shaped targets
> are reproducible bugs with a public proof of concept.

**That is a useful report.** 'The label is a template and the money is not
verifiable' is actionable; a list of fake bounties is not.

## The Selection Funnel, Measured

When a scan runs, the funnel numbers are the evidence:

```
9323 found -> 6087 with a dollar sign -> 234 filtered -> 1 in top
```

**9,323 issues became 1 candidate.** Any report that quotes the 9,323 as the
opportunity size is wrong by four orders of magnitude. Report the funnel, not
the top of the first query.

## The Related Rule: The Market May Genuinely Be Empty

When the funnel ends at zero, that is a legitimate result - **provided you
say so**. On the same day, `label:algora is:open no:assignee` returned **0**
results and the scan reported the market as empty. That was correct.

The failure mode is the opposite one: a scan whose credential had died read
the 401 as 'no results' and reported an empty market that was not empty. See
`prompts/credential-order-is-not-validity.md` and
`prompts/fail-closed-on-unavailable-data.md`.

See also `prompts/opire-scam-fingerprint.md` (the scam fingerprint) and
`prompts/assigned-issue-is-a-taken-issue.md` (the assignee is the claim).
