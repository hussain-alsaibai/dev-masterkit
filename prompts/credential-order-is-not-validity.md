# Credential Order Is Not Validity

**A rule for any code that resolves an API credential from more than one
source.**

> Found 2026-10-27 in the bounty scanner. `getToken()` returned the **first**
> credential it found, which was `process.env.GitHUB_PAT` — a **dead**
> fine-grained token (93 chars, `github_pat_...`, HTTP 401). The **working**
> classic token (40 chars, `ghp_...`) lived in `~/.git-credentials` and in
> `gh auth token`, and was **never reached**. **Last verified:** 2026-10-27 —
> both tokens probed directly (`GitHUB_PAT` → HTTP 401, `gh auth token` →
> HTTP 200); scanner fixed; all five regression suites pass.

## The Defect

```js
// BROKEN — first match wins
if (process.env.GITHUB_TOKEN) return process.env.GITHUB_TOKEN;
if (process.env.GitHUB_PAT)   return process.env.GitHUB_PAT;   // <- DEAD
```

The scan did not crash. That is the problem. It **degraded**: the 401 was
noticed, the scanner fell back to ANONYMOUS (60 req/hr), and the run
produced a plausible-looking result.

| what was true | what was read | consequence |
|---|---|---|
| one credential is dead | no credential | anonymous, 60 req/hr |
| repo metadata unreachable | 0 stars | `farm_flagged_no_stars` |
| 15 genuine candidates | 0 trustworthy picks | "market is all farms" |

**The market was not all farms. The metadata was unreadable**, and unreadable
was read as zero stars, and zero stars was read as scam. Three
transformations, each individually plausible, and the last one is a lie
about the world.

## The Rule

> **A credential lookup must never trust order. Order is not evidence of
> validity. Validate, then use.**

## The Procedure

1. **Collect every candidate, in preference order.** Do not return from
   inside the collection loop.

   ```js
   function tokenCandidates() {
     const out = [];
     for (const v of [process.env.GITHUB_TOKEN, process.env.GitHUB_PAT, process.env.GH_TOKEN]) {
       if (v) out.push(v);
     }
     // credential store: both `user:token@` and bare `token@` forms
     try {
       const raw = fs.readFileSync(path.join(os.homedir(), '.git-credentials'), 'utf8');
       for (const line of raw.split('\n')) {
         const m = line.match(/:([^:@/]+)@github\.com/);
         if (m) out.push(m[1]);
       }
     } catch (e) { /* absent */ }
     try {
       out.push(execFileSync('gh', ['auth', 'token'], { encoding: 'utf8' }).trim());
     } catch (e) { /* absent */ }
     return out.filter(Boolean);
   }
   ```

2. **Validate each candidate, and use the first that authenticates.** The
   validation is the point. Without it, the list is just an ordered list.

   ```js
   const _tokenChecked = new Map();   // keyed BY THE TOKEN, not by a global

   async function tokenIsValid(token) {
     if (_tokenChecked.has(token)) return _tokenChecked.get(token);
     const ok = await probe(token);          // one cheap GET /user
     _tokenChecked.set(token, ok);
     return ok;
   }

   async function getToken() {
     for (const t of tokenCandidates()) {
       if (await tokenIsValid(t)) return t;
     }
     return null;
   }
   ```

3. **Cache the verdict per token, never globally.** A single boolean
   (`_tokenChecked = false`) caches the *dead* token's verdict and applies it
   to the working one too. The cache must be keyed by the credential, or it
   caches a verdict about something other than what it is asked about.

4. **Say WHY there are zero results.** "market is all farms" is a claim about
   the world. "repo metadata was unreachable, so stars were unknown" is a
   claim about the run. Only the second one is actionable.

## The Second Failure — `null` Is Not Zero

The same day, a different function had the same shape:

```js
// BROKEN — an empty array and an absent field are the same thing
function parseLinkedPRs(html) {
  if (!/linkedPullRequests/.test(html)) return null;   // <- unknown
  ...
}
```

An issue page that renders `"linkedPullRequests":{"nodes":[]}` — an
**empty array**, which is a definitive **zero** — matched no marker, so the
function returned `null`, which the caller read as `COMPETITION_UNKNOWN`.
`daily-bounty-work.js` refuses to start work on an unknown count, so two
genuinely uncontested tasks were **skipped for being unmeasurable**.

**The rule:** an empty collection is zero. A missing field is unknown. They
are different values and must not share one representation.

```js
if (!payloadHasKey(obj, 'linkedPullRequests')) return UNKNOWN;  // -1
return payload.linkedPullRequests.nodes.length;                 // 0 is a real answer
```

## The Generalisation

> **Order is a guess. Validity is a measurement. And an empty array is not a
> missing field.**

This applies to every credential resolver, every config loader with a default
chain, every optional field with a sentinel value, and every parser that
returns `null` for "could not tell". The tell is the same each time: **a
sentinel that means two different things will eventually be read as the
wrong one.**

See also `prompts/recover-dead-github-credential.md` (recovering a credential
that is dead everywhere) and
`prompts/fail-closed-on-unavailable-data.md` (the general shape).
