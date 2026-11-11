# A push you can make is not a push you are allowed to keep

**Discovered:** 2026-11-11 (modelscan-bypass-poc, workspace with duplicate
checkouts)
**Last verified:** 2026-11-11 — `git push` exit 0, then the commit measured
against the **default branch's** remote ref

## The claim

A successful push proves that *some* ref moved. It does not prove that the work
landed where anyone will look. Three separate ways a green push is not
published, all encountered the same day:

1. **The remote is not the repo people read.** `origin` pointed at a legacy
   identity's copy; the current owner's repo had an identical tree but a
   different history. The push succeeded into a repo that is superseded.
2. **The branch is not the default.** A push to `master` reported success while
   the repo's default is `main` (or the reverse). GitHub shows the default
   branch first; a commit one branch over is invisible to every URL the README
   cites.
3. **A second local checkout is the one that gets read.** The workspace kept a
   mirror of files that also live in their own repos. Five "modified" files
   turned out **byte-identical to what was already on GitHub**, verified by
   fetching the published blob — the local copy had drifted, the published copy
   had not.

## Procedure

1. Push, and read the exit code — necessary, not sufficient.
2. Ask git what tracks what: `git rev-parse --abbrev-ref <remote>/HEAD` gives
   the remote's default branch. Push to that name unless you have a reason.
3. Confirm the content, not the push: `git ls-remote <remote> <branch>` for the
   SHA, then fetch the blob by URL and `sha256sum` it against the local file.
4. When two checkouts of the same content exist, compare against the **remote
   of the repo that owns the file**. `git status` answers "what differs from
   what I last committed", which is a different question from "what is
   unpublished".

## The rule, stated plainly

`git status` in a workspace with duplicated sources is not a work queue. Three
different conditions look identical there — a nested repo with real unpublished
commits, a nested repo whose patch upstream already superseded, and a mirror of
code that was published all along. Only the first needs a push. Finding out
which one you have costs one `git ls-remote` and one blob comparison, and is
the difference between shipping a fix and shipping a duplicate.
