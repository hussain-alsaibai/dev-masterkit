# tiny-secret Guide

## Repo
https://github.com/hussain-alsaibai/tiny-secret

## What It Does

Zero-dependency secret loading with pluggable sources, value-hiding `Secret`
objects, and a redacting log formatter. One file, no setup.

## Last Verified
2026-10-23

## API Correction (2026-10-23)

The previous version of this guide documented `from tiny_secret import secret,
RedactingFormatter`. **There is no module-level `secret()` function.** Verified
against upstream `tiny_secret.py`:

```
__all__ = ['Secret', 'SecretError', 'SecretNotFound', 'SecretAccessDenied',
           'Source', 'EnvSource', 'FileSource', 'LiteralSource', 'DictSource',
           'KeyringSource', 'VaultSource', 'AWSSource', 'CompositeSource',
           'CachingSource']
```

`RedactingFormatter` **is** present (it is the log formatter), but it is not in
`__all__` — import it explicitly. The value-hiding wrapper is the **`Secret`**
class, and each backend is a `Source` subclass.

## Quick Start

```python
from tiny_secret import Secret, EnvSource, CompositeSource

src = CompositeSource([EnvSource(), FileSource("/etc/app/secrets")])
secret = Secret("DATABASE_URL", source=src)
print(secret.value())   # reveals on demand
print(secret)           # redacted repr
```

Sources available: `EnvSource`, `FileSource`, `LiteralSource`, `DictSource`,
`KeyringSource`, `VaultSource`, `AWSSource`, `CompositeSource`, `CachingSource`.

## When to Use

- Loading credentials without the secret appearing in logs, tracebacks, or
  `repr()` output
- Swapping secret backends (env -> file -> vault) without changing call sites
- Agent and cron workloads where secrets must never be echoed

## Related

- `tools/tiny-secret-mask-guide.md` — redaction of secrets that are already in
  strings/logs (a different concern from *loading* them)
