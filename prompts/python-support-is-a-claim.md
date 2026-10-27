# Python Support Is a Claim You Have To Test

**A checklist for every package that declares `requires-python`, and every CI
matrix that has an oldest version.**

> Found 2026-10-26. Two packages declared `requires-python = ">=3.8"` and
> were **red on 3.8**. `tiny-log` called `asyncio.to_thread` (**3.9+**).
> `fast-cache` called a `staticmethod` object, which is not directly callable
> until **3.10** (bpo-43682). Both shipped because CI was red and nobody read
> the badge. **Last verified:** 2026-10-26 — both fixes are in the local
> trees (`tiny-log/tiny_log.py:701` documents the 3.9 boundary;
> `fast-cache/fast_cache.py:1322-1328` detects the `staticmethod` object
> before calling it); `fast-cache` collects 108 tests and passes.

## The Claim

```toml
[project]
requires-python = ">=3.8"
```

This is a **promise to every consumer who reads it**, and it is the only
place the promise is written. Nothing in the code enforces it. A user on 3.8
who trusts the metadata gets an `AttributeError` or a `TypeError` instead.

The general form:

> **A stdlib API added in version X silently breaks every version below X,
> and the package metadata is the only place that claim is written.**

## The Failure Shapes

### 1. A function added in a later version

```python
# Python 3.9+ only
result = await asyncio.to_thread(fn, arg)
```

On 3.8: `AttributeError: module 'asyncio' has no attribute 'to_thread'`.

### 2. A descriptor that became callable

```python
# BROKEN on 3.8 / 3.9
obj = SomeClass.some_static_method      # TypeError: staticmethod object is not callable
```

`@staticmethod` objects were only made directly callable in **3.10**
(bpo-43682). Before that you must unwrap them:

```python
fn = SomeClass.some_static_method
if isinstance(fn, staticmethod):
    fn = fn.__func__
```

### 3. Syntax the oldest parser cannot read

- **PEP 604** (`str | None`) — 3.10+
- **PEP 585** (`list[str]`) in annotations at runtime — 3.9+
- **PEP 701** (nested same-quote f-strings) — **3.12+**

PEP 604 is the quiet one. `str | None` at runtime on 3.9 raises
`TypeError: unsupported operand type(s) for |`. The fix is one line at the
top of the file:

```python
from __future__ import annotations
```

which defers annotation evaluation. `tiny-mcp-observability` had PEP 604
annotations while its metadata claimed `>=3.9` — a `TypeError` **on import**,
so the whole package was unusable, not merely degraded.

### 4. A stdlib module added later

`sys.stdlib_module_names` is **3.10+**. `tiny-graceful` used it in a test
while claiming `>=3.8`.

## The Procedure

1. **Read the declared floor.** `requires-python` in `pyproject.toml`,
   `python_requires` in `setup.py`, or the `Programming Language :: Python ::
   3.x` classifiers.

2. **Set the CI matrix to include that exact version** — not one above it.
   A matrix of `["3.9", "3.12"]` with a floor of `3.8` is a lie of the
   same family as the badge that was red.

3. **Audit every stdlib call against the OLDEST version in the matrix.**
   Not the newest. The newest version is the one you are running locally,
   and it will not tell you anything.

   ```bash
   # Enumerate the stdlib names the package touches
   grep -ohE '\b(asyncio|inspect|typing|pathlib|importlib|functools|dataclasses|contextlib|importlib\.metadata)\.[a-z_]+' -r src/ | sort -u
   ```

   Then check each against the oldest supported version:
   `asyncio.to_thread` → 3.9, `asyncio.timeout` → 3.11,
   `typing.Self` → 3.11, `itertools.batched` → 3.12,
   `sys.stdlib_module_names` → 3.10, `tomllib` → 3.11,
   `importlib.metadata.entry_points(group=...)` → 3.10,
   `zip(strict=True)` → 3.10, `datetime.UTC` → 3.11,
   `enum.StrEnum` → 3.11.

4. **Grep for the version-specific syntax**, not just the API:

   ```bash
   grep -rnE ': *[A-Za-z_]+ *\| *None|-> *[A-Za-z_]+ *\| *None' src/   # PEP 604, 3.10+
   grep -rn 'from __future__ import annotations' src/                       # the fix
   ```

5. **Actually run the oldest version.** A matrix entry that runs the newest
   interpreter proves nothing about the floor. `tox -e py38`, a container,
   or `uv run --python 3.8` — whatever actually gets the old interpreter.

6. **Make the CI matrix expression correct.** A JS template literal in a YAML
   matrix is not a GitHub expression:

   ```yaml
   # BROKEN — a literal string, not an expression. setup-python gets "${ matrix.python-version }"
   python-version: ${ matrix.python-version }

   # CORRECT
   python-version: ${{ matrix.python-version }}
   ```

   `tiny-graceful` carried the first form; all six matrix jobs died and the
   badge was red for a reason that had nothing to do with the code. That is
   the third failure family: **the matrix that is supposed to test the claim
   was itself broken**.

## The Rule

> **When adding a CI matrix, check every stdlib call against the oldest
> version in the matrix, not just the newest.**
>
> And: **a red badge is a claim about a pipeline, not about the code.** Read
> the log before you change the implementation — then prove which side is
> wrong. A change that does not alter the failing assertion is not a fix.

## The Generalisation

A declared support floor is a contract with people you will never meet, who
will install your package on the oldest machine they can find. The metadata
is where that contract is written, so **the metadata is what has to be
tested.**

See also `prompts/validate-workflow-schema.md` (a workflow that does not
parse never runs) and `prompts/reusable-ci-matrix-template.md` (the template
to copy — and the expression to check inside it).
