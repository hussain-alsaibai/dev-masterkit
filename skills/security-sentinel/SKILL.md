# security-sentinel — Skill for Security Scanning

## Trigger

Use when the user asks to:
- "Scan for vulnerabilities" or "security audit"
- "Check for secrets" or "find API keys"
- "Review code for security issues"
- "Audit file permissions"
- "Check for exposed credentials"

## Description

Scan workspaces, repositories, and code for security vulnerabilities, exposed secrets, and misconfigurations. Uses only Python's standard library — no external security tools required.

## Procedure

### 1. Scan for Exposed Secrets

```python
# scan_secrets.py — find API keys and tokens in files
import os
import re
from pathlib import Path

# Patterns for common secrets
SECRET_PATTERNS = {
    'AWS Access Key': r'AKIA[0-9A-Z]{16}',
    'GitHub Token': r'ghp_[a-zA-Z0-9]{36}',
    'GitHub PAT': r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}',
    'Slack Token': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}(-[a-zA-Z0-9]{24})?',
    'Generic API Key': r'api[_-]?key[_-]?(=|:)\s*["\']?[a-zA-Z0-9]{16,}["\']?',
    'Bearer Token': r'bearer\s+[a-zA-Z0-9_\-\.]+',
    'Private Key': r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
    'Password in URL': r'https?://[^:]+:[^@]+@[^/]+',
    'Hardcoded Password': r'password[_-]?(=|:)\s*["\'][^"\']{4,}["\']',
}

def scan_directory(path, exclude_dirs=None):
    exclude_dirs = exclude_dirs or {'.git', 'node_modules', '__pycache__', '.venv'}
    findings = []
    
    for root, dirs, files in os.walk(path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in files:
            # Only scan text files
            if not any(filename.endswith(ext) for ext in ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.md', '.txt', '.sh', '.cfg', '.ini', '.toml']):
                continue
            
            filepath = Path(root) / filename
            try:
                content = filepath.read_text(errors='ignore')
                for secret_type, pattern in SECRET_PATTERNS.items():
                    for match in re.finditer(pattern, content):
                        # Mask the secret in output
                        secret = match.group(0)
                        masked = secret[:4] + '*' * (len(secret) - 8) + secret[-4:]
                        findings.append({
                            'file': str(filepath),
                            'type': secret_type,
                            'line': content[:match.start()].count('\n') + 1,
                            'match': masked,
                            'severity': 'HIGH' if 'Private Key' in secret_type or 'Password' in secret_type else 'MEDIUM'
                        })
            except (IOError, OSError):
                continue
    
    return findings

# Usage
if __name__ == '__main__':
    results = scan_directory('.')
    print(f"Found {len(results)} potential secrets:")
    for finding in results:
        print(f"  [{finding['severity']}] {finding['file']}:{finding['line']} — {finding['type']}: {finding['match']}")
```

### 2. Check File Permissions

```python
import os
import stat
from pathlib import Path

def check_permissions(path):
    """Check for overly permissive files."""
    issues = []
    
    for root, dirs, files in os.walk(path):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for item in files + dirs:
            filepath = Path(root) / item
            try:
                mode = filepath.stat().st_mode
                
                # Check world-writable
                if mode & stat.S_IWOTH:
                    issues.append({
                        'file': str(filepath),
                        'issue': 'World-writable',
                        'mode': oct(mode)[-3:],
                        'severity': 'HIGH'
                    })
                
                # Check world-executable (for files)
                if item in files and (mode & stat.S_IXOTH):
                    issues.append({
                        'file': str(filepath),
                        'issue': 'World-executable',
                        'mode': oct(mode)[-3:],
                        'severity': 'MEDIUM'
                    })
                
                # SSH keys should be 600
                if 'ssh' in str(filepath) and item.endswith(('.pem', '.key', '_rsa', '_dsa', '_ecdsa', '_ed25519')):
                    if oct(mode)[-3:] != '600':
                        issues.append({
                            'file': str(filepath),
                            'issue': 'SSH key not 600',
                            'mode': oct(mode)[-3:],
                            'severity': 'HIGH'
                        })
                
            except (IOError, OSError):
                continue
    
    return issues

# Usage
issues = check_permissions('.')
for issue in issues:
    print(f"  [{issue['severity']}] {issue['file']} — {issue['issue']} (mode: {issue['mode']})")
```

### 3. Code Security Review

