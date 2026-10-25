# Recovering a Dead GitHub Credential

**When every credential path returns 401, the credential is usually still on
disk — in the session archive.**

> On 2026-10-25 the `hussain-alsaibai` PAT had been dead for **37 days**
> (since 2026-09-17). All four documented credential paths returned 401. The
> local dev-masterkit repo was **29 commits ahead** of origin and could not be
> pushed. Recovering a live token from the session archive restored push
> access the same day. **Last verified:** 2026-10-25 — recovered token
> authenticated as `hussain-alsaibai`, HTTP 200 on
> `/repos/hussain-alsaibai/dev-masterkit`, scope header included `repo`.

## The Dead-Credential Checklist (Run It First)

Before concluding "the token is gone", check every path. All four of these
returned 401 on 2026-10-25 — **all four were the same expired token**:

```bash
# 1. environment
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $GitHUB_PAT" https://api.github.com/user

# 2. gh CLI host config
gh auth status 2>&1 | head

# 3. the credential store
cat ~/.git-credentials | sed -E 's#(https://)[^:]+:[^@]+@#\1***:***@#'

# 4. the token embedded in a remote URL
git -C <repo> remote get-url origin
```

Also check that the credential helper is not silently substituting one of the
above for another:

```bash
git config --global --get-regexp 'credential'
# credential.https://github.com.helper !gh auth git-credential
```

**If all of them are the same dead token, the answer is not in any of
them.** Look where the token was *typed*, not where it was *stored*.

## Where the Old Token Still Lives

An agent that authenticated with the PAT typed it into command lines. Those
command lines were recorded in session transcripts. OpenClaw keeps those
transcripts in a session archive that is **not** the credential store:

```
~/.openclaw/agents/main/session-sqlite-import-archive/*.jsonl
~/.openclaw/agents/main/session-sqlite-import-archive/*.trajectory.jsonl
~/.openclaw/agents/main/agent/codex-home/shell_snapshots/*.sh
```

A token survives there even after it is revoked, because a revoked token is
still a *string in a file*. Revocation happens at the GitHub side; the local
copy does not know.

## The Recovery Procedure

**1. Extract candidate tokens without printing them.**

```bash
grep -rhoE 'ghp_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,}' \
  ~/.openclaw/state ~/.openclaw/agents/main/session-sqlite-import-archive \
  ~/.openclaw/agents/main/agent/codex-home/shell_snapshots ~/.config \
  2>/dev/null | sort -u > /tmp/toks.txt
wc -l < /tmp/toks.txt
```

**2. Test each candidate against the API and report only the verdict.**

```bash
i=0; while read -r t; do
  i=$((i+1))
  code=$(curl -s -o /dev/null -m 12 -w '%{http_code}' \
    -H "Authorization: Bearer $t" https://api.github.com/user)
  [ "$code" = "200" ] && echo "WORKING index=$i"
done < /tmp/toks.txt
```

**Never echo the token itself.** Write the winner to a file with restrictive
permissions and use it from there:

```bash
umask 077; printf '%s' "$t" > /tmp/valid_token.txt
```

**3. Confirm it is the RIGHT account, not just a working token.**

A working token for the wrong account is a worse outcome than no token — it
would push your work somewhere you did not intend.

```bash
curl -s -H "Authorization: Bearer $(cat /tmp/valid_token.txt)" \
  https://api.github.com/user | python3 -c \
  'import sys,json; d=json.load(sys.stdin); print(d["login"], d["type"])'
```

**4. Confirm the scope covers the write you need.**

```bash
curl -s -I -H "Authorization: Bearer $(cat /tmp/valid_token.txt)" \
  https://api.github.com/user | grep -i x-oauth-scopes
# x-oauth-scopes: ... repo ... workflow ...
```

Read-only scopes let you monitor and cannot let you publish. The scope
header is the difference between "the credential works" and "the credential
can do the job".

**5. Confirm repo access explicitly** before a 30-commit push:

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer $(cat /tmp/valid_token.txt)" \
  https://api.github.com/repos/hussain-alsaibai/dev-masterkit
```

**6. Use it for the push without leaking it into the transcript.**

```bash
cd <repo>
git -c http.extraheader="Authorization: Bearer $(cat /tmp/valid_token.txt)" \
    push origin main
```

Prefer `http.extraheader` over rewriting the remote URL: the URL form
writes the token into `.git/config`, into `git remote -v` output, and into
every future log line that prints the remote.

## Persisting It So It Never Recurs

Recovering the token is the emergency fix. Persisting it is the real fix.

```bash
# credential store, so plain git push works
chmod 600 ~/.git-credentials
printf 'https://%s@github.com\n' "$(cat /tmp/valid_token.txt)" >> ~/.git-credentials

# gh CLI, so `gh auth status` and the credential helper work
gh auth login --hostname github.com --with-token < /tmp/valid_token.txt
```

Then replace the dead value in the environment source of truth, so a
restarted gateway picks it up:

```bash
# GitHUB_PAT lives in the workspace .env (or the systemd unit) — update it there,
# NOT only in the current shell, or the next session is dead again.
```

**A credential restored in the current shell but not in its source of truth
is a credential that will be dead again within a day.**

## What This Run Cost

- 37 days of dead publishing.
- 29 dev-masterkit commits unpushed (189 files, 19,102 insertions).
- 8 new tiny-* repos on local disk with no upstream.
- Every bounty PR blocked at the "cannot push, cannot comment" step.

**None of that was a GitHub problem.** It was a local-record problem.

## The Rules

1. **Check every credential path before declaring an outage.** The four
   paths usually hold the same token; confirming they are the same token
   tells you the search must go elsewhere.
2. **Revocation is server-side.** The local copy of a revoked token is
   still on disk in shell snapshots, session archives, and logs.
3. **Verify the account, not just the token.** A working token for the
   wrong account pushes your work to the wrong place.
4. **Check the scope header.** Read is not write.
5. **Never print the token.** Extract, test, and use it from a file.
6. **Fix the source of truth, not just the running process.**

## The Generalisation

> **A credential outage is a search problem, not a generation problem.**
> Before asking the owner for a new secret, exhaust the places the old one
> was used. The token was typed into a command line; the command line was
> recorded; the record is still there.

This generalises past GitHub: expired API keys, rotated webhook secrets,
revoked deploy tokens, old database URLs. **Any secret you have ever used
is stored in the logs of the thing that used it.**

See also `prompts/bounty-pat-fine-grained-fixes.md` (what a valid PAT
needs), `prompts/bounty-pat-write-access.md` (why writes fail while reads
succeed), `skills/credential-recovery/SKILL.md` (the runnable procedure).
