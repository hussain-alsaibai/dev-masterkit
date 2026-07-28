# tiny-eval — Sandboxed Expression Evaluator

**Repo:** `hussain-alsaibai/tiny-eval`
**Version:** 0.1.0 | **Dep:** Zero (stdlib only) | **License:** MIT
**Last verified:** 2026-07-28

Safely evaluate Python expressions and statements in an isolated namespace with
whitelisted builtins, timeout enforcement, and config interpolation.

## Quick Start

```python
from tiny_eval import eval_expr, Sandbox, interpolate

# Sandboxed math
result = eval_expr("math.sqrt(x**2 + y**2)", {"x": 3, "y": 4})  # 5.0

# Config interpolation (Jinja2-free)
interpolate("Port: {{ port }}", port=8080)  # "Port: 8080"

# Strict mode blocks dangerous access
eval_expr("open('/etc/passwd')", sandbox=Sandbox(strict=True))
# raises EvalError: access denied
```

## Key Features

| Feature | Description |
|---------|-------------|
| Sandboxed defaults | Blocks `open`, `__import__`, `os.system`, etc. |
| Strict mode | Only math + basic types; no imports whatsoever |
| Timeout enforcement | SIGALRM guard prevents infinite loops (Unix) |
| Config interpolation | `${env:VAR}` and `${secret:NAME}` in strings |
| Template helper | `{{variable}}` substitution without Jinja2 |
| JSON Schema import | `from_json_schema()` converts JSON Schema to validators |
| Iteration guard | `max_iterations` stops runaway loops |

## When to Use

- Dynamic config expressions in agent systems
- Sandbox for user-provided formulas/logic
- Config interpolation without Jinja2 dependency
- Safe `eval()` replacement for any untrusted code
- Tool parameter computation in agent frameworks

## See Also

- [tiny-config-guide](./tiny-config-guide.md) — Configuration with schema validation
- [tiny-validator-guide](./tiny-validator.md) — Input validation
