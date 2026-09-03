# tiny-scheduler — Zero-Dependency Cron + Interval + Async Scheduler

## Repo
https://github.com/hussain-alsaibai/tiny-scheduler

## One-liner
Cron expressions, interval timers, one-shot timers, and async support — all in one stdlib-only file.

## Install
```bash
pip install tiny-scheduler
```
Or drop `tiny_scheduler.py` into your project — it's a single file.

## Quick Example

```python
from tiny_scheduler import Scheduler

sched = Scheduler(jitter_ms=200)

def backup():
    print("running backup...")

sched.add_cron(backup, "0 2 * * *", name="daily-backup")  # 2 AM daily
sched.add_interval(check_health, seconds=30, name="health-check")
sched.add_once(send_welcome, delay=5, name="welcome")
sched.start()
```

## Cron Syntax (5-field, same as `tiny-cron`)
```
*  *  *  *  *
│  │  │  │  └── day of week (0-6, mon-sun)
│  │  │  └──── month (1-12, jan-dec)
│  │  └─────── day of month (1-31)
│  └────────── hour (0-23)
└───────────── minute (0-59)
```

### Extensions Supported
| Token | Meaning | Example |
|-------|---------|---------|
| `L`   | Last day of month | `0 0 L * *` → last day at 00:00 |
| `W`   | Nearest weekday | `0 9 15W * *` → 9 AM on weekday nearest the 15th |
| `#`   | Nth weekday of month | `0 9 * * 1#2` → 2nd Monday at 9 AM |
| `@hourly/daily/weekly/monthly` | Aliases | `@daily`, `@weekly`, etc. |

## Core Features

| Feature | How |
|---------|-----|
| Cron scheduling | `add_cron(fn, "*/5 * * * *")` |
| Interval timers | `add_interval(fn, seconds=30)` or `minutes=5`, `hours=1` |
| One-shot timers | `add_once(fn, delay=5)` — fires once then auto-removes |
| Async support | Auto-detects coroutines, runs via `asyncio.run()` |
| Timezone-aware | Naive datetimes → UTC; tzinfo objects respected |
| Anti-overlap | `anti_overlap=True` skips a run if previous is in-flight |
| Max runs / TTL | `max_runs=N` or `until=datetime(...)` |
| Jitter | `jitter_ms=N` prevents thundering-herd |
| Thread pool | Scheduler ticks on background thread, workers in pool |
| Decorator style | `@scheduled("*/5 * * * *")` for declarative registration |
| Graceful shutdown | `stop()` waits for in-flight jobs; context-manager friendly |
| Job metadata | `name`, `args`, `kwargs`, `tags` on every job |

## Async Example

```python
async def fetch_status():
    async with aiohttp.ClientSession() as s:
        r = await s.get("https://api.example.com/status")
        return await r.json()

sched.add_interval(fetch_status, seconds=60, name="status")
```

## Testing
- **57/57 tests passing**
- 0 dependencies, 0 transitive deps
- 1 file, ~691 LOC
- MIT licensed

## tiny-cron vs tiny-scheduler

| Feature | tiny-cron | tiny-scheduler |
|---------|-----------|---------------|
| Cron parsing | ✅ | ✅ |
| Interval timers | ❌ | ✅ |
| One-shot timers | ❌ | ✅ |
| Async functions | ❌ | ✅ |
| Thread pool execution | ❌ | ✅ |
| Decorator API | ✅ | ✅ |
| File size | ~500 LOC | ~691 LOC |

**Use tiny-cron** when you only need cron expression parsing and next/previous date math.
**Use tiny-scheduler** when you need a full in-process scheduler with timers, async, and worker pools.

## Gotcha — Naive Datetimes are UTC
```python
# Naive datetime → treated as UTC
sched.add_cron(fn, "0 9 * * *")  # 9 AM UTC

# Timezone-aware → respected
from datetime import timezone, datetime
sched.add_cron(fn, "0 9 * * *", start_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
```

Last verified: 2026-09-03
