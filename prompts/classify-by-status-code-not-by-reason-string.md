# Classify A Failure By Its Status Code, Not By Its Reason String

**A rule for any retry loop, error handler, or backoff policy.**

> Found 2026-11-02. A context-length overflow was retried **8 times** as a
> transient timeout - a request that could never succeed, on a model whose
> 512,000-token window was already exceeded by 666,035 tokens.
>
> **Last verified:** 2026-11-02 — 49 HTTP 400 responses in a 14-minute window,
> all classified as `reason=timeout`, all retryable, none possible.

## The Rule

> **A status code is a fact. A reason string is a guess. Classify on the
> code.**

## The Failure

```
HTTP 400
estimatedPromptTokens=666035
context window = 512000
```

The runtime read the message, found a word it had been taught to associate
with slowness, and classified the failure as *transient*:

```
transient same-model retry 1/8 ... reason=timeout
```

Eight times. Every one of them sent the same oversized request to the same
model and got the same 400 back. The retry budget was spent on a request
whose success probability was exactly zero.

**A context-length 400 is not retryable.** Neither is a 401, a 403, or a 422.

## The Classification Table

| status | retryable? | why |
|---|---|---|
| 400 (context length) | **no** | the request is too large; it will be too large again |
| 401 / 403 | **no** | the credential or policy is wrong; retrying proves nothing |
| 404 | **no** | the endpoint or model does not exist |
| 408 | yes | the server asked for a retry |
| 429 | yes | rate limited — but respect the window |
| 500 / 502 / 503 | yes | transient server-side |
| 504 | yes | gateway timeout |
| network error / DNS | yes | never reached the server |

**The rule is about the *cause*, not the status alone.** A 400 is sometimes
retryable (a transient upstream parse error) and a 429 is sometimes not (a
hard quota). But the status code narrows the field first, and the cause
narrowed from there is worth trusting. The reason string alone is the part
that lied.

## How To Get The Status Code

**This is where the whole thing breaks in practice.** A helper that discards
the body on a non-2xx response also discards the status:

```js
// BROKEN — `-f` makes curl fail on non-2xx and drop the body.
// The caller sees "command failed" and nothing else.
execSync('curl -sf https://api.example/...')
```

That string contains neither `403` nor `rate limit`, so a backoff rule
written as `/403|rate limit/i.test(msg)` never matches. **Every failure is
then classified as "not a rate limit".**

```js
// RIGHT — capture the status on the last line, and keep the body.
const cmd = 'curl -s -w "\\n%{http_code}" ' + auth + ' "https://api.example/..."';
const out = execSync(cmd, { timeout }).toString();
const cut = out.lastIndexOf('\n');
const status = parseInt(out.slice(cut + 1).trim(), 10) || 0;
const raw = cut >= 0 ? out.slice(0, cut) : '';

if (status === 403 || status === 429) {
  searchBackoff();
  process.stderr.write('[WAIT] rate limited (HTTP ' + status + ')\n');
  return null;
}
if (status && (status < 200 || status >= 300)) {
  process.stderr.write('[HTTP] ' + status + '\n');
  return null;
}
```

**Two properties this buys you:** the status survives, and the body survives
so the log can carry the provider's own explanation.

## The Second Half Of The Rule

> **A band that is dropped must be dropped for a recorded reason.**

When the retry gave up, log *why* — with the status next to the drop.
Otherwise the next reader sees "band dropped" and cannot tell a rate limit
from a schema bug from a typo.

In the real incident, the band query burned all three of its retries in
under 20 seconds against a 60-second rate window, then the band was silently
dropped, and the whole `label:bounty` market for the last 7 months was missing
from the scan. **The scan reported the market as `INCOMPLETE` without saying
why.**

See also `prompts/fail-closed-on-unavailable-data.md` (unavailable data read
as a pass) and `prompts/silent-failure-detection.md` (monitoring that cannot
distinguish states).
