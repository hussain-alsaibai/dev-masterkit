# tiny-diff — Zero-Dependency Patch, Diff & Merge

> Unified diffs, object diffs, and three-way merge. No difflib confusion. One file.

**Repo:** https://github.com/hussain-alsaibai/tiny-diff
**Install:** `pip install tiny-diff`
**Last verified:** 2026-08-06

---

## What It Does

`tiny-diff` produces unified diffs, applies patches, deep-diffs arbitrary Python objects (dicts, lists, primitives), and resolves three-way merges. Built for agents that need to track changes, apply updates, or merge conflicting edits.

## Quick Start

### Text Diff

```python
from tiny_diff import diff_strings, apply_patch

old = "Hello world\nHow are you?\nGoodbye."
new = "Hello agents\nHow are you?\nSee you later."

patch = diff_strings(old, new)
restored = apply_patch(old, patch)
assert restored == new
```

### Three-Way Merge

```python
from tiny_diff import merge

base    = "Line 1\nLine 2\nLine 3\n"
ours    = "Line 1\nModified by us\nLine 3\n"
theirs  = "Line 1\nLine 2\nModified by them\n"

result, conflicts = merge(base, ours, theirs)
# No conflicts if changes are on different lines
```

### Structured Object Diff

```python
from tiny_diff import diff_objects, apply_object_changes

old = {"user": {"name": "Alice", "age": 29}, "active": True}
new = {"user": {"name": "Alice", "age": 30}, "active": True, "role": "admin"}

changes = diff_objects(old, new)
# [
#   {"op": "replace", "path": "$.user.age",   "old": 29,  "new": 30},
#   {"op": "add",     "path": "$.role",       "value": "admin"}
# ]

patched = apply_object_changes(old, changes)
assert patched == new
```

### Reverse Patch

```python
from tiny_diff import diff_strings, unapply_patch

patch  = diff_strings(old, new)
undo   = unapply_patch(new, patch)
```

## Key Functions

| Function | Description |
|----------|-------------|
| `diff_strings(old, new)` | Unified diff between two strings |
| `apply_patch(text, patch)` | Apply a unified diff patch |
| `unapply_patch(text, patch)` | Reverse a patch (undo) |
| `diff_objects(old, new)` | Deep diff of Python objects → list of changes |
| `apply_object_changes(obj, changes)` | Apply object changes back |
| `merge(base, ours, theirs)` | Three-way merge with conflict detection |

## When to Use

- Agent code generation workflows (apply patches from LLM output)
- Configuration drift detection
- Three-way merge resolution in custom VCS
- Structured change tracking for objects/configs

## Known Edge Cases Fixed (2026-08-06)

- `apply_patch` offset tracking across hunks
- Root path parsing in `apply_object_changes`
- Sentinel handling in merge conflicts
