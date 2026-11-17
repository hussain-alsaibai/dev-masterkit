# A test file your CI does not name is a test nobody runs

**Discovered:** 2026-11-17 (`tiny-validator`, `tiny-config`)
**Last verified:** 2026-11-17 — both workflows switched to an explicit folded block, one
file per line; `tiny-validator` CI `44089041136` (3.8–3.12) and `tiny-config` CI
`44089484461` (3.8–3.12) both green after the change.

## The claim

A workflow that lists test files as arguments is a **second source of truth** for what
runs. Adding a test file is therefore two changes — the file, and the command that runs
it — and the second one gets forgotten precisely when the first one matters: the release
that fixes a defect class.

## What the tree showed

| repo | test file never run in CI | written for |
|---|---|---|
| `tiny-validator` | `test_v070_export_roundtrip.py` — 14 tests | 0.7.2 |
| `tiny-config` | `test_v042_secret_heuristic.py` — 9 tests | 0.4.2 |
| `tiny-cli` | (none missing) | — |

Two of three releases in one session were guarded by tests the CI could not see. And the
guards were exactly on the defect class each release fixed:

- 0.7.2 fixed an export/import mismatch — which its own round-trip suite would have
  caught.
- 0.4.2 fixed a credential leak — which its own masking suite would have caught.

So the fix shipped, the regression test shipped, and the second one was decorative from
the day it was written.

## How it reads from outside

Nothing fails. The workflow is green, the file is in the tree, `git log` shows a test
commit, and a reviewer reading the PR sees tests added. The only signal is
**`pytest` collected fewer tests than the repo contains** — which nobody measures because
the number is not compared to anything.

Cheap check:

```bash
# every test file named in a workflow must exist, and every test file must be named
grep -oE 'tests/[a-z0-9_]+\.py' .github/workflows/ci.yml | sort -u > /tmp/named
ls tests/test_*.py | sort > /tmp/present
comm -13 /tmp/named /tmp/present      # in the tree, never named
comm -23 /tmp/named /tmp/present      # named, does not exist
```

Both directions matter. The reverse direction catches a renamed file, where the workflow
keeps passing a path that resolves to nothing.

## The fix

A YAML folded block, one file per line, with a comment that a new file must be added
deliberately:

```yaml
run: |
  python -m pytest -q \
    tests/test_a.py \
    tests/test_b.py \
    # adding a test file here is part of adding the file
```

If the runner supports plain collection (`pytest tests/`), prefer it — one source of
truth beats a maintained list. Keep the explicit list only where a file must be excluded,
and make the exclusion the thing that is written down.

## The family this belongs to

This is the second instance of the same rule in this workspace:

- `testpaths = ["tests"]` pointing at a directory that did not exist — CI failed at
  **collection**, not on an assertion.
- A workflow naming files by hand, missing two — CI passed while two suites never ran.

**Rule:** a test that is collected by nobody runs by nobody. When a CI job names tests
individually, the list is a claim about coverage that must be checked both ways.

Last verified 2026-11-17 (12 tests were restored to CI; both matrices green on the changed
workflow).
