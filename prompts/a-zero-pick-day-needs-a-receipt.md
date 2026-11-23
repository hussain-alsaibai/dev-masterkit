# A Zero-Pick Day Needs a Receipt, Not a Summary

**Last verified: 2026-11-23** (`skills/bounty-scanner` — `test-empty-report.js`
17/17 green with the new `gate_counts` branch; live 2026-11-23 scan wrote
`gate_counts` and `rejected_all` to `last-scan.json`.)

## The problem

A zero-pick scan and a broken scan produce the same summary line. On
2026-11-23 the third consecutive zero-pick day was **correct** — every
candidate was genuinely unavailable — but nothing in the stored report could
prove that, and three prior zero days had already trained the reflex to go fix
the scanner.

Two fields made it unreadable:

- **`scored_count` counted post-gate survivors.** It read `0`, and the report
  rendered *"0 reached a score"* — a claim that nothing was ever scored, when
  five candidates had been scored and then killed by a later gate. The number
  was true and the sentence was false.
- **`rejected` was capped at 10 for the stored file.** The two farm rejects
  that day's gate actually produced were absent from it entirely. The only
  honest per-item record was `rejected_by_reason`, a counter, not a list.

**A capped report array is not an audit trail.** Any summary that reads
`rejected[]` for a per-item account is reading a truncated list as a complete
one.

## The rule

Name each population in the pipeline, so a zero-pick day carries a receipt:

```js
const gate_counts = {
  scored: scored.length,            // reached scoring
  shortlisted: shortlist.length,    // reached the competition phase
  rejected_contested: contested,
  rejected_stale: stale,
  rejected_sponsor: shortlist.filter(c =>
    c._reject && /Sponsor org/.test(c._rejectReason || '')).length,
  survived_gates: survived.length,
};
```

and store the untruncated list beside the display slice:

```js
rejected: rejected.slice(0, 10),   // display convenience
rejected_all: rejected,            // audit trail
gate_counts,
```

The rendered line then reads, on a zero-pick day:

```
_6,685 issue(s) carried a readable dollar amount; 5 were scored,
 5 reached the competition shortlist, 2 survived._
_Shortlist deaths: 1 contested, 2 stale._
```

That is a **success report**: two candidates came out of the gates and were
both unavailable for a stated reason. It is falsifiable, and it distinguishes
"the gates killed everything" from "the pipeline never ran".

## Second rule: a zero-pick day is a claim about the gates

Do not ship "nothing to do today". Take **one live reject**, fetch its real
repo metadata, and check the gate caught it for the reason it claims. Here one
`gh api repos/limitlessprojects/Go-Hybrid` showed a 33-star repo with 329
forks, 2 watchers and 862 open issues — genuinely a farm, but caught by a gate
(`young_repo`) whose reason did not describe its signature. That single lookup
is what turned three zero-pick days into a real fix; three more scan reruns
would not have.

## Related

- `prompts/a-ratio-is-not-a-threshold-you-can-buy.md`
- `prompts/a-count-that-shrinks-is-a-bug-report.md`
- `skills/bounty-verifier/` — the verification steps a pick must pass.
