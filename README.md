# Dev-MasterKit

> A comprehensive developer toolkit for AI-assisted repository creation, testing, documentation, security auditing, performance benchmarking, prompt engineering, and infrastructure automation. Zero dependencies. Production-ready.

## Features

- 🏗️ **Repository Scaffolding** — Create zero-dependency Python projects with modern `pyproject.toml` packaging
- 🧪 **Test Automation** — Generate comprehensive unittest suites with mocking, edge cases, and error conditions
- 📝 **Documentation Generation** — Auto-generate professional READMEs, API docs, and usage guides
- 🔒 **Security Auditing** — Scan for secrets, credentials, and insecure patterns using only stdlib
- ⚡ **Performance Benchmarking** — Measure and compare code with statistical analysis
- 🤖 **Agent Personas** — Specialized agents for architecture, security, and performance
- 🔄 **Full Pipeline Orchestration** — End-to-end automation: create → code → test → audit → push
- ✨ **Prompt Engineering** — Write effective system prompts and instruction templates
- 🔌 **API Validation** — Systematically test API keys and endpoints
- ⏰ **Cron Orchestration** — Set up automated monitoring and scheduled jobs
- 📦 **Zero-Dependency Patterns** — Create single-file Python utilities (the "tiny family")

## Quick Start

### As a Plugin

This repository follows the modern agent plugin architecture (`.claude-plugin/plugin.json`).
Install it in your AI assistant's plugin directory:

```bash
git clone https://github.com/hussain-alsaibai/dev-masterkit.git
# Follow your assistant's plugin installation instructions
```

### Manual Usage

Each skill is self-contained in `skills/<name>/SKILL.md`. Follow the procedure
documented in each skill file.

**Example: Scaffold a new project**

```bash
# Read the skill
open skills/repo-creator/SKILL.md
# Follow the procedure to create a new repository
```

## Stats

| Category | Count | Last Updated |
|----------|-------|-------------|
| Skills | 15 | 2026-07-04 |
| Prompts | 11 | 2026-07-04 |
| Commands | 5 | 2026-07-04 |
| Agents | 3 | 2026-07-04 |
| Orchestrators | 1 | 2026-07-04 |
| Tools | 17 | 2026-07-06 |
| Daily Updates | 13 | 2026-07-06 |
| tiny-* Ecosystem Repos | 23 | 2026-07-06 |

## Structure


