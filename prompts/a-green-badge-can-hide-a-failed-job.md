# A Green Badge Can Hide A Failed Job

**A rule for anyone who reads a CI status, a workflow badge, or a
`gh run list` line as evidence that a job passed.**

> Found 2026-11-04. `tiny-timeout` and `tiny-metrics` had a **failing**
> Windows job since 2026-10-29, and `gh run list` reported
> `conclusion: success` for both. The Windows job carried
> `continue-on-error: true`, so the run stayed green while the job was red.
> **Last verified:** 2026-11-04 — read directly out of the GitHub Actions API
> for both repos (`gh api repos/OWNER/REPO/actions/runs/$RID/jobs`); the
> Windows rows show `conclusion: failure` under runs whose overall
> `conclusion` is `success`.

## The Rule

> **`conclusion: success` is the RUN's verdict, not the JOB's. A job marked
> `continue-on-error` is a red job wearing a green badge.**

`gh run list` prints one conclusion per **run**. A run is green when no
job failed *fatally*. A job with `continue-on-error: true` that fails is
recorded, reported as a failure, and **does not fail the run**.

## Reading It Properly

```bash
gh api repos/OWNER/REPO/actions/runs/$RID/jobs \
  --jq '.jobs[] | [.name, .conclusion] | @tsv'
```

```
Test (Windows, py3.12)   failure      <- red job
Zero-deps assertion       success
```

The run says `success`. The job says `failure`. **Only the second one is
about the code.**

## The Two Bugs It Hid

Both were real defects in published libraries, sitting behind a green badge
for six days:

- **`tiny-timeout`** — `sleep_with_deadline(5.0, deadline_with_0.05s_left)`
  returned **True**. It slept the remainder and then asked *"has the
  deadline expired?"*, which was false. A sleep is not guaranteed to last the
  requested time (Windows has ~15.6 ms timer granularity), so **the clock is
  the wrong question** — the contract is *"did the **full** sleep finish"*.
  Reproduced on Linux by simulating an early wake.
- **`tiny-metrics`** — the test HTTP server was bound to all interfaces, so
  `server_address[0]` was `0.0.0.0`. Connecting to `0.0.0.0` is
  undefined: Linux accepts it, Windows refuses it (`WinError 10049`).
  **The library was correct; the test connected to the wrong address.**

## The Procedure

1. **Never read a run conclusion as a job conclusion.** List the jobs.
2. **Find every `continue-on-error` in the workflow.** It is a mask, and it
   is only legitimate while the underlying failure is *known* and tracked.
3. **Remove the mask when the bug is fixed.** A mask left in place after the
   fix turns the next regression into a hidden one.
4. **Search the whole estate for the mask**, not just the repo that failed.
   Two of ours had it; there could be more.
5. **Bind test servers to `127.0.0.1`, not `0.0.0.0` and not `""`.**

```python
server = HTTPServer(("127.0.0.1", 0), handler)
host, port = server.server_address
```

## The Generalisation

Anywhere a status is summarised: a deploy pipeline, a health check, a
scheduled job, a monitor that prints one line for many subjects. **A
summary hides the distribution.** The summary is the thing people read, and
it is the thing that is wrong.

See also `prompts/partial-failure-is-not-a-pass.md` (a monitor that reports a
pass it did not earn) and `prompts/validate-workflow-schema.md` (the
workflow file itself being rejected before any job existed).

<!-- project: github.com/hussain-alsaibai/dev-masterkit -->
