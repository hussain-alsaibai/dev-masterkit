# Health Monitor Skill

> **Last verified:** 2026-07-27 (daily cron job active since Feb 2026)

Automated system health monitoring with FalconEye integration.

## Features
- Periodic health checks (disk, memory, services)
- Automatic alerts via FalconEye API when issues detected
- Auto-recovery attempts for failed services
- Detailed logging
- Configurable thresholds

## Usage

### One-time check
```bash
node health-monitor.js --once
```

### Continuous monitoring (runs every 5 minutes)
```bash
node health-monitor.js
```

### As a module
```javascript
const { healthCheck } = require('./health-monitor');

// Run check
const health = await healthCheck();
console.log(health.disk.usage);  // Disk usage %
console.log(health.memory.usage); // Memory usage %
```

## Monitored Components

| Component | Check | Threshold |
|-----------|-------|-----------|
| Disk Usage | `df -h /` | Alert at >90% |
| Memory Usage | `free` | Alert at >90% |
| Webhook Server | HTTP HEAD :63360 | Restart if down |
| Gateway | HTTP HEAD :63362 | Report if down |

## Alert Format

Alerts sent to FalconEye Meet as agent messages:
```
🚨 Health Alert:
Disk: 95% used (2G free)
Memory: 92% used (700MB/800MB)
Webhook Server: Connection refused
```

## Auto-Recovery Actions

When services are detected as down:
1. Webhook Server: Automatically restart process
2. Other services: Report only (manual intervention needed)

## Logs

Logs written to `/tmp/health-monitor.log`:
```
[2026-02-09T10:30:00Z] [INFO] Starting health check...
[2026-02-09T10:30:00Z] [CHECK] Disk: 15% used (82G free)
[2026-02-09T10:30:00Z] [CHECK] Memory: 12% used (1GB/8GB)
[2026-02-09T10:30:00Z] [INFO] All systems healthy
```

## Configuration

Edit the `CONFIG` object at the top of the file:
```javascript
const CONFIG = {
  checkInterval: 5 * 60 * 1000,  // 5 minutes
  diskThreshold: 90,              // Alert at >90%
  memoryThreshold: 90,            // Alert at >90%
  falconeyeApiKey: 'your-key-here'
};
```
