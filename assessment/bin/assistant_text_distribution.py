#!/usr/bin/env python3
"""Report ASSISTANT_TEXT presence and candidate-selection distribution.

This is a diagnostic script for understanding how many assistant text steps are
present in traces, and how many are selected by the semantic-assessment
candidate prefilter.

Usage:
  python3 assessment/bin/assistant_text_distribution.py campaign/no-fault-localization
"""
import argparse
import csv
import json
import pathlib
import statistics
from collections import Counter, defaultdict

from analyze_assistant_text import (
    candidate_reason,
    deterministic_signals,
    load_actions,
    load_features,
    load_results,
)
from analyze_trajectories import default_output_dir, find_data_root


def bug_sort_key(bug_id):
    project, num = bug_id.rsplit("-", 1)
    return project, int(num)


def number(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def stats(values):
    values = list(values)
    if not values:
        return {"min": 0, "median": 0, "mean": 0, "max": 0}
    return {
        "min": min(values),
        "median": statistics.median(values),
        "mean": statistics.mean(values),
        "max": max(values),
    }


def collect_rows(actions_by_id, features, results, window):
    rows = []
    reason_counts = Counter()
    per_project = defaultdict(lambda: {
        "bugs": 0,
        "assistant_text_steps": 0,
        "candidate_text_steps": 0,
        "zero_assistant_text_bugs": 0,
        "zero_candidate_text_bugs": 0,
    })

    for bug_id in sorted(actions_by_id, key=bug_sort_key):
        actions = actions_by_id[bug_id].get("actions") or []
        assistant_steps = []
        candidate_steps = []
        candidate_reasons = Counter()
        for idx, action in enumerate(actions):
            if action.get("kind") != "ASSISTANT_TEXT":
                continue
            assistant_steps.append(idx)
            lo = max(0, idx - window)
            hi = min(len(actions), idx + window + 1)
            text = action.get("full_text") or action.get("snippet") or ""
            signals = deterministic_signals(actions, idx, lo, hi)
            reasons = candidate_reason(text, signals)
            if reasons:
                candidate_steps.append(idx)
                candidate_reasons.update(reasons)
                reason_counts.update(reasons)

        project = bug_id.rsplit("-", 1)[0]
        feat = features.get(bug_id) or {}
        result = results.get(bug_id) or {}
        row = {
            "id": bug_id,
            "project": project,
            "verdict": result.get("verdict") or feat.get("verdict") or "",
            "excluded": result.get("excluded") or feat.get("excluded") or "",
            "visible_steps": len(actions),
            "agent_actions": number(feat.get("num_actions")),
            "assistant_text_steps": len(assistant_steps),
            "candidate_text_steps": len(candidate_steps),
            "observation_steps": sum(1 for a in actions if a.get("kind") == "OBSERVATION"),
            "first_assistant_text_step": "" if not assistant_steps else assistant_steps[0],
            "candidate_step_indices": " ".join(str(i) for i in candidate_steps),
            "candidate_reasons": " ".join(sorted(candidate_reasons)),
        }
        rows.append(row)

        p = per_project[project]
        p["bugs"] += 1
        p["assistant_text_steps"] += row["assistant_text_steps"]
        p["candidate_text_steps"] += row["candidate_text_steps"]
        p["zero_assistant_text_bugs"] += int(row["assistant_text_steps"] == 0)
        p["zero_candidate_text_bugs"] += int(row["candidate_text_steps"] == 0)

    return rows, reason_counts, per_project


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "id", "project", "verdict", "excluded", "visible_steps", "agent_actions",
        "assistant_text_steps", "candidate_text_steps", "observation_steps",
        "first_assistant_text_step", "candidate_step_indices", "candidate_reasons",
    ]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def md(text):
    return str(text).replace("|", "\\|").replace("\n", "<br>")


