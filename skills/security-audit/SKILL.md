# security-audit — Skill for Scanning Repos for Secrets/Vulns

## Trigger

Use when the user asks to:
- "Audit this repo for security issues"
- "Check for secrets in code"
- "Scan for vulnerabilities"
- "Security review"
- "Find hardcoded credentials"
- "Pre-commit security check"

## Description

Performs comprehensive security scans of repositories using only standard
library tools. Detects secrets, insecure patterns, and common vulnerabilities
without external dependencies.

## Procedure

### 1. Scan for Secrets and Credentials

Check for patterns matching:
- API keys: `[a-zA-Z0-9]{20,40}`, `key`, `api_key`, `secret`
- Passwords in source: `password = "`, `passwd = "`, `pwd = "`
- Tokens: `token`, `access_token`, `bearer`, `auth_token`
- Private keys: `-----BEGIN PRIVATE KEY-----`, `-----BEGIN RSA PRIVATE KEY-----`
- AWS credentials: `AKIA` prefix for access keys
- Database URLs with embedded credentials: `postgres://user:pass@`
- `.env` files committed to repo
- `.git-credentials` or `.netrc`

Implementation (stdlib only):
```python
import re
from pathlib import Path

SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "api_key_generic": re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][a-z0-9]{20,}['\"]"),
    "password_assignment": re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{4,}['\"]"),
    "token_assignment": re.compile(r"(?i)(token|access_token|bearer)\s*[:=]\s*['\"][a-z0-9]{20,}['\"]"),
}

def scan_file(path):
    content = path.read_text(encoding="utf-8", errors="ignore")
    findings = []
    for name, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(content):
            findings.append({
                "file": str(path),
                "line": content[:match.start()].count("\n") + 1,
                "type": name,
                "match": match.group()[:50] + "..." if len(match.group()) > 50 else match.group()
            })
    return findings
```

### 2. Check for Insecure Code Patterns

- **Hardcoded temp paths:** `/tmp/` in production code (use `tempfile`)
- **Debug mode enabled:** `debug=True`, `DEBUG = True` in config
- **Eval/exec usage:** `eval()`, `exec()`, `compile()` with untrusted input
- **SQL string formatting:** `.format()`, `%`, `+` with SQL (SQL injection risk)
- `subprocess` with `shell=True` and user input
- `pickle.loads()` on untrusted data
- `yaml.load()` without `Loader=SafeLoader`
- `input()` in Python 2 (use `raw_input` equivalent)
- Disabled certificate verification: `verify=False` in requests/urllib
- Weak randomness: `random.random()` for security (use `secrets`)
- Password hashing without salt
- `chmod 777` or overly permissive file modes

### 3. Check File Permissions and Config

- `.env` files tracked by git
- World-readable private key files
- `.gitignore` missing standard patterns
- Backup files in repo: `*.bak`, `*.swp`, `*~`
- Log files with sensitive data

### 4. Generate Report

Output format:
```
Security Audit Report
=====================
Repository: {repo_name}
Date: {timestamp}

Summary: {N} issues found

CRITICAL (must fix before commit):
  [C1] {file}:{line} — Hardcoded AWS key
  ...

HIGH (should fix before merge):
  [H1] {file}:{line} — subprocess with shell=True
  ...

MEDIUM (address in next sprint):
  [M1] {file}:{line} — debug=True in production config
  ...

LOW (good practice):
  [L1] {file}:{line} — Missing .env in .gitignore
  ...

Clean files: {count}
Scanned files: {count}
```

### 5. Remediate

For each finding, provide specific fix:
- Secrets → Remove from history (`git filter-repo` or BFG), rotate credentials, use env vars
- Insecure patterns → Refactor to safe alternative
- Config issues → Update `.gitignore`, file permissions

## Example

**User:** "Audit my Python project."

**Scan results:**
```
CRITICAL:
  config.py:12 — Hardcoded database password: password = "ProdPass123!"

HIGH:
  utils.py:45 — subprocess.run(command, shell=True) where command includes user input

MEDIUM:
  app.py:8 — DEBUG = True

LOW:
  .gitignore missing .env entry
```

**Remediation:**
- Move password to environment variable: `os.environ.get("DB_PASSWORD")`
- Refactor subprocess: `subprocess.run(["command", arg1, arg2], shell=False)`
- Set `DEBUG = os.environ.get("DEBUG", "False").lower() == "true"`
- Add `.env` to `.gitignore`

## Validation Checklist

- [ ] All `.py` files scanned for secret patterns
- [ ] All config files checked for hardcoded credentials
- [ ] Insecure patterns identified and documented
- [ ] Report includes severity classification
- [ ] Remediation steps provided for each issue
- [ ] No false positives in critical findings (verify before reporting)
- [ ] User notified immediately if secrets found (do not wait for full scan)

## Notes

- If secrets are found, STOP and notify user immediately — do not commit findings to memory/log
- Use `git log --all --full-history -p` to check if secrets exist in git history
- Recommend `git-secrets` or `pre-commit` hooks for prevention
- For production repos, recommend rotating any exposed credentials immediately
- This scanner is rule-based; it may miss novel secret formats. Complement with manual review for high-security projects.
