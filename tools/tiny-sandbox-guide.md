# tiny-sandbox — Secure Python Code Execution Sandbox

## Repo
https://github.com/hussain-alsaibai/tiny-sandbox

## What It Does

Tiny secure Python code execution sandbox using AST transformation. Zero dependencies. Whitelists safe operations, blocks dangerous ones.

## When to Use

- Running untrusted user code in agents/bots
- Processing Python snippets in a code-execution tool
- Isolating eval/exec from the host environment

## Key Features

- AST-based transformation (no regex blacklists)
- Blocks: `import`, `open`, `os.`, `sys.`, `subprocess`, file I/O, network
- Allows: arithmetic, list/dict operations, builtins (`len`, `range`, etc.)
- Timeout enforcement via signal alarm
- Memory limit via resource setrlimit
- Returns: stdout, return value, execution time

## Quick Start

```python
from tiny_sandbox import run_sandbox

result = run_sandbox(
    code="[x**2 for x in range(10)]",
    timeout=5,
    memory_mb=50
)
print(result.output)    # "[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]"
print(result.elapsed_ms) # execution time
print(result.blocked)    # [] — no blocked operations
```

## Security Notes

- Always set `timeout` and `memory_mb` limits
- Not a full security sandbox — use containers (gVisor, firejail) for untrusted production workloads
- Last verified: 2026-07-23

## Last Verified
2026-07-23
