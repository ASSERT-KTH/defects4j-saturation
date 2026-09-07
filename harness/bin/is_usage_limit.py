#!/usr/bin/env python3
"""Exit 0 if a session was cut short by the account's usage limit.

A run stopped by the usage limit is not a result -- it is an interrupted
attempt, and must go back in the queue rather than be scored.

Decided from the CLI's own final `result` event, not from free text anywhere in
the log. The earlier text-grep version of this check missed the real thing
twice over: the CLI's wording is "session limit", which none of the patterns
matched, and it reports `subtype: "success"` together with `is_error: true`, so
the absence-of-success guard suppressed it anyway.

Usage: is_usage_limit.py <claude.jsonl>
"""
import json, re, sys

LIMIT_RE = (r"session limit|usage limit|rate.?limit(ed)?|too many requests"
            r"|overloaded_error|quota|insufficient credit")

def main():
    try:
        res = None
        for line in open(sys.argv[1], errors="replace"):
            if '"type":"result"' in line:
                try:
                    res = json.loads(line)
                except json.JSONDecodeError:
                    pass
    except OSError:
        return 1
    if not res:
        return 1
    text = " ".join(str(res.get(k) or "") for k in ("result", "error", "message"))
    return 0 if (res.get("is_error") and re.search(LIMIT_RE, text, re.I)) else 1

if __name__ == "__main__":
    sys.exit(main())
