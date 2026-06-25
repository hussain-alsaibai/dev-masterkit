# zero-dep-scaffold — Prompt for Creating Single-File Python Utilities

## Description

Creates production-ready, zero-dependency Python utilities that fit in a single
file. Inspired by the "tiny family" pattern: tiny-router, tiny-config, tiny-cli,
etc.

## The Prompt

```
Create a zero-dependency Python utility called {name} that does {purpose}.

Requirements:
- Single file implementation (can be imported or run standalone)
- Zero third-party dependencies (stdlib only)
- Type hints everywhere (Python 3.9+ syntax)
- Include a self-test block: `if __name__ == "__main__":` with assertions
- Follow this structure:

```python
#!/usr/bin/env python3
"""One-line description.

Extended description with usage examples.
"""
from __future__ import annotations
import {stdlib_modules}

__version__ = "0.1.0"
__all__ = ["MainClass", "helper_function"]

# --- Core Implementation ---

class MainClass:
    """Docstring."""
    def __init__(self, ...) -> None:
        ...

# --- Tests ---
if __name__ == "__main__":
    import unittest
    class TestMainClass(unittest.TestCase):
        def test_basic(self):
            ...
    unittest.main()
```

Guidelines:
- Keep under 300 lines if possible
- Use dataclasses or NamedTuple for data structures
- Prefer pure functions over stateful classes
- Include error handling with descriptive messages
- Match the tone of Python's stdlib (clear, concise, documented)
```

## When to Use

- Creating utility libraries
- Extracting reusable patterns from larger projects
- Building a personal toolkit of zero-dependency tools

## Last Verified: 2026-06-25
