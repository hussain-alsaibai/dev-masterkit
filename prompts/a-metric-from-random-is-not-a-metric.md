# A metric produced by `Math.random()` is not a metric

**Discovered:** 2026-11-15 (CLAW content generator)
**Last verified:** 2026-11-15 — every number now read from the chain; the
values that could not be read are **omitted** in the output, and the deployed
page shows `Burned (so far) 0 (0)`.

## The claim

A daily-content generator filled `{burn_amount}`, `{holder_count}` and
`{percentage}` with `Math.random()` and published them as fact. The output
said **"33463 CLAW burned today"**, **"3239 diamond claws"**, and **"70% of
CLAW holders are in profit"**. None of it was real. It also picked a **random
weekday**, so posts regularly said "It's Monday" on a Tuesday.

The numbers looked plausible, which is exactly what made them dangerous: no
reader can tell a fabricated figure from a real one, and no alarm fires
because the pipeline exits 0.

## The rule

> **If the output states "N tokens burned today", N must be readable from the
> source of truth. When the source is unreachable, omit the metric — never
> substitute a plausible number.**

A random value in a template is not a placeholder to be filled later. It is a
false claim the moment it is rendered.

## The second bug, inside the rewrite

Replacing `Math.random()` with live reads introduced two more, and both were
caught by **checking the output instead of the code**:

1. **An inverted subtraction.** `burned = totalSupply - balanceOf(dead)` —
   burned tokens are *held* by the dead wallet, so burned **is** that balance.
   The inverted version printed **"100% of supply burned"** when nothing had
   ever been burned.
2. **A revert treated as an error.** The generator read `balanceOf` on the dead
   wallet and treated a revert as a hard failure, falling back to `0` — right by
   luck, not by design. A revert on a zero-balance address is data, not an error.

   *Corrected 2026-11-17:* on the contract as it stands, `balanceOf` on the dead
   wallet **returns 0 — it does not revert**. The reverts live on a *superseded*
   revision of the contract. The conclusion (zero burned) was right; the stated
   mechanism was wrong, and it was copied forward into the README, a cron
   reminder and the daily memory without one fresh `eth_call`.

> **A revert on a zero-balance address is data, not an error — and a claim you
> copied forward is a hypothesis. Re-read the chain before you repeat it.**

## How to check a generator

```bash
# render it once, then read the output as a reader would
node scripts/daily-content-generator.js --dry-run
# grep the template for non-deterministic sources
grep -nE 'Math\.random|Math\.floor\(Math\.random' scripts/*.js
```

Any hit in a file that renders user-facing claims is a fabricated metric until
proven otherwise. The weekday is included: `["Mon","Tue",...][random]` is the
same defect in a smaller font.

## Why it matters

A metric that is fabricated is indistinguishable from one that is measured.
The failure is silent by construction — the more plausible the number, the
longer it survives, and here it survived **99 days** of published content.
