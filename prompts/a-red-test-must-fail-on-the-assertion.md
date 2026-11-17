# A red test is only evidence if it fails on the assertion you care about

**Discovered:** 2026-11-17 (`MotionClone` #44 / PR #65, preview-render cap)
**Last verified:** 2026-11-17 — the corrected fixture fails on `1280 == 960` against the
unfixed code and passes with the fix; suite 133 passed / 3 failed, all three pre-existing
environment failures identical on the base commit; [PR #65](https://github.com/blixvip/MotionClone/pull/65) open and `MERGEABLE`.

## The claim

"Watch the test fail first" is the standard advice, and it is incomplete. A test can fail
for a reason that has nothing to do with the bug, and that failure looks exactly like a
successful red phase: the suite goes red, you apply the fix, the suite goes green, and
nothing between the bug and the fix was ever tested.

## What happened

The bug: preview rendering capped the **width** instead of the longest edge, so a portrait
import — `prepare()` allows up to 1080×1920 — rendered at nearly full resolution.
`960 / 720 > 1`, so a 720×1280 source got no downscale at all.

The first draft of the regression test built its fixture with `tracks=[]`:

```python
# first draft — never reached the assertion
project = Project(tracks=[], ...)
```

It **failed**, which reads as a successful red phase. But it failed at **construction**:

```
pydantic_core.ValidationError: tracks — too_short
```

The fix could have been anything and the test would still have gone green, because the
error was in the fixture, not in the code under test.

## The corrected form

```python
def test_preview_caps_the_longest_edge():
    proj = Project(tracks=[video_track(720, 1280)])
    assert preview_size(proj) == (540, 960)      # portrait: the real assert
```

Now the unfixed code fails with `1280 == 960` — the assertion the bug lives in.

## The measurements

| source | before (cap on width) | after (cap on longest edge) |
|---|---|---|
| 1080 × 1920 | 1.64 MP | **0.52 MP** |
| 720 × 1280 | 0.92 MP | **0.52 MP** |
| landscape | unchanged | unchanged |

The landscape row is the one that matters for regression: a cap on the longest edge must
leave a 1920×1080 source with the same output as before.

## The rule

> **A red test is evidence only when it fails on the assertion you are fixing.** Before
> applying the fix, read the failure message and confirm it names the value the bug
> produces — not a schema violation, not an import error, not a missing fixture.

Concretely, three checks before accepting a red phase:

1. **Read the traceback line.** If it is in setup, fixture construction or an import, the
   test has not started.
2. **The assertion text must contain the bug's number.** `1280 == 960` names both sides of
   the defect; `ValidationError: too_short` names nothing.
3. **Re-run after any fixture change.** A fixture edit is a test edit, and the red phase
   starts over.

## The sibling failure, opposite direction

The same discipline applies to green: a suite with **pre-existing failures** must be
compared against the base commit, per test id, before the change is called clean. Here 3
of 136 failed on both — `playwright: Chromium distribution 'chrome' is not found`,
identical on base — so the change is green on its own merits, and the report says so
instead of claiming 136/136.

Last verified 2026-11-17 (failure text confirms `1280 == 960` before the fix; base-commit
failure set is identical).
