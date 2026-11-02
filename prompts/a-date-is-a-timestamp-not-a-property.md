# A Date Is A Timestamp, Not A Property

**Last verified:** 2026-11-02 - two guides in this repo certified two repos as
missing with `Last Verified: 2026-11-02`; both repos were created at 17:10 UTC
that same day, after the check.

## The claim that fails

```
Status: Repo does not exist upstream yet (HTTP 404, checked 2026-10-23)
Last Verified: 2026-11-02 - still returns HTTP 404 (re-checked 2026-11-02)
```

Read it as a reader would: *"as of today, this does not exist."* Read it as an
operator must: *"as of some hour this morning, this did not exist."* A repo
can be created between those two readings.

## Why this is harder than a stale claim

A claim with no date is obviously a claim. A claim with today's date **borrows
the credibility of freshness** and spends it on a check that is already old.
The failure looks like diligence in the diff.

## The rule

1. **Record the moment, not the day**, for anything that can change intraday:
   repo existence, star counts, CI status, open-issue counts, provider model
   availability, package versions on a registry.
2. **Never let a verification outlive the edit it validates.** A snippet that
   was executed before the last edit to the surrounding text is unverified.
3. **Re-probe the whole family when one member turns wrong.** In this run, 2 of
   6 "local only" claims were live upstream. The error was in the *method*, not
   in the row - so every row sharing the method is suspect.
4. **Paste the output, not the description.** A guide snippet with no emitted
   output is a proposal.

## The check, as a procedure

```bash
# existence: status code, with auth, captured - not inferred from a curl -f
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: token $(gh auth token)" \
  "https://api.github.com/repos/<owner>/<name>"

# API surface: the signature, not the README
python3 -c "import inspect, mymod as m; print(inspect.signature(m.Thing))"

# behaviour: run it, and keep the stdout in the doc
python3 /tmp/snippet.py
```

## When to apply

- Any `Last verified` / `Last checked` / `as of` field in documentation.
- Any curated list of repos, packages, models or prices.
- Any guide snippet that was corrected against a *clone* rather than against a
  *published* artifact - the two drift.
