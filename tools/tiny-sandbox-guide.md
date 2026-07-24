# tiny-sandbox Guide

**Repo:** [hussain-alsaibai/tiny-sandbox](https://github.com/hussain-alsaibai/tiny-sandbox)  
**Size:** ~1360 LOC | **Deps:** 0 (stdlib-only) | **Last verified:** 2026-07-24

> Tiny secure Python code execution sandbox using AST transformation.

## What it does

Execute untrusted Python code safely with zero external packages. Uses Python's own AST module to parse, analyze, and transform code before execution, blocking dangerous operations at the AST level.

## When to use

- **Plugin systems** that need to run user-supplied Python code
- **AI agents** that generate and execute code snippets
- **Code evaluation** in educational or competitive platforms
- **Safe eval() replacement** — when you need to run arbitrary Python without `eval()`

## Key patterns

```python
from tiny_sandbox import Sandbox, SecurityPolicy

policy = SecurityPolicy(
    allowed_modules=["math", "random"],
    blocked_names={"__import__", "open", "eval", "exec"},
    max_iterations=1000,
    timeout_seconds=5,
)

sandbox = Sandbox(policy)
result = sandbox.run(user_code)
```

## Related

- `tiny-chain` — for LLM-driven code generation that feeds into sandbox
- `tiny-workflow` — for orchestrating multi-step agent tasks that may include code execution
