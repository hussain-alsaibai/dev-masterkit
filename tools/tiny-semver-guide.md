# tiny-semver Guide

**tiny-semver** — Zero-dependency Semantic Versioning (SemVer 2.0.0) with full constraint algebra (caret, tilde, ranges, conjunctions, disjunctions, pre-release precedence, version bumping, compatibility).

- **Repo:** github.com/hussain-alsaibai/tiny-semver
- **Install:** `pip install tiny-semver` or copy `tiny_semver.py`
- **Size:** ~620 LOC, 0 dependencies
- **Tests:** 115 passing (was 22 at v0.1.0)
- **Last verified:** 2026-10-20

## What's New in v0.2.0

Four real defects fixed (three of them silent wrong-answer bugs) plus a full constraint-set algebra.

### Bugs Fixed

1. **Tilde now patch-level, not major-level.** Per SemVer section 7, PEP 440, and npm: `~=1.2.3` accepts `>=1.2.3, <1.3.0`. v0.1.0 incorrectly accepted `1.3.0` (major-level range).
2. **Caret below 1.0.0 cascades correctly.** `^0.0.3` accepts `>=0.0.3, <0.0.4` (only patch), `^0.2.3` accepts `>=0.2.3, <0.3.0` (only minor), `^1.2.3` accepts `>=1.2.3, <2.0.0` (only major). v0.1.0 did not narrow and accepted the wrong axis.
3. **Pre-release identifiers compare semantically, not lexicographically.** `1.0.0-alpha.2 < 1.0.0-alpha.10`, and `1.0.0-alpha < 1.0.0` (numeric identifiers have lower precedence than alphanumeric). Implemented with `(kind, value)` sort keys; v0.1.0 string-compared.
4. **`Version.raw` preserves dot separators.** `bump_prerelease()` now returns `1.0.0-alpha.2` instead of `100-alpha.2`.

### New Surface

- `ConstraintSet`, `parse_range()` — comma conjunctions (`>=1.0, <2.0`) and `||` disjunctions (`^1.0 || ^2.0`).
- `filter_satisfying(cands, constraint)` and `find_max_satisfying(...)`.
- `Version.precedence`, `Version.is_compatible_with(other)`.
- `bump_release(v)` drops the pre-release tag (e.g. `1.0.0-rc.1` → `1.0.0`).
- `bump_prerelease(v, stable=True)` returns release version first when `stable=False` is explicitly requested.
- `Constraint` is hashable and stringifiable (`str(c) == "~1.2.3"`).

## Quick Start

```python
from tiny_semver import (
    parse, satisfies, Version,
    parse_range, filter_satisfying, find_max_satisfying,
    bump_patch, bump_minor, bump_major,
    bump_prerelease, bump_release,
)

v = parse("1.2.3-beta.1")
assert v.major == 1 and v < parse("2.0.0")

# Spec-correct tilde and caret
assert satisfies("1.2.9", "~1.2.3")        # True — same minor
assert not satisfies("1.3.0", "~1.2.3")   # patch, not major
assert satisfies("1.9.9", "^1.0.0")        # same major
assert satisfies("0.0.9", "^0.0.3")        # same patch under 1.0.0
assert not satisfies("0.1.0", "^0.0.3")    # minor not allowed

# Constraint sets
rng = parse_range(">=1.0.0, <2.0.0 || ^2.5.0")
candidates = [parse(x) for x in ["1.5.0", "2.5.3", "2.9.9", "3.0.0"]]
pick = find_max_satisfying(candidates, rng)        # 2.9.9
matches = filter_satisfying(candidates, rng)       # 1.5.0, 2.5.3, 2.9.9

# Bumping
bump_patch("1.2.3")                       # "1.2.4"
bump_minor("1.2.3")                       # "1.3.0"
bump_major("0.1.0")                       # "1.0.0"
bump_prerelease("1.0.0", tag="rc")        # "1.0.0-rc.0"
bump_release("1.0.0-rc.1")                # "1.0.0"
```

## Key Features (Full Set)

- Full SemVer 2.0.0: prerelease + build metadata
- Comparison operators: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Constraints: `^`, `~`, `>=`, ranges: `>=1.0.0, <2.0.0`
- Conjunctions (`,`) and disjunctions (`||`)
- `parse_range()` and `ConstraintSet` for full constraint algebra
- `filter_satisfying()`, `find_max_satisfying()`
- `Version.precedence`, `is_compatible_with()`
- Sorting helpers: `sorted_versions()`, `max_ver()`, `min_ver()`
- Bumping helpers: `bump_patch/minor/major/prerelease/release`
- Hashable — use in sets and dicts
- `Version.raw` always preserves the dot separators

## When to Use

- Dependency resolution, lockfiles, version comparison
- Replacing `packaging.version` (40 ms cold-start → <0.1 ms)
- Building a lockfile or semantic-version resolver
- Any non-trivial constraint logic (`^1.0 || ^2.0` style)

## When NOT to Use

- PEP 440 versions like `1.0.0a1` / `1!2.0` — strict SemVer only.
- Date-based versions (`2026.10.20`) — those are CalVer, not SemVer.

## The "Plausible Wrong Answer" Lesson

The costliest bug in a small utility is not a crash — it is a plausible wrong answer. `~1.2.3` silently accepting `1.3.0` looks fine in a smoke test that only checks a single version. Same for `^0.0.3` silently accepting `1.0.0`. Tests must probe the boundary, not the centre.

