# tiny-cli-progress v0.1.0 — Stdlib-Only Progress Bars + Spinners

> Zero-dependency progress bars and spinners for Python CLIs. Like `tqdm` and `rich.progress` in one file.
> Last verified: 2026-09-25 | Version 0.1.0 | hussain-alsaibai/tiny-cli-progress

## Overview

Pure-Python progress rendering for command-line tools. No `pip install tqdm`, no `rich` dependency. Works on any Python 3.9+ terminal that supports carriage-return (`\r`) line rewriting.

## What's in v0.1.0

- **Bar renderers:** percentage, ETA, throughput (items/sec), bytes-units auto-scaling (B/KiB/MiB/GiB/TiB), fill character, width, total override.
- **Spinners:** rotating, bouncing-bar, dots, arrow, bouncing-ball, time-ago, moon phases. All unicode, fully configurable interval.
- **Multi-bar manager** (`MultiProgress`) — render multiple bars side-by-side or stacked, independent updates.
- **Context managers** (`with progress(...) as p`) and **iterable wrappers** (`p.iter(items)`) — drop-in for existing loops.
- **No-op fallback** when stdout is not a TTY (`CI=true`, piped output, `tqdm`-style graceful degrade).
- **Thread-safe** updates via internal lock.
- **375 LOC main + 295 LOC tests**, stdlib only, MIT.

## Quick Start

```python
from tiny_cli_progress import progress, BarConfig

with progress(total=1000, desc="Processing") as p:
    for item in items:
        process(item)
        p.update(1)

# Multi-bar
from tiny_cli_progress import MultiProgress
mp = MultiProgress()
bar1 = mp.add_bar(total=500, desc="Download")
bar2 = mp.add_bar(total=300, desc="Verify")
mp.start()
# ... update bar1.update(n) / bar2.update(n) from threads ...
mp.stop()
```

## When to Use

- Tiny-* CLI tools that should stay zero-dep
- CI scripts where `tqdm` adds install time
- Agent command-line output that needs visual feedback
- Anywhere you'd reach for `tqdm` but want stdlib only

## When NOT to Use

- Need rich HTML/LaTeX tables → use `rich`
- Need Jupyter widget integration → use `tqdm.notebook`
- Need millions of bars/sec → `rich` is faster

## Repo

https://github.com/hussain-alsaibai/tiny-cli-progress

## See Also

- `tools/tiny-cli-guide.md` — broader CLI toolkit
- `tools/tiny-cli-table-guide.md` — tabular output companion
