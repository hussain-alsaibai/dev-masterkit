# tiny-config Guide

## Repo
https://github.com/hussain-alsaibai/tiny-config

## What It Does

Zero-dependency layered configuration loader for Python. One file, no setup.
JSON, YAML, INI, `.env`, and env-var sources with dotted-key access, merging,
and profile support.

## Last Verified
2026-11-27 - **137 passed / 14 skipped**, version **0.4.4** (`980cfaa`),
measured by run with `/home/node/venvs/mx-3.12/bin/python -m pytest -q` against
a fresh clone. CI present; version badge current.

> Earlier rows on this page (0.4.0, 54 tests) are historical. The guide was
> re-verified against 0.4.4 on 2026-11-27 — the API list below is from the
> live `__all__` at that revision, not from memory.

## API Surface (verified by import, 2026-11-27, v0.4.4)

```
__all__ = ['ConfigError', 'ConfigWatcher', 'FrozenConfig', 'from_env', 'get',
           'get_bool', 'get_float', 'get_int', 'get_list', 'get_secret',
           'get_str', 'load', 'load_file', 'load_profile', 'mask_secrets',
           'merge', 'set', 'snapshot', 'to_dict', 'to_json', 'to_json_schema',
           'validate']
```

22 exported names, read from `tiny_config.__all__` at 0.4.4. **There is no
`load_config`** (the earlier correction on this page still stands). The surface
grew past the 2026-10-23 list: typed getters (`get_int`, `get_str`,
`get_bool`, `get_float`, `get_list`), `snapshot`, `ConfigWatcher`,
`to_json_schema`, `mask_secrets`, and an immutable `FrozenConfig`.

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_config import
load_config`. **There is no `load_config` function.** Verified against upstream
`tiny_config.py`:

```
__all__ = ['load', 'load_file', 'get', 'set', 'merge', 'from_env', 'validate',
           'get_secret', 'load_profile', 'ConfigError']
```

The entry point is **`load`** (or **`load_file`** for a single file). The
`get` / `set` helpers operate on dotted paths.

## Quick Start (executed 2026-11-27, v0.4.4)

`config.yaml`:

```yaml
server:
  port: 8080
```

```python
import os
from tiny_config import load, get

os.environ["APP_SERVER__PORT"] = "9090"   # env overrides the file
cfg = load("config.yaml", env_prefix="APP_")
print(cfg)                 # {'server': {'port': 9090}}
print(get(cfg, "server.port"))   # 9090  (an int, not "9090")
```

Two things the signature does not advertise:

- **`load()` parses `sys.argv` by default** (`cli=True`). Args become config
  keys, so a script called as `script.py --help` may behave unexpectedly. Pass
  `cli=False` in a library or a cron job.
- `env_prefix` is a keyword-only argument **on `load`**, not just `from_env`.
  `load("config.yaml", "APP_")` is a `TypeError`; the name is required.

## Key Features

- JSON, YAML (built-in mini-parser), INI, `.env` file formats
- `from_env` overlay with a prefix matched as a **boundary** (0.4.4):
  `MYAPP` does not read `MYAPP2_*`, `MYAPP_` and `MYAPP` are the same
  namespace, a case-only collision raises `ConfigError` naming both names,
  and a variable naming no key (`MYAPP_DB__`, `MYAPP__`) raises instead of
  leaving an unreadable value behind
- `"1"`/`"0"` are **numbers**, not booleans (0.4.4); the words
  `true/false/yes/no/on/off` are still booleans; `get_bool`/`get_int` accept
  either spelling
- `merge` for layering config sources
- `validate` with a schema; `to_json_schema` round-trips with `tiny-validator`
- `get_secret` for values that must not be logged; `mask_secrets`
- `load_profile` for per-environment overrides
- `ConfigError` for typed failures

## When to Use

- A service that needs layered config (file + env + profile) without PyYAML
  or pydantic-settings as a dependency
- Reading config in a CLI or cron job where the working directory varies

## Related

- `tools/tiny-secret-guide.md` — secret loading with value-hiding objects
- `prompts/a-prefix-is-a-boundary-not-a-prefix.md` — the 0.4.4 env rules, with
  the five measured scenarios that were red on 0.4.3
- `tools/probing-a-boundary-in-five-lines.md` — the probe table to reuse
