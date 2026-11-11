# A collision warning is not enough if the install command is still there

**Discovered:** 2026-11-11 (tiny-memo `eae14bb`, tiny-eval `d34069e`, xvfbwrapper `b04eb95`)
**Last verified:** 2026-11-11 — all three git URLs checked with `git ls-remote`

## The situation

Six of our package names are owned on PyPI by someone else. Three of those
READMEs still showed the colliding command:

```
pip install tiny-memo      -> an unrelated package by 'meng'
pip install tiny-eval      -> TinyEval, a different evaluation framework
pip install xvfbwrapper    -> Corey Goldberg's wrapper
```

This is the worst failure mode available: **the command succeeds**. The user
gets a working program, just not the one they asked for, and nothing tells
them. `tiny-diff` is worse still — `pip install tiny-diff` gets diffusion-model
code.

## The rule

> The warning has to **replace** the command. A README that says "this name is
> taken, by the way" and then shows the install command anyway has fixed
> nothing.

Wrong:

```markdown
> Note: `tiny-memo` on PyPI is a different project.

pip install tiny-memo
```

Right:

```markdown
> **Not on PyPI.** The name `tiny-memo` on PyPI belongs to an unrelated
> project. Install from source:

pip install git+https://github.com/hussain-alsaibai/tiny-memo.git
```

## How to verify a name is free before writing either

Classify by **owner**, never by HTTP status — the 2026-11-09 mistake was
reading `200` as "published". `info.author` / `info.project_url` must match
the owner before a row counts as a pass.

```bash
curl -s https://pypi.org/pypi/$NAME/json | jq -r '[.info.author,.info.project_url,.info.name]|@tsv'
```

And verify the replacement command resolves:

```bash
git ls-remote https://github.com/hussain-alsaibai/$REPO.git HEAD
```

## Pushing to a diverged fork

`tiny-eval` rejected the push as non-fast-forward — the remote had 3 commits
without us, and a force push would have **deleted 4 real files**
(`tiny_eval_v100.py` and friends). Rebase instead: 0 deletions, and all four
files still on GitHub. Check `git diff --name-status origin/main HEAD | grep -c '^D'`
before any force push.
