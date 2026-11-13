# CI Trigger and Toolchain Audit

**Last verified:** 2026-11-13 (12:00 EST) — commands run against `unzip-http`
(workflow on a non-existent branch) and `ai-git-hooks` (ruff 0.15.20 vs 0.17.5,
`testpaths` with no tests) on this host.

## Does the workflow run at all

```sh
gh run list --repo OWNER/NAME --limit 10          # empty output is the finding
gh api repos/OWNER/NAME/branches  --jq '.[].name'
gh api repos/OWNER/NAME           --jq .default_branch
gh api repos/OWNER/NAME/actions/workflows --jq '.workflows[] | {id,name,state}'
```

`gh run list` returning nothing means the trigger never matched — not that CI
was never written. Both are reported as `NO_CI_WORKFLOW` by naive checks.

## Is the test step reachable

```sh
grep -n "testpaths" pyproject.toml setup.cfg tox.ini 2>/dev/null
ls -d tests 2>/dev/null || echo "NO tests/ DIRECTORY"
grep -n "pip install\|setup.py develop\||| echo ok" .github/workflows/*.yml
```

## Is the linter the same linter

```sh
python3 -m ruff --version                          # local
grep -n "ruff" .github/workflows/*.yml             # CI version
pip install --target /home/node/.cache/ruffci "ruff==<ci-version>"
PYTHONPATH=/home/node/.cache/ruffci python3 -m ruff check .
```

Local 0.15.20 reported *all checks passed*; CI 0.17.5 reported **21 errors** on
identical code, from `BLE001`, `FA100`/`FA102`, `UP045`, `EXE001`/`EXE004`.

`/tmp` is **noexec** on this host — a binary installed under `/tmp` cannot run.
Install to `/home/node/.cache/`.

## Which version actually did the work

```sh
jq -r '.metadata.skillspector_version' report.json
```

Prefer the version stamped inside the artifact over `<tool> --version`, which
answers what is on `PATH`. Two installs (`.local/bin` 2.13.1 vs `.ssvenv`
2.13.2) made the guard's answer depend on path order.

## The `/tmp` noexec trap for tests

```sh
python3 -m pytest -q --basetemp=./.pytest-tmp
```

`/tmp` is a 512 MB **noexec** tmpfs. Default `tmp_path` breaks any test that
chmod+x's a fake binary (7 of 9 tests errored "not an executable file") and
ENOSPCs large fixtures. `--basetemp` on the overlay fixes both — the mount
options were the bug, not the code.
