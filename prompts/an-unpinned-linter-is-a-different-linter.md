# An unpinned linter is a different linter

**Last verified:** 2026-11-13 (12:00 EST) — `ai-git-hooks` CI: local ruff
**0.15.20** "all checks passed", CI-pulled ruff **0.17.5** reported **21
errors**, same command, same code.

## The rule

> **Pin every linter in CI *and* in the dev extras to the same version.** An
> unpinned linter makes "it passes locally" unfalsifiable — you cannot tell a
> real regression from a toolchain change.

The newer version enabled a broader default rule set: `BLE001`, `FA100`/`FA102`,
`UP045`, `EXE001`/`EXE004`.

## Pin the rule set too

`required-version` is not enough. The rules that apply should be written in the
repo, not inherited from whatever the installed version happens to default to:

```toml
[tool.ruff]
target-version = "py38"          # match requires-python
required-version = "0.17.5"      # the CI version
```

## Check it before believing a green local run

Install the CI version and run it yourself. On this host `/tmp` is **noexec**,
so a binary installed under `/tmp` cannot execute — install to
`/home/node/.cache/` and run `python -m ruff`:

```sh
pip install --target /home/node/.cache/ruffci "ruff==0.17.5"
PYTHONPATH=/home/node/.cache/ruffci python3 -m ruff check .
```

## Checklist

1. Same version in `ci.yml` and in `[project.optional-dependencies].dev`.
2. `target-version` matches `requires-python`.
3. `required-version` set, so a stale local tool refuses rather than disagrees.
