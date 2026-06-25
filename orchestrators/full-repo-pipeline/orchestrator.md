# full-repo-pipeline Orchestrator

## Description

A multi-step workflow that automates the entire repository lifecycle:
create → code → test → document → audit → push.

## Trigger

User asks to:
- "Create and push a new repo"
- "Full pipeline for [project-name]"
- "End-to-end repo creation"
- "Generate, test, and publish"

## Workflow

### Step 1: Scaffold Repository

**Skill:** `repo-creator`

Actions:
1. Accept project name and requirements
2. Create directory structure
3. Generate core files (pyproject.toml, __init__.py, main.py)
4. Generate tests (test_main.py)
5. Generate CI config
6. Initialize git repository
7. Run local validation: `python -m unittest discover`

**Output:** Clean, passing repository ready for development

### Step 2: Generate Implementation

**Skill:** `python-architect` (agent)

Actions:
1. Design module architecture
2. Implement core business logic
3. Implement CLI/API entry points
4. Add type hints and docstrings
5. Run `python -m py_compile` on all files

**Output:** Working implementation with clean code

### Step 3: Generate Test Suite

**Skill:** `test-automation`

Actions:
1. Analyze implementation for testable surfaces
2. Generate unittest-based test files
3. Cover happy path, edge cases, errors
4. Mock external dependencies
5. Run full test suite: `python -m unittest discover -v`
6. Fix failures until 100% pass

**Output:** Comprehensive test suite, all tests passing

### Step 4: Generate Documentation

**Skill:** `doc-generator`

Actions:
1. Analyze code structure and API
2. Generate README.md with badges, features, quick start
3. Generate API reference documentation
4. Generate usage examples
5. Generate CONTRIBUTING.md (if open source)
6. Validate all code examples by executing them

**Output:** Professional documentation ready for GitHub

### Step 5: Security Audit

**Skill:** `security-audit`

Actions:
1. Scan all files for secrets/credentials
2. Check for insecure code patterns
3. Verify .gitignore and file permissions
4. Check git history for secrets (if repo existed before)
5. Generate security report
6. If CRITICAL findings: STOP pipeline, notify user immediately
7. If safe issues found: auto-fix or flag for user

**Output:** Clean security report or halted pipeline with findings

### Step 6: Benchmark (Optional)

**Skill:** `benchmark-runner`

Actions:
1. Identify performance-critical functions
2. Generate benchmark harness
3. Run benchmarks with statistical analysis
4. Compare against baseline if available
5. Generate benchmark report

**Output:** Performance baseline and recommendations

### Step 7: Release Preparation

**Skill:** `release` (command)

Actions:
1. Bump version (patch for initial release → 0.1.0)
2. Update CHANGELOG.md
3. Create git commit: `release: v0.1.0`
4. Create annotated git tag: `v0.1.0`

**Output:** Tagged release ready for GitHub

### Step 8: Push to GitHub

**Actions:**
1. Create GitHub repository via API
2. Add remote: `git remote add origin <url>`
3. Push code: `git push -u origin main`
4. Push tags: `git push --tags`
5. Verify: `git ls-remote origin`

**Output:** Live GitHub repository with CI running

## Error Handling

| Step | Failure | Action |
|------|---------|--------|
| 1. Scaffold | Tests fail | Fix tests or implementation, retry |
| 2. Implement | Compile error | Fix syntax, retry |
| 3. Test | Tests fail | Debug, fix, rerun until pass |
| 4. Docs | Examples fail | Fix example code or docs |
| 5. Audit | CRITICAL secret found | STOP, notify user, do not proceed |
| 6. Benchmark | N/A | Log warning, continue |
| 7. Release | Dirty working tree | Refuse, ask user to commit/stash |
| 8. Push | API/auth failure | Log error, provide manual instructions |

## Example

**User:** "Create and push a URL cleaner repo."

**Pipeline execution:**
```
[1/8] Scaffold: url-cleaner
        ✓ Directory created
        ✓ Tests pass

[2/8] Implement: normalize_url(), is_valid_url()
        ✓ All files compile

[3/8] Test: 12 tests generated
        ✓ All pass (0 failures)

[4/8] Docs: README + API reference
        ✓ Examples verified

[5/8] Audit: 23 files scanned
        ✓ No secrets found
        ✓ No insecure patterns

[6/8] Benchmark: normalize_url()
        Mean: 0.045ms | OK for production

[7/8] Release: v0.1.0
        ✓ Commit created
        ✓ Tag v0.1.0

[8/8] Push: github.com/hussain-alsaibai/url-cleaner
        ✓ Repository created
        ✓ Code pushed
        ✓ CI running

Complete: https://github.com/hussain-alsaibai/url-cleaner
```

## Notes

- Each step feeds into the next: tests validate implementation, docs describe tested code
- Security audit is a gate: if it fails, pipeline stops
- Benchmarks are informational: don't block on performance unless user requests
- Pipeline can be resumed from any step if interrupted
- All steps use zero-dependency approach (stdlib only)
