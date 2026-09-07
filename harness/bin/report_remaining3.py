#!/usr/bin/env python3
"""Report the follow-up experiment on the three unsolved bugs.

Reads every runs/remaining3/<cond>-r<k>/ directory and prints the condition x bug
pass@k table, cost per cell, and how each produced patch compares with the
developer fix.

Usage: report_remaining3.py [baseDir]
"""
import json, pathlib, re, sys, collections

BUGS = ["JacksonCore-10", "Math-66", "Jsoup-67"]
CONDS = ["T", "M", "TM", "TM+"]

def norm(lines):
    out = []
    for l in lines:
        s = re.sub(r"//.*$", "", l[1:]).strip()
        s = re.sub(r"\s+", " ", s)
        if s:
            out.append(s)
    return sorted(out)

def sides(text):
    add = [l for l in text.splitlines() if l.startswith("+") and not l.startswith("+++")]
    rem = [l for l in text.splitlines() if l.startswith("-") and not l.startswith("---")]
    files = sorted({l.split(" b/", 1)[1] for l in text.splitlines()
                    if l.startswith("diff --git ") and " b/" in l})
    return norm(add), norm(rem), files

def similarity(bugdir):
    """The developer fix is the inverse of <id>.src.patch, which turns the fixed
    version into the buggy one."""
    p, d = bugdir / "patch.diff", bugdir / "dev.patch"
    if not (p.exists() and d.exists() and p.stat().st_size):
        return "n/a"
    a_add, a_rem, a_files = sides(p.read_text(errors="replace"))
    d_add, d_rem, d_files = sides(d.read_text(errors="replace"))
    if a_add == d_rem and a_rem == d_add:
        return "identical"
    if a_files == d_files:
        return "same-files"
    return "different"

def main():
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                        else "runs/remaining3")
    if not base.is_dir():
        print(f"no such directory: {base}"); return
    # cond -> rep -> bug -> record
    data = collections.defaultdict(lambda: collections.defaultdict(dict))
    meta = {}
    for d in sorted(base.iterdir()):
        if not (d / "condition.json").is_file():
            continue
        c = json.loads((d / "condition.json").read_text())
        cond, rep = c["condition"], c["rep"]
        meta[cond] = c
        rj = d / "results.jsonl"
        if not rj.is_file():
            continue
        for line in rj.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            r["similarity"] = similarity(d / r["id"])
            data[cond][rep][r["id"]] = r        # last attempt wins

    conds = [c for c in CONDS if c in data] + [c for c in data if c not in CONDS]
    reps = sorted({r for c in data for r in data[c]})
    k = len(reps)

    print("# The three remaining Defects4J bugs\n")
    print("| condition | model | cap | " + " | ".join(BUGS) + " |")
    print("|" + "---|" * (len(BUGS) + 3))
    for c in conds:
        m = meta.get(c, {})
        cells = []
        for b in BUGS:
            got = [data[c][r].get(b) for r in reps]
            got = [g for g in got if g]
            if not got:
                cells.append("—"); continue
            n = sum(1 for g in got if g["verdict"] == "PLAUSIBLE")
            mark = "**%d/%d**" % (n, len(got)) if n else "0/%d" % len(got)
            verds = ",".join(sorted({g["verdict"] for g in got if g["verdict"] != "PLAUSIBLE"}))
            cells.append(mark + (f" ({verds})" if verds else ""))
        cap = m.get("agent_timeout_s")
        cap = f"{cap/3600:g} h" if cap and cap >= 3600 else (f"{cap//60} min" if cap else "?")
        print(f"| `{c}` | {m.get('model','?')} | {cap} | " + " | ".join(cells) + " |")
    print(f"\npass@{k} per cell; a non-plausible verdict is named in brackets.\n")

    print("## Cost and effort per cell\n")
    print("| condition | bug | rep | verdict | turns | agent min | cost | patch +/- | vs dev fix |")
    print("|---|---|---|---|---|---|---|---|---|")
    tot = 0.0
    for c in conds:
        for b in BUGS:
            for r in reps:
                g = data[c][r].get(b)
                if not g:
                    continue
                cost = g.get("total_cost_usd") or 0
                tot += cost
                est = "~" if g.get("telemetry_source") == "stream_estimate" else ""
                print(f"| `{c}` | {b} | {r} | {g['verdict']} | {g.get('num_turns')} | "
                      f"{(g.get('agent_s') or 0)/60:.0f} | {est}${cost:.2f} | "
                      f"+{g.get('patch_added_lines')}/-{g.get('patch_removed_lines')} | "
                      f"{g['similarity']} |")
    print(f"\nTotal for this experiment: **${tot:.2f}** "
          f"(`~` marks a cost reconstructed from the stream after a wall-clock kill).")

    print("\n## Per-bug summary\n")
    for b in BUGS:
        got = [data[c][r][b] for c in conds for r in reps if b in data[c][r]]
        n = sum(1 for g in got if g["verdict"] == "PLAUSIBLE")
        print(f"- **{b}**: solved in {n} of {len(got)} runs"
              + (" — " + ", ".join(sorted({g["verdict"] for g in got})) if got else ""))

if __name__ == "__main__":
    main()
