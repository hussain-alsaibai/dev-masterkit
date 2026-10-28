# tiny-cli-progress Guide

## Repo
https://github.com/hussain-alsaibai/tiny-cli-progress

## One-liner
Zero-dependency terminal progress bar for Python. Pure stdlib, TTY-aware,
no-op when not attached to a terminal.

## Status
**The repo now exists upstream.** `https://github.com/hussain-alsaibai/tiny-cli-progress`
returned HTTP 404 on 2026-10-23 and returns **200** now (last push 2026-10-26,
re-checked 2026-10-28). The earlier "local clone only" note is stale.

**The PyPI name `tiny-cli-progress` is free** (verified 2026-10-28), but the
package is not published there yet. Install from the repository URL.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_cli_progress import
progress, BarConfig`. **There is no `BarConfig` class.** Verified against the
local clone:

```
__all__ = ['ProgressBar', 'progress', 'Spinner', 'MultiBar', 'is_tty']
```

The bar object is **`ProgressBar`** and the entry point is **`progress`**.
`Spinner` and `MultiBar` are also exported. `BarConfig` does not exist —
configuration is passed as keyword arguments to `progress()` / `ProgressBar()`.

## Quick Example
```python
from tiny_cli_progress import progress

with progress("indexing", total=len(files)) as bar:
    for f in files:
        do_work(f)
        bar.advance(1)
```

## Key Features
- TTY detection: renders nothing when stdout is piped or redirected
- ETA and human-readable rate
- Cursor hide/show handling
- Nested progress lines

## Related
- `tools/tiny-cli-guide.md` — the CLI builder (`App`, `command`, `option`, ...)
- `tools/tiny-cli-table-guide.md` — table rendering
