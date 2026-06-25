# /release Command

## Trigger

User types: `/release`, `/release patch|minor|major`, or "Prepare a release"

## Description

Bumps version, updates changelog, creates git tag, and optionally pushes to
GitHub. Follows Semantic Versioning (SemVer).

## Usage

```
/release [bump] [--dry-run] [--push]
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `bump` | Version bump type: `patch`, `minor`, `major` | `patch` |
| `--dry-run` | Show what would happen, don't execute | False |
| `--push` | Push tag to origin after creation | False |
| `--message` | Custom tag message | Auto-generated |

## Workflow

1. **Determine current version** — read from `pyproject.toml`, `__init__.py`, or git tags
2. **Calculate new version** — increment per SemVer rules:
   - `patch`: 1.2.3 → 1.2.4 (bug fixes)
   - `minor`: 1.2.3 → 1.3.0 (new features, backward compatible)
   - `major`: 1.2.3 → 2.0.0 (breaking changes)
3. **Validate working tree** — ensure clean git state (no uncommitted changes)
4. **Update version** — write to `pyproject.toml` and `__init__.py`
5. **Update changelog** — prepend entry to `CHANGELOG.md` or `docs/CHANGELOG.md`
6. **Commit** — `git add -A && git commit -m "release: v{new_version}"`
7. **Tag** — `git tag -a v{new_version} -m "Release v{new_version}"`
8. **Push (optional)** — `git push && git push --tags`

## Changelog Entry Format

```markdown
## [1.2.4] - 2024-03-15

### Fixed
- Description of bug fix

### Changed
- Description of change
```

## Example

**User:** `/release minor --push`

**Result:**
```
Current version: 1.2.3
New version: 1.3.0

Changes since 1.2.3:
- feat: add batch URL processing
- fix: handle unicode in domain names
- docs: update API reference

Commit: release: v1.3.0
Tag: v1.3.0
Pushed to origin: ✅
```

## Validation Checklist

- [ ] Working tree is clean (no uncommitted changes)
- [ ] All tests pass before release
- [ ] Version updated in all relevant files
- [ ] Changelog updated with all changes since last tag
- [ ] Git commit created with release message
- [ ] Git tag created with annotation
- [ ] (Optional) Pushed to remote successfully

## Notes

- If working tree is dirty, refuse to release unless `--force` (warn strongly)
- Use `git log --oneline $(git describe --tags --abbrev=0)..HEAD` to list changes
- If no previous tag, use initial commit as baseline
- For `--push`, verify remote is accessible first (`git ls-remote`)
- Changelog format follows Keep a Changelog v1.1.0
