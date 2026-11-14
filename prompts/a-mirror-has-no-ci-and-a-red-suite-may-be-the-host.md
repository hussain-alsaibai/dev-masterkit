---
name: a-mirror-has-no-ci-and-a-red-suite-may-be-the-host.md
description: Use when auditing or inheriting a repo under your own account — a mirror keeps upstream's badges, LICENSE copyright and "good first issues" while carrying none of its CI history, and its failing tests are more often the host than the code.
---

# A mirror has no CI, and a red suite may be the host

## The prompt

> You are about to record a verdict on a repository. Most of what you can see
> is about a different repository, or a different machine. Separate them.
>
> 1. **Provenance first.** Remote, and whether the README badges and the
>    LICENSE copyright name someone else. MIT LICENSE reading "Copyright (c)
>    2026 blixvip and Null Motion contributors", badges linking
>    `blixvip/NullMotion` → a mirror, not a project we wrote. Say that before
>    saying anything about quality.
> 2. **"22 good first issues" and "6 contributors" are the upstream's.**
>    `gh api repos/O/N --jq .open_issues_count` counts PRs as issues —
>    upstream reads **37** while the label query says **21**, and the README
>    says 22. Three numbers, one repo, none of them yours. Label it.
> 3. **Empty CI is not healthy CI.** `gh run list --repo O/N --json
>    status,conclusion` → `[]` means **no run has ever been recorded**. A
>    `ci.yml` with `on: pull_request` + `on: push: branches: [main]` fires
>    neither when a mirrored repo is created. Report "never ran".
> 4. **Run the suite — the README won't warn you.** Two of 127 tests need a
>    real browser and a vendored `gsap.min.js`; neither is mentioned. Get a
>    number before you get an opinion.
> 5. **Then treat each failure as a host hypothesis.** `channel='chrome'`
>    wants `/opt/google/chrome/chrome` (root-owned, no sudo here); the other
>    wants a dependency that was never installed. Change only the
>    environment, re-run **that file** (22/22), then `git checkout` the edit
>    and re-confirm the original failures. A green run under a patched
>    environment is a diagnosis, not a fix — and never commit it.

## Why

A mirror inherits the upstream's credibility — badges, contributor counts,
issue counts — and none of its history. On 2026-11-14 both repos reported
themselves healthy and neither had a single run under our account.
`NullMotion` did pass **27/27** and `MotionClone` did reach **128/128**, but
only after two environment changes; the evidence is the run, and the run
exists only because the host was made to cooperate. The repo's own claim
stayed at zero until something executed.
