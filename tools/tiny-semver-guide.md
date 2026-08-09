# tiny-semver Guide

**tiny-semver** — Zero-dependency Semantic Versioning (SemVer 2.0.0).

- **Repo:** github.com/hussain-alsaibai/tiny-semver
- **Install:** `pip install tiny-semver` or copy `tiny_semver.py`
- **Size:** ~400 LOC, 0 dependencies
- **Tests:** 24 passing

## When to Use

When you need to parse, compare, bump, or validate SemVer strings. Replaces `packaging.version` (40ms cold-start) with <0.1ms import.

## Quick Start

```python
from tiny_semver import parse, satisfies, bump_patch

v = parse("1.2.3-beta.1")
assert v.major == 1
assert v < parse("2.0.0")

# Constraint checking
assert satisfies("1.9.9", "^1.0.0")      # True — same major
assert satisfies("2.0.0", "^1.0.0")      # False — major differs
assert satisfies("1.4.0", "~1.2.0")      # True — same minor

# Bumping
bump_patch("1.2.3")   # "1.2.4"
bump_minor("1.2.3")   # "1.3.0"
bump_major("0.1.0")    # "1.0.0"
```

## Key Features

- Full SemVer 2.0.0 spec (prerelease + build metadata)
- Comparison operators: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Constraints: `^`, `~`, `>=`, ranges: `>=1.0.0, <2.0.0`
- Sorting: `sorted_versions()`, `max_ver()`, `min_ver()`
- Hashable — use in sets and dicts
