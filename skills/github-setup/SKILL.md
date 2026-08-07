---
name: github-setup
description: "Configure GitHub identity and Personal Access Token (PAT) for autonomous agent operations using the 'store' credential helper."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔑",
        "requires": { "bins": ["git"] },
      },
  }
---

# GitHub Setup Skill

This skill documents how to configure an autonomous agent (like me) with a persistent GitHub identity and PAT-based authentication.

## 1. Set Identity

Establish the agent's GitHub username and email. This ensures all commits are correctly attributed.

```bash
git config --global user.name "alsaibaiclaw"
git config --global user.email "alsaibaiclaw@users.noreply.github.com"
```

## 2. Enable Persistent Credentials

Use the `store` credential helper to save the PAT to a local file so the agent doesn't need to authenticate manually for every operation.

```bash
git config --global credential.helper store
```

## 3. Configure the PAT

Store the token in the `.git-credentials` file. This file must be secured with restricted permissions.

### Format
The file should contain a single line in this format:
`https://<username>:<token>@github.com`

### Implementation
```bash
# Create the file with restricted permissions first
touch ~/.git-credentials
chmod 600 ~/.git-credentials

# Add the credentials (replace <username> and <token>)
echo "https://alsaibaiclaw:YOUR_GITHUB_PAT@github.com" > ~/.git-credentials
```

## 4. Verification

Verify the setup by checking the git configuration and performing a test operation.

```bash
# Check config
git config --list

# Verify file permissions
ls -la ~/.git-credentials

# Test push (dry run)
git push --dry-run
```

## Security Best Practices
- **Scope the PAT:** Only grant the minimum required permissions (e.g., `repo` scope).
- **Hardened Permissions:** Always ensure `.git-credentials` is `600`.
- **Isolation:** Run this inside a container to keep credentials separate from the host system.
