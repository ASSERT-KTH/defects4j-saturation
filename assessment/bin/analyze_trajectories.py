#!/usr/bin/env python3
"""Deterministic trajectory abstraction and outlier ranking for agent sessions.

Usage:
  analyze_trajectories.py <campaignDir|dataDir> [--out outDir] [--top N]

For each data/<bug>/session.jsonl(.gz), emits:
  * trajectory_actions.jsonl  normalized action stream per bug
  * trajectory_features.csv   fixed per-bug features
  * trajectory_outliers.jsonl ranked deterministic anomaly candidates
  * trajectory_outliers.md    human-readable report; all rows by default

By default, outputs are written under assessment/results/<campaign-path>/ so the
original campaign tree is treated as input data.
"""
import argparse
import csv
import gzip
import json
import math
import pathlib
import re
import shlex
import statistics
from collections import Counter, defaultdict


SRC_MARKERS = ("/src/main/java/", "/source/", "/src/java/", "/src/", "/java/")
TEST_MARKERS = ("/src/test/", "/tests/", "/test/")
BUILD_NAMES = ("pom.xml", "build.xml", "build.gradle", "settings.gradle", "ivy.xml")
BINARY_EXTS = (".jar", ".class", ".war", ".zip")
SOURCE_EXTS = (".java", ".kt", ".scala", ".groovy")
SEARCH_CMDS = {"grep", "rg", "find", "sed", "awk"}
TEST_PAT = re.compile(
    r"\bdefects4j\s+test\b|\bmvn\s+test\b|\bgradle\s+test\b|\bant\s+test\b|"
    r"\borg\.junit\.runner\.JUnitCore\b"
)
COMPILE_PAT = re.compile(r"\bdefects4j\s+compile\b|\bmvn\s+compile\b|\bgradle\s+compile\b|\bant\s+compile\b")
BINARY_TOOLS = {"javap", "unzip", "jar", "cfr", "procyon", "jd-cli", "fernflower", "strings"}
ROOT_FIND_PAT = re.compile(r"\bfind\s+/\s")
PATH_PAT = re.compile(r"(?:~|/)[A-Za-z0-9_./@%+=:,{}()#~-]+")
SNIPPET_LEN = 240
ROOT = pathlib.Path(__file__).resolve().parents[2]


def open_text(path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", errors="replace")
    return open(path, errors="replace")


def parse_id(name):
    project, bug = name.rsplit("-", 1)
    return project, int(bug)


def load_results(root):
    results = root / "results" / "results.jsonl"
    if not results.is_file() and (root / "results.jsonl").is_file():
        results = root / "results.jsonl"
    out = {}
    if not results.is_file():
        return out
    for line in results.read_text(errors="replace").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["id"]] = r
    return out


def session_path(bugdir):
    plain = bugdir / "session.jsonl"
    gz = bugdir / "session.jsonl.gz"
    if plain.is_file():
        return plain
    if gz.is_file():
        return gz
    return None


def find_data_root(path):
    p = pathlib.Path(path)
    return p / "data" if (p / "data").is_dir() else p


def default_output_dir(campaign):
    resolved = pathlib.Path(campaign).resolve()
    try:
        rel = resolved.relative_to(ROOT)
    except ValueError:
        rel = pathlib.Path(resolved.name)
    return ROOT / "assessment" / "results" / rel


def block_key(msg, block, index):
    return (
        msg.get("id"),
        block.get("type"),
        block.get("id") or index,
        len(json.dumps(block, sort_keys=True)),
    )


def extract_paths(text):
    paths = []
    for m in PATH_PAT.finditer(text or ""):
        p = m.group(0).strip("'\"` ,;)")
        if p and len(p) > 1:
            paths.append(p)
    return paths


