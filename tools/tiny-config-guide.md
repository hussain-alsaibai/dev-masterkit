# tiny-config Guide

## Repo
https://github.com/hussain-alsaibai/tiny-config

## What It Does

Zero-dependency layered configuration loader for Python. One file, no setup.
JSON, YAML, INI, `.env`, and env-var sources with dotted-key access, merging,
and profile support.

## Last Verified
2026-11-02 - **54 tests passing** (measured by run). Version 0.4.0. The repo
now has a CI workflow and a version badge.

## API Surface (verified by import, 2026-11-02)

```
__all__ = ['load', 'load_file', 'get', 'set', 'merge', 'from_env', 'validate',
           'get_secret', 'load_profile', 'ConfigError', 'get_int', 'get_str',
           'get_bool', 'get_float', 'get_list', 'snapshot', 'ConfigWatcher',
           'to_dict', 'to_json', 'to_json_schema', 'mask_secrets',
           'FrozenConfig']
```

**There is no `load_config`** (the earlier correction on this page still
stands). The surface has grown since 2026-10-23: typed getters
(`get_int`, `get_str`, `get_bool`, `get_float`, `get_list`), a `snapshot`
helper, a `ConfigWatcher`, `to_json_schema`, `mask_secrets`, and an immutable
`FrozenConfig`.

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

## Quick Start

```python
from tiny_config import load, get

cfg = load("config.yaml", env_prefix="APP_")
print(get(cfg, "server.port"))
```

## Key Features

- JSON, YAML (built-in mini-parser), INI, `.env` file formats
- `from_env` overlay with a prefix
- `merge` for layering config sources
- `validate` with a schema
- `get_secret` for values that must not be logged
- `load_profile` for per-environment overrides
- `ConfigError` for typed failures

## When to Use

- A service that needs layered config (file + env + profile) without PyYAML
  or pydantic-settings as a dependency
- Reading config in a CLI or cron job where the working directory varies

## Related

- `tools/tiny-secret-guide.md` — secret loading with value-hiding objects
