#!/bin/bash
# xargs worker: honours the shared pause/stop files, then runs one bug.
# Usage: worker.sh <runDir> "<Project>\t<bug>"
set -uo pipefail
source "$(dirname "$0")/env.sh"
RUNDIR="$1"; SPEC="$2"
P="${SPEC%%	*}"; B="${SPEC##*	}"
[ -n "$P" ] && [ -n "$B" ] || exit 0
[ -f "$RUNDIR/STOP" ] && exit 0
grep -qxF "$P	$B" "$RUNDIR/done.txt" 2>/dev/null && exit 0

# wait out an account-level usage limit
while [ -f "$RUNDIR/paused_until" ]; do
  until_ts=$(cat "$RUNDIR/paused_until" 2>/dev/null || echo 0)
  now=$(date +%s)
  [ "$until_ts" -gt "$now" ] 2>/dev/null || { rm -f "$RUNDIR/paused_until"; break; }
  left=$(( until_ts - now ))
  echo "[worker] usage limit: ${left}s left, re-checking in 5 min (reset $(date -d @"$until_ts" -u +%H:%M:%SZ))" >&2
  sleep $(( left > 300 ? 300 : left + 5 ))
  [ -f "$RUNDIR/STOP" ] && exit 0
done

"$D4J_CLAUDE_ROOT/bin/run_bug.sh" "$P" "$B" "$RUNDIR"

# react to what the run observed about rate limits
OUT="$RUNDIR/$P-$B"
python3 - "$OUT" "$RUNDIR" <<'PY'
import json, pathlib, sys, time
out, rundir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
verdict = (out/"verdict").read_text().strip() if (out/"verdict").exists() else ""
last = None
try:
    for line in (out/"claude.jsonl").read_text(errors="replace").splitlines():
        if '"rate_limit_event"' in line:
            try: last = json.loads(line)["rate_limit_info"]
            except Exception: pass
except OSError:
    pass
pause_until = 0
if last:
    if last.get("status") not in (None, "allowed"):
        pause_until = int(last.get("resetsAt") or 0)
    else:
        w = (last.get("unifiedWindows") or {}).get("five_hour") or {}
        if (w.get("utilization") or 0) >= 0.985:
            pause_until = int(w.get("resetsAt") or 0)
if verdict == "USAGE_LIMIT" and not pause_until:
    pause_until = int(time.time()) + 900          # unknown reset: back off 15 min
if pause_until > time.time():
    (rundir/"paused_until").write_text(str(pause_until + 60))
    print(f"[worker] pausing batch until {time.strftime('%H:%M:%SZ', time.gmtime(pause_until))}", file=sys.stderr)
PY
