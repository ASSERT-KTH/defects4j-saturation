#!/bin/bash
# One-time setup: pin a private Defects4J v3.0.1 install and self-check it.
set -euo pipefail
source "$(dirname "$0")/env.sh"

# Optional seed: an existing Defects4J clone whose project_repos/, major/ and
# framework/lib/ are reused to avoid ~1.5 GB of downloads. Unset or absent is fine.
SRC="${D4J_SEED:-$HOME/defects4j}"
TAG=v3.0.1

log() { echo "[setup] $*"; }

UPSTREAM=https://github.com/rjust/defects4j
if [ ! -d "$D4J_HOME/.git" ]; then
  if [ -d "$SRC/.git" ]; then
    log "cloning local seed $SRC -> $D4J_HOME"; git clone --quiet "$SRC" "$D4J_HOME"
  else
    log "cloning $UPSTREAM -> $D4J_HOME"; git clone --quiet "$UPSTREAM" "$D4J_HOME"
  fi
fi
git -C "$D4J_HOME" fetch --quiet --tags "$SRC" 2>/dev/null || git -C "$D4J_HOME" fetch --quiet --tags "$UPSTREAM" || true
git -C "$D4J_HOME" checkout --quiet "$TAG"
log "defects4j at $(git -C "$D4J_HOME" describe --tags)"

# Seed heavy artifacts from an existing install (hardlinks where possible).
mkdir -p "$D4J_HOME/project_repos"
if [ ! -d "$SRC" ]; then
  log "no seed install at $SRC; init.sh will download everything"
fi
for r in "$SRC"/project_repos/*.git; do
  [ -e "$r" ] || continue
  d="$D4J_HOME/project_repos/$(basename "$r")"
  [ -d "$d" ] || { log "seeding $(basename "$r")"; cp -al "$r" "$d" 2>/dev/null || cp -a "$r" "$d"; }
done
[ -d "$D4J_HOME/major" ] || { log "seeding major"; cp -a "$SRC/major" "$D4J_HOME/major"; }
for sub in test_generation build_systems; do
  if [ -d "$SRC/framework/lib/$sub" ] && [ ! -d "$D4J_HOME/framework/lib/$sub" ]; then
    log "seeding framework/lib/$sub"; cp -a "$SRC/framework/lib/$sub" "$D4J_HOME/framework/lib/$sub"
  fi
done

log "running init.sh (should be near no-op with seeded artifacts)"
( cd "$D4J_HOME" && ./init.sh )

log "self-check: Lang-1b checkout/compile/test"
W=$(mktemp -d "${TMPDIR:-/tmp}/d4j-selfcheck-XXXX")
trap 'rm -rf "$W"' EXIT
defects4j checkout -p Lang -v 1b -w "$W/lang1" >/dev/null
( cd "$W/lang1" && defects4j compile >/dev/null 2>&1 && defects4j test >/dev/null 2>&1 )
got=$(grep -c '^---' "$W/lang1/failing_tests" || true)
if [ "$got" != "1" ]; then
  echo "[setup] FAIL: expected exactly 1 failing test for Lang-1b, got $got" >&2
  exit 1
fi
log "self-check OK ($(cat "$W/lang1/failing_tests" | head -1))"
log "done. source $D4J_CLAUDE_ROOT/bin/env.sh to use it."
