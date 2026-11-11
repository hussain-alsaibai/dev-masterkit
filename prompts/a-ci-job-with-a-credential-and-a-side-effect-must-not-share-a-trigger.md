# A CI job with a credential and a side effect must not share a trigger with ordinary commits

**Discovered:** 2026-11-11 (claw-token, `00d0c78`)
**Last verified:** 2026-11-11 — three checks, plus a 499-workflow fleet scan

## What happened

`deploy.yml` ran on **every push to main**, with a live `DEPLOYER_PRIVATE_KEY`
secret and the Tenderly RPC URL configured. Two deployments landed 90 seconds
apart — one for a contract fix, one for a README address update. **Each burns a
new contract address**, and both now exist on-chain holding a supply nobody
chose to keep.

The trigger was never malicious or even careless. It was the default shape of
"deploy on merge", which is correct until the job is expensive, irreversible,
or both.

## The rule

> Push-to-main is for code that cannot change the world. Anything that can
> needs a human to ask for it.

```yaml
on:
  workflow_dispatch:
    inputs:
      reason:
        description: "Why this deployment is needed (lands in the commit message)"
        required: true
```

CI (`fmt`, `build`, `test`) stays on `push`. The deploy does not.

## Verify the fix three ways, not one

1. **The auto-commit does not re-trigger.** A commit pushed with `GITHUB_TOKEN`
   does not start a workflow. Confirm zero runs for the auto-commit SHA
   rather than trusting the docs.
2. **An ordinary push starts nothing.**
   `gh run list --workflow=deploy.yml` after a normal push → no new run.
3. **The artifact is actually the new thing.** For a deployed contract, call it:
   `totalTaxBps()` → 300, `burnBps()` → 200, `rewardBps()` → 100. Source that
   is correct and deployed source that is stale look identical in `git log`.

## Scan the fleet, because it is a pattern

This was one repo, so it became a check:

```
scripts/scan_push_to_main_side_effects.py
scripts/test_scan_push_to_main_side_effects.py
```

499 workflows scanned, **164 owned**. No other hits — the bug was unique. The
parser distinguishes a **branch filter** from a **tag filter**: a first version
that matched the literal string `main` flagged `release-box-images.yml`, which
is tag-triggered, has concurrency, and takes an explicit overwrite input.

The self-test reconstructs the old claw-token workflow as a fixture and asserts
the scanner FLAGS it, and leaves alone the fixed version plus three legitimate
workflows. It earned its place immediately: when the fixture lost the literal
`secrets.` reference, the scanner stopped flagging the old workflow and the
test **failed** — instead of the scanner silently reporting clean.

## Related

- `prompts/a-rule-that-cannot-fire-is-not-a-rule.md`
- `prompts/a-scan-that-returns-nothing-is-evidence-only-if-it-can-find-the-bug.md`
