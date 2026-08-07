# Code Verify

Verify code before sending it. Catch syntax errors, missing deps, and logic flaws *before* they reach the user.

## When to Verify

**Always verify before sending if:**
- Code block is > 5 lines
- It's a command that modifies state (rm, drop, delete, update, insert)
- It's a config file that needs to parse correctly
- User asked for "working code" or "tested code"

**Skip verification if:**
- It's pseudocode or a sketch
- It's a one-liner that's obviously safe (echo, cat, ls)
- Environment lacks the interpreter (no python, no node, etc.)

## Per-Language Patterns

### Bash / Shell

```bash
# Syntax check only (safe, no execution)
bash -n script.sh

# If you need to test execution, use a subshell with set -e
(
  set -e
  source script.sh
)
```

**Check for:**
- Unclosed quotes or backticks
- Missing `fi`, `done`, `esac`
- Unset variables used without `${VAR:-default}`
- Commands that could be destructive (rm -rf, drop, delete)

### JavaScript / Node.js

```bash
# Syntax check
node --check script.js
node -c script.js

# Quick eval test (for small snippets)
node -e "$(cat snippet.js)"
```

**Check for:**
- Missing `await` on async calls
- Undefined variables (use `node --check` or a linter)
- JSON.parse without try/catch
- Callback hell without error handling

### Python

```bash
# Syntax check
python -m py_compile script.py
python3 -m py_compile script.py

# If available, run a quick import test
python -c "import script"
```

**Check for:**
- Indentation errors (mixing tabs and spaces)
- Missing `self` in method definitions
- `except:` without specific exception types
- File operations without `with` context manager

### Go

```bash
# Format + vet (catches many issues)
go fmt ./...
go vet ./...

# Build test (catches compile errors)
go build ./...
```

**Check for:**
- Unused imports or variables
- Error return values ignored
- `defer` inside loops
- Race conditions on shared state

### JSON / YAML

```bash
# JSON validation
python3 -c "import json; json.load(open('file.json'))"

# YAML validation (if python3-yaml available)
python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"
```

**Check for:**
- Trailing commas in JSON (not allowed)
- Unclosed brackets or braces
- YAML indentation inconsistencies
- Duplicate keys

### HTML / CSS

```bash
# No great native validator, but check for:
# - Unclosed tags
# - Missing quotes on attributes
# - CSS syntax errors (unclosed braces)
```

## The Verification Loop

```
1. Write code
2. Ask: "Can I verify this?"
3. If yes → run the appropriate check above
4. If error → fix it, goto 2
5. If no interpreter available → reason through edge cases manually
6. If destructive → ask user before sending, or wrap in dry-run flag
7. Send verified code
```

## Destructive Command Checklist

Before sending any command that modifies state, verify:

| Command Pattern | Required Safeguard |
|-----------------|-------------------|
| `rm` | Use `trash` or `rm -i` or confirm with user |
| `DROP TABLE` | Add `IF EXISTS`, confirm with user |
| `DELETE FROM` | Add `WHERE` clause, show row count first |
| `UPDATE` | Add `WHERE` clause, never without it |
| `INSERT` | Check for duplicates, use `ON CONFLICT` |
| `ALTER` | Show current schema first |
| `chmod` | Use `+x` not `777`, show current perms |
| `chown` | Never `chown -R` without confirming path |
| `docker rm` | Use `--filter` to avoid removing wrong containers |
| `kubectl delete` | Always specify namespace, confirm resource name |

## Dry-Run Pattern

When possible, show what *would* happen before doing it:

```bash
# Instead of:
rm -rf /path/to/files

# Show:
find /path/to/files -type f | head -20
echo "Will delete $(find /path/to/files -type f | wc -l) files. Proceed?"
```

```sql
-- Instead of:
DELETE FROM users WHERE last_login < '2024-01-01';

-- Show:
SELECT COUNT(*) FROM users WHERE last_login < '2024-01-01';
-- "Will delete 1,247 users. Proceed?"
```

## Common Mistakes to Catch

| Mistake | Fix |
|---------|-----|
| `if [ $VAR == "value" ]` | Quote: `if [ "$VAR" == "value" ]` |
| `rm -rf $DIR/` | Quote: `rm -rf "$DIR"/` or check `$DIR` is set |
| `python script.py` without `python3` | Use `python3` explicitly |
| `node script` without `.js` | Add extension: `node script.js` |
| `sudo` in scripts | Remove, use proper permissions |
| Hardcoded paths | Use environment variables or relative paths |
| No error handling | Add `set -e`, `try/catch`, `if err != nil` |
| Missing shebang | Add `#!/usr/bin/env bash` or `#!/usr/bin/env python3` |

## When Verification Fails

If you can't verify code before sending:
1. Say so explicitly: "I can't test this in this environment, but the logic is..."
2. Add a disclaimer: "⚠️ Untested — verify before running in production"
3. Provide a test command the user can run: "You can verify with: bash -n script.sh"

## Integration

This skill is a mental checklist, not a separate tool call. Before sending code:
1. Glance at the language
2. Pick the verification pattern above
3. Run it (or reason through it)
4. Fix errors
5. Send

For critical or complex code, spawn a subagent with context="fork" and ask it to verify and critique.

---

*Pattern: Verify Before Send | Source: Self-improvement initiative 2026-06-09*
