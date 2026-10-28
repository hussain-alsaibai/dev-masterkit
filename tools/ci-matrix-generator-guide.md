# CI Matrix Generator — One Script, 25 Repositories

**A runnable generator that derives a GitHub Actions matrix from a package's own
metadata, so the matrix can never claim a version the package does not support
and can never name a test file that does not exist.**

> Written 2026-10-28 after hand-deriving 25 of these. **Last verified:**
> 2026-10-28 — used to generate the workflows for 25 tiny-* repositories; all 25
> were green on GitHub afterwards, and 8 real defects were found by the step the
> generator makes possible.

## Why a generator instead of a template

`prompts/reusable-ci-matrix-template.md` documents the shape of the workflow.
That is the right thing to **read**. It is the wrong thing to **paste**, because
the two values that matter are different in every repository:

| value | where it comes from | what happens when you guess |
|---|---|---|
| the Python matrix | `requires-python` in `pyproject.toml` | CI claims support for a version the package breaks on |
| the test files | `ls test_*.py tests/test_*.py` | CI runs a subset, or a file that is not there |

Both guesses were wrong in practice. `tiny-scheduler` declared `>=3.8` and
called a **3.9+** keyword. `tiny-diff` and `tiny-eval` shipped **two test files
with the same basename**, so pytest refused to collect the second.

## The generator

Save as `gen_ci.py` and run it with the repository names as arguments:

```python
#!/usr/bin/env python3
"""Generate a GitHub Actions CI workflow for a repo that has tests but no CI.

Reads the real requires-python floor from pyproject.toml and the real test
file list from disk, so the matrix never claims a version the package does
not support and never names a test file that does not exist.
"""
import os
import re
import sys
import tomllib
from pathlib import Path

WS = Path(os.environ.get("REPO_ROOT", "/home/node/.openclaw/workspace"))

# Python versions that exist on the GitHub ubuntu-latest image.
ALL = ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]


def floor_for(req):
    if not req:
        return "3.8"
    m = re.search(r"(\d+)\.(\d+)", req)
    if not m:
        return "3.8"
    return f"{m.group(1)}.{m.group(2)}"


def versions_for(floor):
    fi = tuple(int(x) for x in floor.split("."))
    out = []
    for v in ALL:
        vi = tuple(int(x) for x in v.split("."))
        if vi >= fi:
            out.append(v)
    return out


def test_files(repo):
    """Test files relative to the repo root, excluding caches."""
    found = []
    for p in sorted(repo.iterdir()):
        if (p.is_file() and p.name.startswith("test_") and p.suffix == ".py"):
            found.append(p.name)
    tdir = repo / "tests"
    if tdir.is_dir():
        for p in sorted(tdir.iterdir()):
            if (p.is_file() and p.suffix == ".py"
                    and p.name.startswith("test_")):
                found.append(f"tests/{p.name}")
    return found


def has_dev_extra(repo):
    """True when pyproject declares a [dev] optional-dependency group."""
    pyproject = repo / "pyproject.toml"
    if not pyproject.exists():
        return False
    data = tomllib.loads(pyproject.read_text())
    extras = data.get("project", {}).get("optional-dependencies", {})
    return "dev" in extras


def build(repo_name):
    repo = WS / repo_name
    pyproject = repo / "pyproject.toml"
    req, name = None, repo_name
    if pyproject.exists():
        proj = tomllib.loads(pyproject.read_text()).get("project", {})
        req = proj.get("requires-python")
        name = proj.get("name", repo_name)
    floor = floor_for(req)
    versions = versions_for(floor)
    tests = test_files(repo)

    lines = [
        "name: CI", "",
        "on: [push, pull_request]", "",
        "permissions:", "  contents: read", "",
        "jobs:", "  test:", "    runs-on: ubuntu-latest",
        "    strategy:", "      fail-fast: false", "      matrix:",
        "        python-version: [%s]" % ", ".join('"%s"' % v for v in versions),
        "    steps:",
        "      - uses: actions/checkout@v4",
        "      - uses: actions/setup-python@v5",
        "        with:",
        "          python-version: ${{ matrix.python-version }}",
        "      - name: Install",
    ]
    # Install the dev extra when there is one -- it carries pytest-asyncio
    # for repos whose tests are async.
    if has_dev_extra(repo):
        lines.append("        run: pip install -e .[dev]")
    else:
        lines.append("        run: pip install -e . pytest")
    lines += [
        "      - name: Unit tests",
        "        run: python -m pytest " + " ".join(tests) + " -v",
        "",
    ]
    return name, req, floor, versions, tests, "\n".join(lines)


if __name__ == "__main__":
    for repo_name in sys.argv[1:]:
        name, req, floor, versions, tests, wf = build(repo_name)
        out = WS / repo_name / ".github" / "workflows" / "ci.yml"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(wf)
        print(f"{repo_name}: floor={floor} versions={versions} tests={len(tests)}")
        print(f"  -> {out}")
```

