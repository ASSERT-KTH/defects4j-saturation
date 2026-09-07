#!/usr/bin/env python3
"""Audit every agent session for access to Defects4J ground truth.

The agents ran with unrestricted Bash, so several paths on the host could in
principle have revealed the developer fix:

  1. $D4J_HOME/framework/projects/<P>/patches/<N>.src.patch  - the fix itself
  2. $D4J_HOME/project_repos/<own project>.git               - upstream history
  3. <work>/../<P>-<N>.gitorig                               - the checkout's
     original .git, carrying D4J_<P>_<N>_FIXED_VERSION
  4. `defects4j checkout -v <N>f`                            - the fixed version
  5. any D4J_*_FIXED_VERSION tag reference

This script greps the tool calls of every session for each channel and prints a
per-channel verdict. Reading a *dependency's* published source (e.g. the
jackson-core repo while repairing jackson-databind) is reported separately: it
is not ground truth for the bug under repair.

Usage: audit_contamination.py <runDir>
"""
import json, pathlib, re, sys, collections

RUN = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "runs/full")

# project id -> the bare repo Defects4J clones it from
REPO = {
    "Chart": "jfreechart", "Cli": "commons-cli", "Closure": "closure-compiler",
    "Codec": "commons-codec", "Collections": "commons-collections",
    "Compress": "commons-compress", "Csv": "commons-csv", "Gson": "gson",
    "JacksonCore": "jackson-core", "JacksonDatabind": "jackson-databind",
    "JacksonXml": "jackson-dataformat-xml", "Jsoup": "jsoup",
    "JxPath": "commons-jxpath", "Lang": "commons-lang", "Math": "commons-math",
    "Mockito": "mockito", "Time": "joda-time",
}

CHANNELS = {
    "developer patch (patches/*.src.patch)": re.compile(r"framework/projects/[A-Za-z]+/patches"),
    "moved-aside .git (.gitorig)":           re.compile(r"\.gitorig"),
    "checkout of the fixed version":         re.compile(r"defects4j\s+checkout[^\"']*-v\s*\d+f"),
    "D4J_*_FIXED_VERSION tag":               re.compile(r"D4J_[A-Za-z]+_\d+_(FIXED|POST_FIX)"),
}

def tool_calls(path):
    for line in path.read_text(errors="replace").splitlines():
        if '"tool_use"' not in line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (ev.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if b.get("type") == "tool_use":
                yield json.dumps(b.get("input") or {})

flagged = collections.defaultdict(list)
own_repo, dep_repo = [], []
sessions = sorted(RUN.glob("*/claude.jsonl"))

for path in sessions:
    bug = path.parent.name
    project = bug.rsplit("-", 1)[0]
    own = REPO.get(project)
    for inp in tool_calls(path):
        for name, rx in CHANNELS.items():
            if rx.search(inp):
                flagged[name].append((bug, inp[:200]))
        for m in re.finditer(r"project_repos/([a-z0-9-]+)\.git", inp):
            (own_repo if m.group(1) == own else dep_repo).append((bug, m.group(1), inp[:200]))

print(f"sessions audited: {len(sessions)}\n")
print("ground-truth channels")
bad = 0
for name in CHANNELS:
    n = len({b for b, _ in flagged[name]})
    bad += n
    print(f"  {'HIT ' if n else 'none'}  {name:40} {n} session(s)")
    for b, snip in flagged[name][:5]:
        print(f"          {b}: {snip}")

n_own = len({b for b, _, _ in own_repo})
bad += n_own
print(f"  {'HIT ' if n_own else 'none'}  {'upstream repo of the bug under repair':40} {n_own} session(s)")
for b, r, snip in own_repo[:5]:
    print(f"          {b} -> {r}.git: {snip}")

print(f"\nnot ground truth, reported for completeness")
deps = collections.Counter(b for b, _, _ in dep_repo)
print(f"  a *dependency's* upstream repo: {len(deps)} session(s)")
for b, n in deps.most_common(10):
    repos = sorted({r for bb, r, _ in dep_repo if bb == b})
    print(f"          {b}: {repos} ({n} calls)")

print(f"\nVERDICT: {'CLEAN - no session read the ground truth for its own bug' if bad == 0 else f'{bad} contaminated session(s)'}")
sys.exit(0 if bad == 0 else 1)
