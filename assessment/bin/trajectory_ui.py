#!/usr/bin/env python3
"""Local UI for inspecting and annotating agent repair trajectories.

Usage:
  python3 assessment/bin/trajectory_ui.py campaign/no-fault-localization [--port 8768]
"""
import argparse
import csv
import json
import mimetypes
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from analyze_trajectories import features_for, find_data_root, parse_session, session_path


ROOT = pathlib.Path(__file__).resolve().parents[2]
UI_DIR = ROOT / "assessment" / "ui"
PROMPTS_DIR = ROOT / "assessment" / "prompts"
STEP_EXPLANATION_PROMPT = PROMPTS_DIR / "step_explanation.txt"
ROOT_FIND_PAT = re.compile(r"\bfind\s+/\s")


def default_results_dir(campaign):
    resolved = pathlib.Path(campaign).resolve()
    try:
        rel = resolved.relative_to(ROOT)
    except ValueError:
        rel = pathlib.Path(resolved.name)
    return ROOT / "assessment" / "results" / rel


def read_jsonl(path):
    rows = []
    if not path.is_file():
        return rows
    for line in path.read_text(errors="replace").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def read_csv(path):
    if not path.is_file():
        return {}
    with open(path, newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def bug_sort_key(bug_id):
    project, num = bug_id.rsplit("-", 1)
    return project, int(num)


def norm_patch_lines(lines):
    out = []
    for line in lines:
        s = re.sub(r"//.*$", "", line[1:]).strip()
        s = re.sub(r"\s+", " ", s)
        if s:
            out.append(s)
    return sorted(out)


def patch_sides(text):
    add = [line for line in text.splitlines() if line.startswith("+") and not line.startswith("+++")]
    rem = [line for line in text.splitlines() if line.startswith("-") and not line.startswith("---")]
    files = sorted({
        line.split(" b/", 1)[1]
        for line in text.splitlines()
        if line.startswith("diff --git ") and " b/" in line
    })
    return norm_patch_lines(add), norm_patch_lines(rem), files


def patch_similarity(campaign, bug_id):
    bugdir = campaign / "data" / bug_id
    patch = bugdir / "patch.diff"
    dev = bugdir / "dev.patch"
    if not (patch.is_file() and dev.is_file()):
        return ""
    a_add, a_rem, a_files = patch_sides(patch.read_text(errors="replace"))
    d_add, d_rem, d_files = patch_sides(dev.read_text(errors="replace"))
    if a_add == d_rem and a_rem == d_add:
        return "identical"
    if a_files == d_files:
        return "same-files"
    return "different"


class Store:
    def __init__(self, campaign, ollama_url, ollama_model, results_dir=None):
        self.campaign = pathlib.Path(campaign).resolve()
        self.campaign_results_dir = self.campaign / "results"
        self.results_dir = pathlib.Path(results_dir).resolve() if results_dir else default_results_dir(self.campaign)
        self.annotations_path = self.results_dir / "trajectory_annotations.json"
        self.ollama_url = ollama_url.rstrip("/")
        self.ollama_model = ollama_model
        self.actions = {}
        self.features = {}
        self.results = {}
        self.result_rows = {}
        self.categories = {}
        self.assistant_text_layers = []
        self.assistant_text_rows = {}
        self.analysis_done = False
        self.reload()

    def ollama_models(self):
        req = urllib.request.Request(self.ollama_url + "/api/tags", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read().decode())
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"ollama model listing failed at {self.ollama_url}; start Ollama with `ollama serve`"
            ) from e
        names = []
        for model in data.get("models") or []:
            name = model.get("name") or model.get("model")
            if name:
                names.append(name)
        if self.ollama_model and self.ollama_model not in names:
            names.insert(0, self.ollama_model)
        return names

    def set_ollama_model(self, model):
        model = str(model or "").strip()
        if not model:
            raise ValueError("missing model")
        self.ollama_model = model
        return self.ollama_model

    def reload(self):
        actions_path = self.results_dir / "trajectory_actions.jsonl"
        features_path = self.results_dir / "trajectory_features.csv"
        results_path = self.campaign_results_dir / "results.jsonl"
        result_rows_path = self.campaign_results_dir / "results.csv"
        categories_path = self.results_dir / "trajectory_outlier_categories.jsonl"

        self.results = {r["id"]: r for r in read_jsonl(results_path)}
        self.result_rows = read_csv(result_rows_path)
        self.actions = {r["id"]: r for r in read_jsonl(actions_path)}
        self.features = read_csv(features_path)
        self.analysis_done = actions_path.is_file() and features_path.is_file()
        if not self.actions:
            self.actions, self.features = self.load_raw_sessions()
            self.analysis_done = False
        self.categories = {}
        category_rank = {}
        for r in read_jsonl(categories_path):
            cat = r.get("category")
            category_rank[cat] = category_rank.get(cat, 0) + 1
            self.categories.setdefault(r["id"], []).append({
                "category": cat,
                "rank": category_rank[cat],
                "score": r.get("category_score"),
                "fields": r.get("category_fields") or {},
            })
        self.load_assistant_text_assessments()

    def load_assistant_text_assessments(self):
        self.assistant_text_layers = []
        self.assistant_text_rows = {}
        root = self.results_dir / "assistant_text"
        if not root.is_dir():
            return
        for path in sorted(root.glob("*/*/assistant_text_assessment.jsonl")):
            try:
                rel = path.relative_to(root)
            except ValueError:
                continue
            if len(rel.parts) != 3:
                continue
            model, mode = rel.parts[0], rel.parts[1]
            if mode not in ("suspicious", "all"):
                continue
            rows = []
            bad_rows = 0
            for line in path.read_text(errors="replace").splitlines():
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    bad_rows += 1
                    continue
                rows.append(row)
            key = f"{model}/{mode}"
            self.assistant_text_rows[key] = rows
            self.assistant_text_layers.append({
                "key": key,
                "model": model,
                "mode": mode,
                "count": len(rows),
                "bad_rows": bad_rows,
                "path": str(path),
            })

    def default_assistant_text_layer(self):
        if not self.assistant_text_layers:
            return None
        suspicious = [l for l in self.assistant_text_layers if l["mode"] == "suspicious"]
        return sorted(suspicious or self.assistant_text_layers, key=lambda l: (l["model"], l["mode"]))[0]

    def assistant_text_index(self, key):
        rows = self.assistant_text_rows.get(key) or []
        by_bug = {}
        for row in rows:
            bug_id = row.get("bug_id")
            if not bug_id:
                continue
            by_bug.setdefault(bug_id, {})[str(row.get("step_index"))] = row
        return by_bug

    def assistant_text_rows_for(self, key):
        return self.assistant_text_rows.get(key) or []

    def load_raw_sessions(self):
        data = find_data_root(self.campaign)
        actions = {}
        features = {}
        if not data.is_dir():
            return actions, features
        for bugdir in sorted(d for d in data.iterdir() if d.is_dir() and "-" in d.name):
            sp = session_path(bugdir)
            if not sp:
                continue
            workspace, trace_actions = parse_session(sp)
            result = self.results.get(bugdir.name, {})
            feat = features_for(bugdir.name, workspace, trace_actions, result)
            actions[bugdir.name] = {
                "id": bugdir.name,
                "workspace": workspace,
                "session_file": str(sp),
                "actions": trace_actions,
            }
            features[bugdir.name] = {k: str(v) for k, v in feat.items()}
        return actions, features

    def annotations(self):
        if not self.annotations_path.is_file():
            return []
        try:
            data = json.loads(self.annotations_path.read_text(errors="replace"))
        except json.JSONDecodeError:
            return []
        return data if isinstance(data, list) else []

    def save_annotations(self, annotations):
        self.results_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.annotations_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(annotations, indent=2, sort_keys=True) + "\n")
        tmp.replace(self.annotations_path)

    def bug_list(self):
        anns = self.annotations()
        counts = {}
        suspicious_counts = {}
        for ann in anns:
            bug_id = ann.get("bug_id")
            counts[bug_id] = counts.get(bug_id, 0) + 1
            if ann.get("status") in ("suspicious", "interesting", "unclear"):
                suspicious_counts[bug_id] = suspicious_counts.get(bug_id, 0) + 1
        bugs = []
        for bug_id in sorted(self.actions, key=bug_sort_key):
            feat = self.features.get(bug_id, {})
            result = self.results.get(bug_id, {})
            result_row = self.result_rows.get(bug_id, {})
            similarity = result_row.get("similarity") or patch_similarity(self.campaign, bug_id)
            cats = sorted({c["category"] for c in self.categories.get(bug_id, []) if c.get("category")})
            bugs.append({
                "id": bug_id,
                "project": feat.get("project") or result.get("project"),
                "bug": feat.get("bug") or result.get("bug"),
                "verdict": feat.get("verdict") or result.get("verdict"),
                "excluded": feat.get("excluded") or result.get("excluded", ""),
                "similarity": similarity,
                "num_actions": int(feat.get("num_actions") or 0),
                "num_searches": int(feat.get("num_searches") or 0),
                "num_edits": int(feat.get("num_edits") or 0),
                "num_test_runs": int(feat.get("num_test_runs") or 0),
                "has_find_root": int(feat.get("has_find_root") or 0),
                "has_cache_access": int(feat.get("has_cache_access") or 0),
                "has_binary_inspection": int(feat.get("has_binary_inspection") or 0),
                "categories": cats,
                "annotation_count": counts.get(bug_id, 0),
                "open_count": suspicious_counts.get(bug_id, 0),
            })
        return bugs

    def bug_detail(self, bug_id, assistant_text_key=None):
        if bug_id not in self.actions:
            return None
        anns = [a for a in self.annotations() if a.get("bug_id") == bug_id]
        assessment_by_step = {}
        if assistant_text_key:
            assessment_by_step = self.assistant_text_index(assistant_text_key).get(bug_id, {})
        return {
            "bug": self.bug_list_by_id().get(bug_id),
            "feature": self.features.get(bug_id, {}),
            "result": self.results.get(bug_id, {}),
            "categories": self.categories.get(bug_id, []),
            "workspace": self.actions[bug_id].get("workspace"),
            "session_file": self.actions[bug_id].get("session_file"),
            "actions": self.actions[bug_id].get("actions", []),
            "annotations": anns,
            "assistant_text_assessments": assessment_by_step,
        }

    def bug_list_by_id(self):
        return {b["id"]: b for b in self.bug_list()}

    def explain_step(self, bug_id, step_index, window=3):
        detail = self.bug_detail(bug_id)
        if detail is None:
            raise ValueError("unknown bug")
        actions = detail["actions"]
        if step_index < 0 or step_index >= len(actions):
            raise ValueError("invalid step")
        lo = max(0, step_index - window)
        hi = min(len(actions), step_index + window + 1)
        signals = detected_signals(actions, step_index, lo, hi)
        prompt = build_explanation_prompt(detail, step_index, lo, hi, signals)
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 220,
            },
        }
        req = urllib.request.Request(
            self.ollama_url + "/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                data = json.loads(res.read().decode())
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"ollama request failed at {self.ollama_url}; start Ollama with "
                f"`ollama serve` and ensure model `{self.ollama_model}` is installed"
            ) from e
        return {
            "bug_id": bug_id,
            "step_index": step_index,
            "model": self.ollama_model,
            "detected_signals": signals,
            "explanation": data.get("response", "").strip(),
        }


