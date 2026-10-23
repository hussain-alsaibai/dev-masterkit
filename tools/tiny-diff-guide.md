# tiny-diff Guide

## Repo
https://github.com/hussain-alsaibai/tiny-diff

## What It Does

Zero-dependency diff, patch, and merge for text. One file, no setup. Semantic
(word and character level) diffing, unified patches, and a three-way merge with
conflict detection.

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
