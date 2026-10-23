# tiny-watch Guide

**Repo:** [hussain-alsaibai/tiny-watch](https://github.com/hussain-alsaibai/tiny-watch)  
**Deps:** 0 (stdlib-only) | **Last verified:** 2026-10-23

> Zero-dependency file watcher with debounce, coalescing, and glob filtering for Python.

## What it does

A lightweight file system watcher using Python's stdlib `watchdog`-compatible API (or pure polling fallback), with debounce, coalescing, and glob-based path filtering.

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_watch import
FileWatcher, glob_filter` with a `FileWatcher(patterns=..., ignore=..., debounce_ms=...)`
constructor. **That is not the shipped API.** Verified against upstream
`tiny_watch.py`:

```
__all__ = ['watch', 'ignore', 'AsyncWatcher', 'FileEvent']
```

Top-level names: `watch`, `ignore`, `AsyncWatcher`, `FileEvent`, plus internal
`_NativeWatcher`, `_CoalescingWatcher`, `_ThrottleWatcher`.

The decorator-style entry points are `watch(...)` and `ignore(...)`; the
async watcher is `AsyncWatcher`.

## When to use

- **Hot-reload development** — restart servers, regenerate docs when source files change
- **Watch-and-build pipelines** — trigger builds, lints, tests on file changes
- **Auto-documentation** — regenerate docs when markdown/source files change
- **AI agent file watching** — monitor workspace for new files to process

## Key patterns

```python
from tiny_watch import watch, AsyncWatcher, FileEvent

@watch("**/*.py", ignore=["**/__pycache__/**", "**/.git/**"])
def on_change(event: FileEvent):
    print(f"{event}")
```

`AsyncWatcher` provides the same capability for asyncio applications.
Debouncing and coalescing are applied internally by the watcher chain
(`_CoalescingWatcher` -> `_ThrottleWatcher` -> `_NativeWatcher`).

## Related

- `tiny-pipeline` — pipeline that can be triggered by file watcher events
- `tiny-sandbox` — sandbox that can safely process newly created files
- `tiny-cron` — scheduler that can run periodic file system checks as fallback
