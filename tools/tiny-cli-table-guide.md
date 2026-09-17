# tiny-cli-table — Zero-Dependency Python CLI Table Renderer

> A beautiful, zero-dependency Python CLI table renderer. Eight box-drawing styles, auto-sized columns, color, alignment, sorting, cell merging, nested tables. Stdlib only.
> Last verified: 2026-09-17 | Version 1.1.0 | hussain-alsaibai/tiny-cli-table

## What It Is

A single-file (~700 lines), stdlib-only CLI table renderer with:

- 8 box-drawing styles (`fancy`, `rounded`, `double`, `heavy`, `ascii`, `minimal`, `markdown`, `github`)
- Auto-sized columns based on content width
- ANSI color per-cell or per-column
- Alignment (`left`, `right`, `center`) per column
- Sortable by any column (ascending/descending)
- Cell merging across rows/columns
- Nested tables (table-in-cell)
- `to_csv()` export (added v1.1.0)
- `auto_color_columns_by_name()` heuristic (added v1.1.0)
- 99/99 tests passing, 94% coverage, MIT

## Why It Exists

`tabulate` and `prettytable` are great, but each pulls in `wcwidth` (a C extension) and a small mountain of transitive code. **`tiny-cli-table`** is a **single file**, **~700 lines**, **stdlib only**, with **zero third-party dependencies**. Drop it in any Python 3.7+ project — no `pip install`, no build step, no surprises.

| Library | External deps | Files | Notable |
|---|---|---|---|
| **tiny-cli-table** | **0** | **1** | **stdlib only, fully typed, ~700 lines** |
| tabulate | 0 (but `wcwidth` recommended) | many | mature, but wide |

## Repo

https://github.com/hussain-alsaibai/tiny-cli-table

## When to Use

- You want pretty CLI output without `pip install tabulate`
- You need CSV export from the same data structure
- You're shipping a tiny-* tool and want consistent table rendering across the family
- You want zero-dep tables in cron jobs / agent reports / Telegram digests

## Minimal Example

```python
from tiny_table import Table

t = Table(headers=["Name", "Age", "City"], rows=[
    ["Alice", "30", "NYC"],
    ["Bob",   "25", "LA"],
    ["Carol", "41", "Berlin"],
], style="fancy")

print(t)
```

```
╭──────────────────────╮
│ Name  │ Age │ City   │
├──────────────────────┤
│ Alice │ 30  │ NYC    │
│ Bob   │ 25  │ LA     │
│ Carol │ 41  │ Berlin │
╰──────────────────────╯
```

## v1.1.0 Additions

- `to_csv()` — export rows as CSV string (write to file or stdout)
- `auto_color_columns_by_name()` — heuristic color rules by header keyword (e.g., `cost` → red, `ok`/`pass` → green)
- 9 new tests for CSV + auto-color paths

## Tested Patterns

- All 8 box styles render correctly with multi-byte chars
- ANSI color works on all major terminals + GitHub Actions
- CSV export round-trips with `csv.reader`
- Auto-color respects `NO_COLOR` 12-factor env convention

## See Also

- `prompts/no-color-12factor.md` — color disable convention
- `tools/cost-tracker.md` — uses tiny-cli-table for daily reports
