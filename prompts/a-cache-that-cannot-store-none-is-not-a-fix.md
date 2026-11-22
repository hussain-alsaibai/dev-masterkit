# A Cache That Cannot Store `None` Is Not A Fix

**Last verified:** 2026-11-22 (two shipped packages fixed and re-run this session:
`fast-cache` 0.9.1 `d646559` async path, `tiny-prompt-cache` 0.1.1 `2e03b2c`)

## The prompt

> You are looking at a cache whose hit test is `value is not None`. Before you
> "fix the miss path":
>
> **1. `None` is a value, not an absence.** An LLM call that returns `None` is a
> response, a `dict.get` that finds an explicit `None` is data, and a cache that
> treats it as a miss re-runs the factory. Under a slow or paid backend that is
> the bug, not the margin.
>
> **2. The hit test must be a sentinel, and the sentinel must be the default.**
> `cached = self._get(key, _MISSING)` then `if cached is not _MISSING`. If the
> storage layer's own default is `None`, it cannot express the difference and no
> change to the hit test alone will work — check `_get`'s signature too.
>
> **3. Do not compute on the value before storing it.** `len(response)` on a
> `None` response raises `TypeError` on the **first** call, before any cache
> behaviour is reached. Move the size/stat computation after the sentinel check
> or guard it.
>
> **4. Fix the async path in the same commit.** A sync-only fix ships a bug that
> only appears under load. `get_or_set_async` and `get_or_set` are two call paths
> and one of them is the one CI does not exercise.
>
> **5. Grep the defect SHAPE across your other packages, not the method name.**
> Search for `is not None` used as a hit test, `if cached:` used as one, and
> `len(x)` applied to an optional return. Then check the `__all__`/default branch
> question: a fix merged into a branch nobody installs from is not shipped.

## What happened (2026-11-22)

Two independent libraries failed the same way on the same day, and both had a
previous release that claimed to have fixed it.

`fast-cache` **0.9.0** fixed the cached-`None` miss in the **sync** path and said
so in its changelog. `0.9.1` (`d646559`) found `Cache.get_or_set_async` still
tested `is not None` — the async factory re-ran on every cached `None`. Six new
tests in `tests/test_v091_async_none.py`, **two red on 0.9.0**, suite **159
passed**.

`tiny-prompt-cache` **0.1.1** (`2e03b2c`, merged `d51e093`) had a worse variant:
`get_or_call` ran `len(response)` **before** storing. A `None` LLM response
raised `TypeError` on the first call — a cache that cannot cache a response type
the backend is free to return. Fixed with a `_MISSING` sentinel, a public
`has()`, and the size computation moved behind the hit test. Nine tests, **four
red on 0.1.0**, suite **66 passed**.

The distribution detail nearly hid the second fix entirely: `origin/main` had no
v2 module at all. v2 lived only on `feature/prompt-cache-v2`, three commits
ahead. Merging the fix to `main` was not tidying — without it, the fix would
never have reached anyone installing the default branch.

## Rules

- **A "hit" is a question about presence, not about truthiness.** `if cached:`
  and `if cached is not None:` are both answers to "is there a value?" that give
  the wrong answer for `0`, `""`, `[]`, and `None`. Only a sentinel answers it.
- **Measure the red phase on the previous release.** "Two tests red on 0.9.0" is
  a claim about the old code and it is the only part of the fix that a reviewer
  cannot get from reading the new code.
- **The third occurrence of a shape is the signal to sweep, not to patch.** This
  is the third one-path fix this month (`snapdb` 0.18.3 module-vs-function,
  `fast-cache` sync-vs-async, `tiny-prompt-cache` v1-vs-v2). Grep the shape; see
  `skills/sibling-pattern-sweep/`.
