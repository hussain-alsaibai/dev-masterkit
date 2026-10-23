# Fail Closed on Unavailable Data — "I Could Not Check" Is Not "Checked"

**A checklist for any code path that makes a trust, safety, or selection
decision from data it fetched.**

On 2026-10-23 the bounty scanner's anti-scam filter was **fully armed and
completely disarmed at the same time**. 348 issues were scanned, 161 were
filtered, and every one of the 20 surfaced picks was a fork farm. The
safety net existed. It just never received a signal.

> Found 2026-10-23 while fixing the bounty scanner. Fixed by adding a
> persistent metadata cache, an explicit `unverified_repo` red flag, and a
> min-stars/min-age selection gate. **Last verified:** 2026-10-23

## The Failure Mode

The classic shape:

```python
# BROKEN — a rate-limit 403 and a genuinely empty repo look identical
repo = httpGet(f"https://api.github.com/repos/{owner}/{name}").catch(() => null)
flags = detectScam(repo || {})        # {} -> exactly ONE flag -> "suspicious", not "scam"
if (flags.length >= 2) reject()       # the safety net, never reached
```

`httpGet` returns `null` on a 403 rate limit. `null` becomes `{}`. An empty
repo object produces exactly one flag (`no_stars`), so the candidate scored
`suspicious` instead of `scam` and sailed past the `>= 2 flags = reject` rule.

Meanwhile the **real** zero-star farms passed the same gate, because for them
`no_stars` was a true positive.

The net was armed. The signal never arrived. The net did nothing.

**The general rule:**

> Any code path that does `fetch(...).catch(() => null)` and then *infers*
> quality from the result is silently disarmed. A rate-limit 403 looks exactly
> like "no data", and "no data" gets scored as "clean".
> **Anything making a trust decision must treat unavailable data as a failure
> signal, never as a pass.**

## The Three Failure Shapes

| Shape | What it looks like | Why it is dangerous |
|-------|-------------------|---------------------|
| **Null-collapse** | `fetch().catch(() => null)` then `data || {}` | Missing data becomes an empty object that satisfies a weak filter |
| **Zero-substitution** | `stars: data.stargazers_count ?? 0` | "I could not read the star count" becomes "zero stars" — and zero stars is often the very signal being checked |
| **Silent-skip** | `if (!resp.ok) return;` inside a loop | The item is quietly absent from the analysis instead of failing loudly |

The zero-substitution shape is the most seductive because it looks like
defensive coding. It is the exact opposite: it manufactures a negative
signal from an absence of data, and negative signals are usually the ones a
filter trusts.

## Procedure

1. **Identify every fetch that feeds a decision.** Grep for `.catch(`, `|| {}`,
   `?? 0`, `try:` blocks around HTTP calls, and `if (!res.ok) return`.
2. **Make the unavailable state explicit.** Return a typed result instead of
   `null`:

   ```python
   # GOOD — the caller cannot accidentally treat "missing" as "empty"
   result = fetch_repo_meta(owner, name)
   if result.state == RepoMetaState.UNAVAILABLE:
       flags.append("unverified_repo")   # missing data IS a red flag
       stars = None                      # not 0
   ```

3. **Never substitute a default for a fetched number.** `stars = None` is
   honest. `stars = 0` is a lie that reads as a signal.
4. **Cache successful lookups, and serve stale data rather than null.** A
   persistent cache with a TTL means a transient rate limit returns the last
   known value instead of nothing. Cache **only successful** fetches, so a
   failed fetch cannot poison the cache.
5. **Fail the gate closed.** When the required signal is missing, the
   candidate must be demoted or rejected — never admitted on the grounds that
   "nothing looked wrong".
6. **Assert the gate is armed.** A unit test that feeds a throttled/unavailable
   response and asserts the candidate is rejected.

## Verification Pattern

```python
# known scam            -> must be rejected
# real repo (429 stars) -> must pass
# metadata unavailable   -> must be rejected (not "clean")
```

All three cases were run on 2026-10-23 after the fix. The third case is the
one that reproduces the original bug.

## Before and After (measured, same day)

| Metric | Before fix | After fix |
|--------|-----------|-----------|
| Issues rejected | 161 | **241** |
| Picks surfaced | 20 | **9** |
| Surfaces that were real | 0 | 0 (market genuinely empty) |
| Farm that previously ranked #1 (`javelin-anticheat/py-workedtask`) | **ranked #1** | rejected (1 star, 51 forks, born and abandoned the same day) |

The number of surfaces dropped and the rejection count rose. That is the fix
working: the filter was already rejecting farms that had usable metadata, and
now it also rejects the ones whose metadata never arrived.

## The Companion Lesson: Verify Existence Before Deleting

The same session nearly deleted five tool guides that looked like dead stubs
(7, 7, 14, 40, and 85 lines). All five repos return HTTP 200 upstream — five
distinct existing projects. They were thin, not dead, and all five were
restored.

> **Verify existence upstream before deleting anything from the catalogue.**
> An unverified delete is the expensive direction of that error.

Both lessons are the same lesson: **absence of evidence is not evidence of
absence.** A missing API response means "unavailable", not "clean"; a short
file means "thin", not "dead".

## The Transferable Lesson

> **A gate that cannot distinguish "passed" from "not checked" is not a
> gate.** The failure is silent because the output looks exactly like a clean
> run. When a safety net depends on data that can fail to arrive, the
> unavailable state must be a first-class value in the type, and the default
> must be rejection.
