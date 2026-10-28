# A CI Census Reveals What Was Never Checked

**A procedure for every repository that ships tests but no CI workflow — and for
every repository whose CI exists but whose matrix is wrong.**

> Found 2026-10-28. Twenty-five tiny-* repos had a test suite and **no workflow
> file at all**. Adding one to each found **8 real defects**, including two
> libraries whose central function could never run: `tiny-semantic-cache`'s
> `cosine_similarity()` raised `NameError` on **every call**, and
> `tiny-ai-workflow` could not construct a single `WorkflowStep` because
> `field(default_factory=None)` makes dataclasses call `None()`.
> Every one of those eight repos had shown a **green local test run** at some
> point. **Last verified:** 2026-10-28 — 25 workflows added, 8 defects found,
> all 25 green on GitHub after the fix; every test count in this document was
> measured by run.

## The Claim

A repository with tests is not a tested repository. The tests are a *document*
until something executes them on every change, in the environment the package
claims to support.

The census question is not "is CI green?" It is:

> **Which repositories have a test suite that nothing has ever executed?**

On 2026-10-28 the answer was **25 of 25** sampled repos with tests and no CI.
Eight of them could not work at all.

## Why a green local run proves nothing

Every one of the eight broken repos had passed locally at some point. The
reason is a single, repeatable hole:

```bash
pip install -e .     # editable install: the SOURCE TREE is on sys.path
pytest                # -> imports the loose .py file next to the test
```

An editable install puts the source directory on `sys.path`. A loose
`tiny_semantic_cache.py` sitting next to `test_tiny_semantic_cache.py` is
imported **as if it were the installed package**. So the test suite exercises
the working tree — which is fine — but it never proves the **wheel** ships the
module.

Five packages passed `pip install -e .` and still published a wheel containing
**zero importable modules**. That is the defect the local run cannot see.

## The check that matters

```bash
# 1. fresh environment, nothing inherited
uv venv "$HOME/.venvs/probe" --python 3.11
VIRTUAL_ENV="$HOME/.venvs/probe" uv pip install -e . pytest

# 2. import the module from OUTSIDE the source directory
cd /tmp && "$HOME/.venvs/probe/bin/python" -c "import tiny_semantic_cache; print('OK')"

# 3. run the suite the way CI runs it
cd "$HOME/src/tiny-semantic-cache"
"$HOME/.venvs/probe/bin/python" -m pytest test_tiny_semantic_cache.py -q
```

**Step 2 is the one people skip.** From inside the repo, the loose source file
shadows the installed package and the defect is invisible.

## The eight defects, classified

Every one was found by the procedure above, on 2026-10-28. None was a
hypothetical.

| repo | defect | shape |
|---|---|---|
| `tiny-semantic-cache` | `norm_b = math.sqrt(sum(x * y for y in b))` — `x` is not in that generator, so **every call raised `NameError`** | typo inside a generator |
| `tiny-ai-workflow` | `result: Any = field(default_factory=None, init=False)` — dataclasses **calls** `default_factory`, so `None()` raised `TypeError` | misuse of `default_factory` |
| `tiny-file-watcher` | a scan landing mid-`rename` reported the move as `DELETED + CREATED` | a rename is not atomic |
| `tiny-scheduler` | `ThreadPoolExecutor.shutdown(cancel_futures=...)` is **3.9+**, the package claims `>=3.8` | declared floor not honoured |
| `tiny-bucket-quota` | shipped `py-modules = ["tiny_rate_window"]` — **the wrong module**, copied from a sibling | packaging copy-paste |
| `tiny-llm-router` | `py_modules` instead of `py-modules` — the build failed outright | key typo |
| `tiny-jsonpath` | `package-data` used the empty-string key `""`, which modern setuptools rejects | invalid packaging table |
| `tiny-diff`, `tiny-eval` | two test files with the **same basename**, so pytest refused to collect the second | duplicate basename |

Plus a packaging class of its own: `tiny-semantic-cache`, `tiny-ai-workflow`,
`tiny-event-bus` and `tiny-task` all shipped wheels with **no importable
module**, because

```toml
[tool.setuptools.packages.find]
include = ["tiny_semantic_cache*"]
```

finds nothing — **a single top-level module is not a package.** The fix is

```toml
[tool.setuptools]
py-modules = ["tiny_semantic_cache"]
```

## Rule 1 — A collection error is not a test failure

`pytest` reports **collection errors** when it cannot even import a test
module. They look like failures in the summary line and mean something
completely different:

