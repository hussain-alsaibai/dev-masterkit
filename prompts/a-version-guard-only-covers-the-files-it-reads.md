# A version guard only covers the files it reads

**Last verified:** 2026-11-06 (12:00 EST) — `snapdb` and `tiny-router` published
`main` re-downloaded as tarballs today (0.18.0 / 0.7.5, both consistent). The
2026-11-05 fixes and the `tiny-audit` 3.8 import claim were verified then from a
fresh clone; the sweep caveat below is from 2026-11-06.

## The rule

> **A version stated in more than one file is a version stated once and guessed
> everywhere else.** The guard that should catch it reads the pair its author
> was thinking about — which is almost never the file that drifted.

`snapdb` had `tests/test_version_consistency.py` comparing `pyproject.toml`
against `__version__`, with semver validation. It passed. Beside it, the
`package.json` was **seven minor releases** stale (`0.11.0` vs `0.18.0`).
`tiny-router` was **five** stale (`0.2.0` vs `0.7.5`) with no guard at all. Both
badges were green the whole time, because the test suite agreed with itself.

A guard is a statement about **coverage**, and the coverage is only as wide as
the list of files it opens.

## The machine check

`scripts/check_version_drift.py` is the census form of the rule: it reads every
version surface it can find in a repo and compares every pair that exists.

```bash
python3 scripts/check_version_drift.py --repo .            # one repo
python3 scripts/check_version_drift.py --root ~/github     # siblings
python3 scripts/check_version_drift.py --root . --json     # machine-readable
```

Surfaces read, per repository root:

| file | what is read |
|---|---|
| `pyproject.toml` | `[project] version`, else `[tool.poetry] version` |
| `package.json` | `version` |
| `<pkg>/__init__.py`, `*_pkg.py`, root `<name>.py` | `__version__ = "..."` |

A file that does not exist is **not** a finding — a one-surface repository
cannot drift from itself. Exit code 1 means at least one repo states two
different versions.

Normalisation is deliberately narrow:

- a leading `v` is stripped (`v1.4.2` == `1.4.2`);
- a two-component core is padded (`1.4` == `1.4.0`);
- **the pre-release tail is kept** — `1.0.0-rc1` is *not* `1.0.0`. A normaliser
  that strips every tail calls a release candidate equal to the release it
  never became.

Both of those last two points were bugs the tests caught before the script
shipped: the first version stripped every tail and rejected `1.4` == `1.4.0`.

## The census it enabled

A 170-repo sweep (`reports/2026-11-05-version-drift-census.md`) found **28 repos
carrying a `package.json`**, of which **19 ship one and no `pyproject.toml`**.
**Zero of those 19 are published to npm**, and **six declare an npm name that
already belongs to another maintainer** — `npm i <name>` installs somebody
else's package. A manifest no build step reads cannot fail, so it drifts.

The hardest case: `tiny-audit` is a **Python** library that shipped an npm
manifest instead of a `pyproject.toml`, and used a 3.10-only `dataclass`
keyword while declaring `>=3.8`. Its CI matrix started at 3.10, so CI could
never see the floor it claimed. Fixed: the keyword is gone, the matrix now runs
3.8 → 3.13, and `import tiny_audit` succeeds on 3.8.20, 3.9.25 and 3.11.2.

## What to do

1. Add the check to CI for any repo with two or more version surfaces.
2. When you already have a guard, list the files it opens. Anything outside that
   list is unguarded, no matter what the badge says.
3. For a JS-named file in a Python repo, ask what publishes it. If the answer is
   "nothing", delete it or make it a `pyproject.toml`.

**A guard whose green badge you trust is a guard you have not read.**

## The sweep measures the clones (2026-11-06)

The census above is only as fresh as the trees it walks. Run against a local
corpus four commits behind, the checker reported `snapdb` and `tiny-router`
drifting **after both had been fixed on `main` the previous day** — and the
same stale clone reported `behind=0`, because `HEAD..origin/main` compares two
refs and both were old.

| repo | clone before `fetch` | after `fetch` | published `main` |
|---|---|---|---|
| `snapdb` | `0.11.0` / `0.15.0`, "behind 0" | behind **4** | `0.18.0` on all three surfaces |
| `tiny-router` | `0.2.0` / `0.1.0` | behind **36**, ahead 1 | `0.7.5` on both surfaces |

The checker was right about the files it read. It cannot know they are stale,
and it says nothing about it. **Correctness of the tool is separate from the
freshness of what it is pointed at.**

```bash
for d in ~/github/*/; do git -C "$d" fetch -q origin 2>/dev/null; done
python3 scripts/check_version_drift.py --root ~/github

# before reporting a finding, prove it against the remote, not the ref
git -C repo ls-remote origin main
curl -sL codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/main \
  | tar xzO --wildcards '*/package.json' | grep '"version"'
```

> **A sweep over local clones is a measurement of the clones.** Fetch first,
> and prove a reported defect against the remote before it becomes a finding.
