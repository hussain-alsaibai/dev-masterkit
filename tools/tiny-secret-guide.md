# tiny-secret — Zero-Dependency Secret Management

## Repo
https://github.com/hussain-alsaibai/tiny-secret

## One-liner
7 sources, value-hiding `Secret` class, stdlib `RedactingFormatter` for log masking.
Env, file, dict, literal, keyring, vault, AWS Secrets Manager (SigV4 inline).

## Install
```bash
pip install tiny-secret
```

## Quick Example

```python
from tiny_secret import secret, RedactingFormatter
import logging

# Load from env
api_key = secret("API_KEY")               # -> Secret("sk_live_...") (value hidden)
api_key.value                             # -> "sk_live_..." (explicit only)
print(repr(api_key))                      # -> Secret("***")  ← value masked

# Chain sources
db_pw = secret("DB_PASSWORD",
               sources=["vault", "keyring", "env", "file:/run/secrets/db"])

# Auto-mask logs
handler = logging.StreamHandler()
handler.setFormatter(RedactingFormatter("%(asctime)s %(message)s"))
logger.addHandler(handler)
logger.info("connected with password=hunter2")   # -> "...with password=***"
```

## Sources

| Source | Syntax | Notes |
|--------|--------|-------|
| env | `env` or implicit | `$NAME` lookup |
| file | `file:/path` | First line of file |
| dict | `dict:{...}` | Inline `{...}` JSON-ish |
| literal | `literal:raw_value` | For tests / hard-coding (avoid) |
| keyring | `keyring` | OS keyring (macOS/Windows/Linux secret-tool) |
| vault | `vault:path@addr` | KV-v2 HTTP API, X-Vault-Token |
| aws | `aws:SecretId@region` | Secrets Manager via inline SigV4 |

## `RedactingFormatter` patterns

Default regex masks `password=…`, `api_key=…`, `token=…`, `secret=…`, `bearer …`.
Add custom patterns:

```python
fmt = RedactingFormatter("%(message)s", extra_patterns=[r"client_id=\S+"])
```

## Testing

- **56/56 tests passing**
- 694 LOC + 511 test LOC
- 0 dependencies, 0 transitive deps
- Each source, repr/str/format masking, formatter regex coverage

## Gotcha — AWS SigV4 by hand is ~50 LOC

The 4-step HMAC chain in pure stdlib (`hmac` + `hashlib`):

```
k_date    = HMAC("AWS4" + secret, date)
k_region  = HMAC(k_date, region)
k_service = HMAC(k_region, service)
k_signing = HMAC(k_service, "aws4_request")
signature = HMAC(k_signing, string_to_sign).hex()
```

Then build canonical request → string-to-sign → signature header set.
Only valid for **Secrets Manager GetSecretValue**; other AWS services need
different canonical request shapes. Don't try to make this a general AWS SDK —
the surface area is too big.

Last verified: 2026-07-02
