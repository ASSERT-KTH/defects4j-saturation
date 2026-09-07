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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import telemetry as T

MODEL = os.environ.get("AGENT_MODEL", T.DEFAULT_MODEL)

res = {}
msgseen, blockseen = set(), set()
stream = dict.fromkeys(("input_tokens", "cache_read_input_tokens",
                        "cache_creation_input_tokens",
                        "ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens"), 0)
thinking_delta = text_chars = tool_chars = 0
stream_model = None
try:
    for line in (O / "claude.jsonl").read_text(errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "result":
            res = ev
        elif t == "system" and ev.get("subtype") == "thinking_tokens":
            thinking_delta += ev.get("estimated_tokens_delta") or 0
        elif t == "assistant":
            msg = ev.get("message") or {}
            stream_model = msg.get("model") or stream_model
            mid = msg.get("id")
            if mid not in msgseen:
                msgseen.add(mid)
                u = msg.get("usage") or {}
                for k in ("input_tokens", "cache_read_input_tokens",
                          "cache_creation_input_tokens"):
                    stream[k] += u.get(k) or 0
                cc = u.get("cache_creation") or {}
                for k in ("ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens"):
                    stream[k] += cc.get(k) or 0
            # the stream emits one event per content block, each carrying the
            # whole message so far, so blocks repeat across events
            for i, b in enumerate(msg.get("content") or []):
                key = (mid, b.get("type"), b.get("id") or i,
                       len(json.dumps(b, sort_keys=True)))
                if key in blockseen:
                    continue
                blockseen.add(key)
                if b.get("type") == "text":
                    text_chars += len(b.get("text") or "")
                elif b.get("type") == "thinking":
                    text_chars += len(b.get("thinking") or "")
                elif b.get("type") == "tool_use":
                    tool_chars += len(json.dumps(b.get("input") or {}))
except OSError:
    pass

telemetry_source = "result_event"
if not res and msgseen:
    # No result event: the wall-clock kill beat the CLI's own reporting. Rebuild
    # what can be rebuilt exactly (input and cache tokens, both verified exact on
    # 851/852 sessions of runs/full) and estimate output tokens.
    telemetry_source = "stream_estimate"
    model = stream_model or MODEL
    est_out = T.estimate_output_tokens(thinking_delta, text_chars, tool_chars)
    usage = {"input_tokens": stream["input_tokens"],
             "output_tokens": est_out,
             "cache_read_input_tokens": stream["cache_read_input_tokens"],
             "cache_creation_input_tokens": stream["cache_creation_input_tokens"]}
    res = {"num_turns": len(msgseen),
           "total_cost_usd": round(T.cost_usd(
               model, stream["input_tokens"], est_out,
               stream["cache_read_input_tokens"],
               stream["ephemeral_5m_input_tokens"],
               stream["ephemeral_1h_input_tokens"]), 6),
           "subtype": None, "is_error": None}
else:
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
    "campaign": os.environ.get("CAMPAIGN", "perfect-fault-localization"),
    "model": stream_model or MODEL,
    "effort": os.environ.get("AGENT_EFFORT", "high"),
    "telemetry_source": telemetry_source,
    "thinking_tokens": (usage.get("output_tokens_details") or {}).get("thinking_tokens")
                       if telemetry_source == "result_event" else thinking_delta,
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
