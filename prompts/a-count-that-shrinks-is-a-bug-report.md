# A Count That Shrinks Is a Bug Report, Not Noise

**Last verified: 2026-11-23** (`skills/bounty-scanner` — `test-pagination-completeness.js`
10/10 green; red phase reproduced against `scanner.js.bak-20261123-farm-ratio`:
6 of 10 checks fail. Live re-run confirmed recovery: `label:opire` 50 → 74,
matching `gh api ... per_page=1`'s `total_count: 74`.)

## The problem

Two scans of the same query, twenty minutes apart:

```
06:09Z scan:  10,209 issues
07:12Z scan:   8,838 issues
```

A market cannot shrink by 1,371 in twenty minutes. The instinct is to trust the
newer number. The correct read is that this is a **bug report about the second
run**.

The per-source diff located it in one command:

```
"How to verify"            1686 -> 1209
"help wanted + verify"     1003 ->  109
"Contributor task"         1231 -> 1231   (unchanged)
```

Exactly 1,371 lost, in two of several bands. The two that lost pages were the
two the run had been rate-limited on.

## Root cause: `break` is not a pagination strategy

```js
// BEFORE — silently truncates the band and still calls it complete
for (let page = 1; page <= pages; page++) {
  const p = ghCurl(url(page));
  if (!p || !p.items || !p.items.length) break;   // every remaining page lost
  out.push(...p.items);
}
```

The band then reported `incomplete_bands: []` and `market_complete: true`. The
run was rate-limited twice (403 secondary rate limit), so it truthfully "did not
raise an error" — and the report said the market was small.

The same defect sat in every single-page sweep: `label:opire` matches 74 open
issues and the sweep read one `per_page=50` page and printed "Opire: 50 issues"
as if that were the market. It had been under-reporting by 32% for weeks.

## The rule

**`market_complete` must mean the whole result set was READ, not that no step
raised an error.** A lost page makes the band INCOMPLETE:

```js
// AFTER — a lost page is a recorded fact, not a silent truncation
if (!p || !p.items || !p.items.length) {
  INCOMPLETE_BANDS.push((expr || '(whole query)') + ' page ' + page);
  process.stderr.write('  [CAP] PAGE LOST (page ' + page + ' of ' + pages + '): ' +
    (expr || '(whole query)') + ' - those issues are NOT in this scan\n');
  break;
}
```

and every single-page sweep becomes `searchAllPages(baseQ, label, perPage)`,
which paginates to `total_count`, paces between pages, marks a lost page
incomplete, and caps at 50 pages.

`INCOMPLETE_BANDS` non-empty → `market_complete: false` → the report prints a
**lower-bound warning** instead of a count. Fail loudly, not quietly.

## The diagnostic that is worth reusing

**Two runs of the same query with different totals is a bug report.** Diff the
per-source counts before diffing any code. Three numbers did it:

1. the total drop (1,371) — a claim that cannot be true
2. the per-source split — which bands lost pages
3. `gh api '<same query>' --jq .total_count` with `per_page=1` — ground truth

Verify the fix the same way: after the patch, a clean (unthrottled) run must
restore the per-source counts to within noise of ground truth, not merely stop
crashing. Here Opire went 50 → **74**, exactly the `total_count`.

## Related

- `prompts/a-ratio-is-not-a-threshold-you-can-buy.md` — the same day's farm-gate
  finding.
- `prompts/a-zero-pick-day-needs-a-receipt.md` — why a zero-pick scan must
  report per-population counts, not `scored_count: 0`.
