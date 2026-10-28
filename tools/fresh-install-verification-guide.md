# Fresh-Install Verification — The Check `pip install -e .` Cannot Do

**A runnable guide for proving that a package is actually installable and
importable, before anyone else finds out the hard way.**

> Found 2026-10-28 while adding CI to 25 tiny-* repositories. Five of them
> passed `pip install -e .` and still published a wheel containing **zero
> importable modules**. **Last verified:** 2026-10-28 — every command below was
> run on this host; the counts are measured, not quoted.

## Why the editable install lies

```bash
pip install -e .     # the SOURCE TREE goes on sys.path
pytest                # imports the loose .py file next to the test
```

An editable install puts the source directory on `sys.path`. A loose
`tiny_semantic_cache.py` sitting next to `test_tiny_semantic_cache.py` is
imported **as if it were the installed package**. The test suite therefore
exercises the working tree — which is fine — but it proves nothing about what
the **wheel** contains.

This is not a theoretical distinction. On 2026-10-28:

- `tiny-semantic-cache`, `tiny-ai-workflow`, `tiny-event-bus` and `tiny-task`
  all shipped wheels with **no importable module**,
- `tiny-bucket-quota` shipped the **wrong** module (`tiny_rate_window`,
  copied from a sibling),
- `tiny-llm-router`'s build failed outright (`py_modules` instead of
  `py-modules`),
- `tiny-jsonpath`'s build failed outright (`package-data` with the
  empty-string key `""`).

## The three checks

### 1. Does the wheel ship the module?

```bash
# build exactly what would be published
python3 -m build --wheel 2>/dev/null || pip wheel --no-deps -w dist/ .

# list the payload
python3 -c "import zipfile,glob; z=zipfile.ZipFile(sorted(glob.glob('dist/*.whl'))[-1]); \
print('\n'.join(n for n in z.namelist() if n.endswith('.py')))"
```

If the module is not in that list, **the package installs and does nothing**.

### 2. Can a fresh environment import it from outside the source tree?

```bash
uv venv "$HOME/.venvs/probe" --python 3.11
VIRTUAL_ENV="$HOME/.venvs/probe" uv pip install -e . pytest

cd /tmp
"$HOME/.venvs/probe/bin/python" -c "import tiny_semantic_cache; print('OK')"
```

**`cd /tmp` is not optional.** From inside the repo, the loose source file
shadows the installed package and the defect is invisible. This is the same
trap as `skills/dev-env-defects/SKILL.md` step 5.

### 3. Does the declared Python floor actually work?

```bash
# the claim
grep -n 'requires-python' pyproject.toml

# test the OLDEST version in the matrix, not the newest
uv python install 3.8
uv run --python 3.8 --with pytest --with pytest-asyncio python -m pytest -q
```

The oldest version is where the claims break. `tiny-scheduler` called
`ThreadPoolExecutor.shutdown(cancel_futures=...)` (**3.9+**) while declaring
`>=3.8`; `fast-cache` called a `staticmethod` object, not directly callable
until **3.10** (bpo-43682).

## The packaging rules that keep failing

### A single top-level module is not a package

```toml
# WRONG - finds nothing
[tool.setuptools.packages.find]
include = ["tiny_semantic_cache*"]

# RIGHT
[tool.setuptools]
py-modules = ["tiny_semantic_cache"]
```

`packages.find` looks for **directories with `__init__.py`**. A single file
`tiny_semantic_cache.py` is a *module*, not a package.

### The key is `py-modules`, with a hyphen

```toml
py_modules = [...]   # WRONG - silently ignored, the build ships nothing
py-modules = [...]   # RIGHT
```

### `package-data` keys are globs, and `""` is not one

```toml
[tool.setuptools.package-data]
"" = ["llms.txt"]           # WRONG - modern setuptools rejects it
"*" = ["llms.txt"]          # RIGHT
```

### A sidecar module needs its own entry

```toml
py-modules = [
    "tiny_router",
    "tiny_router_sse",
    "tiny_router_redact_headers",
    "tiny_router_redact_path",
]
```

A sidecar that is not listed is **not importable after install**, and any
`except ImportError` around its import silently degrades to a no-op. That is
the `tiny-secret-mask` v0.5.0 defect class: `mask_route_path()` and
`mask_headers()` returned their input unchanged in every install, because the
sidecars were never in `py-modules` and the code caught the `ImportError` and
fell back to an identity lambda.

See `prompts/silent-security-control-audit.md`.

## The environment facts on this host

| fact | value | consequence |
|---|---|---|
| `/tmp` | `tmpfs`, **512 MB**, `noexec` | a venv there installs and then fails to import |
| `uv` | 0.13.5 | `uv venv` + `uv pip install` is the working path |
| system Python | 3.11.2 | a repo needing 3.12+ cannot even be parsed |
| venv location | `$HOME/.venvs/` | never `/tmp` |

`/tmp` being a tmpfs was the cause of a mid-run `No space left on device`
spike that looked like a build error in 25 different repositories at once.

## The one-liner that catches the common case

```bash
uv venv "$HOME/.venvs/probe" --python 3.11 >/dev/null 2>&1 && \
VIRTUAL_ENV="$HOME/.venvs/probe" uv pip install -q -e . && \
(cd /tmp && "$HOME/.venvs/probe/bin/python" -c "import $MODULE; print('$MODULE OK')")
```

## The generalisation

> **A package is installable when a fresh environment can import it from
> outside the source tree. `pip install -e .` succeeding is not that check —
> it is a different check, and it passes for packages that ship nothing.**

See also `prompts/readme-claims-must-be-runnable.md`,
`prompts/ci-census-reveals-what-was-never-checked.md`,
`skills/dev-env-defects/SKILL.md`,
`tools/uv-venv-toolchain-guide.md`.
