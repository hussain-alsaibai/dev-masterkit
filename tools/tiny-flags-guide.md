# tiny-flags — Zero-Dependency Feature Flags

## Repo
https://github.com/hussain-alsaibai/tiny-flags

## One-liner
Three flag types (bool / percentage / multivariate), 11 rule operators, deterministic SHA-256 bucketing, pluggable sources, decorator-friendly. LaunchDarkly-in-one-file.

## Install
```bash
pip install tiny-flags
```

## Quick Example

```python
from tiny_flags import Client, gate, variant, FileSource

client = Client(source=FileSource("flags.json", watch=True))

@gate(client, "checkout_v2")
def checkout(user_id):
    return legacy(user_id)

@vant(client, "checkout_button_color", default="green")
def button_color(user_id) -> str:
    return "red" if high_risk(user_id) else "green"
```

## Flag types

| Type | Use | Returns |
|------|-----|---------|
| `BoolFlag`     | on/off rollout             | `True` / `False` |
| `PercentageFlag` | percent rollout (0–100) | `True` / `False` |
| `MultivariateFlag` | pick one of N values   | `str` (or any JSON type) |

## 11 rule operators

```
eq            ne
lt le gt ge
in_           not_in
contains      starts_with      ends_with
matches (regex)
between (range on numbers)
truthy
```

## Deterministic bucketing

Every user attribute hash is `sha256(user_id + flag_name) % 10000`.
**Same user → same bucket → same decision** across processes, restarts, and replicas.

```python
# Internally:
bucket = int(hashlib.sha256(f"{user_id}|{flag.name}".encode()).hexdigest()[:8], 16) % 10000
in_pct = bucket < (flag.percentage * 100)
```

This is the property LaunchDarkly, Unleash, and Statsig all require.
Without it, library reuse is impossible (and ops gets surprise flips on restart).

## Sources (pluggable)

| Source | Use |
|--------|-----|
| `DictSource({"flag": value})`           | Tests |
| `EnvSource()`                           | `FLAGS_*` env vars |
| `FileSource("flags.json", watch=True)`  | Hot-reload from disk |
| `CompositeSource([EnvSource(), FileSource()])` | Layered (later overrides earlier) |

Auto-refresh:
```python
client = Client(source=FileSource("flags.json", watch=True), refresh_interval_sec=30)
# OR
client.refresh()  # manual
```

## Decorators

```python
@gate(client, "new_recommender")
def recommend(user_id, ctx):
    return new_recommender(user_id, ctx) if client.bool("new_recommender", user_id) \
           else legacy(user_id, ctx)

@vant(client, "tier", default="free")
def pricing_tier(user_id) -> str:
    return client.multivariate("tier", user_id, default="free")
```

`@gate` short-circuits the wrapped call when the flag is off and returns the
default; `@variant` returns the bucketed value.

## Testing

- **59/59 tests passing**
- 0 dependencies, 0 transitive deps
- 1 file

## Gotcha — bucketing requires stable hashing

Do NOT use Python's built-in `hash()` for stickiness. `hash()` is salted per
process (PYTHONHASHSEED). Always use SHA-256 on `(user_id, flag_name)`.

Last verified: 2026-07-03
