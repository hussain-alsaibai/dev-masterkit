# A Dead Credential Named In A Prompt Fails Every Run That Trusts It

**A rule for any recurring job whose instructions name a credential.**

> Found 2026-11-02. Three scheduled jobs said *"push using the
> hussain-alsaibai account (token from the `GitHUB_PAT` env var)"*. The token
> had been dead. **Last verified:** 2026-11-02 — both credentials probed
> directly on the same host at the same moment, and the push path was proved
> end to end with a dry run:
>
> ```
> GitHUB_PAT   (93-char fine-grained, github_pat_...)  -> HTTP 401  DEAD
> gh auth token (40-char classic, ghp_...)            -> HTTP 200  LIVE
> ```
>
> ```
> git push --dry-run  (gh token)      -> Everything up-to-date
> git push --dry-run  (GitHUB_PAT)    -> Invalid username or token.
>                                       Password authentication is not
>                                       supported for Git operations.
> ```

## The Rule

> **When a credential dies, grep every prompt and job description for its
> name. The fix is not to remove the reference — it is to name the dead
> credential as dead in the prompt, so the next agent does not rediscover
> it.**

This is the same defect the bounty scanner hit on 2026-10-27, three weeks
later, in a different place: **the prompt is the credential**, and the prompt
was never updated when the credential died.

## Why Removing The Reference Is Not Enough

If you merely delete the credential name from the prompt, the next agent has
no idea a credential ever existed there — and no signal that the working one
is somewhere else. The failure returns in a new costume.

Name it:

```
Push to main using the hussain-alsaibai account.

Use the token from the gh CLI credential store (`gh auth token`).

The `GitHUB_PAT` env var is a DEAD token (93-char fine-grained,
github_pat_...) and returns HTTP 401. Do not use it. Last verified:
2026-11-02 — `gh auth token` returned HTTP 200 on the same host.
```

That version is self-documenting. The next agent knows both which credential
works and which one does not, and it can skip the probe.

## The One-Pass Grep

```bash
# Every occurrence of the dead credential's name, in one pass.
grep -rn "GitHUB_PAT" ~/.openclaw/cron/ ~/.openclaw/openclaw.json \
  ~/.openclaw/workspace/ 2>/dev/null
```

In this instance that single command found all three job prompts at once.
**The three failures had one cause and it was findable with one grep.**

## The Probe Is Cheap — Do It Before Assuming

A credential is not dead because a job failed with it. Probe it:

```bash
# 1. The candidate that is supposed to work
gh auth token | head -c 4; echo
curl -s -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer $(gh auth token)" https://api.github.com/user

# 2. The candidate that is supposed to be dead
curl -s -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer $GitHUB_PAT" https://api.github.com/user
```

**Credential order is not validity** — the resolver that returns the *first*
credential it finds will keep returning the dead one, because the dead one
is earlier in the list. See `prompts/credential-order-is-not-validity.md` for
that defect, and `prompts/recover-dead-github-credential.md` for recovering a
credential that is dead in every stored location.

## The Dry Run Is The Proof

A config diff shows the right string. A dry run exercises the exact path the
job would take, and it distinguishes **"auth failed"** from **"nothing to
push"** in one command:

```bash
# Force the candidate credential through the real push path.
TOKEN=$(gh auth token)
git -c http.extraheader="AUTHORIZATION: basic $(printf 'x-access-token:%s' "$TOKEN" | base64 -w0)" \
    push --dry-run origin main
```

The same command with the dead token produces the authentication error. That
pair is the whole proof: it shows the credential works, the path works, and
the failure mode of the bad credential is exactly the one being diagnosed.

## The Related Rule: Order Is Not Evidence

When several credentials are available, **validate, then use** — never
"first match wins". The dead one is often listed first because it was added
first.

```js
for (const t of tokenCandidates()) {          // collect, do not return early
  if (await tokenIsValid(t)) return t;         // validate, then use
}
return null;
```

See also `prompts/credential-order-is-not-validity.md`,
`prompts/recover-dead-github-credential.md`, and
`prompts/fail-closed-on-unavailable-data.md`.
