# A Slot Budget Is Not a Slice Budget

**A rule for every ranker, sampler, scorer, or selector that picks N items out
of a larger set.**

> Found 2026-10-28 in the bounty scanner. The scanner collects contributor tasks
> and cash bounties, then picks a fixed number of candidates to **score**. The
> pick was a **positional slice**: the first N of the collected list. On the live
> sweep, the first 100 collected tasks came from only **39 repos**;
> `k08200/klorn` alone held **14** of them, `tonianev/eonmark` **13**,
> `exceev-consulting/server-prep` **11**. And `pipeshub-ai/pipeshub-ai` — the
> 3.8k-star repo the contributor-task path exists for — sat at positions **200
> and 238** and was cut before it was ever scored. **Last verified:** 2026-10-28 —
> the fix is in the scanner and the regression test is in
> `skills/bounty-scanner/test-contributor-tasks.js`; the scanner's five suites
> all pass.

## The two budgets are different

| budget | what it buys | what it costs |
|---|---|---|
| **slot** (scoring budget) | one metadata fetch + one scam check + one score | N repos' worth of work |
| **slice** (position in the list) | nothing | nothing |

Scoring is **per-repo work**. 250 candidates from 39 repos is 39 repos' worth
of metadata fetches and 39 repos' worth of scam detection. Spending that budget
on 14 issues from one 8-star repo buys nothing at all.

> **Diversity by repo is the cheaper way to spend the same budget.**

A positional slice spends the budget on whichever repo happened to open the
most issues first.

## Why a positional slice is the default (and why it is wrong)

`list.slice(0, N)` is one line, deterministic, and obviously fair *to the
caller*. It is only unfair to the **candidate**. The list order is an artefact
of the collection order, and the collection order is decided by:

- which label was searched first,
- which repo opened the most issues,
- which repo was created most recently.

None of those is a signal about **issue quality**. So the slice converts an
incidental ordering into a **scoring decision**.

## The shape of the bug

```javascript
// BEFORE - positional slice. A flood repo takes the whole window.
return cash.slice(0, cashSlots).concat(tasks.slice(0, taskSlots));

// AFTER - round-robin across repos, so every repo's FIRST task is taken
// before any repo's SECOND task.
return cash.slice(0, cashSlots).concat(spreadAcrossRepos(tasks, taskSlots));
```

```javascript
function spreadAcrossRepos(issues, slots) {
  if (slots <= 0) return [];
  if (issues.length <= slots) return issues.slice();

  const byRepo = new Map();
  for (const issue of issues) {
    const repo = String(issue.repository_url || issue.repo || '')
      .split('/').slice(-2).join('/');
    if (!byRepo.has(repo)) byRepo.set(repo, []);
    byRepo.get(repo).push(issue);
  }

  const out = [];
  const queues = [...byRepo.values()];
  let progressed = true;
  while (out.length < slots && progressed) {
    progressed = false;
    for (const q of queues) {
      if (!q.length) continue;
      out.push(q.shift());
      progressed = true;
      if (out.length >= slots) break;
    }
  }
  return out;
}
```

Four properties that matter:

1. **The count is exact.** `out.length === slots`, always.
2. **It is deterministic.** Same input, same output — no randomness, no seed.
3. **Every repo's first item is reachable.** A quiet repo with one good issue
   is not beaten by a flood repo with two hundred.
4. **The flood is still visible.** A repo with more tasks than any other still
   has its first task scored. It simply cannot take the whole window.

## The rule

> **When the budget is spent on per-item work, the selection must be
> diversified over the dimension that makes the work expensive.**

Concretely, per-item cost is driven by the **repo**, so the selection is
spread over repos.

The same reasoning applies elsewhere:

| the budget buys | per-item cost is driven by | spread over |
|---|---|---|
| a metadata fetch per candidate | the repo | repo |
| an LLM call per candidate | the prompt shape | prompt shape |
| a CI minute per matrix job | the OS image | OS image |
| a network round-trip per shard | the host | host |

## The failure to guard against

Spreading by repo **is not** the same as ignoring the flood. The flood is real:
one repo opened 14 tasks in a window. Round-robin does not delete it, it
prevents the flood from **deciding the outcome**.

If a flood needs its own defence (a per-repo cap, a duplicate-issue filter,
a trust score on the repo), that is a **separate, explicit** rule. Do not smuggle
it in through the selection order.

## The regression test that proves it

The property to assert is not "the flood count is small". It is **"a task
past the positional window is still scored"**:

```javascript
const late = [];
for (let i = 0; i < 250; i++) {
  late.push({
    id: 'late' + i,
    _platform: 'contributor_task',
    repository_url: 'https://api.github.com/repos/noisy' + (i % 30) + '/noisy-repo' + (i % 30),
  });
}
late.push({
  id: 'theOne',
  _platform: 'contributor_task',
  repository_url: 'https://api.github.com/repos/pipeshub-ai/pipeshub-ai',
});
const spreadLate = pickCandidates(cashForSpread.concat(late), 250, 0.4);
check('a task past the positional window is still scored',
  spreadLate.some(i => String(i.repository_url).includes('pipeshub-ai/pipeshub-ai')),
  'the late task was cut');
```

Plus two more, because each one can fail independently:

- **one repo cannot take every task slot** (`floodCount < 100`),
- **a quiet repo is still represented** (`quietCount > 0`),
- **the slot count stays exact** (`spread.length === 250`).

## The generalisation

> **A slice of a list is chosen by whoever built the list. If the slice decides
> the outcome, the list order is deciding the outcome — and list order is
> usually an artefact.**

Ask of every ranker: *what does my selection order actually know?* If the
answer is "whatever was collected first", the order is arbitrary and must not
be load-bearing.

See also `prompts/parallel-issue-scoring-pattern.md` (the API-call side of the
same pipeline) and `prompts/reserve-before-work.md` (the race after selection).
