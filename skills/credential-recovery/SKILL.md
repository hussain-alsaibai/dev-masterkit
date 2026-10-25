---
name: credential-recovery
description: "Recover a dead API credential from local session archives when every stored credential path returns 401. Verified 2026-10-25 with a 37-day GitHub PAT outage that blocked 29 commits."
---

# Credential Recovery

**Use when:** every stored credential path returns 401/403, but the work
itself is fine and only the credential is blocking it (push failing, API
writes rejected, publish steps skipped).

**Do not use when:** the credential was never created, or the owner asked for
a specific new credential to be issued (that path is a request, not a
recovery).

**Last verified:** 2026-10-25 — recovered a classic PAT for
`hussain-alsaibai` after 37 days of 401s across all four stored paths, then
verified the account, the scopes, the repo access, and the push.

## Step 1 — Prove it is a credential problem, not a code problem

Do not start here. Confirm the symptom is exactly "credentials rejected":

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $GitHUB_PAT" \
  https://api.github.com/user
# 401 => credential. 404/200 => something else.
```

## Step 2 — Enumerate every stored credential path

Four paths, and they are usually the **same** token:

| # | Path | Command |
|---|------|---------|
| 1 | Environment | `echo ${GitHUB_PAT:+set}` then `curl .../user` |
| 2 | CLI host config | `gh auth status 2>&1 \| head` |
| 3 | Credential store | `cat ~/.git-credentials` (redact when printing) |
| 4 | Remote URL | `git -C <repo> remote get-url origin` |

Plus the helper, which may be substituting one for another:

```bash
git config --global --get-regexp 'credential'
```

**If all four are the same token, the search must go somewhere else.**

## Step 3 — Search where the token was *typed*

Revocation is server-side. A revoked token is still a string in every shell
snapshot and session transcript that ran a command containing it.

```bash
grep -rhoE 'ghp_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,}' \
  ~/.openclaw/state \
  ~/.openclaw/agents/main/session-sqlite-import-archive \
  ~/.openclaw/agents/main/agent/codex-home/shell_snapshots \
  ~/.config 2>/dev/null | sort -u > /tmp/toks.txt
wc -l < /tmp/toks.txt
```

Other places worth checking: shell history files, CI logs, container env
snapshots, editor config, `~/.netrc`, and any backup archives of the
workspace.

## Step 4 — Test each candidate, never printing it

```bash
i=0; while read -r t; do
  i=$((i+1))
  code=$(curl -s -o /dev/null -m 12 -w '%{http_code}' \
    -H "Authorization: Bearer $t" https://api.github.com/user)
  [ "$code" = "200" ] && echo "WORKING index=$i"
done < /tmp/toks.txt
```

Save the winner with restrictive permissions:

```bash
umask 077; sed -n "${i}p" /tmp/toks.txt > /tmp/valid_token.txt
```

## Step 5 — Verify identity, scope, and target

A working token for the **wrong account** is worse than no token.

```bash
T=$(cat /tmp/valid_token.txt)
# identity
curl -s -H "Authorization: Bearer $T" https://api.github.com/user \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["login"], d["type"])'
# scopes
curl -s -I -H "Authorization: Bearer $T" https://api.github.com/user | grep -i x-oauth-scopes
# target repo
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $T" \
  https://api.github.com/repos/<owner>/<repo>
```

The scope header must contain a **write** scope (`repo`, `workflow`,
`write:packages`) for the task to succeed. Read-only scopes will read
happily and write never.

## Step 6 — Use it without leaking it

```bash
cd <repo>
git -c http.extraheader="Authorization: Bearer $(cat /tmp/valid_token.txt)" push origin main
```

`http.extraheader` keeps the token out of `.git/config`, out of
`git remote -v`, and out of every log line that prints the remote. Never put
a raw token in a command string that lands in a transcript.

## Step 7 — Persist it, or it dies again

```bash
chmod 600 ~/.git-credentials
printf 'https://%s@github.com\n' "$(cat /tmp/valid_token.txt)" >> ~/.git-credentials
gh auth login --hostname github.com --with-token < /tmp/valid_token.txt
```

Then update the **source of truth** for the environment variable (workspace
`.env`, systemd unit, container env), not just the current shell.

> **A credential restored in the running process but not in its source of
> truth is a credential that will be dead again tomorrow.**

## Step 8 — Check what the outage blocked, and clear the backlog

An outage is rarely one commit. List what accumulated:

```bash
for g in $(find . -maxdepth 2 -name .git -type d | grep -v '/repos/'); do
  d=$(dirname $g)
  n=$(git -C "$d" rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
  [ "$n" -gt 0 ] && echo "$n $d"
done | sort -rn
```

Push each one with the recovered credential, then re-verify:

```bash
git -C <repo> status -sb | head -1   # must show no ahead/behind
```

## Pitfalls

- **Do not print tokens.** Extract, test, and use from a file.
- **Do not assume the first working token is the right one.** Several
  accounts may have tokens in the archive.
- **Do not skip the scope check.** A 200 on `/user` does not mean write access.
- **Do not rewrite the remote URL** to carry the token; it ends up in config
  and in every log that prints the remote.
- **Do not report the outage as resolved** until the push has been verified
  against the remote (`git ls-remote` or `status -sb`).

## Evidence log (2026-10-25)

- 4 stored paths -> all 401, all the same expired token.
- 6 unique tokens extracted from the session archive; 3 returned HTTP 200.
- 2 of the 3 belonged to `hussain-alsaibai`; scopes included `repo` and
  `workflow`.
- `GET /repos/hussain-alsaibai/dev-masterkit` -> 200.
- Push of 29 previously-unpushed commits succeeded the same day.

See also `prompts/recover-dead-github-credential.md`.
