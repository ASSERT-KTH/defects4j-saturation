#!/usr/bin/env python3
"""Per-bug results table for a campaign (RESULTS.md).

Usage: report_per_bug.py <runDir> [dataPrefix]
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from report import similarity

run = pathlib.Path(sys.argv[1])
prefix = sys.argv[2] if len(sys.argv) > 2 else "data"
recs = {}
for line in open(run / "results.jsonl"):
    if line.strip():
        r = json.loads(line)
        recs[r["id"]] = r
rows = sorted(recs.values(), key=lambda r: (r["project"], r["bug"]))

print("# Per-bug results\n")
print(f"{len(rows)} bugs, one Claude Code (Sonnet 5) session each. "
      "See [README](README.md) for the protocol.\n")
print("`vs dev fix` compares the agent's patch with the inverse of Defects4J's "
      "`<N>.src.patch`, normalised for\nwhitespace and comments: `identical` means the same "
      "lines added and removed, `same-files` means the same\nfile(s) changed a different way, "
      "`different` means the defect was repaired elsewhere.\n")
print("| bug | verdict | vs dev fix | files | +/- | turns | cost | min |")
print("|---|---|---|---|---|---|---|---|")
for r in rows:
    sim = similarity(run / r["id"]) if r["verdict"] == "PLAUSIBLE" else ""
    est = "~" if r.get("telemetry_source") == "stream_estimate" else ""
    print(f"| [{r['id']}]({prefix}/{r['id']}) | {r['verdict']} | {sim} | "
          f"{len(r['patch_files'])} | +{r['patch_added_lines']}/-{r['patch_removed_lines']} | "
          f"{r.get('num_turns') or ''} | {est}${r.get('total_cost_usd') or 0:.2f} | "
          f"{(r.get('wallclock_s') or 0)/60:.1f} |")
