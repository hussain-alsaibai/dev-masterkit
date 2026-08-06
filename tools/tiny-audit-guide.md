# tiny-audit — Immutable, Tamper-Evident Audit Log

> Zero dependencies. HMAC-SHA256 signed. Append-only. Verifiable.

**Repo:** https://github.com/hussain-alsaibai/tiny-audit
**Install:** `pip install tiny-audit`
**Last verified:** 2026-08-06

---

## What It Does

Every log entry is signed with HMAC-SHA256 and chained via `prev_hash`. Entries can never be deleted or modified — only appended. The chain is verifiable at any point. Great for compliance, agentic workflows, financial systems, and anywhere you need **"this happened and nobody tampered with it"**.

## Quick Start

```python
from tiny_audit import AuditLog, Level

log = AuditLog("/data/audit.log", secret="super-secret-key")

# Log any action
log.log(Level.INFO, "user.login",    {"user_id": 42, "ip": "1.2.3.4"})
log.log(Level.WRITE, "order.placed", {"order_id": "ORD-99", "amount": 150.00})
log.log(Level.READ,  "config.fetch", {"keys": ["api_key", "db_url"]})
log.log(Level.ADMIN, "user.promote", {"user_id": 99, "role": "admin"})

# Verify integrity — raises AuditError if tampered
log.verify()

# Query entries
for entry in log.query(actor="agent-1", limit=100):
    print(entry.action, entry.data)

# Export for compliance
log.export_jsonl("/data/audit-export.jsonl")
```

## Decorator — Auto-Log Function Calls

```python
audit = AuditLog("/data/audit.log", secret="key")

@audit.audit("user.fetch", level=Level.READ, actor_arg=0)
def get_user(user_id: int) -> dict:
    return db.get(user_id)

@audit.audit("order.create", level=Level.WRITE, actor_arg=1)
async def create_order(user_id: int, items: list) -> dict:
    ...
```

## How Integrity Works

Each entry stores a **chain hash** (`prev_hash`) — the hash of the previous entry. The first entry uses `"GENESIS"`. Every entry is also signed with HMAC-SHA256. When you call `verify()`, we walk the entire file and confirm:

1. `prev_hash` chains correctly
2. HMAC signature is valid

If any line is modified or deleted, `verify()` raises `AuditError`.

## When to Use

- Agentic workflow audit trails
- Compliance logging (SOC2, GDPR)
- Financial transaction audit
- Any system where "this happened" must be provable

## Key Methods

| Method | Description |
|--------|-------------|
| `log(level, action, data)` | Append a signed entry |
| `verify()` | Verify entire chain integrity |
| `query(actor=, action=, limit=)` | Query entries |
| `export_jsonl(path)` | Export to JSONL for compliance |
| `export_csv(path)` | Export to CSV |
| `@audit(action, level, actor_arg)` | Decorator for auto-logging |

## Comparison

| Approach | Problem |
|----------|---------|
| `logging` module | Entries can be deleted/modified |
| SQL audit table | DB admin can DELETE |
| CloudWatch / Datadog | Costly, vendor lock-in |
| **tiny-audit** | **Zero deps, verifiable, self-contained** |
