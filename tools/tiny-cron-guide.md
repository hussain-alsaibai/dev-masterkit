# tiny-cron — Zero-Dependency Cron-Style Scheduler

## Repo
https://github.com/hussain-alsaibai/tiny-cron

## One-liner
Standard cron parsing + scheduler in one file. Handles 5-field syntax, `@hourly` / `@daily` / `@weekly` aliases, and three extensions (`L` / `W` / `#`). Decorator-friendly.

## Install
```bash
pip install tiny-cron
```

## Quick Example

```python
from tiny_cron import Scheduler, every

sched = Scheduler(jitter_ms=200)

@every(sched, "*/5 * * * *")      # every 5 minutes
def fetch_metrics():
    ...

@every(sched, "0 9 * * 1-5")      # 9 AM, weekdays only
def morning_report():
    ...

sched.start()
```

## Cron syntax (supported)

```
*          any value
*/n        every n
n,m        list
n-m        range
n-m/k      range with step
```

### Aliases
```
@hourly   @daily    @weekly    @monthly    @yearly    @reboot
```

### Extensions
| Token | Meaning | Example |
|-------|---------|---------|
| `L`   | last day of month | `0 0 L * *` → last day at 00:00 |
| `W`   | nearest weekday to that day-of-month | `0 9 15W * *` → 9 AM on weekday nearest the 15th |
| `#`   | Nth weekday of the month | `0 9 * * 1#2` → 2nd Monday at 9 AM |

## Scheduler features

| Feature | How |
|---------|-----|
| Anti-overlap | `Scheduler(anti_overlap=True)` skips a run if the previous one is still in flight |
| Jitter | `jitter_ms=N` randomizes each fire by up to N ms |
| Run limits | `max_runs=N` or `until=datetime(...)` auto-stops the scheduler |
| Window | `start_time=` / `end_time=` only fire inside the window |
| Decoration | `@tiny_cron.every(sched, "0 * * * *")` |

## Pure date math (no scheduler needed)

```python
from tiny_cron import parse, next, previous, iter_between

nxt = next(parse("*/15 * * * *"), after=datetime.now(UTC))
window = list(iter_between(parse("0 9 * * *"),
                           start=yesterday, end=tomorrow))
```

## Testing

- **48/48 tests passing**
- 0 dependencies, 0 transitive deps
- 1 file

## Gotcha — multi-digit `dom`

The `dom` field accepts `1W`, `15W`, `31W` (weekday-nearest to day-of-month).
A regex like `^([0-6])W$` only matches single digits and silently drops `15W`.

```python
# Wrong
DOM_W_RE = re.compile(r"^([0-6])W$")

# Right
DOM_W_RE = re.compile(r"^(\d+)W$")   # allows multi-digit
```

Combined with bounded month validation in `_validate_dom` so `32W` is rejected
before reaching the regex.

Last verified: 2026-07-03
