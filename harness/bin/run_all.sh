#!/bin/bash
# Batch driver: runs every active Defects4J bug through run_bug.sh.
# Usage: run_all.sh [runDir] [parallelism]
# Resumable: re-running skips everything already in <runDir>/done.txt.
set -uo pipefail
source "$(dirname "$0")/env.sh"

RUNDIR="$(realpath -m "${1:-$D4J_CLAUDE_ROOT/runs/full}")"
JOBS="${2:-4}"
mkdir -p "$RUNDIR"
touch "$RUNDIR/results.jsonl"
# never leave done.txt empty: the NR==FNR join below would then read the
# queue itself as the done-set and report zero pending.
[ -s "$RUNDIR/done.txt" ] || echo "# completed bugs" > "$RUNDIR/done.txt"

# ---- build the queue: all active bugs of all 17 projects (Defects4J 3.0.1)
if [ ! -s "$RUNDIR/queue.txt" ]; then
  for csv in "$D4J_HOME"/framework/projects/*/active-bugs.csv; do
    p=$(basename "$(dirname "$csv")")
    tail -n +2 "$csv" | cut -d, -f1 | sed "s/^/$p\t/"
  done | sort -t$'\t' -k1,1 -k2,2n > "$RUNDIR/queue.txt"
fi
TOTAL=$(wc -l < "$RUNDIR/queue.txt")
echo "[run_all] $TOTAL bugs queued, $JOBS workers, run dir $RUNDIR"

pass=0
while :; do
  [ -f "$RUNDIR/STOP" ] && { echo "[run_all] STOP file present, exiting"; break; }
  pass=$((pass+1))
  # pending = queue - done
  awk -F'\t' 'NR==FNR{d[$1"\t"$2]=1;next} !(($1"\t"$2) in d)' \
      "$RUNDIR/done.txt" "$RUNDIR/queue.txt" > "$RUNDIR/pending.txt"
  PENDING=$(wc -l < "$RUNDIR/pending.txt")
  echo "[run_all] pass $pass: $PENDING pending / $TOTAL"
  [ "$PENDING" -eq 0 ] && { echo "[run_all] all bugs done"; break; }
  [ "$pass" -gt 400 ] && { echo "[run_all] pass limit reached, giving up"; break; }

  xargs -a "$RUNDIR/pending.txt" -d '\n' -I{} -P "$JOBS" \
        "$D4J_CLAUDE_ROOT/bin/worker.sh" "$RUNDIR" {}

  # if a pass made no progress at all, avoid a hot loop
  NEWPEND=$(awk -F'\t' 'NR==FNR{d[$1"\t"$2]=1;next} !(($1"\t"$2) in d)' \
      "$RUNDIR/done.txt" "$RUNDIR/queue.txt" | wc -l)
  if [ "$NEWPEND" -eq "$PENDING" ]; then
    echo "[run_all] no progress in pass $pass; sleeping 10 min"
    sleep 600
  fi
done
python3 "$D4J_CLAUDE_ROOT/bin/report.py" "$RUNDIR" || true
