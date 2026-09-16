#!/usr/bin/env python3
"""Stage 3: could the agent have ASSEMBLED the phrase from what it could read?

Stage 2 asks whether a phrase appears verbatim in the buggy checkout. That is
necessary but not sufficient evidence of recall, because a test may assert a
*substring*:

    assertTrue(e.getMessage().contains("Truncated TAR"))

The full phrase "Truncated TAR archive" is then absent, yet the agent had most
of it handed over. So for every phrase stage 2 confirmed, find the longest
contiguous word sequence of that phrase which DOES appear somewhere in the buggy
tree, and report the fraction. A phrase whose longest readable fragment is most
of it was reconstructed; one whose longest readable fragment is a word or two
was recalled.

Usage: audit_memorisation_stage3.py <stage2-output.txt> [--workdir DIR]
"""
import re, subprocess, sys, pathlib, json

TEXTY = {".java", ".txt", ".xml", ".properties", ".html", ".htm", ".md", ".json",
         ".csv", ".js", ".css", ".sql", ".yml", ".yaml", ".cfg", ".ini", ".sh", ""}

def slurp(tree):
    """Every readable text file under `tree`, concatenated.

    One pass, held in memory, because the alternative -- a `grep -r` per
    candidate n-gram -- is O(words^2) subprocesses over trees the size of
    Closure's, and takes hours."""
    buf = []
    for f in pathlib.Path(tree).rglob("*"):
        if not f.is_file() or f.suffix.lower() not in TEXTY:
            continue
        try:
            if f.stat().st_size > 8_000_000:
                continue
            buf.append(f.read_text(errors="replace"))
        except OSError:
            continue
    return "\n".join(buf)

def longest_readable(phrase, blob):
    """Longest contiguous word n-gram of `phrase` present in `blob`."""
    words = phrase.split()
    for n in range(len(words), 0, -1):
        for i in range(len(words) - n + 1):
            frag = " ".join(words[i:i+n])
            if len(frag) >= 4 and frag in blob:
                return frag, n / len(words)
    return "", 0.0

def main():
    if "--reclassify" in sys.argv:
        rows = [(r["bug"], r["phrase"], r["longest_readable"], r["fraction"])
                for r in json.load(open(sys.argv[sys.argv.index("--reclassify")+1]))]
        print("# Stage 3 — was the phrase assemblable from readable text?\n")
        print(f"phrases: {len(rows)}, bugs: {len({r[0] for r in rows})}\n")
        summarise(rows)
        return
    src = pathlib.Path(sys.argv[1]).read_text(errors="replace")
    workdir = sys.argv[sys.argv.index("--workdir")+1] if "--workdir" in sys.argv else "/tmp"
    stage2 = src[src.index("## Stage 2"):] if "## Stage 2" in src else src

    # bug -> confirmed phrases (deduplicated across campaigns)
    confirmed, cur = {}, None
    for line in stage2.splitlines():
        m = re.match(r"- \*\*([A-Za-z]+-\d+)\*\*.*confirmed:", line)
        if m:
            cur = m.group(1); confirmed.setdefault(cur, set()); continue
        m = re.match(r"\s+- `(.+)`\s*$", line)
        if m and cur:
            confirmed[cur].add(m.group(1))
        elif line.startswith("- "):
            cur = None

    print("# Stage 3 — was the phrase assemblable from readable text?\n")
    print(f"bugs with a stage-2 confirmed phrase: {len(confirmed)}\n")
    print("| bug | phrase | longest readable fragment | fraction |")
    print("|---|---|---|---|")
    rows = []
    for bug in sorted(confirmed):
        project, num = bug.rsplit("-", 1)
        w = pathlib.Path(workdir) / f"{project}-{num}.s3"
        subprocess.run(["rm", "-rf", str(w)], check=False)
        r = subprocess.run(["defects4j", "checkout", "-p", project, "-v", f"{num}b", "-w", str(w)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"| {bug} | (checkout failed) | | |"); continue
        blob = slurp(w)
        for ph in sorted(confirmed[bug]):
            frag, frac = longest_readable(ph, blob)
            rows.append((bug, ph, frag, frac))
            disp = ph if len(ph) <= 58 else ph[:55] + "..."
            fdisp = frag if len(frag) <= 34 else frag[:31] + "..."
            print(f"| {bug} | `{disp}` | `{fdisp or '(nothing)'}` | {frac:.0%} |")
        subprocess.run(["rm", "-rf", str(w)], check=False)

    summarise(rows)

def summarise(rows):
    """Rank by how much readable text the agent actually had.

    The FRACTION is the wrong statistic on its own, and using it alone produced a
    false negative on the known positive control: `and bit more` scores 67%
    because the two-word English fragment `bit more` turns up somewhere in a
    large tree by chance. What matters is the ABSOLUTE size of the longest
    readable fragment -- one or two short words is coincidence, five words and
    twenty-plus characters is the agent having read most of the phrase.

    No threshold here is principled, so the tiers are reported rather than
    collapsed into a verdict."""
    def w(s): return len(s.split())
    strong   = [r for r in rows if w(r[1]) >= 6 and w(r[2]) <= 3]
    moderate = [r for r in rows if r not in strong and w(r[1]) >= 6 and w(r[2]) <= 5]
    short    = [r for r in rows if w(r[1]) < 6]
    weak     = [r for r in rows if r not in strong and r not in moderate and r not in short]

    print(f"\n## Ranked by how much of the phrase was actually readable\n")
    print(f"- **strong** — phrase of 6+ words, at most 3 readable: "
          f"**{len(strong)} phrases / {len({r[0] for r in strong})} bugs**")
    print(f"- moderate — phrase of 6+ words, 4-5 readable: "
          f"{len(moderate)} phrases / {len({r[0] for r in moderate})} bugs")
    print(f"- short phrases (under 6 words), where this metric is unreliable in "
          f"both directions: {len(short)}")
    print(f"- weak — most of the phrase was readable: {len(weak)}\n")
    for label, group in (("Strong", strong), ("Moderate", moderate)):
        if not group: continue
        print(f"### {label}\n")
        for bug, ph, frag, frac in sorted(group, key=lambda r: len(r[2])):
            print(f"- **{bug}** — `{ph}`")
            print(f"  longest readable fragment: `{frag or 'nothing'}` "
                  f"({len(frag.split())} words, {len(frag)} chars, {frac:.0%})")
    if short:
        print(f"\n### Short phrases — judge these on context, not on this metric\n")
        for bug, ph, frag, frac in sorted(short, key=lambda r: len(r[2])):
            print(f"- {bug} — `{ph}` (readable: `{frag}`, {len(frag)} chars)")
    pathlib.Path("results/memorisation-stage3.json").write_text(json.dumps(
        [{"bug": b, "phrase": p, "longest_readable": f, "fraction": fr} for b, p, f, fr in rows],
        indent=2) + "\n")

if __name__ == "__main__":
    main()
