# Browser Automation

Automate web browser interactions using natural language via CLI commands or the OpenClaw `browser` tool.

## Trigger

Use when the user asks to:
- "Browse this website"
- "Navigate to [URL]"
- "Fill out this form"
- "Take a screenshot"
- "Click the [button]"
- "Extract data from [page]"
- "Interact with [web app]"

## Description

Automates browser interactions for data extraction, form filling, navigation, and screenshots. Supports both Stagehand CLI and OpenClaw's native browser tool.

## Modes

### Mode 1: OpenClaw Browser Tool (Recommended)
```json
{
  "action": "navigate",
  "url": "https://example.com"
}
```

### Mode 2: Stagehand CLI (Local/Remote)
```bash
browser navigate https://example.com
browser act "click the Sign In button"
browser extract "get the page title"
browser screenshot
browser close
```

## OpenClaw Browser Tool Reference

```json
// Navigate
{ "action": "navigate", "url": "https://example.com" }

// Click element
{ "action": "act", "kind": "click", "ref": "e12" }

// Type text
{ "action": "act", "kind": "type", "ref": "e34", "text": "hello" }

// Fill form fields
{ "action": "act", "kind": "fill", "fields": [{"ref": "e34", "text": "value"}] }

// Take screenshot
{ "action": "screenshot", "fullPage": true }

// Get page snapshot (element refs)
{ "action": "snapshot" }

// Evaluate JS
{ "action": "act", "kind": "evaluate", "fn": "document.title" }
```

## Best Practices

1. **Always navigate first** before interacting
2. **Take snapshots** to get element references
3. **Use refs from snapshots** for stable interaction
4. **Be specific** in action descriptions
5. **Close browser** when done

## Environment Selection (Stagehand)

| Feature | Local | Browserbase |
|---------|-------|-------------|
| Speed | Faster | Slightly slower |
| Setup | Chrome required | API key required |
| Stealth mode | No | Yes |
| Proxy/CAPTCHA | No | Yes |
| Best for | Development | Production/scraping |

## Troubleshooting

- **Chrome not found**: Install Chrome or use Browserbase mode
- **Action fails**: Use snapshot to discover available elements
- **Browserbase fails**: Verify API key and project ID are set
- **Stale refs**: Re-snapshot after page changes

## Last Verified: 2026-06-28
