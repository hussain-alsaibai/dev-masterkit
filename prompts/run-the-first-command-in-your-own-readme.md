---
name: run-the-first-command-in-your-own-readme
description: Use when auditing a published package's onboarding — execute the install line verbatim in a clean environment before believing CI, tests, or docs that describe the package from the inside.
---

# Run the first command in your own README

## The prompt

> You are auditing a published package. Before you read its CI badge or its
> test results:
>
> 1. Open the README and copy the **first command** a stranger would run.
>    Usually the install line. Copy it character-for-character.
> 2. Run it in a clean environment — no editable install, no `PYTHONPATH`, no
>    sibling checkouts on the path. A venv and a network connection.
> 3. If it installs, **import the package and call one function.** Installing
>    is not the goal; the package working is.
> 4. If a package of that name resolves on the registry, check **who owns it**
>    before calling the install a pass. `pip install tiny-cli` succeeding is a
>    failure if the resulting CLI is someone else's genomics tool.
>
> Every other check you have inspects the package from the inside. This one is
> the only instruction a user follows before they can run any of it.

## Why

On 2026-11-14 the 65 workspace packages were censused against PyPI:

| name status | count |
|---|---|
| resolves to us | 1 (`pysnapdb`) |
| belongs to another maintainer | 5 |
| does not exist | 59 |

41 READMEs opened with a bare `pip install <name>`. **40 of those were
unhedged** — no note that the package was not on the registry at all.
Reproduced directly:

```
pip download --no-deps tiny-cors
-> ERROR: Could not find a version that satisfies the requirement tiny-cors
```

That was the entire onboarding experience for the package. It had a green
CI badge, a passing suite, and a README whose first instruction could not
succeed.

46 READMEs were rewritten to the `git+https` form already used by
`fast-cache`/`tiny-config`/`tiny-cli`, and each was verified with
`pip download` — not by reading the diff.

## The shape it belongs to

| Looks like | Actually is |
|---|---|
| green CI | the code compiles and the tests pass, inside the repo |
| passing tests | the suite runs in a tree with `src/` on the path |
| a README | a description of the package, not a test of it |
| **an install line** | **the only claim a stranger tests first** |

Nothing in CI ever runs the README. A docs build renders the line; it does not
execute it. So the install line is the single most-read and least-tested
sentence in any repository.

## A 200 from the registry is not a pass

Five names resolved — to other people's packages:

- `tiny-cli` -> `TinyBio`'s bioinformatics CLI
- `tiny-router` -> `nekonoshiri`'s package
- `tiny-diff`, `tiny-memo`, `tiny-eval` -> other maintainers

The only pass condition is a registry entry whose project URL points at *our*
repository. Check ownership, not existence.

## Two wrong answers a bulk rewrite produces

Both are worth knowing because both shipped behind a success count.

1. **`pip install https://github.com/...` without the `git+` prefix**, written
   into 39 files. pip treats a bare VCS URL as malformed, so every "fixed"
   README still failed, with a different error. Found by opening one edited
   file; a regex sweep then found the other 38.
2. **A URL pointing at the wrong repository.** `tiny-task` got the
   `openclaw-workspace` URL because the nested checkout's `origin` points at
   the parent repo. Found by diffing every written URL's slug against its
   directory name.

**Verify the artifact, not the exit code.** `fixed: 40` verifies that 40 files
were written, not that 40 *correct* files were written.

## The guard

`scripts/check_install_lines.py` walks the tree, asks the registry whether each
advertised name is ours, and exits **1** if one is not. It exits **2** when the
registry cannot be reached — a check that reports "all fine" on a network error
is worse than no check at all.

See also `prompts/pypi-name-collision-is-a-silent-success.md` (a collision that
installs *something* is the harder case) and
`prompts/a-collision-warning-must-replace-the-install-command.md` (a warning
next to a working install line changes nothing).

Last verified: 2026-11-14 — census and 46 fixes reproduced with `pip download`
in a clean environment on this host.
