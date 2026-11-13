---
name: ci-that-actually-runs
description: Audit and repair a repo's CI so the workflow actually triggers, collects the tests, and runs the pinned toolchain. Use when a repo shows a green badge but has never run CI, when CI fails on collection, or when local and CI linters disagree.
---

# CI That Actually Runs

**Last verified:** 2026-11-13 (12:00 EST) — derived from `unzip-http` (workflow
never ran once) and `ai-git-hooks` (collection failure, linter drift, raw-string
syntax bug) in the same session.

A green badge is a claim about the last run. Three of today's repos had a badge
that described a workflow which could not have run, or a step that could only
fail.

## Step 0 — Has it ever run?

```sh
gh run list --repo OWNER/NAME --limit 5       # empty == never ran
gh api repos/OWNER/NAME/branches --jq '.[].name'
gh api repos/OWNER/NAME --jq .default_branch
```

If the run list is empty, the trigger never matched. Do not read the YAML as CI.
Check that every branch named in `on.push.branches` exists on the **remote**.
`branches:` is an allowlist; `master` and `main` are different branches.

## Step 1 — Will the tests be found?

- `testpaths` in `pyproject.toml` must point at a directory that exists and
  contains `test_*.py`. A `testpaths` entry pointing at nothing fails on
  collection, which reads as a code failure.
- Install the package before the test step (editable, or
  `--target /home/node/.cache/<name>` + `PYTHONPATH=...:src` on this host —
  PEP 668 blocks a bare `pip install -e .`).
- Use `--basetemp=<repo>/.pytest-tmp`. `/tmp` is **noexec** and 512 MB here, so
  tests with fake executables fail and tests with big fixtures hit ENOSPC.

## Step 2 — Is the toolchain the one you tested against?

Pin, in one place, and have the test read the pin:

| tool | pin where | checked by |
|---|---|---|
| ruff | `ci.yml` **and** `dev` extra | `required-version` + `target-version` |
| scanner | script constant, referenced by CI | version inside the artifact |
| python | `requires-python` + matrix | the matrix row that proves it |

An unpinned linter makes "passes locally" unfalsifiable. Install the CI version
to `/home/node/.cache/` (not `/tmp`) and run `python -m ruff` before believing
a local pass.

## Step 3 — Does any step fail by construction?

Grep the workflow for the two shapes that always fail:

```sh
grep -n "setup.py develop\||| echo ok\||| true" .github/workflows/*.yml
grep -n "branches:" -A3 .github/workflows/*.yml
```

- `python setup.py develop` — removed from modern setuptools.
- `command || echo ok` — a `||` fallback on a verification step reports success
  for the failure it was added to catch.
- Network fetches of hardcoded external fixtures — replace with a local server.

## Step 4 — Prove it, then prove it failed before

1. Push; confirm the run appears and reaches the Test step **in the logs**.
2. Restore the old workflow/regex/config and confirm the new tests go red.
3. Record the run id in the commit message or daily update.

A suite never seen red is a suite you know nothing about.
