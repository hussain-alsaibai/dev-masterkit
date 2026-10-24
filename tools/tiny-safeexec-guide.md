# tiny-safeexec — Safe Python Code Execution

**Source:** [hussain-alsaibai/tiny-safeexec](https://github.com/hussain-alsaibai/tiny-safeexec)
**License:** MIT | **Language:** Python 3.8+ | **Last verified:** 2026-10-24

## Status
**The upstream repository is named `tiny-safeexec` but its contents are
`tiny-sandbox`.** The upstream README's own title is "tiny-sandbox", and the
only Python module shipped is `tiny_sandbox.py`. There is no `tiny_safeexec.py`.

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_safeexec import
safe_exec` with a `safe_exec(code=..., timeout=5, memory_mb=64)` call.
**`tiny_safeexec` does not exist and `safe_exec` does not exist.** Verified
upstream `tiny_sandbox.py`:

```
SandboxError, TimeoutException, SandboxStats, SandboxResult,
SafeASTTransformer, SandboxedImport, Sandbox, execute
```

The entry points are the **`Sandbox`** class and the module-level **`execute`**
function.

## When to use

- Running untrusted Python code in agent/tool contexts
- Safer alternative to `eval()` or `exec()` for dynamic code execution
- Sandboxed code execution where you need more than AST transformation alone

## What it does

Safe Python code execution for AI agents via AST validation plus resource
guards. Rejects dangerous imports and calls, enforces timeouts and memory
limits, and captures stdout/stderr and the return value.

## Quick start

```python
from tiny_sandbox import execute

result = execute("print(sum(range(100)))")
print(result.stdout)       # "4950\n"
print(result.returncode)   # 0
```

## Key features

- AST-level safety validation (`SafeASTTransformer`)
- Timeout and memory guards
- Captures stdout, stderr, return value
- Blocks network, filesystem, and dangerous imports
- Zero dependencies beyond stdlib

## Verification (2026-10-24)

**35 tests passing** (verified by run). Version `1.0.0` in both
`pyproject.toml` and `__version__` - they match. `ruff check` is clean.

The repo's CI lint step was failing on ruff findings; fixed 2026-10-24.

Note the naming trap from the API Correction above: this repo ships
`tiny_sandbox.py`, so `import tiny_safeexec` will fail. The module is
`tiny_sandbox`.

## Security model

AST validation plus resource limits — **not** subprocess isolation, despite the
repo name. For a real process boundary use `subprocess` with a restricted
environment, or a container.

## Related

- `tools/tiny-sandbox-guide.md` — `tiny-sandbox`, the separate Python repo with
  the same `Sandbox` / `execute` API
- `tools/tiny-eval-guide.md` — agent evaluation harness