```bash
python3 gen_ci.py tiny-semantic-cache tiny-ai-workflow tiny-file-watcher
```

```
tiny-semantic-cache: floor=3.9 versions=['3.9', '3.10', '3.11', '3.12', '3.13'] tests=1
  -> .../tiny-semantic-cache/.github/workflows/ci.yml
```

## Validate before you push

A workflow file that does not parse produces a run with **zero jobs**, which
looks exactly like a flaky runner:

```bash
python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

For the full schema check against the official Actions JSON Schema, see
`prompts/validate-workflow-schema.md`.

## Then simulate CI locally, exactly

```bash
#!/bin/bash
# fresh venv, pip install -e ., run the tests the workflow names,
# on the oldest and newest Python in the matrix.
d="$1"; v="$2"
V="$HOME/.venvs/cisim-$d-$v"
rm -rf "$V"; uv venv -q "$V" --python "$v" 2>/dev/null
cd "$WS/$d"
VIRTUAL_ENV="$V" uv pip install -q --link-mode=copy -e . pytest \
  || { echo "  $d@$v INSTALL FAILED"; rm -rf "$V"; exit 1; }
tests=$(grep -A2 'Unit tests' .github/workflows/ci.yml | grep 'run:' \
  | sed 's/.*python -m pytest //; s/ -v//')
out=$(cd "$WS/$d" && "$V"/bin/python -m pytest $tests -q 2>&1 | tail -1)
echo "  $d@$v: $out"
rm -rf "$V"
```

```bash
for v in 3.8 3.13; do ./ci_sim.sh tiny-semantic-cache $v; done
```

**Put the venv under `$HOME`.** `/tmp` here is a 512 MB tmpfs; one venv per
repo filled it mid-run and produced `No space left on device` failures that
looked like build errors in a dozen repositories at once.

## The step the generator makes possible

Generating the workflow is cheap. **Running it against a fresh environment is
what finds the bugs.** On 2026-10-28 that step found 8 real defects across 25
repositories — two libraries whose central function could never run:

- `tiny-semantic-cache`: `sum(x * y for y in b)` — `x` is not in that
  generator, so **every call** raised `NameError`.
- `tiny-ai-workflow`: `field(default_factory=None, init=False)` — dataclasses
  **calls** the factory, so `None()` raised `TypeError` on every step
  registration.

Full list: `skills/ci-census/SKILL.md` and
`prompts/ci-census-reveals-what-was-never-checked.md`.

## The generalisation

> **Generate the matrix from the package's own metadata. A hand-written matrix
> is a second, unaudited source of truth about what the package supports — and
> it will disagree with the pyproject.**

See also `prompts/reusable-ci-matrix-template.md` (the workflow shape),
`prompts/python-support-is-a-claim.md` (why the floor matters),
`prompts/ci-target-must-match-repo-layout.md` (why the test list must be real),
`tools/fresh-install-verification-guide.md` (the import check).
