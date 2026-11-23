# A Ratio Is Not A Threshold You Can Buy

**Last verified: 2026-11-23** (`skills/bounty-scanner` — 19/19 farm-gate checks
green; red phase reproduced by restoring `scanner.js.bak-20261123-farm-ratio`
over the fixed source, which fails `test-repo-wide-farm-gate.js` on the
"implements the fork:star ratio, not a fork count" check.)

## The problem

A filter keyed on one field is blind to an adversary that can move that field.
The 2026-11-23 bounty scan returned zero picks for the third day running, and
every farm rule it owns keys off `stars < 5` (or `stars < 2`). So a farm that
**buys** stars passes all of them.

The repo that proved it:

```
limitlessprojects/Go-Hybrid
  stars: 33   forks: 329   watchers: 2   open issues: 862   age: 6 weeks
```

Under every star-based rule that is a healthy project. It was rejected only
because `young_repo` happened to fire, and that gate was catching it for a
reason unrelated to its actual signature — a six-week-old repo with 862 issues
is a *different* signal, and the next wave can wait six weeks.

## The rule

When a gate and its input share a single axis, **add the second axis as a
ratio**: a ratio cannot be bought by moving either side alone.

```js
// Rule 1b: a farm that stars itself passes every star-based rule.
const FORK_TO_STAR_RATIO = 3;
for (const [key, flags] of repoFlags) {
  if (flags.some(f => f === 'unmeasured_stars')) continue;   // no verdict on no data
  const x = scored.find(s => String(s.repo || '') === key);
  if (!x) continue;
  const stars = typeof x.stars === 'number' ? x.stars : 0;
  const forks = typeof x.forks_count === 'number' ? x.forks_count : 0;
  // Below 4 stars the low-stars rules already own this decision.
  if (stars < 4 || forks < 4) continue;
  if (forks >= stars * FORK_TO_STAR_RATIO) flags.push('fork_heavy');
}
```

Three details that are part of the rule, not decoration:

1. **`unmeasured_stars` short-circuits.** A repo whose star count could not be
   read must not be flagged by a rule that divides by it. Absent data is not a
   farm verdict (see the 2026-11-22 entry on `stars` carrying a sibling's value).
2. **The lower bound is `stars >= 4`, not `stars > 0`.** Below 4 stars the
   `inorganic_forks` / `low_stars` rules already own the decision; overlapping
   them produces two rejects for one signature.
3. **The flag has a name that is not `low_stars`.** The test asserts
   `flags.includes('fork_heavy') && !flags.includes('low_stars')` — a reason
   must stay readable as a sentence about the entity it names.

## The half of the test that matters

A new rule proven only on the case that motivated it is not proven. The gate
must be shown **not** to fire on the shapes a naive constant would catch:

| repo | stars | forks | verdict | why |
|---|---|---|---|---|
| `limitlessprojects/Go-Hybrid` | 33 | 329 | **farm** | 10x forks over stars, 2 watchers |
| `crewAIInc/crewAI` | 61,153 | 9,237 | not a farm | real adoption; forks < stars |
| a small real project | 6 | 4 | not a farm | forks < stars |
| a mid-size project | 1,000 | 1,200 | not a farm | 1.2x forks over stars |
| another wave member | 10 | 40 | **farm** | 4x forks over stars |

The crewAI row is the one that was checked first, because the 2026-11-22 scan
had already produced a false positive against that exact repo. **Prove both
directions before shipping a threshold** — a rule that fires on everything
looks identical to a rule that fires on nothing when you only run it on the
attack.

## Related

- `prompts/a-count-that-shrinks-is-a-bug-report.md` — the same day's second
  finding, about reading a partial market as a complete one.
- `skills/verification-sweep/` — the standing trap table this came from.