def write_md(path, rows, reason_counts, per_project, window):
    n = len(rows)
    assistant_counts = [r["assistant_text_steps"] for r in rows]
    candidate_counts = [r["candidate_text_steps"] for r in rows]
    observation_counts = [r["observation_steps"] for r in rows]
    zero_assistant = [r for r in rows if r["assistant_text_steps"] == 0]
    zero_candidate = [r for r in rows if r["candidate_text_steps"] == 0]

    astats = stats(assistant_counts)
    cstats = stats(candidate_counts)
    ostats = stats(observation_counts)

    with open(path, "w") as f:
        f.write("# Assistant Text Distribution\n\n")
        f.write(f"Context window for candidate signals: {window}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- bugs: {n}\n")
        f.write(f"- ASSISTANT_TEXT steps: {sum(assistant_counts)}\n")
        f.write(f"- candidate ASSISTANT_TEXT steps: {sum(candidate_counts)}\n")
        f.write(f"- bugs with zero ASSISTANT_TEXT: {len(zero_assistant)}\n")
        f.write(f"- bugs with zero candidate ASSISTANT_TEXT: {len(zero_candidate)}\n")
        f.write(f"- OBSERVATION steps: {sum(observation_counts)}\n\n")

        f.write("## Distribution\n\n")
        f.write("| metric | min | median | mean | max |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        for name, s in (
            ("ASSISTANT_TEXT per bug", astats),
            ("candidate ASSISTANT_TEXT per bug", cstats),
            ("OBSERVATION per bug", ostats),
        ):
            f.write(f"| {name} | {s['min']} | {s['median']:.1f} | {s['mean']:.2f} | {s['max']} |\n")

        f.write("\n## By Project\n\n")
        f.write("| project | bugs | ASSISTANT_TEXT | candidates | zero text bugs | zero candidate bugs |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for project in sorted(per_project):
            p = per_project[project]
            f.write(
                f"| {project} | {p['bugs']} | {p['assistant_text_steps']} | "
                f"{p['candidate_text_steps']} | {p['zero_assistant_text_bugs']} | "
                f"{p['zero_candidate_text_bugs']} |\n"
            )

        f.write("\n## Candidate Reasons\n\n")
        f.write("| reason | count |\n")
        f.write("|---|---:|\n")
        for reason, count in reason_counts.most_common():
            f.write(f"| `{md(reason)}` | {count} |\n")

        f.write("\n## Bugs With Zero ASSISTANT_TEXT\n\n")
        if zero_assistant:
            f.write(", ".join(r["id"] for r in zero_assistant) + "\n")
        else:
            f.write("None.\n")

        f.write("\n## Bugs With Zero Candidate ASSISTANT_TEXT\n\n")
        if zero_candidate:
            f.write(", ".join(r["id"] for r in zero_candidate) + "\n")
        else:
            f.write("None.\n")

        f.write("\n## Highest ASSISTANT_TEXT Counts\n\n")
        f.write("| bug | ASSISTANT_TEXT | candidates | visible steps | verdict | excluded | reasons |\n")
        f.write("|---|---:|---:|---:|---|---|---|\n")
        for r in sorted(rows, key=lambda x: (-x["assistant_text_steps"], x["id"]))[:50]:
            f.write(
                f"| {r['id']} | {r['assistant_text_steps']} | {r['candidate_text_steps']} | "
                f"{r['visible_steps']} | {md(r['verdict'])} | {md(r['excluded'])} | "
                f"{md(r['candidate_reasons'])} |\n"
            )

        f.write("\n## Highest Candidate Counts\n\n")
        f.write("| bug | candidates | ASSISTANT_TEXT | visible steps | verdict | excluded | reasons |\n")
        f.write("|---|---:|---:|---:|---|---|---|\n")
        for r in sorted(rows, key=lambda x: (-x["candidate_text_steps"], x["id"]))[:50]:
            f.write(
                f"| {r['id']} | {r['candidate_text_steps']} | {r['assistant_text_steps']} | "
                f"{r['visible_steps']} | {md(r['verdict'])} | {md(r['excluded'])} | "
                f"{md(r['candidate_reasons'])} |\n"
            )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("campaign", help="campaign directory or data directory")
    ap.add_argument("--out", help="base assessment output directory; default: assessment/results/<campaign-path>")
    ap.add_argument("--window", type=int, default=3)
    args = ap.parse_args()

    campaign = pathlib.Path(args.campaign).resolve()
    data = find_data_root(campaign)
    campaign = data.parent if data.name == "data" else campaign
    outdir = pathlib.Path(args.out).resolve() if args.out else default_output_dir(campaign)

    results = load_results(campaign)
    actions = load_actions(campaign, outdir)
    features = load_features(campaign, outdir, actions, results)
    rows, reason_counts, per_project = collect_rows(actions, features, results, args.window)
    if not rows:
        raise SystemExit("no traces found")

    csv_path = outdir / "assistant_text_distribution.csv"
    md_path = outdir / "assistant_text_distribution.md"
    write_csv(csv_path, rows)
    write_md(md_path, rows, reason_counts, per_project, args.window)

    total_text = sum(r["assistant_text_steps"] for r in rows)
    total_candidates = sum(r["candidate_text_steps"] for r in rows)
    zero_text = sum(1 for r in rows if r["assistant_text_steps"] == 0)
    zero_candidates = sum(1 for r in rows if r["candidate_text_steps"] == 0)
    print(f"bugs: {len(rows)}")
    print(f"ASSISTANT_TEXT steps: {total_text}")
    print(f"candidate ASSISTANT_TEXT steps: {total_candidates}")
    print(f"bugs with zero ASSISTANT_TEXT: {zero_text}")
    print(f"bugs with zero candidate ASSISTANT_TEXT: {zero_candidates}")
    print(f"wrote {csv_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
