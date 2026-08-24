# tiny-cost — Token Cost Tracking & Budget Enforcement for Python AI Agents

**Repo:** github.com/hussain-alsaibai/tiny-cost
**Install:** `pip install tiny-cost` or copy `tiny_cost.py`
**Last verified:** 2026-08-22

Zero-dependency Python cost tracker for LLM API calls. Tracks spend across providers, enforces USD/token limits, and circuit-breaks on overspend.

## Key Features

- Built-in pricing for OpenAI, Anthropic, Google, Groq, Llama
- `BudgetExceeded` + `CircuitBroken` exceptions
- Thread-safe, atomic JSON persistence
- `CostTracker` + `CircuitBreaker` classes
- ~500 LOC, stdlib only, MIT
