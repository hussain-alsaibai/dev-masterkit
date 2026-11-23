# Adding a Second Axis to a Single-Field Gate

**Last verified: 2026-11-23** — applied to `skills/bounty-scanner` (farm gate,
pagination, report counts); 19/19 scanner suites green; red phase reproduced
twice by restoring `scanner.js.bak-20261123-farm-ratio`.

A short procedure for the case where a filter keyed on one field has stopped
discriminating. Worked example: the 2026-11-23 bounty scanner, where every farm
rule keyed off `stars` and a farm that bought stars passed all of them.

## When to reach for it

- A gate rejects everything for days and the operator names one candidate that
  should have survived.
- A gate and the field it reads share one axis (price, stars, downloads, stars
  in a trend chart, stars after a boost campaign).
- An adversary has an obvious, cheap way to move that one field.

## Steps

1. **Reproduce the decision on one candidate before touching the gate.**
   One `gh api repos/<owner>/<repo>` (or equivalent) against the named
   candidate. Print the field *and* its provenance. This is cheaper than a
   rerun and it is the step that finds out the gate caught the right entity for
   the wrong reason.

2. **Check whether the field is per-entity or per-record.** A fact about a
   repository (stars, forks, age) must be computed once per repository, keyed by
   repo — never aggregated over issue/PR records. The 2026-11-22 version of this
   bug summed `no_stars` across six issues and produced an identical input for
   a 61k-star org repo and a 0-star farm.

3. **Move the constant to the second axis, as a ratio.**
   `forks >= stars * 3` cannot be satisfied by buying either side alone.
   Prefer a ratio to a bigger count: a bigger count is a better constant on the
   same blind axis.

4. **Handle absent data explicitly.** Skip the ratio rule when the field could
   not be measured (`unmeasured_stars`), and keep the flag name distinct from
   the rules it complements (`fork_heavy`, not `low_stars`).

5. **Prove both directions before shipping.** Minimum four cases:
   the attack (fires), the real project with the same shape (does not fire),
   the boundary just under the threshold (does not fire), and the shape a
   naive count would catch (does not fire). Here: Go-Hybrid 33/329 fires,
   crewAI 61k/9k does not, 6-star/4-fork does not, 1,000-star/1,200-fork does
   not, 10-star/40-fork fires.

6. **Run the new test against the pre-fix source.** Copy the tree, restore the
   `.bak` of the previous scanner, run the test file. A red phase of 1 failed
   check out of 19 is the evidence the test is measuring the rule. A test that
   passes on both versions measures nothing.

7. **Re-run the real query and compare per-source counts to ground truth.**
   The fix is done when the numbers match `total_count` from an independent
   call, not when the suite is green.

## Trap table

| Trap | Symptom | Fix |
|---|---|---|
| Bigger constant on the bought axis | farm with 33 stars passes `stars < 5` | ratio against the second axis |
| Per-record aggregation of a per-entity fact | 61k-star repo treated as a farm | compute once per repo, keyed by repo |
| Overlapping rules | two reject flags for one signature | lower bound (`stars >= 4`) so the old rule owns its range |
| Verdict on missing data | crash or divide-by-zero flag | explicit skip on `unmeasured_*` |
| Green-only test | passes on the pre-fix source | restore the `.bak` and prove it red |
| Display array used as the audit | rejects silently absent from the file | store the untruncated list separately |