def safe_annotation(raw):
    bug_id = str(raw.get("bug_id") or "")
    if not re.match(r"^[A-Za-z]+-\d+$", bug_id):
        raise ValueError("invalid bug_id")
    start = int(raw.get("start_step"))
    end = int(raw.get("end_step"))
    if start < 0 or end < start:
        raise ValueError("invalid step range")
    status = str(raw.get("status") or "interesting")
    label = str(raw.get("label") or "uncategorized")[:80]
    note = str(raw.get("note") or "")[:2000]
    ann_id = str(raw.get("id") or "")
    if not ann_id:
        ann_id = f"{bug_id}:{start}-{end}:{label}"
    return {
        "id": ann_id[:180],
        "bug_id": bug_id,
        "start_step": start,
        "end_step": end,
        "status": status[:40],
        "label": label,
        "note": note,
    }


def format_step(i, action):
    paths = action.get("paths") or []
    cats = action.get("path_categories") or []
    path_bits = []
    for p, c in list(zip(paths, cats))[:4]:
        path_bits.append(f"{c}:{p}")
    text = action.get("full_text") or action.get("snippet") or ""
    return (
        f"Step {i}: {action.get('kind')}\n"
        f"Tool: {action.get('tool') or 'none'}\n"
        f"Text: {text}\n"
        f"Paths: {', '.join(path_bits) if path_bits else 'none'}"
    )