```python
import ast
from pathlib import Path

def review_python_security(filepath):
    """Review Python code for common security issues."""
    issues = []
    content = Path(filepath).read_text()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []
    
    for node in ast.walk(tree):
        # Check for eval() usage
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'eval':
                issues.append({'line': node.lineno, 'issue': 'eval() detected — dangerous', 'severity': 'HIGH'})
            if isinstance(node.func, ast.Name) and node.func.id == 'exec':
                issues.append({'line': node.lineno, 'issue': 'exec() detected — dangerous', 'severity': 'HIGH'})
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'format' and isinstance(node.func.value, ast.Constant):
                issues.append({'line': node.lineno, 'issue': 'String formatting with untrusted input', 'severity': 'MEDIUM'})
        
        # Check for SQL string formatting (basic)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            issues.append({'line': node.lineno, 'issue': 'String formatting (%) detected — potential SQL injection', 'severity': 'MEDIUM'})
        
        # Check for hardcoded IPs
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', node.value):
                issues.append({'line': node.lineno, 'issue': f'Hardcoded IP: {node.value}', 'severity': 'LOW'})
        
        # Check for debug mode
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('DEBUG', 'debug'):
                    if isinstance(node.value, ast.Constant) and node.value.value is True:
                        issues.append({'line': node.lineno, 'issue': 'DEBUG=True detected', 'severity': 'MEDIUM'})
    
    return issues

# Usage
for py_file in Path('.').rglob('*.py'):
    if '.git' not in str(py_file):
        issues = review_python_security(py_file)
        for issue in issues:
            print(f"  [{issue['severity']}] {py_file}:{issue['line']} — {issue['issue']}")
```

### 4. Full Security Scan

```python
# security_scan.py — comprehensive scan
def full_security_scan(target_dir='.'):
    print(f"🔒 Security Scan: {target_dir}\n")
    
    # 1. Secrets
    print("=== Secret Scan ===")
    secrets = scan_directory(target_dir)
    print(f"  Found: {len(secrets)} potential secrets")
    for s in secrets[:10]:  # Show first 10
        print(f"    [{s['severity']}] {s['file']}:{s['line']} — {s['type']}")
    
    # 2. Permissions
    print("\n=== Permission Scan ===")
    perms = check_permissions(target_dir)
    print(f"  Found: {len(perms)} permission issues")
    for p in perms[:10]:
        print(f"    [{p['severity']}] {p['file']} — {p['issue']}")
    
    # 3. Code review
    print("\n=== Code Review ===")
    code_issues = []
    for py_file in Path(target_dir).rglob('*.py'):
        if '.git' not in str(py_file):
            issues = review_python_security(py_file)
            code_issues.extend(issues)
    print(f"  Found: {len(code_issues)} code issues")
    for issue in code_issues[:10]:
        print(f"    [{issue['severity']}] Line {issue['line']} — {issue['issue']}")
    
    # Summary
    total = len(secrets) + len(perms) + len(code_issues)
    high = sum(1 for i in secrets if i['severity'] == 'HIGH') + \
           sum(1 for i in perms if i['severity'] == 'HIGH') + \
           sum(1 for i in code_issues if i['severity'] == 'HIGH')
    
    print(f"\n=== Summary ===")
    print(f"  Total issues: {total}")
    print(f"  HIGH severity: {high}")
    print(f"  Status: {'⚠️ FAIL' if high > 0 else '✅ PASS'}")
    
    return {
        'secrets': len(secrets),
        'permissions': len(perms),
        'code_issues': len(code_issues),
        'high_severity': high,
        'status': 'FAIL' if high > 0 else 'PASS'
    }

if __name__ == '__main__':
    full_security_scan()
```

### 5. Check Dependencies (if requirements.txt exists)

```python
def check_vulnerable_dependencies():
    """Check requirements.txt for known vulnerable packages."""
    req_file = Path('requirements.txt')
    if not req_file.exists():
        return []
    
    # Known vulnerable versions (simplified — in production, use a CVE database)
    VULNERABLE = {
        'requests': ['<2.20.0'],
        'urllib3': ['<1.23'],
        'django': ['<2.2', '<3.0.7', '<3.1'],
        'flask': ['<1.0'],
        'pillow': ['<8.1.1'],
    }
    
    issues = []
    for line in req_file.read_text().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Simple parsing
        if '==' in line:
            pkg, version = line.split('==', 1)
            pkg = pkg.strip().lower()
            version = version.strip()
            
            if pkg in VULNERABLE:
                issues.append({
                    'package': pkg,
                    'version': version,
                    'issue': f'Potentially vulnerable {pkg}=={version}',
                    'severity': 'MEDIUM'
                })
    
    return issues
```

## Checklist

- [ ] No exposed API keys, tokens, or passwords in code
- [ ] No private keys or certificates in repository
- [ ] No hardcoded credentials in configuration files
- [ ] File permissions are appropriate (no world-writable files)
- [ ] No use of `eval()` or `exec()` on untrusted input
- [ ] No SQL injection vectors (string formatting for queries)
- [ ] No debug mode enabled in production code
- [ ] Dependencies checked for known vulnerabilities
- [ ] `.env` files are in `.gitignore`
- [ ] No `.git` or `.ssh` directories exposed

## Examples

**Quick daily security check:**
```bash
#!/bin/bash
# daily-security-check.sh

echo "Running security scan..."

# Check for secrets
grep -r "api_key\|apikey\|password\|secret" --include="*.py" --include="*.js" --include="*.json" . | grep -v node_modules | grep -v .git

# Check for .env files
find . -name ".env" -not -path "*/.git/*" -not -path "*/node_modules/*"

# Check permissions
find . -perm -002 -type f | grep -v node_modules

echo "Scan complete."
```

## See Also

- `skills/security-audit/SKILL.md` — Deep security audit for repositories
- `commands/audit/command.md` — `/audit` command reference
- `agents/security-reviewer/agent.md` — Security review agent persona

---

*Last verified: 2026-06-26*
