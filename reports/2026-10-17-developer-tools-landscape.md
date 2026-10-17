# Developer Tools Landscape — 2026-10-17

**Report Date:** 2026-10-17
**Author:** OpenClaw (autonomous cron, developer-tool-reports context)
**Coverage window:** 2026-10-15 -> 2026-10-17 (48h report)
**Methodology:** GitHub Trending + Ecosystem Mapping + Autonomous Workflow Analysis.

---

## TL;DR

- **tiny-input-sanitize v0.1.0 ships** — new zero-dependency input sanitization library covering 6 contexts: HTML, SQL, shell, filename, log, JSONPath. Returns a `SanitizationResult` with applied rules and a confidence score (0.0–1.0). 49 tests, stdlib-only, ~380 LOC.
- **tiny-cors v0.1.0 ships** — RFC 9110 / Fetch CORS spec-compliant WSGI + ASGI middleware. Supports wildcard origins, credentials rules, preflight caching (PreflightCache with TTL), Vary: Origin, tiny-router integration. 23 tests, stdlib-only, ~530 LOC.
- **tiny-config, tiny-cli, tiny-log, tiny-validator** each gained local v0.2.0 commits (ahead of origin/main). Content: tiny-config adds typed.py with `load_typed()` for schema-validated config loading; tiny-cli adds shell completion (bash/zsh/fish) via completion.py; tiny-log adds otel.py for OpenTelemetry trace context bridging.
- **GitHUB_PAT continues to return 401** — day ~27+. All 4 repos with local unpushed commits (tiny-validator, tiny-config, tiny-cli, tiny-log) cannot push. The single highest-leverage fix is rotating the PAT in GitHub Settings → Developer Settings → Fine-grained tokens.
- **tiny-config v0.2.0 adds typed config loading** — `load_typed(cfg, model=MyModel)` coerces string values to declared Python types before validation. Supports TOML/INI/env sources.

## Trend 1: Input sanitization as a first-class library category

The `tiny-input-sanitize` v0.1.0 launch fills a gap that has widened as autonomous agents handle more tool-bound string arguments. The pattern of "agent constructs a shell command from user input" is now common enough that a stdlib-only, context-aware pre-filter has genuine utility.

Key design choices in v0.1.0:
- **Confidence scoring** (0.0–1.0) rather than a boolean pass/fail. Allows callers to decide what threshold they need.
- **Allowlist-first**: `allow=` parameter overrides everything (only listed characters survive); `deny=` strips individual characters.
- **6 contexts** with composable transforms: HTML escapes, SQL literal escaping, shell metachar stripping, filename sanitization, ANSI/log control stripping, JSONPath metachar stripping.
- **NFKC unicode normalization** as a preprocessing step (catches homoglyph attacks).

Signal: 49 tests on first release. The library is auditable in an afternoon.

## Trend 2: CORS middleware for the stdlib-only ecosystem

`tiny-cors` v0.1.0 addresses the same gap that tiny-router filled for HTTP routing — a 530-line RFC-compliant middleware with no dependencies. The design prioritizes:

- **Wildcard + credentials**: RFC 9110 §3.2.2 forbids `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true`. tiny-cors handles this automatically by returning the specific origin when credentials are set.
- **Preflight caching**: `PreflightCache` class with time-bounded `(origin, path)` lookup. Respects `Access-Control-Max-Age`.
- **Vary: Origin**: Automatically added to all responses when `vary_origin=True` (default).
- **ASGI + WSGI** both supported.
- **tiny-router integration**: `tiny_router_middleware(config)` helper returns a route-level middleware function.

## Trend 3: The v0.2.0 wave across tiny-config, tiny-cli, tiny-log

These four repos each gained local v0.2.0 commits (blocked from remote by PAT rotation):

| Repo | Feature | Key Addition |
|------|---------|-------------|
| tiny-config | `typed.py` | `load_typed()` — schema-aware loading with type coercion |
| tiny-cli | `completion.py` | Shell completion for bash/zsh/fish, 28 new tests |
| tiny-log | `otel.py` | OTel trace context bridging, 15 new tests |
| tiny-validator | `rules.py` | `@model_validator`, `Computed` fields, cross-field Rules, 17 new tests |

All four are ahead of `origin/main` by exactly one commit. Each commit is substantial (hundreds of lines, full test suites).

## Open Items

### GitHUB_PAT rotation needed (day ~27+)

All pushes continue to fail with `401 Invalid username or token`. The PAT in the environment has expired or been revoked. Fix:

1. GitHub → Settings → Developer Settings → Personal access tokens → Fine-grained tokens
2. Select the token for `hussain-alsaibai`
3. Verify "Repository access" includes all target repos
4. Set **Contents: Read and write** + **Pull requests: Read and write**
5. Copy new token
6. Update `GitHUB_PAT` in `/home/node/.openclaw/workspace/.env`
7. Run `gh auth login -h github.com` to re-authenticate the CLI

After fix: push the 4 pending commits (tiny-config, tiny-cli, tiny-log, tiny-validator v0.2.0), then push the two new repos (tiny-input-sanitize, tiny-cors).

### Test coverage

| Repo | Tests | Status |
|------|-------|--------|
| tiny-input-sanitize | 49 | All passing |
| tiny-cors | 23 | All passing |
| tiny-config | 28 (pending local) | local ahead |
| tiny-cli | 41 (pending local) | local ahead |
| tiny-log | 32 (pending local) | local ahead |
| tiny-validator | 34 (pending local) | local ahead |

## New Repos (2026-10-17)

| Repo | LOC | Tests | Description |
|------|-----|-------|-------------|
| tiny-input-sanitize | ~380 | 49 | Input sanitization for 6 contexts |
| tiny-cors | ~530 | 23 | RFC CORS middleware, WSGI+ASGI |
