#!/usr/bin/env python3
"""Assemble result.json for one bug and append it to the run's results.jsonl."""
import json, os, sys, time, fcntl, pathlib

out, proj, bug, rundir = sys.argv[1:5]
O = pathlib.Path(out)

def txt(name, default=""):
    p = O / name
    try:
        return p.read_text().strip()
    except OSError:
        return default

def count(name, prefix="--- "):
    try:
        return sum(1 for l in (O / name).read_text().splitlines() if l.startswith(prefix))
    except OSError:
        return None

res = {}
try:
    for line in (O / "claude.jsonl").read_text(errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            res = ev
except OSError:
    pass

usage = res.get("usage") or {}
patch = txt("patch.diff")
patch_files = sorted({l.split(" b/", 1)[1] for l in patch.splitlines()
                      if l.startswith("diff --git ") and " b/" in l})
added = sum(1 for l in patch.splitlines() if l.startswith("+") and not l.startswith("+++"))
removed = sum(1 for l in patch.splitlines() if l.startswith("-") and not l.startswith("---"))

rec = {
    "project": proj,
    "bug": int(bug),
    "id": f"{proj}-{bug}",
    "verdict": txt("verdict", "ERROR"),
    "note": txt("note"),
    "model": "claude-sonnet-5",
    "effort": "high",
    "finished_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "wallclock_s": int(txt("wallclock_s", "0") or 0),
    "agent_s": int(txt("agent_s", "0") or 0),
    "agent_rc": int(txt("agent_rc", "-1") or -1),
    "num_turns": res.get("num_turns"),
    "api_duration_ms": res.get("duration_api_ms"),
    "total_cost_usd": res.get("total_cost_usd"),
    "session_id": res.get("session_id"),
    "agent_subtype": res.get("subtype"),
    "agent_is_error": res.get("is_error"),
    "input_tokens": usage.get("input_tokens"),
    "output_tokens": usage.get("output_tokens"),
    "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
    "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
    "src_dir": txt("src_dir"),
    "test_dir": txt("test_dir"),
    "trigger_tests": [t for t in txt("trigger_tests").splitlines() if t],
    "failing_before": count("test_before.txt"),
    "failing_relevant_after": count("test_rel.txt"),
    "failing_full_after": count("test_after.txt"),
    "patch_files": patch_files,
    "patch_added_lines": added,
    "patch_removed_lines": removed,
    "has_dev_patch": (O / "dev.patch").exists(),
}

(O / "result.json").write_text(json.dumps(rec, indent=2) + "\n")

R = pathlib.Path(rundir)
with open(R / ".lock", "a") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    with open(R / "results.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    # USAGE_LIMIT is an infrastructure stall, not a result: leave it in the queue.
    if rec["verdict"] != "USAGE_LIMIT":
        with open(R / "done.txt", "a") as f:
            f.write(f"{proj}\t{bug}\n")
    fcntl.flock(lk, fcntl.LOCK_UN)