```
dev-masterkit/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── prompts/                      # Ready-to-use system prompts
│   ├── system-instruction.md     # Vibe Coding session setup
│   ├── api-test-suite.md         # API validation prompt
│   ├── automation-pattern-research.md  # AI automation research
│   ├── zero-dep-scaffold.md      # Single-file utility prompt
│   ├── yaml-debug-tuple-unpack.md # Subset YAML parser tuple bug
│   ├── cli-bool-flag-pattern.md  # argparse boolean flag correctness
│   ├── no-color-12factor.md      # NO_COLOR + TTY color decisions
│   ├── cron-stagger-rpm.md       # Avoid synchronized model RPM bursts
│   ├── decorator-composition-order.md # Stacked-decorator call/return order
│   ├── aws-sigv4-handrolled.md   # Stdlib-only AWS SigV4 for one action
│   └── test-isolation-singleton-registry.md # Per-test registry isolation pattern
├── skills/                       # Reusable skill files
│   ├── repo-creator/             # Create zero-dependency Python repos
│   ├── test-automation/          # Auto-generate test suites
│   ├── doc-generator/            # Generate README + docs
│   ├── security-audit/           # Scan for secrets/vulns
│   ├── benchmark-runner/         # Performance benchmarking
│   ├── prompt-engineering/       # Write effective prompts
│   ├── api-validation/           # Test API keys/endpoints
│   ├── cron-orchestrator/        # Set up scheduled jobs
│   ├── api-dev/                # Build, test, and debug APIs
│   ├── data-analyst/           # Data analysis and visualization
│   ├── security-sentinel/      # Scan for secrets and vulnerabilities
│   ├── bounty-scanner/          # Scan GitHub for official bounties (Algora/Opire)
│   ├── browser-automation/      # Web browser automation and data extraction
│   ├── bounty-verifier/         # Two-stage verification gate (hard filters + behavioral)
│   └── zero-dep-pattern/         # Single-file utility pattern
├── commands/                     # Chat commands
│   ├── scaffold/                 # /scaffold — create repo
│   ├── test/                     # /test — run test suite
│   ├── benchmark/                # /benchmark — benchmark
│   ├── release/                  # /release — version + tag
│   └── audit/                    # /audit — security scan
├── agents/                       # Agent personas
│   ├── python-architect/         # Design Python architectures
│   ├── security-reviewer/        # Review code for security
│   └── performance-optimizer/    # Optimize Python performance
├── orchestrators/                # Multi-step workflows
│   └── full-repo-pipeline/       # Create → code → test → push
├── tools/                        # Tool guides and references
│   ├── plugin-install-guide.md   # OpenClaw plugin setup
│   ├── snapdb-guide.md           # SnapDB usage guide
│   ├── cost-tracker.md           # API cost tracking
│   ├── tiny-config-guide.md      # Layered config loader (tiny-config)
│   ├── tiny-cli-guide.md         # CLI builder (tiny-cli)
│   ├── fast-cache-guide.md       # LRU+TTL cache (fast-cache)
│   ├── tiny-compose-guide.md     # Decorator stacker (tiny-compose)
│   ├── tiny-trace-guide.md       # OTel-API-compat tracing (tiny-trace)
│   ├── tiny-secret-guide.md      # Secret management (tiny-secret)
│   ├── tiny-cron-guide.md        # Cron-style scheduler (tiny-cron)
│   ├── tiny-flags-guide.md       # Feature flags (tiny-flags)
│   ├── tiny-queue-guide.md       # Persistent job queue (tiny-queue)
│   ├── tiny-budget-guide.md      # Runtime budget enforcement (tiny-budget)
│   └── tiny-eventbus-guide.md    # Durable pub/sub with replay (tiny-eventbus)
├── daily-updates/                # Daily changelog
│   ├── 2026-06-25.md             # June 25 update
│   ├── 2026-06-26.md             # June 26 update
│   ├── 2026-06-27.md             # June 27 update
│   ├── 2026-06-28.md             # June 28 update
│   ├── 2026-06-29.md             # June 29 update
│   ├── 2026-06-30.md             # June 30 update
│   ├── 2026-07-01.md             # July 1 update (resilience stack)
│   ├── 2026-07-02.md             # July 2 update (compose/trace/secret + 2 new prompts)
│   ├── 2026-07-03.md             # July 3 update (cron/flags/queue + 13 cross-links)
│   ├── 2026-07-04.md             # July 4 update (metrics/timeout/idempotency + 18 cross-links)
│   ├── 2026-07-05.md             # July 5 update (agent workflow positioning + docs refresh)
│   └── 2026-07-06.md             # July 6 update (budget/eventbus + agent primitive positioning)
├── README.md
└── LICENSE
```

## Skills

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `repo-creator` | Scaffold zero-dependency Python repos | "Create a repo" / `/scaffold` |
| `test-automation` | Generate unittest suites | "Write tests" / `/test` |
| `doc-generator` | Generate README + API docs | "Write documentation" |
| `security-audit` | Scan for secrets/vulnerabilities | "Security scan" / `/audit` |
| `benchmark-runner` | Performance benchmarking | "Benchmark this" / `/benchmark` |
| `prompt-engineering` | Write effective prompts | "Write a system prompt" |
| `api-validation` | Test API keys/endpoints | "Test this API" |
| `cron-orchestrator` | Set up scheduled jobs | "Automate [task]" |
| `zero-dep-pattern` | Single-file utilities | "Create a tiny [tool]" |
| `api-dev` | Build, test, and debug APIs | "Create an API" / "Test this endpoint" |
| `data-analyst` | Data analysis and visualization | "Analyze this data" / "Generate report" |
| `security-sentinel` | Scan for secrets and vulnerabilities | "Security scan" / "Find secrets" |
| `bounty-scanner` | Scan GitHub for official bounties (Algora/Opire) | "Find bounties" / "Scan for bounties" |
| `browser-automation` | Web browser automation and data extraction | "Browse this" / "Fill this form" |
| `bounty-verifier` | Two-stage verification gate (hard filters + behavioral) | "Verify this bounty" / "Is this legit?" |

### 🧩 tiny-* Ecosystem Skills (built using these patterns)

