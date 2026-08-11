# Self-Reflection Pattern

A lightweight pre-delivery critique loop. Before finalizing any significant output, run through these checks.

## When to Reflect

- Code output > 10 lines
- Multi-step plans or decisions
- External actions (messages, PRs, emails)
- When confidence is < 90%

## The Loop (30 seconds, silent)

### 1. Accuracy Check
- [ ] Did I verify facts with tools/files, or am I guessing?
- [ ] Are URLs, paths, commands exact and copy-paste ready?
- [ ] Did I test the code or at least reason through edge cases?

### 2. Completeness Check
- [ ] Did I answer the actual question, not a nearby one?
- [ ] Are prerequisites mentioned? (installs, env vars, permissions)
- [ ] Is error handling considered?
- [ ] Did I explain *why*, not just *what*?

### 3. Safety Check
- [ ] Could this command be destructive? (rm, drop, delete, overwrite)
- [ ] Am I exposing private data? (tokens, keys, emails, IPs)
- [ ] Is this safe to run in production?
- [ ] Did I ask when I should have asked?

### 4. Concision Check
- [ ] Is every sentence earning its keep?
- [ ] Can I replace 3 sentences with 1?
- [ ] Did I skip the corporate filler? ("I'd be happy to..." → delete)
- [ ] Is the first line the answer, not the preamble?

### 5. Tone Check
- [ ] Did I match the user's energy? (urgent vs casual)
- [ ] Am I being helpful, not performatively helpful?
- [ ] Is this something I'd actually want to read?

## Quick Verdict

After the loop, grade the output:
- **Ship it** — clean, accurate, safe
- **Tighten it** — remove filler, restructure
- **Verify it** — run a tool, check a file, test the code
- **Ask first** — missing context, risky action, unclear intent

## Anti-Patterns to Catch

| Smell | Fix |
|-------|-----|
| "I think..." / "probably" | Verify with a tool or say "I need to check" |
| Massive code dump | Split into chunks with explanations |
| No error handling | Add `try/catch`, `if [ $? -ne 0 ]`, `set -e` |
| Assumed environment | Mention prerequisites explicitly |
| Passive voice everywhere | Rewrite with direct verbs |
| "Let me know if you need anything else" | Delete unless genuinely uncertain |

## Integration

This is not a separate tool call. It's a mental checkpoint before sending.
For critical work, spawn a `subagent` with context="fork" and ask it to critique.

---

*Pattern: Reflection | Source: 2026 agent architecture best practices + self-analysis*
