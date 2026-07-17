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
| Skills | 15 | 2026-07-15 |
| Prompts | 20 | 2026-07-17 |
| Commands | 5 | 2026-07-04 |
| Agents | 3 | 2026-07-04 |
| Orchestrators | 1 | 2026-07-04 |
| Tools | 22 | 2026-07-15 |
| Daily Updates | 24 | 2026-07-17 |
| tiny-* Ecosystem Repos | 25 | 2026-07-07 |

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
│   ├── gitea-cross-fork-pr-blocker.md # Fine-grained PAT `pull`-only blocks cross-fork PRs [NEW 2026-07-09]
│   ├── go-build-on-tmpfs.md         # Workaround for tmpfs-backed `/tmp` failing `go build` [NEW 2026-07-09]
│   ├── cost-tracker-session-ingest.md # Re-register per-session cost tracker or it goes silent [NEW 2026-07-10]
│   ├── reusable-ci-matrix-template.md # Drop-in GitHub Actions CI for tiny-* Python libs [NEW 2026-07-11]
│   ├── bounty-saturation-resolved-not-skip.md # Override the saturation rule when mirror-shape fits [NEW 2026-07-11]
│   ├── bounty-saturation-pat-blocked-skip.md # Skip saturated bounties when PR creation is blocked [NEW 2026-07-12]
│   ├── agent-boundary-contracts.md # Harden agent side-effect boundaries [NEW 2026-07-13]
│   ├── chainable-redaction-wrapper.md # Preserve chat surfaces while redacting PII [NEW 2026-07-16]
│   ├── external-bounty-clean-branch.md # Clean fork branch + handoff for PAT-blocked bounty PRs [NEW 2026-07-17]
│   └── openclaw-self-version-check.md # Detect upstream OpenClaw updates without trusting stale install paths [NEW 2026-07-17]
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
│   ├── tiny-log-guide.md         # Structured evidence logs and audit bundles [NEW 2026-07-15]
│   ├── fast-cache-guide.md       # LRU+TTL cache (fast-cache)
│   ├── tiny-compose-guide.md     # Decorator stacker (tiny-compose)
│   ├── tiny-trace-guide.md       # OTel-API-compat tracing (tiny-trace)
│   ├── tiny-secret-guide.md      # Secret management (tiny-secret)
│   ├── tiny-cron-guide.md        # Cron-style scheduler (tiny-cron)
│   ├── tiny-flags-guide.md       # Feature flags (tiny-flags)
│   ├── tiny-queue-guide.md       # Persistent job queue (tiny-queue)
│   ├── tiny-budget-guide.md      # Runtime budget enforcement (tiny-budget)
│   ├── tiny-eventbus-guide.md    # Durable pub/sub with replay (tiny-eventbus)
│   ├── tiny-router-guide.md      # Stdlib routing + agent callback receiver [NEW 2026-07-13]
│   ├── tiny-validator-guide.md   # JSON Schema bridge for tool contracts [NEW 2026-07-13]
│   ├── tiny-policy-guide.md      # ABAC policy engine (tiny-policy)        [NEW 2026-07-07]
│   └── tiny-otel-guide.md        # OTLP/HTTP trace exporter (tiny-otel)    [NEW 2026-07-07]
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
│   ├── 2026-07-06.md             # July 6 update (budget/eventbus + agent primitive positioning)
│   ├── 2026-07-07.md             # July 7 update (policy/otel + control-plane positioning)
│   ├── 2026-07-07-afternoon.md   # July 7 afternoon verification + CI coverage gap
│   ├── 2026-07-08.md             # July 8 update (bounty scam filter re-check)
│   ├── 2026-07-09.md             # July 9 update (Gitea PR #4898 + cross-fork PAT + tmpfs gotchas)
│   ├── 2026-07-10.md             # July 10 update (cost tracker ingest + saturated bounty defer)
│   ├── 2026-07-11.md             # July 11 update (CI matrix + Qdrant bounty)
│   ├── 2026-07-12.md             # July 12 update (saturated bounty + PAT-blocked skip gate)
│   ├── 2026-07-13.md             # July 13 update (agent boundary contracts + tool guides)
│   ├── 2026-07-14.md             # July 14 update (signed callbacks, cache ROI, schema-drift repair)
│   ├── 2026-07-15.md             # July 15 update (operator leases, audit bundles, typed boundaries)
│   ├── 2026-07-16.md             # July 16 update (chainable PII redaction wrapper)
│   └── 2026-07-17.md             # July 17 update (agent runtime gateways and capability contracts)
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
| tiny-policy | OpenFGA/Cerbos/Cedar light tier | 19/19 | ~1.5 us/eval | 2026-07-07 |
| tiny-otel | OpenTelemetry OTLP/HTTP exporter | 10/10 | ~1 us span create | 2026-07-07 |
| tiny-rate | limits | 33/33 | ~720K ops/s | 2026-07-01 |
| tiny-retry | tenacity | 34/34 | ~1 µs/op | 2026-07-01 |
| tiny-pool | concurrent.futures+ | 25/25 | — | 2026-07-01 |
| tiny-compose | decorator chains | 53/53 | — | 2026-07-02 |
| tiny-trace | OpenTelemetry-API | 57/57 | — | 2026-07-02 |
| tiny-secret | pydantic.SecretStr | 56/56 | — | 2026-07-02 |
| tiny-config | python-decouple | 15/15 | 35 µs load | 2026-06-30 |
| tiny-cli | Click/argparse | 13/13 | 258 ns color | 2026-06-30 |
| fast-cache | Redis | 26/26 | 2.2M ops/s | 2026-07-13 |
| tiny-router | Flask | 15/15 + 11 examples | 76K req/s | 2026-07-13 |
| tiny-log | structlog | 17/17 | 32K logs/s | 2026-06-29 |
| tiny-validator | Pydantic / JSON Schema | 34/34 | 247K val/s | 2026-07-13 |
| tiny-agent | LangChain | ✅ | — | 2026-06-28 |
| tiny-embed | sentence-transformers | ✅ | — | 2026-06-28 |
| tiny-mcp | Model Context Protocol | ✅ | — | 2026-06-28 |

