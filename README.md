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
| Skills | 12 | 2026-06-27 |
| Prompts | 4 | 2026-06-27 |
| Commands | 5 | 2026-06-27 |
| Agents | 3 | 2026-06-27 |
| Orchestrators | 1 | 2026-06-27 |
| Tools | 3 | 2026-06-27 |
| Daily Updates | 8 | 2026-06-27 |

## Structure


```
dev-masterkit/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── prompts/                      # Ready-to-use system prompts
│   ├── system-instruction.md     # Vibe Coding session setup
│   ├── api-test-suite.md         # API validation prompt
│   ├── automation-pattern-research.md  # AI automation research
│   └── zero-dep-scaffold.md      # Single-file utility prompt
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
│   └── cost-tracker.md           # API cost tracking
├── daily-updates/                # Daily changelog
│   ├── 2026-06-25.md             # June 25 update
│   ├── 2026-06-26.md             # June 26 update
│   └── 2026-06-27.md             # June 27 update
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

## 🏗️ Our Tools

Production-tested tools and libraries built by this team:

| Repo | Description | Stars | Lang |
|------|-------------|-------|------|
| [context-bridge](https://github.com/hussain-alsaibai/context-bridge) | MCP server with persistent semantic knowledge graph | ⭐0 | TypeScript |
| [snapdb](https://github.com/hussain-alsaibai/snapdb) | Lightning-fast in-memory DB, zero dependencies | ⭐0 | Python |
| [fast-cache](https://github.com/hussain-alsaibai/fast-cache) | High-performance cache (TTL, LRU, memory limits) | ⭐0 | Python |
| [tiny-router](https://github.com/hussain-alsaibai/tiny-router) | Minimal WSGI router — Flask in one file | ⭐0 | Python |
| [tiny-config](https://github.com/hussain-alsaibai/tiny-config) | Config loader (JSON, .env, INI, Python) | ⭐0 | Python |
| [tiny-cli](https://github.com/hussain-alsaibai/tiny-cli) | Minimal argument parser — Click in one file | ⭐0 | Python |
| [tiny-log](https://github.com/hussain-alsaibai/tiny-log) | Structured logging — structlog in one file | ⭐0 | Python |
| [tiny-validator](https://github.com/hussain-alsaibai/tiny-validator) | Data validation — Pydantic in one file | ⭐0 | Python |
| [ai-git-hooks](https://github.com/hussain-alsaibai/ai-git-hooks) | AI-powered Git hooks with local LLMs | ⭐0 | Shell/Python |
| [tiny-worker](https://github.com/hussain-alsaibai/tiny-worker) | Background task queue — Celery in one file | ⭐0 | Python |
| [tiny-events](https://github.com/hussain-alsaibai/tiny-events) | Event bus — Redis Pub/Sub in one file | ⭐0 | Python |
| [tiny-http](https://github.com/hussain-alsaibai/tiny-http) | HTTP client — requests in one file | ⭐0 | Python |
| [container-security-monitor](https://github.com/hussain-alsaibai/container-security-monitor) | Continuous container security with Trivy | ⭐0 | Python |

*All Python tools follow the "zero-dependency, single-file" philosophy. Total ecosystem: 10 libraries (~80KB).*

## Tools

| Tool | Description | Last Verified |
|------|-------------|---------------|
| [Cost Tracker](tools/cost-tracker.md) | API cost monitoring | 2026-06-27 |
| [Plugin Install Guide](tools/plugin-install-guide.md) | OpenClaw plugin management | 2026-06-27 |
| [SnapDB Guide](tools/snapdb-guide.md) | Ultra-lightweight in-memory DB | 2026-06-27 |

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
