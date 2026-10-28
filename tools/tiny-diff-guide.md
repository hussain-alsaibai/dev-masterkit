# tiny-diff Guide

## Repo
https://github.com/hussain-alsaibai/tiny-diff

## What It Does

Zero-dependency diff, patch, and merge for text. One file, no setup. Semantic
(word and character level) diffing, unified patches, and a three-way merge with
conflict detection.

## Last Verified
2026-10-28 - **20 tests passing** (measured by run against the upstream clone).
The package had **no CI** until 2026-10-28.

## The Duplicate-Test-File Defect (fixed 2026-10-28)

The repository shipped **two** files named `test_tiny_diff.py` - one in the repo
root and one under `tests/`. pytest refuses to collect the second because of
the duplicate basename, and the `tests/` copy was **stale**: it imported APIs
that no longer exist. The stale copy is removed.

Same defect, same day, in `tiny-eval`.

**Note on the PyPI name:** `tiny-diff` on PyPI is owned by someone else - a
package described as "Hackable implementation of diffusion models" (v0.1.0,
verified 2026-10-28). `pip install tiny-diff` installs **that**, not this
project. Install from the repository URL instead.

## Previous verification
2026-10-23
## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_diff import
diff_strings, apply_patch`. **Neither name exists.** Verified against upstream
`tiny_diff.py`:

```
__all__ = ['diff', 'patch', 'merge', 'apply_interactive', 'DiffResult',
           'MergeResult', 'Hunk', 'Conflict', 'Operation']
```

The functions are **`diff`**, **`patch`**, **`merge`**, and
**`apply_interactive`**. `DiffResult` / `MergeResult` / `Hunk` / `Conflict` /
`Operation` are the value objects.

## Key Features

- `diff(a, b)` — semantic diff with word- and char-level refinement
- `patch(text, diff_result)` — apply a diff
- `patch_from_string(text)` — parse a unified patch
- `merge(base, ours, theirs)` — three-way merge with conflict detection
- `apply_interactive(...)` — resolve conflicts interactively

## Quick Start

```python
from tiny_diff import diff, patch, merge

d = diff("hello world", "hello brave world")
print(d.hunks)

new_text = patch("hello world", d)

m = merge(base, ours, theirs)
if m.conflicts:
    for c in m.conflicts:
        print(c)
```

## When to Use

- Showing a change set to a human or an LLM without shelling out to `diff`
- Applying and merging patches in agent workflows
- Reviewing generated edits before accepting them

## Related

- `tools/tiny-middleware-guide.md` — request/response middleware, a different concern
