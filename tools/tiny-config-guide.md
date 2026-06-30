# tiny-config — Zero-Dependency Config Loader

## Repo
https://github.com/hussain-alsaibai/tiny-config

## One-liner
JSON / YAML (subset) / INI / .env / CLI flags, layered: defaults < file < env < CLI.

## Install
```bash
# Zero deps — just copy or pip install
pip install tiny-config
```

## Layered Precedence (low → high)
1. Defaults passed to `load_config(defaults={...})`
2. Config file (JSON, YAML subset, INI, .env)
3. Environment variables (`MYAPP_FOO_BAR` → `foo.bar`)
4. CLI flags (`--foo-bar=...`)

Higher-numbered sources override lower-numbered ones.

## Quick Example
```python
from tiny_config import load_config

cfg = load_config(
    defaults={"port": 8000, "debug": False, "db": {"host": "localhost"}},
    files=["config.yaml", ".env"],
    env_prefix="MYAPP_",
    argv=True,
)
print(cfg["port"], cfg["db"]["host"])
```

## What Works
- JSON ✅ full
- YAML ✅ subset (mappings, sequences, scalars, comments, multi-line strings)
- INI ✅ standard `key=value` + sections
- .env ✅ `KEY=value` plus `export` prefix
- CLI flags ✅ `--key=value`, `--key value`, `--flag` (bool)

## Gotchas
- **YAML subset returns tuples.** `_yaml_parse_block` returns `(value, pos)`.
  Callers must unpack: `parsed, _ = _yaml_parse_block(...)`. Otherwise
  `isinstance(parsed, dict)` is always False → `ValueError`.
- **Env var mapping:** nested keys via `__` separator: `MYAPP_DB__HOST` → `db.host`
- **CLI overrides win:** even if `--port=9000` is passed, env vars are
  shadowed (this is by design — explicit > implicit).

## Benchmarks
- File load: ~35 µs (faster than `python-decouple`, comparable to pydantic-settings
  on warm cache)
- Cold start: < 5 ms

## Tests
15/15 passing.

## Last Verified: 2026-06-30