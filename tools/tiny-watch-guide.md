# tiny-watch Guide

**Repo:** [hussain-alsaibai/tiny-watch](https://github.com/hussain-alsaibai/tiny-watch)  
**Deps:** 0 (stdlib-only) | **Last verified:** 2026-07-24

> Zero-dependency file watcher with debounce, coalescing, and glob filtering for Python.

## What it does

A lightweight file system watcher using Python's stdlib `watchdog`-compatible API (or pure polling fallback), with debounce, coalescing, and glob-based path filtering.

## When to use

- **Hot-reload development** — restart servers, regenerate docs when source files change
- **Watch-and-build pipelines** — trigger builds, lints, tests on file changes
- **Auto-documentation** — regenerate docs when markdown/source files change
- **AI agent file watching** — monitor workspace for new files to process

## Key patterns

```python
from tiny_watch import FileWatcher, glob_filter

watcher = FileWatcher(
    patterns=["**/*.py", "**/*.md"],
    ignore=["**/__pycache__/**", "**/.git/**"],
    debounce_ms=300,
)

@watcher.on_change
def handle_change(path, event):
    print(f"{event}: {path}")

watcher.start()
```

## Related

- `tiny-pipeline` — pipeline that can be triggered by file watcher events
- `tiny-sandbox` — sandbox that can safely process newly created files
- `tiny-cron` — scheduler that can run periodic file system checks as fallback
