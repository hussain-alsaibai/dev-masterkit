# A Future Import Hides The Error The Syntax Check Accepts

**Last verified:** 2026-11-21

## The prompt

> You changed a module-level annotation and the 3.8 matrix job is red. Before
> you rewrite it as `Dict[...]`:
>
> **1. Look for `from __future__ import annotations` at the top of the file.**
> `PEP 563` stores every annotation as a *string*. At module level a
> `X: dict[str, int] = {}` is **not evaluated** under that import — on 3.8,
> 3.9, any version. If the import is there, the PEP 585 spelling is safe and
> is not your bug.
>
> **2. If it is not there, the annotation is a runtime expression.**
> `X: dict[int, str] = {}` raises
> `TypeError: 'type' object is not subscriptable` on 3.8 at import, before any
> function in the file can run.
>
> **3. The syntax check will not tell you which case you are in.** `ast.parse`
> and `compile` accept both spellings — `feature_version=(3, 8)` too. They
> prove the file parses. Nothing more.

## Why the check lies

```
python3 -c "import ast; ast.parse(src, feature_version=(3,8))"   # passes
python3 -c "import mymodule"                                     # 3.8: TypeError
```

`compile()` does not execute an annotated assignment. On 3.8 the assignment is
*also* executed at import, so the annotation expression runs and fails on a
name or a subscription the parser was happy with.

The same shape bites in reverse: an annotation whose name was never imported
(`X: Coroutine = ...`) raises `NameError` at import on the version where it is
evaluated — and is silently fine under the future import, in the file that
"fixed" a different module.

## How to settle it in one command, without a 3.8 interpreter

Use a name that does not exist. If the annotation is deferred, the module
imports; if it is evaluated, the import raises.

```python
# probe_mod.py
from __future__ import annotations   # <- the line under test
X: NOEXIST = 1
```

```bash
python3 -c "import probe_mod"   # rc=0 -> deferred;  NameError -> evaluated
```

Run both arms. The arm without the future import **must** fail, otherwise the
probe cannot tell a deferred annotation from a probe that never ran:

```
no future import     -> rc=1 NameError: name 'NOEXIST' is not defined
WITH future import   -> rc=0
```

(`tools/probing-annotation-deferral.md` carries the script.)

## What it cost when missed

`tiny-cli-table` declares `requires-python = ">=3.7"`, has **no** future
import, and carries a PEP 585 module-level constant. `tiny-secret-mask`
declares `>=3.8` and its annotations *are* deferred by the future import. The
two look identical in a `grep` for `dict[` and behave in opposite ways — one
is a 3.7 import failure, the other is fine. **The future import is part of the
annotation, not a style choice.**

## Related

- `prompts/python-support-is-a-claim.md` — the `requires-python` promise
- `prompts/a-module-that-cannot-be-imported-is-not-a-library.md` — import as a test
- `tools/probing-annotation-deferral.md` — the executed probe
