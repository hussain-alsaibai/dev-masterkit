# When a fork PR is blocked, check the release contract first

**Last verified: 2026-11-26** — derived from the `g1mn/pqproof` 0.9.0 release PR
(#35) still open while two contributor PRs (#33, #34) stayed rebased on it.

## The situation this prompt is for

You have one or more open PRs against an upstream repo. A scheduled review says
they are stale, blocked, or "needs rebase". The instinct is to re-run the test
matrix and fix whatever is red.

Do not start there. Start with the question: **what will upstream's next release
change, and is it merged yet?**

## The prompt

```
Before changing anything in my open PRs on <repo>, establish:
1. What is the newest commit on the default branch, and what did its message claim
   to change (verdict/behaviour impact or not)?
2. Which open PRs touch VERSION, RULESET, schema, or a findings format? For each:
   state, mergeable, mergedAt.
3. For each of my PRs: state, mergeable, and head sha today vs at my last push.
4. Only if (2) shows nothing pending: re-run my tests and diff them against
   the default branch, not against my branch's parent.
Report (1)-(3) as facts with the API output quoted. Do not call anything
"blocked" until (2) is answered.
```

## Why this ordering is not pedantic

A release PR carries a **global** decision — a rule number, a version, a schema
field. A contributor PR carries a **local** one. When both are open, the local
change can be correct and still be wrong on merge, because the global number
moved. Re-running tests cannot see that: they compare your branch to a base that
is about to change underneath it.

Concretely, in this run: the branch had already been moved from ruleset 9 to 10
to make room for a release that had **not merged**. Upstream `main` was still
reporting 8.0. The rebase was locally green and globally speculative.

## The output form

A three-line block, reproducible by someone else:

```
upstream head   e53979a  2026-11-26T10:58Z  "Merge #32: release 0.8.0 ..."
release PR      #35 OPEN MERGEABLE mergedAt=null  all checks pass
my PRs          #33 OPEN MERGEABLE ed9acc4   #34 OPEN MERGEABLE 32048b8
```

Then, and only then, a decision. "Wait for #35" is a legitimate decision and is
often the cheapest one.
