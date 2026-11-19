#!/bin/sh
# Prune regenerable caches when the disk is close to the health-monitor's
# alert threshold (90%, compared against df's rounded-up integer).
#
# WHY THE THRESHOLD IS 85, NOT 90:
# A single go build adds ~2.1G (module cache 2.0G + build cache 322M).
# Pruning AT 90% frees 2.1G and lands at 89%, but the next build puts it
# straight back to 91%. The measured cycle on 2026-11-19:
#
#   prune at 88% -> after a 2.1G build: 90.19% raw, df reports 91%  (still alerting)
#   prune at 86% -> after a 2.1G build: 88.19% raw, df reports 89%  (clear)
#   prune at 84% -> after a 2.1G build: 86.19% raw, df reports 87%  (clear)
#
# So the prune must leave room for ONE BUILD CYCLE, not merely reach the
# line. 85% is the chosen value: it clears the alert AND survives a build.
#
# WHAT IT PRUNES (all regenerable, all verified unused):
#   - the go module cache, via `go clean -modcache`
#   - the go build cache
#   - the node-gyp headers
#   - the zig global/cache dirs
#
# WHAT IT MUST NEVER TOUCH:
#   - /home/node/memory-backup-2026-10-24.tar.gz. The unpushed-backup
#     directory it holds was DELETED, so this tarball is the only remaining
#     copy of the bundles for the repos that still have unpushed commits
#     (15 of them, EdgeChains 319 commits and gaia 389 among them).
#   - .openclaw/agents/main/agent/openclaw-agent.sqlite - the LIVE database.
#   - .openclaw/tmp/plugin-captures - the gateway holds it open.
#   - the playwright browser fallback.
#
# WHY `go clean -modcache` AND NOT `rm -rf`: go makes module-cache files
# read-only, so rm -rf fails with 'Permission denied' and removes nothing.
# `go clean -modcache` uses go's own removal path and works.
set -u

THRESHOLD=85
GOBIN=/home/node/goroot/bin/go

used=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
if [ -z "$used" ]; then
  echo "disk-check: could not read usage"
  exit 0
fi

if [ "$used" -le "$THRESHOLD" ]; then
  echo "disk-check: ${used}% is within budget; nothing to prune"
  exit 0
fi

echo "disk-check: ${used}% is over ${THRESHOLD}%; pruning regenerable caches"

freed() {
  du -sm "$1" 2>/dev/null | awk '{print $1}'
}

# The go module cache. `go env GOMODCACHE` is /home/node/go/pkg/mod, but a
# second, older cache lived at /home/node/go-mod and was the big one (1.2G).
for M in /home/node/go/pkg/mod /home/node/go-mod; do
  if [ -d "$M" ]; then
    echo "  go module cache: $M ($(freed "$M")M)"
    if [ -x "$GOBIN" ]; then
      GOMODCACHE="$M" "$GOBIN" clean -modcache 2>/dev/null
    else
      chmod -R u+w "$M" 2>/dev/null
      rm -rf "$M" 2>/dev/null
    fi
  fi
done

# The go build cache and the node-gyp headers.
for D in /home/node/.cache/go-build /home/node/.cache/node-gyp; do
  if [ -d "$D" ]; then
    echo "  $D ($(freed "$D")M)"
    rm -rf "$D" 2>/dev/null
  fi
done

# The zig caches: pure build caches, regenerated on the next zig build.
for D in /home/node/tmp/zigglobal /home/node/tmp/zigcache; do
  if [ -d "$D" ]; then
    echo "  $D ($(freed "$D")M)"
    rm -rf "$D" 2>/dev/null
  fi
done

after=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
echo "disk-check: ${used}% -> ${after}%"
exit 0