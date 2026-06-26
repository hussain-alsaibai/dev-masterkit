# Plugin Installation Guide

## What This Tool Does

Manages OpenClaw plugin installation across 80+ plugins. Handles batch installs,
gateway restarts, and verification. Used to add messaging, productivity, AI
provider, and utility plugins.

## Installation

Already installed as part of OpenClaw. No separate install needed.

## Usage

### Install Plugin

```bash
gateway action=config.patch path=plugins.entries.<name>.enabled=true
```

### Install Multiple Plugins (Batch)

Install in groups to avoid config conflicts:

```bash
# Messaging plugins
gateway action=config.patch \
  raw='{"plugins.entries.discord.enabled":true,"plugins.entries.signal.enabled":true,"plugins.entries.nostr.enabled":true}'

# Productivity plugins  
gateway action=config.patch \
  raw='{"plugins.entries.diffs.enabled":true,"plugins.entries.perplexity.enabled":true}'

# AI provider plugins
gateway action=config.patch \
  raw='{"plugins.entries.google.enabled":true,"plugins.entries.openai.enabled":true}'
```

### Restart Gateway After Install

```bash
gateway action=restart
```

### Verify Plugin Status

```bash
gateway action=config.get path=plugins.entries
```

## Common Plugins

### Messaging
| Plugin | Status | Use For |
|--------|--------|---------|
| discord | Installed | Servers, DMs |
| signal | Installed | E2E encrypted |
| nostr | Installed | Decentralized |
| googlechat | Installed | Spaces, DMs |
| line | Installed | Asia-Pacific |

### Productivity
| Plugin | Status | Use For |
|--------|--------|---------|
| diffs | Installed | Read-only diff viewer |
| perplexity | Active | AI web search |
| firecrawl | Active | Web scraping |
| canvas | Active | HTML rendering |

### AI Providers
| Provider | Plugin | Status |
|----------|--------|--------|
| Synthetic | synthetic | Active (GLM, Kimi, Qwen, etc.) |
| Google | google | Active (Gemini) |
| OpenAI | openai | Active (GPT) |
| xAI | xai | Active (Grok) |
| DeepSeek | deepseek | Active |
| Qwen | qwen | Active |

## Troubleshooting

### Plugin Install Fails
- Install sequentially, not in parallel
- Restart gateway after each batch
- Check `gateway action=config.get` for error state

### Plugin Not Working After Install
- Verify gateway restarted successfully
- Check plugin dependencies (some need API keys)
- Look for config conflicts in logs

## Last Verified: 2026-06-26
