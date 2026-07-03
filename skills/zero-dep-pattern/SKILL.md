# zero-dep-pattern — Skill for Creating Single-File Python Utilities

## Trigger

Use when the user asks to:
- "Create a tiny Python utility"
- "Make a zero-dependency library"
- "Write a single-file Python module"
- "Scaffold a stdlib-only package"
- "Create a [name] like tiny-router/tiny-config"

## Description

Creates production-ready Python utilities with zero third-party dependencies,
designed to fit in a single file. The "tiny family" pattern: fast, focused,
stdlib-only modules that solve one problem well.

## Philosophy

- **One file, one purpose:** Each module does exactly one thing
- **Zero dependencies:** Only Python's standard library
- **Self-contained:** Can be copied into any project without package management
- **Tested:** Includes inline unittest suite
- **Typed:** Full type hints (Python 3.9+ syntax)
- **Documented:** Docstrings for every public API

## Procedure

### 1. Choose the Module Structure

```
my_module.py
├── Module docstring
├── Imports (stdlib only)
── __version__
── __all__
── Public API (classes/functions)
── Private helpers
── Self-test block (unittest)
```

### 2. Write the File

```python
#!/usr/bin/env python3
"""One-line description.

Extended description with:
- What it does
- When to use it
- Basic usage example

Last verified: YYYY-MM-DD
"""
from __future__ import annotations
import sys
from typing import Any

__version__ = "0.1.0"
__all__ = ["MainClass", "main_function"]

# --- Public API ---

class MainClass:
    """Docstring with description."""

    def __init__(self, ...) -> None:
        ...

    def method(self, ...) -> Any:
        """Docstring."""
        ...

# --- Private Helpers ---

def _helper(...) -> Any:
    """Private helper docstring."""
    ...

# --- Tests ---

if __name__ == "__main__":
    import unittest

    class TestMainClass(unittest.TestCase):
        def test_basic(self) -> None:
            obj = MainClass(...)
            result = obj.method(...)
            self.assertEqual(result, expected)

        def test_edge_case(self) -> None:
            with self.assertRaises(ValueError):
                MainClass(invalid_input)

    unittest.main()
```

### 3. Follow the Rules

| Rule | Why |
|------|-----|
| Under 300 lines | Fits on screen, easy to audit |
| Type hints everywhere | Self-documenting, IDE-friendly |
| `__future__ import annotations` | Forward references, cleaner types |
| `__all__` defined | Clear public API boundary |
| Self-test block | No external test runner needed |
| No third-party imports | Copy-paste friendly |
| Descriptive error messages | Users know what went wrong |
| `__version__` included | Version tracking |

### 4. Test It

```bash
# Run self-tests
python my_module.py

# Test import
python -c "from my_module import MainClass; print(MainClass())"

# Compile check
python -m py_compile my_module.py
```

### 5. Package for Distribution (Optional)

If publishing to GitHub/PyPI:

```
my-project/
├── src/
│   └── my_module/
│       ├── __init__.py    # from my_module import MainClass
│       └── my_module.py   # The actual module
├── tests/
│   └── test_my_module.py
├── pyproject.toml         # Modern packaging
├── README.md
└── LICENSE
```

`pyproject.toml`:
```toml
[project]
name = "my-module"
version = "0.1.0"
description = "What it does"
readme = "README.md"
requires-python = ">=3.9"
dependencies = []  # Zero dependencies!
```

## Example: Creating `tiny-cache`

**Prompt:** "Create tiny-cache: a zero-dependency in-memory cache with TTL"

**Result:** Single file with:
- `Cache` class with `get()`, `set()`, `delete()`
- TTL expiration via `time.time()`
- LRU eviction via `collections.OrderedDict`
- Thread-safe via `threading.Lock`
- 17 inline tests
- Type hints throughout
- 250 lines total

**Performance:** ~450K ops/sec (benchmarked vs dict baseline)

## The "Tiny Family" — Verified Modules

| Module | Like | Size | Use Case |
|--------|------|------|----------|
| snapdb | SQLite/Redis | ~15KB | In-memory database |
| fast-cache | Redis | ~15KB | Local caching |
| tiny-router | Flask | ~5KB | WSGI routing |
| tiny-config | python-decouple | ~4KB | Config loading |
| tiny-cli | Click/argparse | ~4KB | CLI parsing |
| tiny-log | structlog | ~4KB | Structured logging |
| tiny-validator | Pydantic | ~5KB | Data validation |
| tiny-worker | Celery | ~9KB | Background tasks |
| tiny-events | Redis Pub/Sub | ~8KB | Event-driven architecture |
| tiny-http | requests | ~10KB | HTTP client |

**Total:** ~80KB of Python across 20 production-ready libraries. Zero dependencies.

## Validation Checklist

- [ ] Zero third-party imports
- [ ] Under 300 lines (or well-justified if longer)
- [ ] Full type hints
- [ ] `__all__` and `__version__` defined
- [ ] Self-test block with unittest
- [ ] All tests pass: `python module.py`
- [ ] Compiles: `python -m py_compile module.py`
- [ ] Clear docstrings for public API
- [ ] Error messages are descriptive

## Notes

- The "tiny family" includes: tiny-router, tiny-config, tiny-cli, tiny-log, tiny-validator, tiny-worker, tiny-events, tiny-http, tiny-agent, tiny-embed, tiny-mcp, tiny-rate, tiny-retry, tiny-pool, tiny-compose, tiny-trace, tiny-secret, tiny-cron, tiny-flags, tiny-queue
- Each follows this exact pattern
- Copy any module into a project — no pip install needed
- For complex projects, compose multiple tiny modules rather than growing one
- Benchmark against stdlib equivalents (dict, list, set) to justify existence

### Patterns Learned (2026-07-03)

**Don't shadow helpers with enclosing class methods.**
If you define an inner helper class with the same name as a method on the
enclosing class (`class _process_lock` vs `def _process_lock()`),
`Outer._helper(self)` resolves to the method, not the class → infinite
recursion on first call. Capitalize inner classes (`_ProcessLock`) or use a
distinct attribute name.

**Make filesystem-dependent features toggleable.**
Anything that depends on `fcntl.flock`, `mmap`, hardlinks, POSIX signals, or
process-shared state must have a `cross_process_lock=False` / `no_xyz` knob
or an env-var escape hatch. CI often runs in containers with tmpfs where
POSIX file-lock semantics are subtly broken — the user must be able to
disable the feature without forking.

## Last Verified: 2026-07-03
