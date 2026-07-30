# Silent Failure Detection — Monitoring Design Patterns

**Created:** 2026-07-30
**Last verified:** 2026-07-30
**Author:** OpenClaw / hussain-alsaibai
**Source:** Real 17-day infrastructure outage caught by coincidence

---

## The Problem

A monitoring system can report "healthy" while the service has been dead for weeks.
This happens when the system tracks *when it last checked* instead of *what it checked*.

## Core Anti-Patterns

### ❌ State-File Lies
```python
# BAD: Assumes last_check timestamp means "still working"
last_check = state.get("webhook_last_check")
if last_check and time.time() - last_check < 86400:
    status = "OK"  # LIES if nothing wrote to state in 17 days
```

### ❌ Passive Health Checks
```python
# BAD: Only runs when manually triggered
def health_check():
    check_webhook()  # On-demand only — silent failures go undetected
```

### ❌ External Services Without Probes
```python
# BAD: Assumes DNS + process = working endpoint
if dns_resolves("webhook.alsaibai.cloud") and cloudflared.running():
    status = "OK"  # LIES if tunnel is registered but connections fail
```

## Correct Patterns

### ✅ Active Liveness Probes
```python
# GOOD: Actually hit the endpoint, update state after verification
def health_monitor():
    state["webhook_last_check"] = time.time()
    state["webhook_healthy"] = check_webhook()  # Real HTTP probe
    write_state(state)  # Always write after checking
```

### ✅ Separate Check Time from Health State
```python
# GOOD: Track both when checked AND what the result was
state = {
    "last_check_at": timestamp,      # When we looked
    "last_check_result": "ok|error", # What we found
    "consecutive_failures": 0,       # How many bad checks in a row
}
```

### ✅ External Endpoint Probes (Not Just Process Checks)
```bash
# GOOD: Actually make the HTTP call, not just check DNS
curl -f -m 5 https://webhook.alsaibai.cloud/falconeye-meet \
  -H "Content-Type: application/json" \
  -d '{"probe": true}' \
  && echo "UP" || echo "DOWN"
```

### ✅ Process Monitoring + Endpoint Probing
```python
# GOOD: Two-layer check
def is_service_healthy():
    process_ok = is_process_running("cloudflared")
    endpoint_ok = probe_endpoint("https://webhook.alsaibai.cloud/health")
    return process_ok and endpoint_ok  # Both must pass
```

## Design Rules

1. **Never trust a "last checked" timestamp as proof of health.** If nothing wrote to the state file recently, the service could be dead.
2. **Heartbeat-state.json lies unless actively updated.** A cron job must write to it on every run, not just on startup.
3. **External-facing services need active probes, not on-demand checks.** DNS resolves + process running ≠ endpoint responding.
4. **Alert on absence of state updates, not just errors.** If `last_check_at` is stale, that's a failure.
5. **17-day silent failures are unacceptable for critical infra.** Set up liveness probes, not just health checks.

## Alerting Logic

```python
# Good alert conditions
should_alert = (
    state.get("consecutive_failures", 0) >= 3  # 3 consecutive failures
    or (time.time() - state.get("last_check_at", 0)) > 7200  # No check in 2 hours
    or state.get("last_check_result") == "error"  # Any error
)
```

## The 2026-07-30 Case

- Webhook: declared "active" but `lastChecks.webhook` in heartbeat-state.json was never updated after 2026-07-13
- Cloudflared: process check passed but tunnel connections failed silently for 17 days
- Result: External webhook URL broken for 17 days, zero alerts fired

**Fix pattern:** Update heartbeat-state.json on every health-monitor run, then check staleness as an alert condition.

---

**Tags:** `#monitoring` `#infrastructure` `#alerting` `#reliability` `#devops`
