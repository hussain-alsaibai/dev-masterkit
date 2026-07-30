# Opire Fork-Scam Fingerprint

**Created:** 2026-07-30
**Last verified:** 2026-07-30
**Author:** OpenClaw / hussain-alsaibai
**Source:** Real bounty scanner results, July 30 2026

---

## The Problem

Opire bounties are being systematically abused via throwaway GitHub fork accounts.
These are not real bugs — they are credential phishing operations disguised as bounty boards.

## Known Scam Patterns

### Pattern 1: Opire Fork-Scam (Active July 2026)

**Fingerprint:**
- **Owner account:** Created same day as the bounty, zero GitHub history
- **Repo:** Fork of a popular library (redis, gitea, traefik, vault, pulsar, etc.)
- **Size:** ~1 KB — just the fork, no real code changes
- **README:** Contains `Hello, Bounty Hunter!` or similar social engineering hook
- **Stars:** 0
- **Issues:** 1-5 "bounty" issues referencing the fork, priced $25-$300
- **Source:** Via aggregator boards like `Vikingr2023/awesome-agent-bounties`

**Examples (July 2026):**
- `thaohuynh14zc/go-redis` — 10-day-old account, 0 stars, "Hello, Bounty Hunter!" README
- `elnahomenick123/go-redis` — same pattern
- `quachminh11/go-redis` — same pattern
- `simschad12/go-redis` — added to blocklist 2026-07-30
- `murphythomas87/go-redis` — added to blocklist 2026-07-30

### Pattern 2: Credential Harvester (Historical — ClankerNation)

From MEMORY.md (2026-07-01): ClankerNation/OpenAgents is a social engineering trap.
Accepts contributor "session initialization context" = credential exfiltration attempt.

**Fingerprint:** Repo requests system info, environment variables, or "session context" from contributors.

## Detection Rules (Scanner Implementation)

### Hard Blocks
```
IF repo_stars == 0 AND repo_age_days < 14 AND "Hello, Bounty Hunter!" IN readme:
    → REJECT (scam: same-day fork + social hook)

IF owner.account_age_days < 30 AND owner.total_repos == 1 AND repo_stars == 0:
    → REJECT (scam: throwaway account)

IF "session" IN issue_body AND "context" IN issue_body AND repo_name IN suspicious_list:
    → REJECT (credential harvester)
```

### Soft Flags (downscore heavily)
```
young_repo = repo_age_days < 30
no_stars = repo_stars < 1
no_activity = last_commit_days > 90
single_fork = fork_count == 1
```

## Scanner Gap (July 30 2026)

**Issue:** Anti-scam filter caught `young_repo` flag but scam score (42/100) was still the "winner" among top pool picks.

**Fix:** When the top-ranked candidate in the pool has a scam score above threshold, the **entire pool** should be flagged as degraded, not just the top pick skipped. A pool where the best option is a 42/100 scam is not a valid pool.

```python
# Good scanner logic
if top_pick.scam_score > 40:
    log.warning(f"Top pool candidate is a scam (score={top_pick.scam_score}). Pool invalid.")
    return []  # Don't surface any picks from this pool
```

## Blocklist Management

Maintain a `BOUNTY_FARMS` blocklist of known scam aggregator boards:

```python
BOUNTY_FARMS = {
    "Vikingr2023/awesome-agent-bounties",   # Opire fork scams
    "SecureBananaLabs/...",                   # Previous pattern
    "UnsafeLabs/...",                         # Previous pattern
    "ClankerNation/OpenAgents",             # Credential harvester
}
```

Update blocklist when new patterns emerge.

## Legitimate Bounty Verification Checklist

Before investing time in any bounty:
- [ ] Repo has >100 stars OR is a verified bounty platform (Algora, Opire direct)
- [ ] Issue author has >30 days history and >5 repos
- [ ] Issue references actual code in the target repo (not a fork stub)
- [ ] Bounty is attached via `algora-pbc[bot]` or `opire[bot]` comment
- [ ] No "Hello, Bounty Hunter!" or similar social engineering text
- [ ] Repo was created >60 days ago OR has >50 stars
- [ ] Issue body asks for real code changes (not "add me to Discord")

## Source Attribution

Scanner that caught these: `skills/bounty-scanner/bounty-scanner.js`
- Filters: `algora-pbc[bot]` comments with 💎 bounty header
- Hard blocks: `BOUNTY_FARMS` blocklist, age thresholds, star thresholds
- Blocked repos (2026-07-30): `simschad12/go-redis`, `murphythomas87/go-redis`

---

**Tags:** `#security` `#scam-detection` `#bounty-hunting` `#opire` `#anti-phishing`
