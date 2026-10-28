# tiny-file-watcher Guide

> Zero-dependency Python file system watcher with debounce, throttle, and glob
> filtering. Pure polling, stdlib-only. **Last verified:** 2026-10-28 —
> **46 tests passing**, measured by run against the upstream clone on Python
> 3.8–3.13; the rename defect below was fixed and re-verified.

**Repo:** https://github.com/hussain-alsaibai/tiny-file-watcher
**Version:** 0.1.0 | **Deps:** 0 (stdlib only) | **License:** MIT
**Install:** `pip install "git+https://github.com/hussain-alsaibai/tiny-file-watcher.git"`
(the package is **not** on PyPI — verified 2026-10-28)

## What It Does

Polls one or more paths on a background thread and emits `CREATED`,
`MODIFIED`, `DELETED` and `MOVED` events. No inotify, no native extension —
works identically on Linux, macOS and Windows.

## API

```
__all__ = ["EventType", "Event", "FileWatcher", "AsyncFileWatcher",
           "watch", "awatch", "main"]
```

### `FileWatcher(paths, **options)`

| option | default | meaning |
|---|---|---|
| `paths` | — | one path or an iterable of paths (files or directories) |
| `interval` | `1.0` | seconds between polls |
| `debounce_ms` | `100` | coalesce events within this window, per path |
| `throttle_rate` | `None` | max callbacks dispatched per second, across the watcher |
| `include` | `()` | glob patterns; only matching paths are tracked |
| `exclude` | `()` | glob patterns; matching paths are ignored |
| `recursive` | `True` | recurse into subdirectories |
| `max_depth` | `None` | maximum recursion depth (root = 0) |
| `follow_symlinks` | `False` | follow symlinks |
| `ignore_directories` | `False` | do not emit events about directories themselves |
| `on_error` | `None` | callback invoked when polling raises unexpectedly |

Invalid options raise `ValueError` at construction (`interval <= 0`,
`debounce_ms < 0`, `throttle_rate <= 0`, no paths).

### `Event`

```python
@dataclass(frozen=True)
class Event:
    type: EventType      # created | modified | deleted | moved
    path: str            # absolute path
    old_path: str = ""   # previous path, for MOVED only
    timestamp: float     # time.monotonic() at detection
    is_directory: bool = False
```

### `watch()` / `awatch()`

Context-manager shortcuts:

```python
from tiny_file_watcher import watch

with watch("src", interval=0.5, include=["**/*.py"]) as w:
    w.on("modified", lambda e: print(e.path))
    ...
```

`awatch(paths, **kwargs)` returns an `AsyncFileWatcher`.

## The rename defect — a rename is not atomic

This is the package's one interesting bug, and the reason it had no guide
before.

`os.rename` is **not atomic**. Between the two halves there is a window in
which the old path no longer exists and the new path does not exist yet. A
scan that lands in that window sees the file as deleted; the next scan sees
the new path as created. The move was reported as `DELETED + CREATED` and the
pairing was lost permanently.

The original move detector compared inodes between the **current and previous
snapshot**, so it only worked when the rename happened to fall between two
scans. Reproduced locally at about **1 run in 30**, and it made the rename test
fail intermittently in CI — **3 of the 6 matrix jobs failed** (on 3.8, 3.12
and 3.13).

**The fix** keeps a map of `inode -> the path that inode was last seen at`.
When a path appears whose inode was last seen somewhere else, the file was
renamed, not created. The history survives a transient snapshot, so the move
is recovered one scan later instead of being swallowed.

Verified with a **400-trial** stress harness: **0 misses**, where the old code
missed 2–4 per 60.

```python
# inode -> the path that inode was last seen at. A rename is not atomic:
# for a brief window the old path is gone and the new path has not appeared
# yet. Diffing against that transient state loses the move for good.
self._inode_history: Dict[int, str] = {}
```

## The test-side fix (separate, and also necessary)

The suite used a fixed `time.sleep(0.3)` against a **background polling
thread**. Under load the thread may not have run yet, so the assertion failed
intermittently. Replacing the sleep with a **condition wait** returns as soon
as the event arrives — and halves the suite time (4.1s -> 2.1s).

> **Reproduce the race before you fix the test. A longer sleep hides a real
> defect; a condition wait removes the flake without touching the library.**

## When to Use

- Reload a config or plugin when a file changes, without a native dependency
- Trigger rebuilds on source edits in a polling-friendly environment
- Async agent workflows that need to react to file changes

**Not for:** high-frequency event streams — this is polling, so the latency
floor is `interval`. Use an inotify binding if you need sub-millisecond
reaction.

## Related

- `prompts/ci-census-reveals-what-was-never-checked.md` — how the rename bug
  was found, and the general shape of "a flaky test hiding a real race"
- `tools/fresh-install-verification-guide.md` — proving it imports after install
