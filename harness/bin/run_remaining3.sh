#!/bin/bash
# The three bugs that got no test-adequate patch in the main sweep, re-run under
# four conditions that vary wall-clock cap and model independently.
#
#   condition   model              cap     isolates
#   T           claude-sonnet-5    4 h     time alone
#   M           claude-opus-5      30 min  model alone
#   TM          claude-opus-5      4 h     both
#   TM+         claude-fable-5-1   4 h     strongest available
#
# Everything else -- prompt, tool restrictions, .git removal, independent
# verification on a fresh checkout -- is identical to the main sweep, so results
# are directly comparable. Effort stays `high` so the model is the only variable
# in M and TM.
#
# Usage: run_remaining3.sh <condition> [reps]      condition in T|M|TM|TM+|all
# Resumable: a rep whose done.txt already lists the bug is skipped.
#
# BUGS_SUBSET restricts the queue, e.g. BUGS_SUBSET="JacksonCore-10 Math-66" to skip a bug
# an earlier condition already solved. Default: all three.
set -uo pipefail
source "$(dirname "$0")/env.sh"

COND="${1:-}"
REPS="${2:-2}"
ALL_BUGS=$'JacksonCore\t10\nMath\t66\nJsoup\t67'
if [ -n "${BUGS_SUBSET:-}" ]; then
  BUGS=""
  for want in $BUGS_SUBSET; do
    line=$(printf '%s\n' "$ALL_BUGS" | awk -F'\t' -v w="$want" '$1"-"$2==w')
    [ -n "$line" ] || { echo "unknown bug: $want" >&2; exit 2; }
    BUGS="${BUGS:+$BUGS$'\n'}$line"
  done
else
  BUGS="$ALL_BUGS"
fi
BASE="$D4J_CLAUDE_ROOT/runs/remaining3"

usage() { echo "usage: $0 <T|M|TM|TM+|all> [reps]" >&2; exit 2; }
[ -n "$COND" ] || usage

settings() {
  case "$1" in
    T)   AGENT_MODEL=claude-sonnet-5  AGENT_TIMEOUT=14400 ;;
    M)   AGENT_MODEL=claude-opus-5    AGENT_TIMEOUT=1800  ;;
    TM)  AGENT_MODEL=claude-opus-5    AGENT_TIMEOUT=14400 ;;
    TM+) AGENT_MODEL=claude-fable-5-1 AGENT_TIMEOUT=14400 ;;
    *)   usage ;;
  esac
}

run_one() {
  local cond="$1" rep="$2"
  settings "$cond"
  local dir="$BASE/${cond}-r${rep}"
  mkdir -p "$dir"
  printf '%s\n' "$BUGS" > "$dir/queue.txt"
  cat > "$dir/condition.json" <<EOF
{"condition": "$cond", "rep": $rep, "model": "$AGENT_MODEL",
 "agent_timeout_s": $AGENT_TIMEOUT, "effort": "${AGENT_EFFORT:-high}",
 "max_budget_usd": "${AGENT_MAX_BUDGET_USD:-none}",
 "bugs": "$(printf '%s\n' "$BUGS" | awk -F'\t' '{printf "%s%s-%s", (NR>1?",":""), $1, $2}')"}
EOF
  echo "[remaining3] === $cond rep $rep: $AGENT_MODEL, cap ${AGENT_TIMEOUT}s, dir $dir"
  # One worker: these bugs include timing-sensitive numerical tests, and the
  # main sweep's only flake appeared under the CPU load of parallel workers.
  AGENT_MODEL="$AGENT_MODEL" AGENT_TIMEOUT="$AGENT_TIMEOUT" \
  AGENT_EFFORT="${AGENT_EFFORT:-high}" \
  AGENT_MAX_BUDGET_USD="${AGENT_MAX_BUDGET_USD:-}" \
    "$D4J_CLAUDE_ROOT/bin/run_all.sh" "$dir" 1
}

mkdir -p "$BASE"
if [ "$COND" = all ]; then
  for c in T M TM TM+; do
    for r in $(seq 1 "$REPS"); do run_one "$c" "$r"; done
  done
else
  for r in $(seq 1 "$REPS"); do run_one "$COND" "$r"; done
fi
echo "[remaining3] done"
