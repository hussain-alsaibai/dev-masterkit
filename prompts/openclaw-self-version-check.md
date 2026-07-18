# openclaw-self-version-check - Detect available OpenClaw updates without trusting stale install paths

## What this solves

When a cron job wants to alert on a new OpenClaw release, naive
recipes hardcode paths like `/skeleton/.npm-global/...` or
`node /opt/openclaw/cli.js`. These go stale on every container
restart and reinstall because OpenClaw is a single-file CLI shipped
at `/usr/local/bin/openclaw` → `/app/openclaw.mjs` and reports its
version via `openclaw --version`. Reading that string is the only
authoritative local version source.

## The recipe that works

```bash
# 1. Local version (authoritative)
LOCAL="$(openclaw --version | awk '{print $2}')"

# 2. Upstream latest (GitHub Releases API, no auth needed)
LATEST="$(curl -fsSL https://api.github.com/repos/openclaw/openclaw/releases/latest \
  | awk -F'"' '/"tag_name":/ {print $4}' | sed 's/^v//')"

# 3. Compare and decide
if [ "$LOCAL" != "$LATEST" ]; then
  echo "OpenClaw update available: $LOCAL -> $LATEST"
fi
```

## Why hardcoded paths fail

Today's run on 2026-07-17 hit this directly. The cron task spec
still reads `cat /skeleton/.npm-global/lib/node_modules/openclaw/package.json`
which is a left-over from a build-time layout that no longer matches
the runtime install. The install is now a symlink shim at
`/usr/local/bin/openclaw` that exec's `/app/openclaw.mjs`. Both
`ls -la /usr/local/bin/openclaw` and `openclaw --version` are stable
across restarts; the legacy path is not.

## Verify before you ship

Run these three before trusting the recipe in a cron job:

```bash
which openclaw                       # /usr/local/bin/openclaw
ls -la /usr/local/bin/openclaw       # symlink target
openclaw --version                   # "OpenClaw <semver>"
```

If any of the three return something different, your container has
been customised - update the recipe before relying on it.

## When to alert vs. stay quiet

- Local == upstream: no message (still file the daily log line).
- Local older by a patch release: log only.
- Local older by a minor/major release, OR upstream has a security
  advisory: announce to the operator's preferred channel.

Last verified: 2026-07-18 (OpenClaw 2026.7.1 installed, 2026.7.1 upstream — in sync).
