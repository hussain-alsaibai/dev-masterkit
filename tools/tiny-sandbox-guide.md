# tiny-sandbox Guide

## Repo
https://github.com/hussain-alsaibai/tiny-sandbox

## What It Does

Zero-dependency sandboxed Python execution. AST-level safety checks plus timeout
and memory guards. One file, no setup.

## Last Verified
2026-10-24

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_sandbox import
run_sandbox`. **There is no `run_sandbox` function.** Verified against upstream
`tiny_sandbox.py`:

```
SandboxError, TimeoutException, SandboxStats, SandboxResult,
SafeASTTransformer, SandboxedImport, Sandbox, execute
```

The entry points are the **`Sandbox`** class and a module-level **`execute`**
function.

## Key Features

- `SafeASTTransformer` — rejects dangerous imports and calls at the AST level
- `Sandbox` — the executor, with `SandboxStats` and `SandboxResult`
- `TimeoutException` / `SandboxError` — typed failures
- `_TimeoutGuard` / `_MemoryGuard` — resource limits
- `SandboxedImport` — restricted import machinery

## Quick Start

```python
from tiny_sandbox import Sandbox, execute

result = execute("print(sum(range(100)))")
print(result.stdout)      # "4950\n"
print(result.returncode)  # 0
```

`Sandbox` is the configurable form when you need to set limits explicitly.

## Verification (2026-10-24)

**35 tests passing** (verified by run). Version `1.0.0` in both
`pyproject.toml` and `__version__` - they match. `ruff check` is clean.

The repo's CI lint step was failing on ruff findings and its test/benchmark
targets did not exist; both were fixed on 2026-10-24.

## When to Use

- Running untrusted or generated Python in agent/tool contexts
- Safer alternative to `eval()` / `exec()` for dynamic code execution
- Sandboxed execution where you want more than AST transformation alone

## Related

- `tools/tiny-safeexec-guide.md` — subprocess isolation, complementary depth
