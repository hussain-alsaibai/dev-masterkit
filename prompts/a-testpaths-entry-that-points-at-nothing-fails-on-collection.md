# `testpaths` pointing at nothing fails CI on collection

**Last verified:** 2026-11-13 (12:00 EST) — `ai-git-hooks` had
`testpaths = ["tests"]` and no `tests/` directory; the first CI run to reach the
Test step died on collection, not on a failing assertion.

## The rule

> **A `testpaths` entry is a claim that tests exist there.** Adding CI to a repo
> with a test config but no tests ships a job that can only fail. Either write
> the suite or remove the config first.

The repo had **zero tests**. The config was aspirational and read as done.

## The editable install is a CI prerequisite

`pip install -e .` puts `src/` on the path. Without it `pytest` cannot import
the package and every test errors with `ModuleNotFoundError` — which looks like
a hundred broken tests and is one missing step.

On this host `pip install -e .` needs `--break-system-packages` (PEP 668) and
`python3-venv` is not installed, so:

```sh
pip install --target /home/node/.cache/<name> -e .
PYTHONPATH=/home/node/.cache/<name>:src python3 -m pytest -q --basetemp=./.pytest-tmp
```

`--basetemp` matters: `/tmp` is **noexec** here, so any test that chmod+x's a
fake binary fails with "not an executable file" on the default tempdir.

## Checklist

1. `testpaths` exists on disk and contains at least one `test_*.py`.
2. Editable/target install is a step in CI before the Test step.
3. The first CI run reaches the Test step — confirm from logs, not from a green
   badge on the previous commit.
