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
# Park only when a window is actually spent, and only until THAT window resets.
#
# Two traps here, both hit in practice:
#   * `allowed_warning` still means allowed -- it is a heads-up that a window is
#     filling, not a block. Treating it as one parked a whole campaign.
#   * the top-level `resetsAt` tracks whichever window raised the notice, so on a
#     seven-day warning it points up to a week out. Always take the reset from
#     the specific window that is exhausted.
ALLOWED = (None, "allowed", "allowed_warning")
windows = (last.get("unifiedWindows") or {}) if last else {}

def spent(name, thresh=0.985):
    w = windows.get(name) or {}
    return int(w.get("resetsAt") or 0) if (w.get("utilization") or 0) >= thresh else 0

pause_until = 0
if last and last.get("status") not in ALLOWED:
    # hard block: wait for the soonest window that could clear it
    cands = [int((windows.get(n) or {}).get("resetsAt") or 0) for n in ("five_hour", "seven_day")]
    cands = [c for c in cands if c > time.time()]
    pause_until = min(cands) if cands else int(last.get("resetsAt") or 0)
else:
    pause_until = spent("five_hour") or spent("seven_day")

if verdict == "USAGE_LIMIT" and not pause_until:
    pause_until = int(time.time()) + 900          # unknown reset: back off 15 min

if pause_until > time.time():
    (rundir/"paused_until").write_text(str(pause_until + 60))
    hrs = (pause_until - time.time()) / 3600
    print(f"[worker] pausing batch until "
          f"{time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime(pause_until))} ({hrs:.1f} h)",
          file=sys.stderr)
PY
