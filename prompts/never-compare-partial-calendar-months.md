# Never Compare Partial Calendar Months

**A rule for every trend report, growth metric, or "this month vs last month"
comparison that is written on a day other than the 1st.**

> Found 2026-10-26. The first Q4 trends report compared calendar-month download
> totals. The data ended on the 25th, so the final month had **25 of 31 days**
> and every package looked like it was collapsing. **Last verified:** 2026-10-28 —
> the corrected method (trailing 30 days vs the previous 30 days) has now been
> used for two consecutive reports, and the raw table ships alongside the report
> so the arithmetic is checkable.

## The failure

The report was not wrong. The measurement was right and the comparison was
misleading:

| package | naive calendar-month comparison | corrected (30d vs 30d) |
|---|---|---|
| `fastapi` | −29.9% | **+28.4%** |
| `langchain` | −45.8% | **−4.4%** |

`fastapi` went from *"collapsing"* to *"growing fastest in its category"*
because of nothing but the day of the month the report was written on.

## The rule

> **Use trailing 30 days against the previous 30 days. It is partial-month safe,
> and it is the only comparison that survives being written on any day other
> than the 1st.**

A calendar month is only comparable to a calendar month when **both** months
are complete. If the data ends mid-month, one of them is not.

## What is safe and what is not

| comparison | safe? | why |
|---|---|---|
| trailing 30d vs previous 30d | ✅ | both windows are complete by construction |
| trailing 7d vs previous 7d | ✅ | same, and sensitive to a single spike |
| calendar month vs calendar month, both complete | ✅ | fine |
| calendar month-to-date vs the same month-to-date last year | ✅ | **if you state the day** |
| calendar month vs previous calendar month, written mid-month | ❌ | the final month is partial |
| calendar-to-date vs a full previous month | ❌ | unequal windows |

The one other safe form — month-to-date against the **same** month-to-date last
year — requires you to print the cutoff day next to the number, or the reader
cannot tell what window they are looking at.

## The procedure

1. **Find the cutoff.** What is the last date the data covers? If it is not the
   last day of the month, the current month is partial.
2. **Use rolling windows.** `trailing 30d` against `previous 30d`.
3. **State the window in the table header**, not in a footnote. A column
   labelled `change` with no window is a claim with no units.
4. **Ship the raw table** next to the report. Every figure must be re-derivable
   from published data by someone who does not trust you.
5. **Verify the arithmetic with a script** before publishing, not by reading the
   numbers.

```python
# trailing 30 days vs the previous 30 days
def pct_change(now: int, before: int) -> float:
    if before == 0:
        return float("inf")
    return (now - before) / before * 100.0
```

## The report shape that makes this checkable

```markdown
### Growing fastest

| package | downloads/mo | change |
|---|---|---|
| marvin | 226,310 | **+80.1%** |
| opentelemetry-api | 606,882,343 | **+57.5%** |

Trailing 30 days vs the previous 30 days. `/mo` is the trailing-30-day
download volume. Raw data: `2026-10-28-pyPI-numbers.md`.
```

Three properties that cost nothing:

- the window is in the section header,
- `/mo` is defined once,
- the raw table is a sibling file, not a screenshot.

## The verification that caught it

The 2026-10-28 report covered **160 packages** (up from 100 two days earlier)
and **every figure was re-derived by a script** from the raw download data
before publication. That is what makes the table auditable rather than
merely published.

The same report's conclusion also flipped once the comparison was fixed:
**agent frameworks did not consolidate — they fractured.** `marvin` +80.1%,
`agno` +29.8%, `letta` +29.6%, `langchain-anthropic` +29.3%, while
`langchain` itself is **−3.4%** and `llama-index` **−14.9%**. The
meta-frameworks are flat-to-down and the usage is moving to provider-specific
packages. The naive calendar comparison would have shown the opposite.

## The generalisation

> **A percentage without its window is not a measurement. Write the window into
> the column, not into a footnote.**

And, for anyone comparing two periods at all:

> **If one of the two periods is incomplete, the comparison is a statement
> about the report's date, not about the subject.**

See also `prompts/assert-invariants-not-fixed-values.md` (assert the property,
not the number that happened to be true on the day).
