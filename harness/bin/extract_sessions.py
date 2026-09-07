#!/usr/bin/env python3
"""One pass over every claude.jsonl in a run directory.

Emits <runDir>/sessions.jsonl with, per bug:
  * the result event's usage (ground truth, where the event survived)
  * the same quantities re-summed from the stream (for the timeout fallback)
  * the agent's closing claim, for the self-certification analysis: every
    assistant text block emitted after its LAST `defects4j test` run. The
    success assertion and the required root-cause report are usually separate
    messages, so the final message alone is not the claim; the last test run is
    an objective delimiter for the window in which the agent states its verdict.

Usage: extract_sessions.py <runDir>
"""
import json, pathlib, sys

def blocks(msg, seen):
    """Content blocks of one assistant message, de-duplicated.

    The stream emits one `assistant` event per content block, each carrying the
    whole message-so-far, so blocks repeat across events."""
    for i, b in enumerate(msg.get("content") or []):
        key = (msg.get("id"), b.get("type"), b.get("id") or i, len(json.dumps(b, sort_keys=True)))
        if key in seen:
            continue
        seen.add(key)
        yield b

def one(path):
    rec = {"result_usage": None, "num_turns": None, "cost": None, "subtype": None,
           "stream": {"input_tokens": 0, "cache_read_input_tokens": 0,
                      "cache_creation_input_tokens": 0,
                      "ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0},
           "thinking_delta": 0, "text_chars": 0, "tool_chars": 0,
           "turns": 0, "model": None, "final_text": "", "all_text_tail": [],
           "closing_text": "", "test_runs": 0, "rate_limit_events": 0,
           "bad_lines": 0}
    msgseen, blockseen = set(), set()
    texts = []
    # (is_test_run, text) in stream order, so the closing window can be cut at
    # the last test run
    timeline = []
    for line in open(path, errors="replace"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            rec["bad_lines"] += 1
            continue
        t = ev.get("type")
        if t == "result":
            rec["result_usage"] = ev.get("usage")
            rec["num_turns"] = ev.get("num_turns")
            rec["cost"] = ev.get("total_cost_usd")
            rec["subtype"] = ev.get("subtype")
        elif t == "rate_limit_event":
            rec["rate_limit_events"] += 1
        elif t == "system" and ev.get("subtype") == "thinking_tokens":
            rec["thinking_delta"] += ev.get("estimated_tokens_delta") or 0
        elif t == "assistant":
            msg = ev.get("message") or {}
            rec["model"] = msg.get("model") or rec["model"]
            mid = msg.get("id")
            if mid not in msgseen:
                msgseen.add(mid)
                rec["turns"] += 1
                u = msg.get("usage") or {}
                for k in ("input_tokens", "cache_read_input_tokens",
                          "cache_creation_input_tokens"):
                    rec["stream"][k] += u.get(k) or 0
                cc = u.get("cache_creation") or {}
                for k in ("ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens"):
                    rec["stream"][k] += cc.get(k) or 0
            for b in blocks(msg, blockseen):
                bt = b.get("type")
                if bt == "text":
                    s = b.get("text") or ""
                    rec["text_chars"] += len(s)
                    if s.strip():
                        texts.append(s)
                        timeline.append((False, s))
                elif bt == "thinking":
                    rec["text_chars"] += len(b.get("thinking") or "")
                elif bt == "tool_use":
                    inp = b.get("input") or {}
                    rec["tool_chars"] += len(json.dumps(inp))
                    cmd = inp.get("command") or ""
                    if isinstance(cmd, str) and "defects4j test" in cmd:
                        rec["test_runs"] += 1
                        timeline.append((True, None))
    rec["final_text"] = texts[-1] if texts else ""
    rec["all_text_tail"] = texts[-3:]
    cut = max((i for i, (t, _) in enumerate(timeline) if t), default=-1)
    rec["closing_text"] = "\n\n".join(x for t, x in timeline[cut + 1:] if not t)
    return rec

def main():
    run = pathlib.Path(sys.argv[1])
    out = run / "sessions.jsonl"
    with open(out, "w") as f:
        for d in sorted(run.iterdir()):
            log = d / "claude.jsonl"
            if not log.is_file():
                continue
            rec = one(log)
            rec["id"] = d.name
            f.write(json.dumps(rec) + "\n")
    print(f"wrote {out}")

main()