| Library | Mirrors | Tests | Throughput | Last Verified |
|---------|---------|-------|------------|---------------|
| tiny-cron | APScheduler | 48/48 | — | 2026-07-05 |
| tiny-flags | LaunchDarkly/Flagsmith | 59/59 | — | 2026-07-05 |
| tiny-queue | Celery/RQ | 29/29 | — | 2026-07-05 |
| tiny-metrics | prometheus_client | 32/32 | — | 2026-07-05 |
| tiny-timeout | N/A (stdlib-only) | 21/21 | — | 2026-07-05 |
| tiny-idempotency | N/A (Stripe-style) | 23/23 | — | 2026-07-05 |
| tiny-budget | LiteLLM/LangSmith budget controls | 16/16 | — | 2026-07-06 |
| tiny-eventbus | Redis Streams/EventEmitter middle tier | 17/17 | — | 2026-07-06 |
| tiny-rate | limits | 33/33 | ~720K ops/s | 2026-07-01 |
| tiny-retry | tenacity | 34/34 | ~1 µs/op | 2026-07-01 |
| tiny-pool | concurrent.futures+ | 25/25 | — | 2026-07-01 |
| tiny-compose | decorator chains | 53/53 | — | 2026-07-02 |
| tiny-trace | OpenTelemetry-API | 57/57 | — | 2026-07-02 |
| tiny-secret | pydantic.SecretStr | 56/56 | — | 2026-07-02 |
| tiny-config | python-decouple | 15/15 | 35 µs load | 2026-06-30 |
| tiny-cli | Click/argparse | 13/13 | 258 ns color | 2026-06-30 |
| fast-cache | Redis | 18/18 | 2.2M ops/s | 2026-06-30 |
| tiny-router | Flask | 15/15 | 76K req/s | 2026-06-29 |
| tiny-log | structlog | 17/17 | 32K logs/s | 2026-06-29 |
| tiny-validator | Pydantic | 31/31 | 247K val/s | 2026-06-29 |
| tiny-agent | LangChain | ✅ | — | 2026-06-28 |
| tiny-embed | sentence-transformers | ✅ | — | 2026-06-28 |
| tiny-mcp | Model Context Protocol | ✅ | — | 2026-06-28 |

*23 zero-dep libraries total. Built with the `zero-dep-pattern` and `repo-creator` skills. ~16,000 LOC lib + ~549 tests across the entire stack.*

## Commands

| Command | Description | Skill |
|---------|-------------|-------|
| `/scaffold <name>` | Create a new repo from template | repo-creator |
| `/test [path]` | Run test suite | test-automation |
| `/benchmark <target>` | Benchmark code performance | benchmark-runner |
| `/release [bump]` | Version bump + git tag | release |
| `/audit [path]` | Security scan | security-audit |

## Agents

| Agent | Role | Trigger |
|-------|------|---------|
| `python-architect` | Design clean Python architectures | "Design the structure for..." |
| `security-reviewer` | Find and fix security issues | "Review this for security" |
| `performance-optimizer` | Optimize speed and memory | "Make this faster" / "Profile..." |

## Prompts

| Prompt | Purpose | When to Use |
|--------|---------|-------------|
| `api-test-suite` | Systematic API validation | Onboarding keys, debugging integrations |
| `automation-pattern-research` | Research AI automation patterns | Exploring use cases, benchmarking |
| `system-instruction` | Vibe Coding session setup | Starting dev sessions, setting AI expectations |
| `zero-dep-scaffold` | Single-file utility creation | Creating tiny Python modules |
| `yaml-debug-tuple-unpack` | Subset YAML parser tuple bug | Hand-rolled parsers returning `(value, pos)` |
| `cli-bool-flag-pattern` | argparse boolean flag correctness | Click-style wrappers, store_true errors |
| `no-color-12factor` | NO_COLOR + TTY color decisions | ANSI color in CLIs/loggers, 12-factor compliance |
| `cron-stagger-rpm` | Cron job RPM stagger policy | Recurring 429 errors, synchronized bursts |
| `decorator-composition-order` | Stacked-decorator call/return order | Building `composed()`/`stack()` meta-decorators |
| `aws-sigv4-handrolled` | Stdlib-only AWS SigV4 for one action | Zero-dep secret fetch from Secrets Manager |
| `test-isolation-singleton-registry` | Per-test isolation for module-level registries | Duplicate-metric / duplicate-flag test failures |

## 🏗️ Our Tools