def path_category(path, workspace):
    p = path.replace("\\", "/")
    ws = (workspace or "").replace("\\", "/")
    in_ws = bool(ws and (p == ws or p.startswith(ws + "/")))
    low = p.lower()
    name = p.rsplit("/", 1)[-1]
    if any(x in low for x in ("/.m2/", "/.gradle/", "/.ivy2/", "/repository/")):
        return "cache"
    if low.startswith("/tmp/") or low.startswith("/private/tmp/"):
        return "tmp"
    if in_ws and any(m in p for m in TEST_MARKERS):
        return "test"
    if in_ws and any(m in p for m in SRC_MARKERS):
        return "source"
    if in_ws and name in BUILD_NAMES:
        return "build"
    if in_ws:
        return "workspace_other"
    if p.startswith("/") or p.startswith("~"):
        return "external"
    return "relative"


def file_kind(path):
    low = path.lower()
    if low.endswith(SOURCE_EXTS):
        return "source_file"
    if low.endswith(BINARY_EXTS):
        return "binary_file"
    if low.endswith((".xml", ".gradle", ".properties", ".yml", ".yaml")):
        return "config_file"
    if low.endswith((".patch", ".diff")):
        return "patch_file"
    if low.endswith((".txt", ".log", ".out")):
        return "text_file"
    return "other_file"


def shell_tokens(command):
    try:
        toks = shlex.split(command)
    except ValueError:
        toks = command.split()
    clean = []
    for t in toks:
        t = t.strip()
        if not t:
            continue
        if t.startswith("-"):
            continue
        if "/" in t:
            continue
        if len(t) > 40:
            continue
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.+-]*", t):
            clean.append(t.lower())
    return clean


def snippet(text, max_len=SNIPPET_LEN):
    return " ".join((text or "").split())[:max_len]


def command_action(command, paths, workspace):
    c = command or ""
    cats = {path_category(p, workspace) for p in paths}
    if TEST_PAT.search(c):
        return "RUN_TEST"
    if COMPILE_PAT.search(c):
        return "RUN_COMPILE"
    toks = shell_tokens(c)
    if any(t in BINARY_TOOLS for t in toks) and any(p.lower().endswith(BINARY_EXTS) for p in paths):
        return "BINARY_INSPECTION"
    if toks and toks[0] in SEARCH_CMDS:
        if "source" in cats:
            return "SEARCH_SOURCE"
        if "test" in cats:
            return "SEARCH_TEST"
        if "cache" in cats or ROOT_FIND_PAT.search(c):
            return "SEARCH_EXTERNAL"
        return "SEARCH"
    if "cache" in cats or "external" in cats:
        return "TOUCH_EXTERNAL"
    if "source" in cats:
        return "BASH_SOURCE"
    if "test" in cats:
        return "BASH_TEST"
    return "BASH_OTHER"


def tool_action(name, inp, workspace):
    text = json.dumps(inp, sort_keys=True)
    paths = extract_paths(text)
    if name == "Bash":
        command = inp.get("command") or ""
        return command_action(command, paths, workspace), paths, shell_tokens(command), command
    path = inp.get("file_path") or inp.get("path") or ""
    paths = [path] if path else paths
    cats = {path_category(p, workspace) for p in paths}
    prefix = "READ" if name == "Read" else "EDIT" if name == "Edit" else "WRITE" if name == "Write" else name.upper()
    if "source" in cats:
        return f"{prefix}_SOURCE", paths, [], ""
    if "test" in cats:
        return f"{prefix}_TEST", paths, [], ""
    if "build" in cats:
        return f"{prefix}_BUILD", paths, [], ""
    if "cache" in cats or "external" in cats:
        return f"{prefix}_EXTERNAL", paths, [], ""
    return f"{prefix}_OTHER", paths, [], ""


