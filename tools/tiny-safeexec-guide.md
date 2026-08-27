# tiny-safeexec — Safe Python Code Execution via Subprocess Isolation

**Source:** [hussain-alsaibai/tiny-safeexec](https://github.com/hussain-alsaibai/tiny-safeexec)
**License:** MIT | **Language:** Python 3.8+ | **Last verified:** 2026-08-27

## When to use

- Running untrusted Python code in agent/tool contexts
- Safer alternative to `eval()` or `exec()` for dynamic code execution
- Sandboxed code execution where you need stronger isolation than AST transformation alone

## What it does

Safe Python code execution for AI agents via subprocess isolation. Spawns a child Python process with restricted environment, capturing stdout/stderr and enforcing resource limits.

## Quick start

```python
from tiny_safeexec import safe_exec

result = safe_exec(
    code="print(sum(range(100)))",
    timeout=5,
    memory_mb=64
)
print(result.stdout)   # "4950\n"
print(result.returncode) # 0
```

## Key features

- Subprocess-based isolation (stronger than AST alone)
- Timeout and memory limits via `resource` module
- Captures stdout, stderr, return value
- Blocks network, filesystem, and dangerous imports
- Zero dependencies beyond stdlib

## Security model

Subprocess isolation via `subprocess.run()` with restricted environment variables and resource limits. Complementary to `tiny-sandbox`'s AST approach — use both for defense in depth.

## Ecosystem context

Part of the **tiny-*** zero-dependency Python ecosystem focused on AI agent infrastructure. Related: `tiny-sandbox` (AST-based), `tiny-eval` (agent evaluation), `tiny-checkpoint` (crash recovery).

## Last Verified
2026-08-27
