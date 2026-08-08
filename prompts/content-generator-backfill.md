# Content Generator Backfill Recovery

## Problem

The daily content generator (`scripts/daily-content-generator.js`) can silently fail for extended periods, leaving gaps in the content buffer. When discovered, there's no way to retroactively fill the gap without manual intervention.

## Detection

Check the last entry in `content/daily/`:
```bash
ls content/daily/ | sort | tail -1
# Expected: today's date in YYYY-MM-DD format


```

If the last entry is more than 1 day old, a gap exists.

## Backfill Procedure

```bash
# Calculate days between last entry and today
LAST=$(ls content/daily/ | sort | tail -1)
TODAY=$(date +%Y-%m-%d)
DAYS=$(python3 -c "from datetime import datetime; print((datetime.strptime('$TODAY','%Y-%m-%d') - datetime.strptime('$LAST','%Y-%m-%d')).days)")

# Run the generator for each missing day
for i in $(seq 1 $DAYS); do
  date -d "$LAST + $i days" +%Y-%m-%d
  # Pass the date to the generator
  node scripts/daily-content-generator.js "$(date -d "$LAST + $i days" +%Y-%m-%d)"
done
```

## Prevention

Add a cron job that fires daily and verifies the generator ran:
```
0 0 * * * node /path/to/scripts/daily-content-generator.js
```

Add a self-check: if the last content file is > 25 hours old, send an alert and skip the next run (don't double-generate).

## Key Lesson

Never assume a scheduled task ran successfully. Verify output state, not just cron firing.

## Last Verified

2026-08-08 — Backfilled 76-day gap (May 25 → Aug 7) in content buffer