*25 zero-dep libraries total. Built with the `zero-dep-pattern` and `repo-creator` skills. ~16,000 LOC lib + ~590 tests across the entire stack.*

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
| `gitea-cross-fork-pr-blocker` | Fine-grained PAT `pull`-only blocks cross-fork PRs | 403 on `gh pr create` against upstream |
| `go-build-on-tmpfs` | Workaround for `go build` `no space left on device` on tmpfs | Building Go projects in sandboxed/container hosts |
| `cost-tracker-session-ingest` | Re-register per-session cost tracker or it goes silent | Cost dashboard shows $0/stale; no events from new sessions |
| `reusable-ci-matrix-template` | Drop-in `.github/workflows/ci.yml` for zero-dep Python libs | Adding CI to a new or stale `tiny-*` repo |
| `bounty-saturation-resolved-not-skip` | Override the saturation rule when mirror-shape fits | Saturated bounty with mirror-able class shape |
| `bounty-saturation-pat-blocked-skip` | Skip saturated bounties when PR creation is blocked | All top bounty candidates saturated and fork PRs already blocked |
| `agent-boundary-contracts` | Harden agent side-effect boundaries | Callback receivers, tool calls, job queues, API writes |
| `chainable-redaction-wrapper` | Preserve chat surfaces while redacting PII | Adding a redaction layer around LLM/client APIs |
| `external-bounty-clean-branch` | Prepare clean fork branches for bounty PR handoff | Local/fork work exists but PR automation is PAT-blocked |

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
| [tiny-eventbus](https://github.com/hussain-alsaibai/tiny-eventbus) | Durable pub/sub with JSONL replay — topic filtering, wildcards, cursor consumers, automatic log rotation | ⭐0 | Node |
| [tiny-policy](https://github.com/hussain-alsaibai/tiny-policy) | ABAC policy engine — JSON policies, glob matching, deny-overrides, 11 condition ops, ~1.5 µs/eval | ⭐0 | Node |
| [tiny-otel](https://github.com/hussain-alsaibai/tiny-otel) | OTLP/HTTP trace exporter — ships to Honeycomb/Tempo/SigNoz/Datadog, ~250 LOC zero-dep | ⭐0 | Node |

*All tools follow the "zero-dependency, single-file" philosophy where the target runtime allows it. Total ecosystem: **25 active libraries** spanning routers, config, CLI, logging, validation, workers, events, HTTP, agents, embeddings, MCP, rate limiting, retry, pooling, composition, tracing, secrets, cron, feature flags, queues, metrics, timeouts, idempotency, budgets, durable event streams, authorization, and OTLP tracing (~16,000 LOC lib + ~590 tests across the stack).*

### 🆕 Latest additions (2026-07-17) — Clean bounty handoff branch
- **`external-bounty-clean-branch.md` prompt** — Captures the verified workflow for rebuilding bounty work from a fresh upstream target branch, cherry-picking only issue-specific commits, running focused verification, pushing an issue-named fork branch, and recording a precise handoff when PR creation is blocked by PAT scope.
- **EdgeChains #290 handoff cleaned up** — AWS Comprehend redaction work was republished as `hussain-alsaibai/EdgeChains:fix/issue-290`, verified with `npm run build` and `npm test -- --run src/ai/src/tests/awsComprehend.test.ts`, then left ready for manual PR creation because GitHub returned `403 Resource not accessible by personal access token`.
- Prompts 19 -> 20; daily-updates remains 24; Skills 15 unchanged; Tools 22 unchanged; nothing removed.

### Previous additions (2026-07-16) — Chainable PII redaction wrapper
- **`chainable-redaction-wrapper.md` prompt** — Captures the verified pattern for adding a sensitive-data redaction layer in front of an existing chat-style client while preserving `.chat({ prompt })` and `.chat({ messages })`, exposing redaction events, supporting custom replacements, and testing provider responses through mocks.
- **EdgeChains AWS Comprehend implementation recorded** — Fork branch `hussain-alsaibai/EdgeChains:ts` commit `c7bfdae4` added inline SigV4 Comprehend helpers, a `Redact` wrapper for OpenAI/GeminiAI/LlamaAI/RetellAI-style endpoints, 12 focused unit tests, and a runnable `examples/redact-with-comprehend/` example.
- Prompts 18 -> 19; daily-updates 22 -> 23; Skills 15 unchanged; Tools 22 unchanged; no new general-purpose tool guide and nothing removed. Upstream PR creation remains blocked by fine-grained PAT scope.

### Previous additions (2026-07-15) — Operator leases, audit bundles, and typed tool boundaries
- **`fast-cache` operator lease guidance** — Source field note `2820fef` records `Cache.add()` first-writer-wins claims, `touch()` keepalive refreshes, short TTLs, explicit lease keys, and the warning that local leases do not coordinate across multiple hosts.
- **`tiny-log` audit bundle guide** — New `tools/tiny-log-guide.md` captures JSONL evidence logs, Markdown summaries, event vocabulary (`started`, `claimed`, `skipped`, `validated`, `executed`, `retried`, `reported`, `failed`), bound context, and redaction defaults for agent runs.
- **`tiny-validator` typed tool-boundary guidance** — Local field note `reports/2026-07-15-typed-tool-boundaries.md` records fail-closed validation before filesystem, GitHub, browser, messaging, deployment, or billing side effects.
- **Bounty skip verification refreshed** — 336 total issues scanned, 334 with dollar markers, 241 hard-filtered/rejected, top 9 unchanged in shape, fresh cross-fork PR probe still blocked with `403 Resource not accessible by personal access token`. Existing parked branches (`hussain-alsaibai/EdgeChains:ts @ d0ceb72a`, `hussain-alsaibai/gitea:feat/commit-inline-comments-4898 @ c50dffec5a`) remain parked pending PAT scope fix.
- Tools 21 -> 22; daily-updates 21 -> 22; Skills 15 unchanged; Prompts 18 unchanged (one prompt verification refreshed); no repos created and nothing removed.

### Previous additions (2026-07-14) — Signed callbacks, cache ROI, and schema-drift repair
- **`tiny-router` signed callback guidance** — Source field note `41ddb67` records HMAC verification over the exact raw body, timestamp tolerance, TTL delivery-ID dedupe, deterministic 401/409/422 responses, and health/readiness/status observability. Existing callback receiver recipe remains at `902691d`.
- **`fast-cache` cache-ROI guidance** — Source field note `8389359` records cache-key design, live/fresh/stale source labels, `stats()`-based avoided-call measurement, bounded local caches, and never-cache boundaries.
- **`tiny-validator` schema-drift repair guidance** — Source field note `84b0f8d` records strict validation, redacted path-specific repair input, a one- or two-attempt cap, re-validation before side effects, and structured repair logging.
- **Daily bounty skip recorded as a verified artifact** — 336 official issues scanned, 240 rejected by anti-scam heuristics, top 5 saturated or out-of-skill-stack. No code committed, no PR API calls. Existing parked branches (`hussain-alsaibai/EdgeChains:ts @ d0ceb72a`, `hussain-alsaibai/gitea:feat/commit-inline-comments-4898 @ c50dffec5a`) remain parked pending PAT scope fix. Saturation-floor masking was confirmed across the 2026-07-12 and 2026-07-14 runs.
- daily-updates 20 → 21; Skills 15 unchanged; Tools 21 unchanged (three guides refreshed); no new prompts or repos, and nothing removed.

### 🆕 Latest additions (2026-07-13) — Agent boundary contracts + tool guides
- **`agent-boundary-contracts.md` prompt** — Captures the verified pattern for hardening autonomous-agent side-effect boundaries: auth, request IDs, idempotency, rate limits, schema validation, structured logs, status endpoints, TTL cleanup, and negative-path tests.
- **`tiny-router` callback receiver recipe** — `tiny-router` commit `902691d` added `examples/agent_callback_receiver.py` with auth, request IDs, rate limiting, TTL idempotency, JSON validation, `/health`, `/ready`, `/status`, structured logs, and CI-covered example tests. Verification: 15 core tests + 11 example tests passing.
- **`fast-cache` atomic claim + keepalive** — `fast-cache` commit `29ee08b` added `Cache.add()` and `Cache.touch()` for callback/job dedupe and long-running work. Verification: 26 tests passing.
- **`tiny-validator` JSON Schema bridge** — `tiny-validator` commit `296079e` added `from_json_schema()` for practical MCP/tool-call JSON Schema contracts. Verification: 34 tests passing.
- 1 new verified prompt (17 -> 18); 2 new tool guides (19 -> 21); daily-updates 19 -> 20. No skill added and nothing removed.

### 🆕 Latest additions (2026-07-12) — Saturated bounty + PAT-blocked skip gate
- **`bounty-saturation-pat-blocked-skip.md`** prompt — Captures when the right bounty-scanner action is no new implementation: all top candidates saturated, cross-fork PR creation still blocked by PAT scope, existing fork branches already parked, and no mirror-shape override available.
- **Daily bounty scan recorded as a verified skip** — 200 official issues, 327 bounty-labeled issues, 10 bounty-farm/scam candidates rejected, top 7 all saturated or oversized. No new fork, no new commits, no PR API calls.
- **Parked branch context carried forward** — `hussain-alsaibai/EdgeChains:ts` (`d0ceb72a`) and `hussain-alsaibai/gitea:feat/commit-inline-comments-4898` (`c50dffec5a`) still need a PAT scope fix or human PR open.
- 1 new verified prompt (16 → 17); daily-updates 18 → 19. No new skill or tool added, and nothing removed.

### 🆕 Latest additions (2026-07-11) — CI hygiene for `tiny-router` / `tiny-validator` / `fast-cache` + Qdrant bounty implementation
- **Qdrant vector DB in EdgeChains JS SDK** (branch `ts`, commit `d0ceb72a` on `hussain-alsaibai/EdgeChains`) — `Qdrant` class mirroring the existing `Supabase` class method-for-method (7 methods: insertVectorData, searchVector, getData, getDataById, getDataFromQuery, updateById, deleteById); 2 test files; cross-fork PR blocked by fine-grained PAT `pull`-only scope (see `gitea-cross-fork-pr-blocker`)
- **CI matrix rolled out to 3 repos** — `tiny-router` (`7254ea7`, 15/15), `tiny-validator` (`eff3dd9`, 31/31), `fast-cache` (`9755a43`, 18/18). Each repo now has GitHub Actions CI on Python 3.8 / 3.11 / 3.12 with `ruff` + `pytest`; Actions confirmed `completed/success` on 2026-07-11
- **`reusable-ci-matrix-template.md`** prompt — Drop-in `.github/workflows/ci.yml` for any zero-dep Python library. Verified by rolling it out to three repos in one morning with zero per-repo customization
- **`bounty-saturation-resolved-not-skip.md`** prompt — Companion to the saturation-rejection heuristic. Documents when to override the `≥10 open PRs → skip` rule (issue forbids the obvious path; mirror-able class shape) and how to ship (mirror method-for-method, one happy-path test per public method, no novel features)
- 2 new verified prompts (14 → 16); 3 ecosystem repos CI-bumped (fast-cache / tiny-router / tiny-validator); daily-updates 17 → 18. No new skill or tool added — the Qdrant implementation is an upstream contribution, and the CI template is a one-file artifact.

### 🆕 Latest additions (2026-07-09) — Gitea PR #4898 + cross-fork PR gotchas
- **Gitea PR #4898** (branch `feat/commit-inline-comments-4898`, SHA `c50dffec5a`) — full inline-comments-on-commits implementation in `hussain-alsaibai/gitea`; cross-fork PR blocked by fine-grained PAT `pull`-only scope; handoff doc at `~/.openclaw/workspace/gitea-pr-handoff.md`
- **`gitea-cross-fork-pr-blocker.md`** prompt — Documents the deterministic 403 from `gh pr create` against upstream repos when the bot PAT has `pull`-only scope, plus the recommended handoff workflow (branch + SHA + `gh pr create` command + PR body file)
- **`go-build-on-tmpfs.md`** prompt — Documents the `importcfg: no space left on device` failure mode on tmpfs-backed `/tmp` and the `TMPDIR=~/go-build-tmp` + `GOFLAGS=-tmpdir=...` fix
- 2 new verified prompts (11 → 13); daily-updates 15 → 16. No new skill or tool added — the Gitea work was a one-off bounty implementation, not a reusable primitive.

### Previous additions (2026-07-07) — Authorization + Observability
- **tiny-policy** — Attribute-based authorization policy engine for agents (19/19 tests, 174 LOC, ~1.5 µs/eval). JSON policy files, glob matching (`*`/`**`/`?`), 11 condition ops (`eq`, `ne`, `in`, `nin`, `gt`/`gte`/`lt`/`lte`, `contains`, `startsWith`, `endsWith`, `matches`, `exists`), deny-overrides semantics, optional default-allow, metrics + explain().
- **tiny-otel** — Zero-dep OTLP/HTTP trace exporter for agents (10/10 tests, 268 LOC). Ships the exact `ExportTraceServiceRequest` envelope from the OTLP v1.5.0 spec. `inSpan()` wrapper with auto status + exception capture, standard `OTEL_*` env vars, fetch injection for testing. ~1 µs per span creation. Targets Honeycomb / Tempo / SigNoz / Datadog (via otel-collector) / Jaeger.
- All 4 sibling Node ecosystem repos updated with cross-links (tiny-router, tiny-budget, tiny-eventbus, dev-masterkit)

### Previous additions (2026-07-06) — Cost + Durable Events
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
- **fast-cache** — LRU+TTL+stale-while-revalidate (26/26 tests, 2.2M ops/sec)

### Previous additions (2026-06-29)
- **tiny-router** — 76K req/s HTTP/WSGI router (15/15 core tests + 11 callback receiver example tests)
- **tiny-log** — 32K logs/s structured logging (17/17 tests)
- **tiny-validator** — 247K val/s Pydantic-style validation + JSON Schema bridge (34/34 tests)

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
| [tiny-log Guide](tools/tiny-log-guide.md) | Structured evidence logs and agent audit bundles | 2026-07-15 |
| [fast-cache Guide](tools/fast-cache-guide.md) | LRU+TTL+stale-while-revalidate cache with operator leases | 2026-07-15 |
| [tiny-router Guide](tools/tiny-router-guide.md) | Stdlib WSGI routing + agent callback receiver pattern | 2026-07-14 |
| [tiny-validator Guide](tools/tiny-validator-guide.md) | Data validation + typed tool boundaries for side effects | 2026-07-15 |
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
| [tiny-policy Guide](tools/tiny-policy-guide.md) | ABAC policy engine with deny-overrides and JSON policies | 2026-07-07 |
| [tiny-otel Guide](tools/tiny-otel-guide.md) | OTLP/HTTP trace exporter for agent spans | 2026-07-07 |

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