def detected_signals(actions, selected, lo, hi):
    selected_action = actions[selected]
    nearby = actions[lo:hi]
    signals = []
    if selected_action.get("kind") == "BINARY_INSPECTION":
        signals.append("selected step is classified as BINARY_INSPECTION")
    if selected_action.get("kind") == "SEARCH_EXTERNAL":
        signals.append("selected step searches outside the workspace")
    if any(c == "cache" for a in nearby for c in a.get("path_categories", [])):
        signals.append("nearby steps reference a dependency cache path")
    if any(c == "external" for a in nearby for c in a.get("path_categories", [])):
        signals.append("nearby steps reference paths outside the workspace")
    if any(ROOT_FIND_PAT.search(a.get("full_text") or a.get("snippet", "")) for a in nearby):
        signals.append("nearby steps use find rooted at /")
    binary_tokens = {"javap", "unzip", "jar", "cfr", "procyon", "fernflower", "strings"}
    toks = sorted({t for a in nearby for t in a.get("tokens", []) if t in binary_tokens})
    if toks:
        signals.append("nearby binary/decompilation tokens: " + ", ".join(toks))
    return signals


def build_explanation_prompt(detail, selected, lo, hi, signals):
    bug = detail.get("bug") or {}
    result = detail.get("result") or {}
    categories = ", ".join(bug.get("categories") or [])
    actions = detail.get("actions") or []
    previous = "\n\n".join(format_step(i, actions[i]) for i in range(lo, selected))
    following = "\n\n".join(format_step(i, actions[i]) for i in range(selected + 1, hi))
    selected_step = format_step(selected, actions[selected])
    template = STEP_EXPLANATION_PROMPT.read_text(errors="replace")
    return template.format(
        bug_id=bug.get("id") or "",
        verdict=bug.get("verdict") or "",
        excluded=bug.get("excluded") or "",
        categories=categories,
        result_note=result.get("note") or "",
        detected_signals="\n".join("- " + s for s in signals) if signals else "none",
        previous_steps=previous or "none",
        selected_step=selected_step,
        following_steps=following or "none",
    )


