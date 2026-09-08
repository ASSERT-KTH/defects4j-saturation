#!/usr/bin/env python3
"""Summarise a run: verdicts, cost, timing, similarity to the developer fix.

Usage: report.py <runDir> [--csv out.csv]
"""
import csv, json, pathlib, statistics, sys, re

VERDICTS = ["PLAUSIBLE", "REGRESSION", "TEST_FAIL", "COMPILE_FAIL", "NO_PATCH",
            "TAMPERED", "TIMEOUT", "USAGE_LIMIT", "BASELINE_FAIL", "CHECKOUT_FAIL", "ERROR"]

def norm(lines):
    """Normalised multiset of code lines: whitespace- and comment-insensitive."""
    out = []
    for l in lines:
        s = re.sub(r"//.*$", "", l[1:]).strip()
        s = re.sub(r"\s+", " ", s)
        if s:
            out.append(s)
    return sorted(out)

def sides(patch_text):
    add = [l for l in patch_text.splitlines() if l.startswith("+") and not l.startswith("+++")]
    rem = [l for l in patch_text.splitlines() if l.startswith("-") and not l.startswith("---")]
    files = sorted({l.split(" b/", 1)[1] for l in patch_text.splitlines()
                    if l.startswith("diff --git ") and " b/" in l})
    return norm(add), norm(rem), files

def similarity(bugdir):
    """Compare the agent patch with the developer fix.

    Defects4J's <id>.src.patch turns the FIXED version into the BUGGY one, so the
    developer fix is its inverse."""
    p, d = bugdir / "patch.diff", bugdir / "dev.patch"
    if not (p.exists() and d.exists()):
        return "n/a"
    a_add, a_rem, a_files = sides(p.read_text(errors="replace"))
    d_add, d_rem, d_files = sides(d.read_text(errors="replace"))
    if a_add == d_rem and a_rem == d_add:
        return "identical"
    if a_files == d_files:
        return "same-files"
    return "different"

def main():
    rundir = pathlib.Path(sys.argv[1])
    recs = {}
    with open(rundir / "results.jsonl") as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                recs[r["id"]] = r            # last attempt wins
    if not recs:
        print("no results yet"); return

    # A run whose ground truth leaked is not a result. Records carry
    # "excluded" with a reason (see audit_own_artefact.py); drop them from the
    # rates and say so, rather than quietly counting them.
    excluded = {i: r for i, r in recs.items() if r.get("excluded")}
    for i in excluded:
        del recs[i]

    for r in recs.values():
        r["similarity"] = similarity(rundir / r["id"]) if r["verdict"] == "PLAUSIBLE" else ""

    projects = sorted({r["project"] for r in recs.values()})
    print(f"# Defects4J x Claude Code (Sonnet 5) — {rundir}\n")
    print(f"{len(recs)} bugs attempted\n")
    if excluded:
        print("Excluded from every figure below:\n")
        for i, r in sorted(excluded.items()):
            print(f"- **{i}** ({r['verdict']}) — {r.get('excluded')}: "
                  f"{r.get('excluded_reason','')}")
        print()

    hdr = ["project", "n", "plausible", "rate", "identical", "test_fail", "compile_fail",
           "no_patch", "other", "cost_usd", "med_turns", "med_min"]
    print("| " + " | ".join(hdr) + " |")
    print("|" + "|".join("---" for _ in hdr) + "|")

    def row(name, rs):
        n = len(rs)
        pl = sum(1 for r in rs if r["verdict"] == "PLAUSIBLE")
        ident = sum(1 for r in rs if r.get("similarity") == "identical")
        def c(v): return sum(1 for r in rs if r["verdict"] == v)
        other = n - pl - c("TEST_FAIL") - c("COMPILE_FAIL") - c("NO_PATCH")
        cost = sum(r.get("total_cost_usd") or 0 for r in rs)
        turns = [r["num_turns"] for r in rs if r.get("num_turns")]
        mins = [r["wallclock_s"] / 60 for r in rs if r.get("wallclock_s")]
        print(f"| {name} | {n} | {pl} | {100*pl/n:.1f}% | {ident} | {c('TEST_FAIL')} | "
              f"{c('COMPILE_FAIL')} | {c('NO_PATCH')} | {other} | {cost:.2f} | "
              f"{statistics.median(turns) if turns else 0:.0f} | "
              f"{statistics.median(mins) if mins else 0:.1f} |")

    for p in projects:
        row(p, [r for r in recs.values() if r["project"] == p])
    row("**ALL**", list(recs.values()))

    print("\n## Verdict breakdown\n")
    for v in VERDICTS:
        n = sum(1 for r in recs.values() if r["verdict"] == v)
        if n:
            print(f"- {v}: {n}")

    cut = [r for r in recs.values() if r.get("agent_rc") == 124 or r.get("num_turns") is None]
    if cut:
        print(f"\nAgent hit the wall-clock cap on {len(cut)} bug(s): "
              + ", ".join(sorted(r["id"] for r in cut)))

    plaus = [r for r in recs.values() if r["verdict"] == "PLAUSIBLE"]
    if plaus:
        print("\n## Patch similarity to the developer fix (plausible patches)\n")
        for k in ("identical", "same-files", "different"):
            print(f"- {k}: {sum(1 for r in plaus if r['similarity'] == k)}")

    tot = sum(r.get("total_cost_usd") or 0 for r in recs.values())
    ti = sum(r.get("input_tokens") or 0 for r in recs.values())
    to = sum(r.get("output_tokens") or 0 for r in recs.values())
    tc = sum(r.get("cache_read_input_tokens") or 0 for r in recs.values())
    print(f"\nTotal list-price cost: ${tot:.2f}   "
          f"tokens in/out/cache-read: {ti:,}/{to:,}/{tc:,}")

    csvpath = rundir / "results.csv"
    cols = ["id", "project", "bug", "verdict", "note", "similarity", "num_turns",
            "total_cost_usd", "wallclock_s", "agent_s", "patch_added_lines",
            "patch_removed_lines", "input_tokens", "output_tokens",
            "cache_read_input_tokens"]
    with open(csvpath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in sorted(recs.values(), key=lambda r: (r["project"], r["bug"])):
            w.writerow(r)
    print(f"\nCSV: {csvpath}")

if __name__ == "__main__":
    main()
