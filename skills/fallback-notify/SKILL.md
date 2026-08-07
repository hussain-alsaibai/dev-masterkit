# Fallback Notification System

Multi-channel notification system for when primary FalconEye webhook fails.

## Purpose

Ensures critical alerts always reach you, even if:
- FalconEye API is down
- Webhook server is not responding
- Network issues occur

## Fallback Chain

1. **Primary:** FalconEye API (`/agent/send`)
2. **Fallback 1:** Telegram direct message (if bot token configured)
3. **Fallback 2:** Local alert file (`/tmp/critical-alerts.log`)

## Usage

### Simple notification
```javascript
const { notify } = require('./fallback-notify');

await notify('System backup completed');
// Returns: { success: true, channel: 'falconeye' }
```

### Critical alert (never fails silently)
```javascript
const { criticalAlert } = require('./fallback-notify');

await criticalAlert('🚨 Disk space critical: 95% used!');
// Tries all channels, logs to console if all fail
```

### Webhook health monitoring
```bash
# Run continuous monitoring
node fallback-notify.js --monitor

# Or as a module
const { monitorWebhook } = require('./fallback-notify');
monitorWebhook(); // Checks webhook and alerts if down
setInterval(monitorWebhook, 60000); // Check every minute
```

## Configuration

Edit CONFIG at top of file:
```javascript
const CONFIG = {
  falconeyeWebhook: 'http://webhook.alsaibai.cloud:64850/falconeye-meet',
  telegramBotToken: process.env.TELEGRAM_BOT_TOKEN, // Optional
  telegramChatId: '1813960255',
  alertFile: '/tmp/critical-alerts.log'
};
```

## Features

- **Auto-restart:** Attempts to restart webhook server if down
- **Escalation:** Critical alerts try all channels
- **Logging:** All attempts logged to console
- **Non-blocking:** Falls through quickly if channel unavailable

## Example: Integration with Health Monitor

```javascript
const { healthCheck } = require('../health-monitor/health-monitor');
const { criticalAlert } = require('../fallback-notify/fallback-notify');

async function monitoredHealthCheck() {
  const health = await healthCheck();
  
  if (health.disk.status === 'warning') {
    await criticalAlert(`Disk critical: ${health.disk.usage}% used`);
  }
}
```