Production-tested tools and libraries built by this team:

| Repo | Description | Stars | Lang |
|------|-------------|-------|------|
| [context-bridge](https://github.com/hussain-alsaibai/context-bridge) | MCP server with persistent semantic knowledge graph | ⭐0 | TypeScript |
| [snapdb](https://github.com/hussain-alsaibai/snapdb) | Lightning-fast in-memory DB, zero dependencies | ⭐0 | Python |
| [fast-cache](https://github.com/hussain-alsaibai/fast-cache) | High-perf cache (LRU+TTL+stale-while-revalidate, async) | ⭐0 | Python |
| [tiny-router](https://github.com/hussain-alsaibai/tiny-router) | Minimal WSGI router — Flask in one file | ⭐0 | Python |
| [tiny-config](https://github.com/hussain-alsaibai/tiny-config) | Layered config loader (JSON, YAML, INI, .env, CLI) | ⭐0 | Python |
| [tiny-cli](https://github.com/hussain-alsaibai/tiny-cli) | Minimal CLI builder — Click in one file | ⭐0 | Python |
| [tiny-log](https://github.com/hussain-alsaibai/tiny-log) | Structured logging — structlog in one file | ⭐0 | Python |
| [tiny-validator](https://github.com/hussain-alsaibai/tiny-validator) | Data validation — Pydantic in one file | ⭐0 | Python |
| [ai-git-hooks](https://github.com/hussain-alsaibai/ai-git-hooks) | AI-powered Git hooks with local LLMs | ⭐0 | Shell/Python |
| [tiny-worker](https://github.com/hussain-alsaibai/tiny-worker) | Background task queue — Celery in one file | ⭐0 | Python |
| [tiny-events](https://github.com/hussain-alsaibai/tiny-events) | Event bus — Redis Pub/Sub in one file | ⭐0 | Python |
| [tiny-http](https://github.com/hussain-alsaibai/tiny-http) | HTTP client — requests in one file | ⭐0 | Python |
| [container-security-monitor](https://github.com/hussain-alsaibai/container-security-monitor) | Continuous container security with Trivy | ⭐0 | Python |
| [tiny-agent](https://github.com/hussain-alsaibai/tiny-agent) | Agent framework — LangChain in one file | ⭐0 | Python |
| [tiny-embed](https://github.com/hussain-alsaibai/tiny-embed) | Text embeddings — sentence-transformers in one file | ⭐0 | Python |
| [tiny-mcp](https://github.com/hussain-alsaibai/tiny-mcp) | MCP server — Model Context Protocol in one file | ⭐0 | Python |
| [tiny-rate](https://github.com/hussain-alsaibai/tiny-rate) | Rate limiter — token bucket + fixed + sliding window, sync + async | ⭐0 | Python |
| [tiny-retry](https://github.com/hussain-alsaibai/tiny-retry) | Retry + backoff (4 jitter modes) + circuit breaker, sync + async | ⭐0 | Python |
| [tiny-pool](https://github.com/hussain-alsaibai/tiny-pool) | Bounded ThreadPool + AsyncPool for batched work | ⭐0 | Python |
| [tiny-compose](https://github.com/hussain-alsaibai/tiny-compose) | Decorator stacker — composed()/stack()/pipeline() + global layer | ⭐0 | Python |
| [tiny-trace](https://github.com/hussain-alsaibai/tiny-trace) | OTel-API-compat tracing — W3C traceparent, 4 samplers, 3 exporters | ⭐0 | Python |
| [tiny-secret](https://github.com/hussain-alsaibai/tiny-secret) | Secret loader — 7 sources, value-hiding Secret, redacting log formatter | ⭐0 | Python |
| [tiny-cron](https://github.com/hussain-alsaibai/tiny-cron) | Cron-style scheduler — 5-field syntax + @aliases + L/W/# extensions, Scheduler w/ anti-overlap | ⭐0 | Python |
| [tiny-flags](https://github.com/hussain-alsaibai/tiny-flags) | Feature flags — bool / percentage / multivariate, 11 rule operators, deterministic SHA-256 bucketing | ⭐0 | Python |
| [tiny-queue](https://github.com/hussain-alsaibai/tiny-queue) | Persistent job queue — NDJSON, fcntl.flock, exponential backoff, dead-letter, idempotency | ⭐0 | Python |
| [tiny-metrics](https://github.com/hussain-alsaibai/tiny-metrics) | Prometheus-compatible metrics — Counter / Gauge / Histogram / Summary, OpenMetrics exposition, /metrics HTTP endpoint | ⭐0 | Python |
| [tiny-timeout](https://github.com/hussain-alsaibai/tiny-timeout) | Timeouts — hard cut-off via worker thread + cooperative Deadline, works on every thread/OS | ⭐0 | Python |
| [tiny-idempotency](https://github.com/hussain-alsaibai/tiny-idempotency) | Stripe-style idempotency keys — fingerprint detection, atomic claim/complete/fail, in-memory + FileStore | ⭐0 | Python |
| [tiny-budget](https://github.com/hussain-alsaibai/tiny-budget) | Runtime USD + token budget enforcement for AI agents | ⭐0 | JavaScript |
| [tiny-eventbus](https://github.com/hussain-alsaibai/tiny-eventbus) | Durable pub/sub with JSONL replay, wildcard subscribers, and one-shot waits | ⭐0 | JavaScript |

*All tools follow the "zero-dependency, single-file" philosophy where the target runtime allows it. Total ecosystem: **23 active libraries** spanning routers, config, CLI, logging, validation, workers, events, HTTP, agents, embeddings, MCP, rate limiting, retry, pooling, composition, tracing, secrets, cron, feature flags, queues, metrics, timeouts, idempotency, budgets, and durable event streams (~16,000 LOC lib + ~549 tests across the stack).*

### 🆕 Latest additions (2026-07-06) — Agent Budget / Durable Events
- **tiny-budget** — Runtime USD + token budget enforcement for AI agents, atomic JSON persistence, OpenAI/Anthropic usage-shape support, and warning thresholds (16/16 tests)
- **tiny-eventbus** — Durable JSONL pub/sub with replay, wildcard subscribers, offset cursors, `once()` waits, and log rotation (17/17 tests)
- Existing router/CLI/config/log/validator repos updated with agent-workflow cross-links

### Previous additions (2026-07-04) — Metrics / Timeouts / Idempotency
- **tiny-metrics** — Prometheus-compatible Counter/Gauge/Histogram/Summary with OpenMetrics exposition + /metrics HTTP endpoint (32/32 tests, ~980 LOC)
- **tiny-timeout** — Hard cut-off via worker thread + cooperative Deadline; works on every thread/OS, no `signal.alarm` (21/21 tests, ~500 LOC)
- **tiny-idempotency** — Stripe-style idempotency keys with fingerprint detection + atomic claim/complete/fail + crash-safe FileStore (23/23 tests, ~570 LOC)
- All 18 sibling ecosystem repos updated with cross-links (~18 commits today)

### Previous additions (2026-07-03) — Agent Control Plane
- **tiny-cron** — Cron-style scheduler with @aliases + L/W/# extensions, anti-overlap, jitter, decorator API (48/48 tests)
- **tiny-flags** — Bool/percentage/multivariate feature flags with SHA-256 bucketing + 11 rule operators (59/59 tests)
- **tiny-queue** — NDJSON persistent queue with flock + dead-letter + idempotency (29/29 tests)
- All 13 sibling ecosystem repos updated with cross-links (~15 commits)

### Previous additions (2026-07-02) — Composition / Tracing / Secrets
- **tiny-compose** — Meta-decorator stacker with sync+async auto-detect (53/53 tests, 411 LOC)
- **tiny-trace** — OTel-API-compat tracing with W3C propagation (57/57 tests, 802 LOC)
- **tiny-secret** — 7-source secret loader with redacting log formatter (56/56 tests, 694 LOC)

### Previous additions (2026-07-01) — Resilience Stack
- **tiny-rate** — Token bucket + fixed + sliding window, sync + async decorators (33/33 tests, ~720K ops/s, 538 LOC)
- **tiny-retry** — Exponential backoff (4 jitter modes) + circuit breaker, sync + async (34/34 tests, ~1 µs/op, 500 LOC)
- **tiny-pool** — Bounded ThreadPool + AsyncPool with submit/map/join (25/25 tests, 294 LOC)

### Previous additions (2026-06-30)
- **tiny-config** — Layered config loader (15/15 tests, ~35 µs file load)
- **tiny-cli** — Click-style CLI builder (13/13 tests, NO_COLOR compliant)
- **fast-cache** — LRU+TTL+stale-while-revalidate (18/18 tests, 2.2M ops/sec)

### Previous additions (2026-06-29)
- **tiny-router** — 76K req/s HTTP/WSGI router (15/15 tests)
- **tiny-log** — 32K logs/s structured logging (17/17 tests)
- **tiny-validator** — 247K val/s Pydantic-style validation (31/31 tests)

### Ecosystem cohesion (2026-06-28)
- tiny-agent, tiny-embed, tiny-mcp gained cross-linking "Ecosystem" sections
- Each README now links all sibling repos for discoverability

**SnapDB** is the flagship database: v0.3.1 with columnar engine, metrics, CDC, and batch insert. 47/47 tests passing. Benchmarks vs DuckDB/SQLite available in repo.

## Tools

| Tool | Description | Last Verified |
|------|-------------|---------------|
| [Cost Tracker](tools/cost-tracker.md) | API cost monitoring | 2026-07-02 |
| [Plugin Install Guide](tools/plugin-install-guide.md) | OpenClaw plugin management | 2026-07-02 |
| [SnapDB Guide](tools/snapdb-guide.md) | Ultra-lightweight in-memory DB (v0.3.1) | 2026-07-02 |
| [tiny-config Guide](tools/tiny-config-guide.md) | Layered config loader (JSON/YAML/INI/.env/CLI) | 2026-07-02 |
| [tiny-cli Guide](tools/tiny-cli-guide.md) | Click-style CLI builder with NO_COLOR | 2026-07-02 |
| [fast-cache Guide](tools/fast-cache-guide.md) | LRU+TTL+stale-while-revalidate cache | 2026-07-02 |
| [tiny-compose Guide](tools/tiny-compose-guide.md) | Decorator stacker with async auto-detect | 2026-07-02 |
| [tiny-trace Guide](tools/tiny-trace-guide.md) | OTel-API-compat tracing + W3C propagation | 2026-07-02 |
| [tiny-secret Guide](tools/tiny-secret-guide.md) | 7-source secret loader + redacting formatter | 2026-07-02 |
| [tiny-cron Guide](tools/tiny-cron-guide.md) | Cron-style scheduler with @aliases + L/W/# extensions | 2026-07-03 |
| [tiny-flags Guide](tools/tiny-flags-guide.md) | Feature flags with SHA-256 bucketing + 11 rule ops | 2026-07-03 |
| [tiny-queue Guide](tools/tiny-queue-guide.md) | Persistent NDJSON queue + dead-letter + idempotency | 2026-07-03 |
| [tiny-metrics Guide](tools/tiny-metrics-guide.md) | Prometheus-compatible metrics with /metrics endpoint | 2026-07-04 |
| [tiny-timeout Guide](tools/tiny-timeout-guide.md) | Timeouts that work on every thread/OS | 2026-07-04 |
| [tiny-idempotency Guide](tools/tiny-idempotency-guide.md) | Stripe-style idempotency keys with fingerprint detection | 2026-07-04 |
| [tiny-budget Guide](tools/tiny-budget-guide.md) | Runtime USD + token budget enforcement for agents | 2026-07-06 |
| [tiny-eventbus Guide](tools/tiny-eventbus-guide.md) | Durable JSONL pub/sub with replay and one-shot waits | 2026-07-06 |

## Daily Updates

Each day's learnings are logged in `daily-updates/YYYY-MM-DD.md`.

## Pipeline

The **Full Repo Pipeline** orchestrator automates the entire lifecycle:

1. **Scaffold** — Create directory structure and core files
2. **Implement** — Write business logic with clean architecture
3. **Test** — Generate comprehensive unittest suites
4. **Document** — Generate professional README and API docs
5. **Audit** — Security scan for secrets and vulnerabilities
6. **Benchmark** — Performance baseline and comparison
7. **Release** — Version bump, changelog, git tag
8. **Push** — Create GitHub repo and push code

## Philosophy

- **Zero dependencies** — Every skill uses only Python's standard library
- **Production-ready** — Generated code passes tests, has docs, and runs in CI
- **Composable** — Use individual skills or chain them in pipelines
- **Documented** — Every skill has triggers, procedures, examples, and checklists

## Requirements

- Python 3.9+
- Git
- (Optional) GitHub CLI (`gh`) for repository creation

## License

MIT — see [LICENSE](LICENSE) file.
