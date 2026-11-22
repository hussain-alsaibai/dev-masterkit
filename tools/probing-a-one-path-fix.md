# Probing A One-Path Fix

**Last verified:** 2026-11-22 (run against `fast-cache` 0.9.0 → 0.9.1 and
`tiny-prompt-cache` 0.1.0 → 0.1.1 in this container)

A fix that lands in one of two call paths looks complete from inside the file it
touched. This is the check that finds the other path in about a minute.

## 1. Enumerate the call paths, not the files

```bash
# every public entry point that ends in a cache lookup
grep -n "def .*\(get\|call\|fetch\|cached\|or_set\|or_call\)" -r . --include=*.py --include=*.js
```

The pairs that bit us:

| package | fixed path | unfixed path |
|---|---|---|
| `fast-cache` | `get_or_set` | `get_or_set_async` |
| `tiny-prompt-cache` | v1 `get_or_call` | v2 module (only on a feature branch) |
| `snapdb` | module-level function | class method |

## 2. Grep the defect shape, not the function name

```bash
grep -n "is not None\|if cached\|if hit\|len(.*response" -r src/ *.py
```

A hit test written as truthiness or `is not None` is the shape. `if cached:`
is the same bug for `0`, `""`, and `[]`, which is why a `None`-only fix can
regress a different value type.

## 3. Write the test so it is red on the PREVIOUS release

```python
# tests/test_<version>_async_none.py
def test_cached_none_is_a_hit():
    c = Cache()
    calls = []
    async def factory():
        calls.append(1)
        return None
    asyncio.run(c.get_or_set_async("k", factory))
    asyncio.run(c.get_or_set_async("k", factory))
    assert len(calls) == 1, f"factory re-ran {len(calls)}x on a cached None"
```

Then prove it:

```bash
git stash && python3 -m pytest tests/test_v091_async_none.py -q | tail -2   # expect failures
git stash pop && python3 -m pytest tests/ -q | tail -2                      # expect all pass
```

The failure count is the deliverable. A test that was written green against the
new code has not been shown to test anything.

## 4. Check which branch people actually get

```bash
git branch -a --contains <fix-sha>        # is main among them?
git ls-tree origin/main -- path/to/module # does the module exist on the default branch?
```

On 2026-11-22 the prompt-cache v2 module existed **only** on
`feature/prompt-cache-v2`. The fix was correct and unreachable. `git ls-tree
origin/main` answered it in one command; a full test run would not have.

## 5. Confirm coverage moved, in the right file

```bash
python3 -m pytest tests/ -q | tail -2      # recorded total before
# ... add tests ...
python3 -m pytest tests/ -q | tail -2      # recorded total after
```

Quote both numbers. `159 passed` after a run that used to be `153` is evidence;
`all passing` is not.
