# A Stale Clone Makes Shipped Work Look Unshipped

**Last verified:** 2026-11-20

## The prompt

> You just checked a fix in the working tree and it is not there. Before you
> conclude the push failed, or worse, re-apply the fix:
>
> **1. Which tree are you reading?** `repos/<name>` is often a working clone,
> not the published one. `git status -sb` prints the upstream; `git log -1
> origin/main` prints the commit the *remote* named, as of your last fetch —
> which may be days old.
>
> **2. Ask the remote directly.** The published state is
> `gh api repos/<org>/<repo>/contents/<path>`, not any file on this disk.
>
> **3. Only then decide.** Delivered-but-stale reads exactly like
> never-delivered from inside a working tree, and the wrong guess re-does work
> that was already merged.

## What happened

The 2026-11-20 fleet census found 15 repos whose `llms.txt` told an agent to
run `pip install <own-name>`, a name not on PyPI. All 15 were fixed and pushed.

Checking the fix afterwards from `repos/`, three clones still showed the
**original broken line** — `- Install: \`pip install tiny-config\``. The
obvious reading is "the fix never landed". It had:

```
gh api repos/hussain-alsaibai/tiny-config/contents/llms.txt
  - Install: `pip install git+https://github.com/hussain-alsaibai/tiny-config.git`
    ... `pip install tiny-config` would fail with "no matching distribution".

repos/tiny-config  -> 3 commits behind origin/main, last fetched days ago
```

The clone was behind. `git log -1 origin/main` on it showed the *old* tip,
because `origin/main` in a stale clone is a memory, not a query.

## Why this is the dangerous direction

This is the mirror of the AGENTS.md rule about a stale clone being a loaded
weapon. There the risk was pushing *over* newer work. Here it is the opposite
and subtler: **re-doing work that already shipped**, producing a duplicate
commit or a conflicting re-application of the same three-line fix, and
reporting a "fix" that was already on `main`.

Both directions have one cheap antidote: **`git fetch` before you believe any
`origin/*` ref, and `gh api` before you believe any file.**

## The one-line check

```
git -C repos/<name> fetch -q origin && \
git -C repos/<name> rev-list --count HEAD..origin/main
```

`0` means the clone has everything. Anything else means the file you are
looking at is older than the repository, and no conclusion about delivery can
be drawn from it.
