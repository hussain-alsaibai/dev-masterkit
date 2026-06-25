# /audit Command

## Trigger

User types: `/audit`, `/audit <path>`, or "Security audit"

## Description

Scans the repository for security issues: secrets, credentials, insecure patterns,
and misconfigurations. Reports findings by severity with remediation steps.

## Usage

```
/audit [path] [--severity=LEVEL] [--history] [--fix]
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `path` | Directory or file to audit | Current repo |
| `--severity` | Minimum severity to report: `critical`, `high`, `medium`, `low`, `all` | `all` |
| `--history` | Also scan git history for secrets | False |
| `--fix` | Automatically fix safe issues (permissions, .gitignore) | False |

## Workflow

1. **Scan files** — iterate over `.py`, `.json`, `.yml`, `.env`, config files
2. **Pattern matching** — detect secrets, credentials, API keys
3. **Code analysis** — find insecure patterns (eval, shell=True, etc.)
4. **Config check** — verify .gitignore, file permissions
5. **Git history (optional)** — scan all commits for secrets
6. **Severity classification** — assign critical/high/medium/low
7. **Generate report** — formatted findings with file:line references
8. **Auto-fix (optional)** — fix low-risk issues automatically

## Output Format

```
Security Audit Report
=====================
Repository: /home/user/project
Date: 2024-03-15T10:30:00Z
Files scanned: 23

CRITICAL (1)
------------
[CRITICAL] config.py:12
  Hardcoded database password: password = "..."
  Remediation: Move to environment variable
  Fix: export DB_PASSWORD="..."; python -c "import os; os.environ['DB_PASSWORD']"

HIGH (1)
--------
[HIGH] utils.py:45
  subprocess.run(command, shell=True) with user input
  Remediation: Use shell=False with argument list

MEDIUM (2)
----------
[MEDIUM] app.py:8
  DEBUG = True in production config
  ...

LOW (1)
-------
[LOW] .gitignore
  Missing .env entry
  Auto-fixed: ✅

Summary: 5 issues (1 critical, 1 high, 2 medium, 1 low)
Auto-fixed: 1
```

## Example

**User:** `/audit --history --fix`

**Result:**
```
Scanning git history... found 45 commits
Scanning current files... 23 files

CRITICAL: 1 finding
- config.py:12 — hardcoded password (remove from history with git-filter-repo)

HIGH: 0 findings
MEDIUM: 2 findings
- app.py:8 — DEBUG=True
- auth.py:23 — weak token generation

LOW: 1 finding
- .gitignore missing .env (auto-fixed ✅)

Recommendation: Rotate exposed credentials immediately.
```

## Notes

- Uses `security-audit` skill for scanning logic
- Stops immediately and notifies user if CRITICAL secrets found
- `--fix` only applies to safe changes (permissions, .gitignore)
- Never auto-fixes code logic or removes secrets (requires user confirmation)
- If secrets found in history, recommend `git-filter-repo` or BFG Repo-Cleaner
