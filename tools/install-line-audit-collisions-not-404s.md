# Install-Line Audit: Finding Collisions, Not Just 404s

**Last verified:** 2026-11-16 (workspace census: 2,854 files, 541 bare install references,
201 distinct names; six collisions confirmed against the PyPI JSON API).

## When to use this

Before publishing a README, `llms.txt`, or any quickstart for a package you maintain.
Also as a periodic fleet check — the author allowlist drifts.

## The two questions

| question | catches | misses |
|---|---|---|
| does the name resolve? | typos, unpublished packages | anyone else's package with the same name |
| does it resolve **to us**? | that too | nothing relevant |

Only the second question is worth automating for your own packages.

## Procedure

**1. Enumerate every install reference.** Read and fenced blocks, `llms.txt`, `docs/`,
changelogs, and agent-facing files. Do not filter by file extension — `llms.txt` is the
highest-risk artifact because agents execute it without judgement.

**2. Classify each name against the registry.**

```
GET https://pypi.org/pypi/<name>/json   ->  { info: { author, author_email, home_page } }
```

- 404 → **absent** (visible, self-correcting)
- 200, author not in your allowlist → **collision** (silent, dangerous)
- 200, author in allowlist → **owned**
- network error / 429 → **unknown**, never a violation

**3. Read the remote before writing any fix.**

```bash
git -C repos/<repo> show origin/main:README.md | grep -n "pip install"
```

Three repos in this census were flagged and were **already correct remotely**; only the
stale local clone held the old text. Patching from the working tree would have reinstated
the bug.

**4. Fix by deciding, not by regex.** Either publish the name to the registry (preferred)
or point the line at a VCS URL or a warning. A bare name that resolves to a stranger
belongs in neither the quickstart nor `llms.txt`.

## False positives to suppress deliberately

- **Warning lines.** `"pip install tiny-x would fetch that package"` is the fix, not the
  defect. Skip matches within the warning's own sentence, scoped to the name it names.
- **Commented lines.** `# pip install tiny-*` documents a family. Not an instruction.
- **Historical reports.** A 2026-09 report describing the world as it was is accurate
  history. Mark it as such; do not silently rewrite it.

## Reporting

Report by **file class** (README / `llms.txt` / docs / changelog / history), because the
fix priority follows risk, not count. `llms.txt` and quickstarts outrank a changelog
entry from six months ago.

## Failure modes this procedure exists to prevent

- A green CI run on a README that installs a stranger's package.
- A checker that reports its own warnings, then gets disabled for noise.
- A "fix" applied to a stale clone that reverts a correct remote.
- An `unknown` bucket counted as breakage during a registry outage, burning a day.
