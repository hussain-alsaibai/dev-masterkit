# reusable-ci-matrix-template — Reusable GitHub Actions Python CI

## Description

A drop-in `.github/workflows/ci.yml` for any zero-dep Python library that
runs the same matrix (ruff lint + pytest across multiple Python versions)
that ships in `tiny-router`, `tiny-validator`, `fast-cache` and the rest
of the `tiny-*` ecosystem. Verified by rolling it out to three
production repos in one morning with no per-repo customization.

## Why a single template instead of `actions/setup-python` boilerplate

Three repos × boilerplate `setup-python@v5` × matrix entries = copy-paste
drift. A repo-specific lint gap appears, three CI configs go stale, and
two weeks later you're fixing CI in repos that haven't shipped code in
months. One file, one source of truth, one place to bump
`actions/setup-python` or `ruff` versions.

## The template

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.8", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Lint with ruff
        run: |
          python -m pip install --upgrade pip
          pip install ruff
          ruff check .

      - name: Run tests
        run: |
          pip install -r requirements-dev.txt 2>/dev/null || true
          pytest -v --tb=short
```

Drop this in `.github/workflows/ci.yml`, commit, push. Done.

## When to use

- A Python repo has zero CI and you want the bare minimum: lint + test
  across multiple Python versions on PRs
- You're adding a new `tiny-*` library and want to skip CI setup
- You're cleaning up a repo whose existing `.github/workflows/ci.yml`
  is broken / duplicated / stale

## When NOT to use

- Repo already has working CI - don't churn
- Repo needs a build matrix (C extensions, Rust extensions) - extend this
  template with a `build-wheel` job instead of replacing
- Repo needs coverage reporting + codecov - add a `pytest-cov` step,
  don't rip out the matrix
- Repo tests need real services (postgres, redis, k8s) - this template
  only covers unit tests in an ephemeral runner; add a `services:` block

## Customization checklist

Before committing, check:

1. `python-version` matrix: change if the project drops 3.8 support or
   adds 3.13. Don't ship a matrix the project doesn't actually test.
2. `requirements-dev.txt` may not exist - drop that line if there's no
   pinned dev deps, or replace with `pip install -e .` if
   `pyproject.toml` has a `[project.optional-dependencies.test]` block.
3. If `pytest.ini` or `pyproject.toml` has `[tool.pytest.ini_options]`,
   nothing special needed - `pytest` picks it up automatically.
4. If `ruff.toml` or `pyproject.toml` has `[tool.ruff]` config, ruff
   picks it up automatically. Don't paste a second config file.

## What this template does NOT do (worth knowing)

- No coverage reporting - add `pytest-cov` + `codecov` separately
- No build job - this is unit-test CI only, no `python -m build` step
- No Windows matrix - Ubuntu runner only (add `windows-latest` if the
  project needs Windows coverage)
- No caching of `pip` downloads beyond what `setup-python` does by default
- No release publishing - add a separate `release.yml` workflow

## Last verified: 2026-07-11

- `hussain-alsaibai/tiny-router` - `7254ea7` on `main` - added CI, 15/15 tests passing locally
- `hussain-alsaibai/tiny-validator` - `eff3dd9` on `main` - added CI, 31/31 tests passing locally
- `hussain-alsaibai/fast-cache` - `9755a43` on `main` - added CI, 18/18 tests passing locally

All three are zero-dep Python libraries with `pyproject.toml` only, so
the `requirements-dev.txt` install step is a no-op (`pip install -r ...`
returns exit 0 when the file is absent under `pip` 21+). The
`cache: pip` hint relies on a `requirements*.txt` or `pyproject.toml`
being present; `pyproject.toml` is sufficient for setup-python@v5 to
cache wheels.