| outcome | what ran |
|---|---|
| `11 errors` | **nothing ran.** The module could not be imported. |
| `11 failed` | 11 assertions ran and were wrong. |

`snapdb`'s profiler bug produced **11 collection errors** — not 11 test
failures. The whole suite was unrunnable on two of the five Python versions
in CI, and the badge said nothing about the code. **Read the summary line
carefully before you diagnose anything.**

See `prompts/zero-tests-ran-is-a-failure.md` for the neighbouring case where a
suite collects zero tests and reports green.

## Rule 2 — Derive the matrix from the package's own metadata

The matrix must come from `requires-python`, not from a guess:

```bash
# the declared floor
grep -n 'requires-python' pyproject.toml

# then check every stdlib call in the package against the OLDEST version
# in that matrix, not the newest
grep -rnE 'asyncio\.to_thread|cancel_futures|str\s*\|\s*None|staticmethod' \
  --include='*.py' .
```

`tiny-scheduler` called a **3.9+** keyword while claiming `>=3.8`.
`fast-cache` called a `staticmethod` object, which is not directly callable
until **3.10** (bpo-43682). Both shipped, because CI was red and nobody read
the badge. See `prompts/python-support-is-a-claim.md`.

## Rule 3 — Name the tests that exist, not the tests you remember

`tiny-diff` and `tiny-eval` shipped `test_tiny_diff.py` in **both** the repo
root and a `tests/` directory. pytest refuses to collect the second because of
the duplicate basename — and the `tests/` copy was stale, importing APIs that
no longer existed.

```bash
ls test_*.py tests/test_*.py 2>/dev/null | sort
# then name those exact files in the workflow, or use a bare `pytest`
```

A hardcoded list that misses a file makes the badge a fiction. A bare `pytest`
runs whatever exists. See `prompts/ci-target-must-match-repo-layout.md`.

## Rule 4 — A flaky test can hide a real race

`tiny-file-watcher`'s rename test failed **3 of 6** CI matrix jobs and passed
locally most of the time. The first instinct is to make the sleep longer.
That is not the bug.

The bug was in the library: `os.rename` is **not atomic**. Between the two
halves there is a window where the old path is gone and the new path does not
exist yet. A scan landing in that window sees a deletion; the next scan sees a
creation. The move detector compared inodes between **consecutive** snapshots,
so the pairing was lost permanently.

The fix keeps an `inode -> last-seen-path` map, so a move is recovered one scan
later instead of being swallowed. Verified with a **400-trial** stress harness:
0 misses, where the old code missed 2–4 per 60.

The test fix was separate: the suite used a fixed `time.sleep(0.3)` against a
background polling thread. Replacing it with a **condition wait** returns as
soon as the event arrives and halves the suite time.

> **Reproduce the race before you fix the test.** A fixed sleep hides a real
> defect; a condition wait removes the flake without touching the library.

## Rule 5 — Use `uv`, not docker, to test a version you do not have

```bash
uv python install 3.13
uv run --python 3.13 --with pytest --with pytest-asyncio python -m pytest -q
```

Fast, leaves no image behind, and made it practical to run every repo's suite
on six versions instead of guessing.

**Put the venv under `$HOME`, not `/tmp`.** On this host `/tmp` is a 512 MB
**tmpfs**, not the 16 GB disk — creating one venv per repo there filled it
mid-run and produced spurious `No space left on device` failures that looked
like build errors.

## The procedure

1. **Enumerate** every repo with a test suite and no workflow. That set is the
   backlog; it is almost always bigger than expected.
2. **Derive** the matrix from `requires-python`, and check every stdlib call
   against the oldest version in it.
3. **Name** the test files that exist on disk, or run a bare `pytest`.
4. **Simulate CI exactly**: fresh venv, `pip install -e .`, import the module
   from outside the source tree, run the workflow's own test command.
5. **Read the outcome honestly**: collection errors ≠ test failures.
6. **Fix the defect, not the symptom**, and confirm the fix by running the
   suite on both the oldest and newest matrix versions.

## The generalisation

> **A repo with tests and no CI is not "tested" — it is untested in the only
> sense that matters. And a green local run is evidence about the source tree,
> not about the package.**

The eight defects above were not subtle, and they were not rare. They were
invisible because **nothing executed the tests in the environment the package
claims to support.**

See also `prompts/python-support-is-a-claim.md`,
`prompts/zero-tests-ran-is-a-failure.md`,
`prompts/ci-target-must-match-repo-layout.md`,
`skills/dev-env-defects/SKILL.md`.
