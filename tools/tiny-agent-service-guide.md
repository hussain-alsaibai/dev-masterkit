# tiny-agent-service — Production Agent Service from tiny-* Components

**Repo:** github.com/hussain-alsaibai/tiny-agent-service
**Install:** python tiny_agent_service.py serve --port 8080
**Last verified:** 2026-08-14

REST API + MCP server assembled from tiny-*, stdlib-only. Handles task submission, budget enforcement, rate limiting, crash recovery. Start with: python tiny_agent_service.py serve --port 8080 --budget 50.0 --model gpt-4o-mini