def make_handler(store):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, data, status=200):
            payload = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def read_body(self):
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0:
                return {}
            return json.loads(self.rfile.read(n).decode())

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/api/bugs":
                self.send_json({
                    "bugs": store.bug_list(),
                    "campaign": str(store.campaign),
                    "analysis_done": store.analysis_done,
                    "assessment_results": str(store.results_dir),
                })
                return
            if path == "/api/assistant-text/layers":
                self.send_json({
                    "layers": store.assistant_text_layers,
                    "default": store.default_assistant_text_layer(),
                })
                return
            if path == "/api/assistant-text/results":
                q = parse_qs(parsed.query)
                key = q.get("key", [""])[0]
                self.send_json({
                    "key": key,
                    "rows": store.assistant_text_rows_for(key),
                })
                return
            if path == "/api/annotations":
                self.send_json({"annotations": store.annotations()})
                return
            if path == "/api/ollama/models":
                try:
                    models = store.ollama_models()
                except Exception as e:
                    self.send_json({
                        "error": str(e),
                        "models": [store.ollama_model] if store.ollama_model else [],
                        "selected": store.ollama_model,
                    }, 503)
                    return
                self.send_json({"models": models, "selected": store.ollama_model})
                return
            if path.startswith("/api/bug/"):
                bug_id = path.rsplit("/", 1)[-1]
                q = parse_qs(parsed.query)
                assessment_key = q.get("assistant_text", [""])[0]
                detail = store.bug_detail(bug_id, assessment_key)
                if detail is None:
                    self.send_json({"error": "unknown bug"}, 404)
                else:
                    self.send_json(detail)
                return
            rel = "index.html" if path == "/" else path.lstrip("/")
            target = (UI_DIR / rel).resolve()
            if not str(target).startswith(str(UI_DIR.resolve())) or not target.is_file():
                self.send_json({"error": "not found"}, 404)
                return
            data = target.read_bytes()
            ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/reload":
                store.reload()
                self.send_json({
                    "ok": True,
                    "analysis_done": store.analysis_done,
                    "assessment_results": str(store.results_dir),
                    "num_bugs": len(store.actions),
                })
                return
            if parsed.path == "/api/annotations":
                raw = self.read_body()
                ann = safe_annotation(raw)
                anns = [a for a in store.annotations() if a.get("id") != ann["id"]]
                anns.append(ann)
                store.save_annotations(anns)
                self.send_json({"ok": True, "annotation": ann})
                return
            if parsed.path == "/api/ollama/model":
                raw = self.read_body()
                try:
                    selected = store.set_ollama_model(raw.get("model"))
                except Exception as e:
                    self.send_json({"error": str(e)}, 400)
                    return
                self.send_json({"ok": True, "selected": selected})
                return
            if parsed.path == "/api/explain":
                raw = self.read_body()
                try:
                    data = store.explain_step(
                        str(raw.get("bug_id") or ""),
                        int(raw.get("step_index")),
                        int(raw.get("window") or 3),
                    )
                except Exception as e:
                    self.send_json({"error": str(e)}, 500)
                    return
                self.send_json(data)
                return
            self.send_json({"error": "not found"}, 404)

        def do_DELETE(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/annotations":
                q = parse_qs(parsed.query)
                ann_id = q.get("id", [""])[0]
                anns = [a for a in store.annotations() if a.get("id") != ann_id]
                store.save_annotations(anns)
                self.send_json({"ok": True})
                return
            self.send_json({"error": "not found"}, 404)

        def log_message(self, fmt, *args):
            sys.stderr.write(fmt % args + "\n")

    return Handler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("campaign")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8768)
    ap.add_argument("--results-dir", help="assessment results directory; default: assessment/results/<campaign-path>")
    ap.add_argument("--ollama-url", default=os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434"))
    ap.add_argument("--ollama-model", default=os.environ.get("OLLAMA_MODEL", "gemma3:4b"))
    args = ap.parse_args()

    store = Store(args.campaign, args.ollama_url, args.ollama_model, args.results_dir)
    if not store.actions:
        raise SystemExit(
            f"no trajectory_actions.jsonl found under {store.results_dir} and no session.jsonl(.gz) "
            f"files found under {store.campaign / 'data'}"
        )
    server = ThreadingHTTPServer((args.host, args.port), make_handler(store))
    print(f"trajectory UI: http://{args.host}:{args.port}")
    print(f"analysis done: {store.analysis_done}")
    print(f"assessment results: {store.results_dir}")
    print(f"campaign results: {store.campaign_results_dir}")
    print(f"annotations: {store.annotations_path}")
    print(f"ollama: {store.ollama_url} model={store.ollama_model}")
    server.serve_forever()


if __name__ == "__main__":
    main()