def parse_session(path):
    workspace = ""
    actions = []
    blockseen = set()
    with open_text(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "system" and ev.get("subtype") == "init":
                workspace = ev.get("cwd") or workspace
                continue
            if ev.get("type") == "assistant":
                msg = ev.get("message") or {}
                for i, b in enumerate(msg.get("content") or []):
                    key = block_key(msg, b, i)
                    if key in blockseen:
                        continue
                    blockseen.add(key)
                    if b.get("type") == "text":
                        text = b.get("text") or ""
                        if text.strip():
                            actions.append({
                                "line": lineno,
                                "kind": "ASSISTANT_TEXT",
                                "tool": "",
                                "paths": [],
                                "tokens": [],
                                "snippet": snippet(text),
                                "full_text": text,
                            })
                    elif b.get("type") == "tool_use":
                        name = b.get("name") or ""
                        inp = b.get("input") or {}
                        action, paths, tokens, command = tool_action(name, inp, workspace)
                        full_text = command or json.dumps(inp, sort_keys=True)
                        actions.append({
                            "line": lineno,
                            "kind": action,
                            "tool": name,
                            "paths": paths,
                            "path_categories": [path_category(p, workspace) for p in paths],
                            "file_kinds": [file_kind(p) for p in paths],
                            "tokens": tokens,
                            "snippet": snippet(full_text),
                            "full_text": full_text,
                        })
            elif ev.get("type") == "user":
                msg = ev.get("message") or {}
                for i, b in enumerate(msg.get("content") or []):
                    key = block_key(msg, b, i)
                    if key in blockseen:
                        continue
                    blockseen.add(key)
                    if b.get("type") != "tool_result":
                        continue
                    content = b.get("content") or ""
                    if isinstance(content, list):
                        full_text = "\n".join(
                            str(x.get("text") if isinstance(x, dict) else x)
                            for x in content
                        )
                    else:
                        full_text = str(content)
                    if not full_text.strip():
                        continue
                    paths = extract_paths(full_text)
                    actions.append({
                        "line": lineno,
                        "kind": "OBSERVATION",
                        "tool": "tool_result",
                        "tool_use_id": b.get("tool_use_id") or "",
                        "paths": paths,
                        "path_categories": [path_category(p, workspace) for p in paths],
                        "file_kinds": [file_kind(p) for p in paths],
                        "tokens": [],
                        "snippet": snippet(full_text),
                        "full_text": full_text,
                    })
            elif ev.get("type") == "result":
                full_text = json.dumps(ev, sort_keys=True)
                actions.append({
                    "line": lineno,
                    "kind": "RESULT",
                    "tool": "",
                    "paths": [],
                    "tokens": [],
                    "snippet": f"subtype={ev.get('subtype')} turns={ev.get('num_turns')} cost={ev.get('total_cost_usd')}",
                    "full_text": full_text,
                })
    return workspace, actions


def ngrams(seq, n):
    return [" > ".join(seq[i:i+n]) for i in range(0, max(0, len(seq) - n + 1))]


def features_for(bugid, workspace, actions, result):
    tool_actions = [a for a in actions if a["kind"] not in ("ASSISTANT_TEXT", "OBSERVATION", "RESULT")]
    kinds = [a["kind"] for a in tool_actions]
    paths = [p for a in tool_actions for p in a.get("paths", [])]
    cats = [path_category(p, workspace) for p in paths]
    toks = [t for a in tool_actions for t in a.get("tokens", [])]
    first_edit = next((i for i, k in enumerate(kinds) if k.startswith("EDIT") or k.startswith("WRITE")), None)
    first_test = next((i for i, k in enumerate(kinds) if k == "RUN_TEST"), None)
    tests = [i for i, k in enumerate(kinds) if k == "RUN_TEST"]
    edits = [i for i, k in enumerate(kinds) if k.startswith("EDIT") or k.startswith("WRITE")]
    max_no_test_span = 0
    last = -1
    for t in tests + [len(kinds)]:
        max_no_test_span = max(max_no_test_span, t - last - 1)
        last = t
    proj, bug = parse_id(bugid)
    return {
        "id": bugid,
        "project": proj,
        "bug": bug,
        "verdict": result.get("verdict", ""),
        "excluded": result.get("excluded", ""),
        "num_actions": len(kinds),
        "num_text_messages": sum(1 for a in actions if a["kind"] == "ASSISTANT_TEXT"),
        "num_unique_actions": len(set(kinds)),
        "num_reads": sum(1 for k in kinds if k.startswith("READ")),
        "num_source_reads": sum(1 for k in kinds if k == "READ_SOURCE"),
        "num_test_reads": sum(1 for k in kinds if k == "READ_TEST"),
        "num_searches": sum(1 for k in kinds if k.startswith("SEARCH")),
        "num_external_searches": sum(1 for k in kinds if k == "SEARCH_EXTERNAL"),
        "num_edits": len(edits),
        "num_compile": sum(1 for k in kinds if k == "RUN_COMPILE"),
        "num_test_runs": len(tests),
        "num_binary_inspections": sum(1 for k in kinds if k == "BINARY_INSPECTION"),
        "num_external_path_refs": sum(1 for c in cats if c in ("external", "cache")),
        "num_tmp_path_refs": sum(1 for c in cats if c == "tmp"),
        "num_unique_paths": len(set(paths)),
        "num_unique_source_paths": len({p for p in paths if path_category(p, workspace) == "source"}),
        "num_unique_test_paths": len({p for p in paths if path_category(p, workspace) == "test"}),
        "num_unique_external_paths": len({p for p in paths if path_category(p, workspace) in ("external", "cache")}),
        "turn_to_first_edit": "" if first_edit is None else first_edit + 1,
        "turn_to_first_test": "" if first_test is None else first_test + 1,
        "edits_before_first_test": sum(1 for e in edits if first_test is None or e < first_test),
        "actions_before_first_edit": "" if first_edit is None else first_edit,
        "longest_no_test_span": max_no_test_span,
        "has_find_root": int(any(ROOT_FIND_PAT.search(a.get("full_text") or a.get("snippet", "")) for a in tool_actions)),
        "has_cache_access": int(any(path_category(p, workspace) == "cache" for p in paths)),
        "has_binary_inspection": int(any(k == "BINARY_INSPECTION" for k in kinds)),
        "tokens": " ".join(sorted(set(toks))),
        "sequence": " ".join(kinds),
        "bigrams": " || ".join(ngrams(kinds, 2)),
        "trigrams": " || ".join(ngrams(kinds, 3)),
    }


def robust_score(value, vals):
    vals = [v for v in vals if isinstance(v, (int, float))]
    if len(vals) < 3:
        return 0.0
    med = statistics.median(vals)
    devs = [abs(v - med) for v in vals]
    mad = statistics.median(devs)
    if mad == 0:
        return 1.0 if value != med else 0.0
    return abs(value - med) / (1.4826 * mad)


def rarity_maps(rows):
    action_df = Counter()
    token_df = Counter()
    bigram_df = Counter()
    trigram_df = Counter()
    for r in rows:
        action_df.update(set(r["sequence"].split()))
        token_df.update(set(r["tokens"].split()))
        bigram_df.update(set(x for x in r["bigrams"].split(" || ") if x))
        trigram_df.update(set(x for x in r["trigrams"].split(" || ") if x))
    return action_df, token_df, bigram_df, trigram_df


def score_rows(rows):
    numeric = [
        "num_actions", "num_reads", "num_searches", "num_edits", "num_test_runs",
        "num_external_path_refs", "num_unique_paths", "num_unique_source_paths",
        "actions_before_first_edit", "longest_no_test_span",
    ]
    cols = defaultdict(list)
    for r in rows:
        for k in numeric:
            v = r.get(k)
            if v != "":
                cols[k].append(float(v))
    action_df, token_df, bigram_df, trigram_df = rarity_maps(rows)
    n = len(rows)
    scored = []
    for r in rows:
        reasons = []
        score = 0.0
        for k in numeric:
            v = r.get(k)
            if v == "":
                continue
            z = robust_score(float(v), cols[k])
            if z >= 3:
                score += min(z, 8)
                reasons.append(f"extreme {k}: {v} (robust_z={z:.1f})")
        for flag, label in (
            ("has_find_root", "uses find rooted at /"),
            ("has_cache_access", "references dependency cache path"),
            ("has_binary_inspection", "inspects binary/archive artefact"),
        ):
            if int(r.get(flag) or 0):
                score += 4
                reasons.append(label)
        rare_actions = [a for a in set(r["sequence"].split()) if action_df[a] <= max(2, math.ceil(0.01 * n))]
        rare_tokens = [t for t in set(r["tokens"].split()) if token_df[t] <= max(2, math.ceil(0.01 * n))]
        rare_bigrams = [b for b in set(r["bigrams"].split(" || ")) if b and bigram_df[b] <= max(2, math.ceil(0.01 * n))]
        rare_trigrams = [t for t in set(r["trigrams"].split(" || ")) if t and trigram_df[t] <= max(2, math.ceil(0.01 * n))]
        if rare_actions:
            score += min(4, len(rare_actions))
            reasons.append("rare actions: " + ", ".join(sorted(rare_actions)[:6]))
        if rare_tokens:
            score += min(4, len(rare_tokens) * 0.5)
            reasons.append("rare command tokens: " + ", ".join(sorted(rare_tokens)[:10]))
        if rare_bigrams:
            score += min(3, len(rare_bigrams) * 0.5)
            reasons.append("rare action bigrams: " + " | ".join(sorted(rare_bigrams)[:4]))
        if rare_trigrams:
            score += min(3, len(rare_trigrams) * 0.5)
            reasons.append("rare action trigrams: " + " | ".join(sorted(rare_trigrams)[:4]))
        out = dict(r)
        out["anomaly_score"] = round(score, 3)
        out["reasons"] = reasons
        scored.append(out)
    return sorted(scored, key=lambda r: (-r["anomaly_score"], r["project"], r["bug"]))


def number(r, key):
    v = r.get(key)
    return 0 if v == "" else v


def category_rankings(scored):
    """Separate audit queues so qualitatively different deviations surface."""
    categories = [
        (
            "external_access",
            "Outside-workspace and dependency-cache behavior.",
            lambda r: (
                8 * number(r, "has_cache_access")
                + 8 * number(r, "has_find_root")
                + 2 * number(r, "num_external_searches")
                + number(r, "num_unique_external_paths")
            ),
            [
                "has_find_root", "has_cache_access", "num_external_searches",
                "num_unique_external_paths", "num_external_path_refs",
            ],
        ),
        (
            "binary_inspection",
            "Archive/class-file inspection and decompilation-like behavior.",
            lambda r: (
                10 * number(r, "has_binary_inspection")
                + 4 * number(r, "num_binary_inspections")
                + 2 * sum(t in r["tokens"].split() for t in ("javap", "unzip", "jar", "cfr", "procyon", "fernflower", "strings"))
            ),
            ["has_binary_inspection", "num_binary_inspections", "tokens"],
        ),
        (
            "volume",
            "Large exploratory trajectories by action/read/search/path volume.",
            lambda r: (
                number(r, "num_actions")
                + 2 * number(r, "num_reads")
                + 2 * number(r, "num_searches")
                + number(r, "num_unique_paths")
            ),
            ["num_actions", "num_reads", "num_searches", "num_unique_paths"],
        ),
        (
            "late_edit",
            "Long localization/search phase before the first source edit.",
            lambda r: (
                number(r, "actions_before_first_edit")
                + number(r, "num_unique_source_paths")
                + number(r, "num_searches")
            ),
            ["turn_to_first_edit", "actions_before_first_edit", "num_unique_source_paths", "num_searches"],
        ),
        (
            "test_loop",
            "Unusual compile/test cadence.",
            lambda r: (
                3 * number(r, "num_test_runs")
                + 2 * number(r, "num_compile")
                + number(r, "longest_no_test_span")
                + 3 * number(r, "edits_before_first_test")
            ),
            ["num_compile", "num_test_runs", "edits_before_first_test", "longest_no_test_span"],
        ),
        (
            "rare_sequence",
            "Rare action n-grams and rare command vocabulary.",
            lambda r: (
                sum(1 for reason in r["reasons"] if reason.startswith("rare action")) * 3
                + sum(1 for reason in r["reasons"] if reason.startswith("rare command")) * 2
            ),
            ["reasons"],
        ),
    ]
    out = {}
    for name, description, score_fn, fields in categories:
        ranked = []
        for r in scored:
            s = score_fn(r)
            if s:
                x = dict(r)
                x["category"] = name
                x["category_score"] = round(s, 3)
                x["category_fields"] = {k: r.get(k) for k in fields}
                ranked.append(x)
        out[name] = {
            "description": description,
            "rows": sorted(ranked, key=lambda r: (-r["category_score"], r["project"], r["bug"])),
        }
    return out


def md_cell(text):
    return str(text).replace("|", "\\|").replace("\n", "<br>")


def action_summary(action, max_len=170):
    snippet = action.get("snippet") or ""
    if len(snippet) > max_len:
        snippet = snippet[: max_len - 1] + "..."
    return f"L{action.get('line')} {action.get('kind')}: `{snippet}`"


def interesting_actions(actions, category, limit=3):
    tool_actions = [a for a in actions if a["kind"] not in ("ASSISTANT_TEXT", "OBSERVATION", "RESULT")]
    if category == "external_access":
        picks = [
            a for a in tool_actions
            if a["kind"] in ("SEARCH_EXTERNAL", "TOUCH_EXTERNAL")
            or any(c in ("external", "cache") for c in a.get("path_categories", []))
            or ROOT_FIND_PAT.search(a.get("full_text") or a.get("snippet", ""))
        ]
    elif category == "binary_inspection":
        binary_tokens = {"javap", "unzip", "jar", "cfr", "procyon", "fernflower", "strings"}
        picks = [
            a for a in tool_actions
            if a["kind"] == "BINARY_INSPECTION"
            or any(t in binary_tokens for t in a.get("tokens", []))
            or any(k == "binary_file" for k in a.get("file_kinds", []))
        ]
    elif category == "late_edit":
        first_edit = next((i for i, a in enumerate(tool_actions)
                           if a["kind"].startswith("EDIT") or a["kind"].startswith("WRITE")), None)
        before = tool_actions if first_edit is None else tool_actions[:first_edit]
        picks = before[-limit:]
    elif category == "test_loop":
        picks = [
            a for a in tool_actions
            if a["kind"] in ("RUN_COMPILE", "RUN_TEST")
            or a["kind"].startswith("EDIT")
            or a["kind"].startswith("WRITE")
        ]
    elif category == "volume":
        if len(tool_actions) <= limit:
            picks = tool_actions
        else:
            picks = tool_actions[:2] + tool_actions[-1:]
    elif category == "rare_sequence":
        rare_kinds = {"BINARY_INSPECTION", "TOUCH_EXTERNAL", "READ_EXTERNAL",
                      "EDIT_BUILD", "WRITE_BUILD", "EDIT_TEST", "WRITE_TEST"}
        picks = [a for a in tool_actions if a["kind"] in rare_kinds]
        if not picks:
            picks = [a for a in tool_actions
                     if any(t in a.get("tokens", []) for t in ("javap", "unzip", "jar", "strings", "python", "perl"))]
    else:
        picks = tool_actions[:limit]
    return picks[:limit]


def noteworthy_categories(r):
    reasons = r.get("reasons") or []
    names = []
    if r.get("has_find_root") or r.get("has_cache_access") or r.get("num_external_searches"):
        names.append("external-access")
    if r.get("has_binary_inspection") or r.get("num_binary_inspections"):
        names.append("binary-inspection")
    if any("num_actions" in x or "num_reads" in x or "num_searches" in x or "num_unique_paths" in x
           for x in reasons):
        names.append("volume")
    if any("actions_before_first_edit" in x for x in reasons):
        names.append("late-edit")
    if any("longest_no_test_span" in x or "num_test_runs" in x or "num_edits" in x for x in reasons):
        names.append("test-loop")
    if any(x.startswith("rare ") for x in reasons):
        names.append("rare-sequence")
    return names


def primary_category(r):
    for name in ("binary-inspection", "external-access", "late-edit", "test-loop", "rare-sequence", "volume"):
        if name in noteworthy_categories(r):
            return name.replace("-", "_")
    return "volume"


def compact_reasons(r, category_specific=False):
    if r.get("reasons") and not category_specific:
        return "<br>".join(r["reasons"][:5])
    fields = r.get("category_fields") or {}
    parts = []
    for k, v in fields.items():
        if k == "tokens":
            toks = str(v).split()
            interesting = [t for t in toks if t in ("javap", "unzip", "jar", "cfr", "procyon", "fernflower", "strings", "find")]
            v = ", ".join(interesting[:10]) if interesting else ", ".join(toks[:10])
        elif k == "reasons":
            v = "; ".join(str(x) for x in (v or [])[:4])
        parts.append(f"{k}={v}")
    return "<br>".join(parts)


def write_outputs(outdir, action_records, rows, scored, top):
    outdir.mkdir(parents=True, exist_ok=True)
    limit = None if top <= 0 else top
    actions_by_id = {r["id"]: r["actions"] for r in action_records}
    with open(outdir / "trajectory_actions.jsonl", "w") as f:
        for rec in action_records:
            f.write(json.dumps(rec) + "\n")
    cols = [k for k in rows[0].keys() if k not in ("sequence", "bigrams", "trigrams", "tokens")]
    with open(outdir / "trajectory_features.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sorted(rows, key=lambda x: (x["project"], x["bug"])):
            w.writerow({k: r.get(k, "") for k in cols})
    with open(outdir / "trajectory_outliers.jsonl", "w") as f:
        for r in scored:
            f.write(json.dumps(r) + "\n")
    cats = category_rankings(scored)
    with open(outdir / "trajectory_outlier_categories.jsonl", "w") as f:
        for name, cat in cats.items():
            for r in cat["rows"]:
                f.write(json.dumps(r) + "\n")
    with open(outdir / "trajectory_outliers.md", "w") as f:
        f.write("# Trajectory Outliers\n\n")
        f.write("Deterministic rankings over normalized session traces. Scores are heuristics for audit priority, not labels.\n\n")
        f.write("## Global Ranking\n\n")
        f.write("| rank | bug | verdict | excluded | score | categories | reasons | example actions |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(scored[:limit], 1):
            reasons = compact_reasons(r)
            memberships = ", ".join(noteworthy_categories(r))
            examples = "<br>".join(
                action_summary(a) for a in interesting_actions(actions_by_id.get(r["id"], []), primary_category(r))
            )
            f.write(f"| {i} | {r['id']} | {r['verdict']} | {r['excluded']} | "
                    f"{r['anomaly_score']:.1f} | {md_cell(memberships)} | {md_cell(reasons)} | "
                    f"{md_cell(examples)} |\n")
        for name, cat in cats.items():
            f.write(f"\n## {name.replace('_', ' ').title()}\n\n")
            f.write(cat["description"] + "\n\n")
            f.write("| rank | bug | verdict | excluded | category score | evidence | example actions |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for i, r in enumerate(cat["rows"][:limit], 1):
                examples = "<br>".join(
                    action_summary(a) for a in interesting_actions(actions_by_id.get(r["id"], []), name)
                )
                f.write(f"| {i} | {r['id']} | {r['verdict']} | {r['excluded']} | "
                        f"{r['category_score']:.1f} | {md_cell(compact_reasons(r, category_specific=True))} | "
                        f"{md_cell(examples)} |\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="campaign directory or data directory")
    ap.add_argument("--out", help="output directory; default: assessment/results/<campaign-path>")
    ap.add_argument("--top", type=int, default=0,
                    help="limit Markdown tables to top N rows; default 0 writes all rows")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    data = find_data_root(root)
    campaign = data.parent if data.name == "data" else root
    outdir = pathlib.Path(args.out) if args.out else default_output_dir(campaign)
    results = load_results(campaign)

    rows = []
    action_records = []
    for bugdir in sorted(d for d in data.iterdir() if d.is_dir() and "-" in d.name):
        sp = session_path(bugdir)
        if not sp:
            continue
        workspace, actions = parse_session(sp)
        result = results.get(bugdir.name, {})
        feat = features_for(bugdir.name, workspace, actions, result)
        rows.append(feat)
        action_records.append({
            "id": bugdir.name,
            "workspace": workspace,
            "session_file": str(sp),
            "actions": actions,
        })
    if not rows:
        raise SystemExit(f"no session.jsonl(.gz) files found under {data}")
    scored = score_rows(rows)
    write_outputs(outdir, action_records, rows, scored, args.top)
    print(f"analysed {len(rows)} sessions")
    print(f"wrote {outdir / 'trajectory_features.csv'}")
    print(f"wrote {outdir / 'trajectory_outliers.md'}")


if __name__ == "__main__":
    main()
