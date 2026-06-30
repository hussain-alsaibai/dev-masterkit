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
| Skills | 14 | 2026-06-30 |
| Prompts | 8 | 2026-06-30 |
| Commands | 5 | 2026-06-30 |
| Agents | 3 | 2026-06-30 |
| Orchestrators | 1 | 2026-06-30 |
| Tools | 6 | 2026-06-30 |
| Daily Updates | 6 | 2026-06-30 |
| tiny-* Ecosystem Repos | 19 | 2026-06-30 |

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
│   └── cron-stagger-rpm.md       # Avoid synchronized model RPM bursts
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
│   └── fast-cache-guide.md       # LRU+TTL cache (fast-cache)
├── daily-updates/                # Daily changelog
│   ├── 2026-06-25.md             # June 25 update
│   ├── 2026-06-26.md             # June 26 update
│   ├── 2026-06-27.md             # June 27 update
│   ├── 2026-06-28.md             # June 28 update
│   ├── 2026-06-29.md             # June 29 update
│   └── 2026-06-30.md             # June 30 update
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

### 🧩 tiny-* Ecosystem Skills (built using these patterns)

| Library | Mirrors | Tests | Throughput | Last Verified |
|---------|---------|-------|------------|---------------|
| tiny-config | python-decouple | 15/15 | 35 µs load | 2026-06-30 |
| tiny-cli | Click/argparse | 13/13 | 258 ns color | 2026-06-30 |
| fast-cache | Redis | 18/18 | 2.2M ops/s | 2026-06-30 |
| tiny-router | Flask | 15/15 | 76K req/s | 2026-06-29 |
| tiny-log | structlog | 17/17 | 32K logs/s | 2026-06-29 |
| tiny-validator | Pydantic | 31/31 | 247K val/s | 2026-06-29 |
| tiny-agent | LangChain | ✅ | — | 2026-06-28 |
| tiny-embed | sentence-transformers | ✅ | — | 2026-06-28 |
| tiny-mcp | Model Context Protocol | ✅ | — | 2026-06-28 |

*19 zero-dep, single-file Python libraries total. Built with the `zero-dep-pattern` and `repo-creator` skills.*

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

*All Python tools follow the "zero-dependency, single-file" philosophy. Total ecosystem: 19 libraries (~130KB).*

### Latest additions (2026-06-30)
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
| [Cost Tracker](tools/cost-tracker.md) | API cost monitoring | 2026-06-28 |
| [Plugin Install Guide](tools/plugin-install-guide.md) | OpenClaw plugin management | 2026-06-28 |
| [SnapDB Guide](tools/snapdb-guide.md) | Ultra-lightweight in-memory DB (v0.3.1) | 2026-06-28 |
| [tiny-config Guide](tools/tiny-config-guide.md) | Layered config loader (JSON/YAML/INI/.env/CLI) | 2026-06-30 |
| [tiny-cli Guide](tools/tiny-cli-guide.md) | Click-style CLI builder with NO_COLOR | 2026-06-30 |
| [fast-cache Guide](tools/fast-cache-guide.md) | LRU+TTL+stale-while-revalidate cache | 2026-06-30 |

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
