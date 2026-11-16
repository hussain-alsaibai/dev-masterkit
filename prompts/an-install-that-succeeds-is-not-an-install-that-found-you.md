---
title: An install that succeeds is not an install that found you
date: 2026-11-16
tags: [packaging, pypi, naming, audit]
source: workspace install-line census, 2026-11-16
last_verified: 2026-11-16
---

# An install that succeeds is not an install that found you

Four consecutive sweeps for broken install lines assumed one failure mode: **the name
does not exist**. That is the *visible* failure. The dangerous one is the name that
exists and belongs to somebody else.

`pip install tiny-cli` exits 0. It installs TinyBio LLC's genomics CLI.

## The rule

For a package you publish, "does this name resolve?" is the wrong question. The right
question is **"does it resolve to us?"**

A 404 is self-correcting: the command fails, the reader investigates, the line gets
fixed. A collision is silent:

1. The install succeeds, so CI and the reader both see green.
2. The wrong package is often thematically plausible, so the reader blames themselves.
3. If nothing breaks immediately, the line survives the next audit too.
4. `llms.txt` and other agent-facing docs amplify it — agents run instructions without
   applying judgement. One repo's `llms.txt` carried the bare install while its
   `README.md` two files away correctly warned against it.

## The check

Every install reference gets classified, not just existence-tested:

- **absent** — the name is not on the registry (the visible class)
- **collision** — the name resolves, but the registry author is not in the allowlist of
  own authors → the reader gets somebody else's code
- **allowed** — a third-party dependency stated deliberately, passed by name
- **unknown** — registry unreachable. Never count this as a violation; a 429 during a
  sweep must not read as a hundred broken installs.

```bash
python3 scripts/check_install_lines.py repos \
    --mine <your-author-substring> \
    --allow httpx --allow pytest --allow pyyaml
```

## Two rules the checker had to learn, both by being wrong

**Do not report the warning.** Three repos warned explicitly — *"`pip install tiny-x`
would fetch that package instead"* — and the first version flagged all three. A check
that reports the fix punishes the fix. Skip lines near warning phrasing, but only for the
package the warning actually names, or one warning masks every command on the page.

**A commented line is not an instruction.** `# pip install tiny-*` inside a fence
documents a family of names; nobody runs it.

## Before fixing a hit, read the remote

Three READMEs that looked like live collisions were **already correct on `origin/main`**.
The local clones were stale and held an older README; patching from the working tree would
have replaced correct warning text with the broken form it warns about. `git show
origin/main:README.md` before writing, every time.

## Why this class of bug persists

Each sweep fixed the shapes the previous regex imagined. The regex can only encode the
failure mode its author believed in, so the fix for a name-absent bug will always scan
for names that are absent. The two questions are not variants of each other: one is a
lookup, the other is an **ownership check against the registry's author field**.

**The collision class needs a standing check, not a sweep.** The author allowlist drifts
as accounts are renamed, so run it in the health job rather than by hand.
