# Dev-MasterKit

> A comprehensive developer toolkit for AI-assisted repository creation, testing, documentation, security auditing, and performance benchmarking. Zero dependencies. Production-ready.

## Features

- 🏗️ **Repository Scaffolding** — Create zero-dependency Python projects with modern `pyproject.toml` packaging
- 🧪 **Test Automation** — Generate comprehensive unittest suites with mocking, edge cases, and error conditions
- 📝 **Documentation Generation** — Auto-generate professional READMEs, API docs, and usage guides
- 🔒 **Security Auditing** — Scan for secrets, credentials, and insecure patterns using only stdlib
- ⚡ **Performance Benchmarking** — Measure and compare code with statistical analysis
- 🤖 **Agent Personas** — Specialized agents for architecture, security, and performance
- 🔄 **Full Pipeline Orchestration** — End-to-end automation: create → code → test → audit → push

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

## Structure

```
dev-masterkit/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/                   # Reusable skill files
│   ├── repo-creator/         # Create zero-dependency Python repos
│   ├── test-automation/      # Auto-generate test suites
│   ├── doc-generator/        # Generate README + docs
│   ├── security-audit/       # Scan for secrets/vulns
│   └── benchmark-runner/     # Performance benchmarking
├── commands/                 # Chat commands
│   ├── scaffold/             # /scaffold — create repo
│   ├── test/                 # /test — run test suite
│   ├── benchmark/            # /benchmark — benchmark
│   ├── release/              # /release — version + tag
│   └── audit/                # /audit — security scan
├── agents/                   # Agent personas
│   ├── python-architect/     # Design Python architectures
│   ├── security-reviewer/    # Review code for security
│   └── performance-optimizer/# Optimize Python performance
├── orchestrators/            # Multi-step workflows
│   └── full-repo-pipeline/   # Create → code → test → push
├── README.md
└── LICENSE
```

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
