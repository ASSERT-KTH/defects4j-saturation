#!/usr/bin/env python3
"""Compare two campaigns bug by bug.

The campaigns differ only in the prompt, so a per-bug transition table isolates
the effect of that difference. Built for perfect-FL vs no-FL, where the question
is how much of the headline rate came from being handed the fault location.

Usage: compare_campaigns.py <runDirA> <runDirB> [--label-a X --label-b Y]
"""
import json, pathlib, sys, collections, statistics

def load(run):
    recs = {}
    f = pathlib.Path(run) / "results.jsonl"
    if not f.is_file():
        sys.exit(f"no results.jsonl in {run}")
    for line in f.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            recs[r["id"]] = r          # last attempt wins
    return recs

def named_classes(proj, bug):
    p = pathlib.Path("d4j/framework/projects")/proj/"modified_classes"/f"{bug}.src"
    return {x.split(".")[-1] for x in p.read_text().split()} if p.is_file() else set()

def main():
    a_dir, b_dir = sys.argv[1], sys.argv[2]
    la = sys.argv[sys.argv.index("--label-a")+1] if "--label-a" in sys.argv else a_dir
    lb = sys.argv[sys.argv.index("--label-b")+1] if "--label-b" in sys.argv else b_dir
    A, B = load(a_dir), load(b_dir)
    common = sorted(set(A) & set(B))

    def ok(r): return r["verdict"] == "PLAUSIBLE"
    print(f"# {la} vs {lb}\n")
    print(f"{len(A)} vs {len(B)} bugs attempted; {len(common)} in both\n")

    for lbl, R in ((la, A), (lb, B)):
        n = len(R); pl = sum(1 for r in R.values() if ok(r))
        cost = sum(r.get("total_cost_usd") or 0 for r in R.values())
        print(f"- **{lbl}**: {pl}/{n} plausible ({100*pl/n:.1f}%), ${cost:.2f}")
    if not common:
        return

    # transition table
    t = collections.Counter((ok(A[i]), ok(B[i])) for i in common)
    print(f"\n## Per-bug transitions ({len(common)} bugs in both)\n")
    print(f"| | {lb} solved | {lb} failed |")
    print("|---|---|---|")
    print(f"| **{la} solved** | {t[(True,True)]} | {t[(True,False)]} |")
    print(f"| **{la} failed** | {t[(False,True)]} | {t[(False,False)]} |")
    lost = [i for i in common if ok(A[i]) and not ok(B[i])]
    won  = [i for i in common if not ok(A[i]) and ok(B[i])]
    print(f"\nLost by {lb}: **{len(lost)}**   gained: **{len(won)}**   "
          f"net: **{len(won)-len(lost):+d}**")

    # did the failures become localization failures?
    print(f"\n## How {lb} failed\n")
    vc = collections.Counter(B[i]["verdict"] for i in common if not ok(B[i]))
    for v, n in vc.most_common():
        print(f"- `{v}`: {n}")
    wrongfile = []
    for i in common:
        r = B[i]
        if ok(r) or not r["patch_files"]:
            continue
        named = named_classes(r["project"], r["bug"])
        touched = {f.split("/")[-1].replace(".java","") for f in r["patch_files"]}
        if named and not (touched & named):
            wrongfile.append(i)
    nopatch = [i for i in common if B[i]["verdict"] == "NO_PATCH"]
    print(f"\nFailed having edited **no file the developer touched** (a localization miss, "
          f"not a repair miss): **{len(wrongfile)}**")
    print(f"Failed having produced no patch at all: **{len(nopatch)}**")
    if wrongfile[:15]:
        print("\n  e.g. " + ", ".join(wrongfile[:15]))

    # Paired cost, on the same bugs. A naive per-bug extrapolation conflates the
    # project mix -- projects differ in cost by an order of magnitude -- so the
    # only mix-independent comparison is bug by bug.
    pair = [i for i in common
            if B[i]["verdict"] != "USAGE_LIMIT"
            and (A[i].get("total_cost_usd") or 0) and (B[i].get("total_cost_usd") or 0)]
    if pair:
        ca = sum(A[i]["total_cost_usd"] for i in pair)
        cb = sum(B[i]["total_cost_usd"] for i in pair)
        print(f"\n## Paired cost on the same {len(pair)} bugs (mix-independent)\n")
        print(f"| | {la} | {lb} | delta |")
        print("|---|---|---|---|")
        rows = [("cost", "total_cost_usd", "${:,.2f}"), ("turns", "num_turns", "{:,.0f}"),
                ("agent seconds", "agent_s", "{:,.0f}"),
                ("cache-read tokens", "cache_read_input_tokens", "{:,.0f}"),
                ("output tokens", "output_tokens", "{:,.0f}")]
        for lab, k, fmt in rows:
            va = sum(A[i].get(k) or 0 for i in pair)
            vb = sum(B[i].get(k) or 0 for i in pair)
            d = f"{100*(vb/va-1):+.1f}%" if va else "-"
            print(f"| {lab} | {fmt.format(va)} | {fmt.format(vb)} | {d} |")
        # The sum ratio is not a safe statistic here: per-bug ratios span roughly
        # 0.5-2.2 and the ten costliest bugs carry ~17% of the total, so the sum
        # swings on which expensive bugs happen to be in scope. Report the paired
        # median and a sign test, which are stable, and say when a difference is
        # indistinguishable from a coin flip.
        print(f"\n### Robust paired statistics\n")
        print("| metric | median ratio | sum ratio | " + lb + " higher on | p5-p95 | reading |")
        print("|---|---|---|---|---|---|")
        for lab, k in (("cost","total_cost_usd"), ("turns","num_turns"),
                       ("agent seconds","agent_s"),
                       ("cache-read tokens","cache_read_input_tokens"),
                       ("output tokens","output_tokens")):
            rr = sorted((B[i].get(k) or 0)/(A[i].get(k) or 1) for i in pair)
            med = rr[len(rr)//2]
            p5, p95 = rr[int(.05*len(rr))], rr[int(.95*len(rr))]
            hi = sum(1 for i in pair if (B[i].get(k) or 0) > (A[i].get(k) or 0))
            frac = hi/len(pair)
            sa = sum(A[i].get(k) or 0 for i in pair); sb = sum(B[i].get(k) or 0 for i in pair)
            sr = (sb/sa) if sa else float("nan")
            verdict = "**real**" if abs(frac-0.5) >= 0.07 else "noise"
            print(f"| {lab} | {med:.3f} | {sr:.3f} | {hi}/{len(pair)} ({100*frac:.0f}%) | "
                  f"{p5:.2f}-{p95:.2f} | {verdict} |")
        top = sorted(pair, key=lambda i: -(A[i].get("total_cost_usd") or 0))[:10]
        tot = sum(A[i].get("total_cost_usd") or 0 for i in pair)
        share = 100*sum(A[i].get("total_cost_usd") or 0 for i in top)/tot if tot else 0
        print(f"\nThe ten costliest bugs carry {share:.0f}% of the paired total, which is why "
              f"the sum ratio is unstable at partial coverage. A sign test within 7 points of "
              f"50% is reported as noise.")
        # mix-adjusted projection onto the complete campaign
        byproj = collections.defaultdict(lambda: [0.0, 0.0])
        for i in pair:
            byproj[A[i]["project"]][0] += A[i]["total_cost_usd"]
            byproj[A[i]["project"]][1] += B[i]["total_cost_usd"]
        a_tot = sum(r.get("total_cost_usd") or 0 for r in A.values())
        proj = 0.0
        for p_ in {r["project"] for r in A.values()}:
            pf = sum(r.get("total_cost_usd") or 0 for r in A.values() if r["project"] == p_)
            x, y = byproj.get(p_, [0, 0])
            proj += pf * ((y/x) if x > 0 else (cb/ca))
        if len(B) < len(A):
            print(f"\nMix-adjusted projection for a complete {lb} campaign: "
                  f"**${proj:,.2f}** against {la}'s ${a_tot:,.2f} ({100*(proj/a_tot-1):+.1f}%). "
                  f"{len(A)-len(B)} bugs still unmeasured.")
        print("\nPer-project cost ratio:\n")
        print("| project | ratio | " + la + " | " + lb + " | n |")
        print("|---|---|---|---|---|")
        for p_, (x, y) in sorted(byproj.items()):
            if x > 0:
                n_ = sum(1 for i in pair if A[i]["project"] == p_)
                print(f"| {p_} | {y/x:.3f} | ${x:,.2f} | ${y:,.2f} | {n_} |")

    # effort deltas on bugs both solved
    both = [i for i in common if ok(A[i]) and ok(B[i])]
    if both:
        def med(R, k): return statistics.median([R[i].get(k) or 0 for i in both])
        print(f"\n## Effort on the {len(both)} bugs both campaigns solved\n")
        print(f"| | {la} | {lb} |")
        print("|---|---|---|")
        for k, lab in (("num_turns","median turns"), ("agent_s","median agent s"),
                       ("cache_read_input_tokens","median cache-read tokens"),
                       ("total_cost_usd","median cost")):
            va, vb = med(A,k), med(B,k)
            print(f"| {lab} | {va:,.2f} | {vb:,.2f} |" if k=="total_cost_usd"
                  else f"| {lab} | {va:,.0f} | {vb:,.0f} |")
        # how often did no-FL find the right file unaided?
        hit = 0
        for i in both:
            named = named_classes(B[i]["project"], B[i]["bug"])
            touched = {f.split("/")[-1].replace(".java","") for f in B[i]["patch_files"]}
            if named and (touched <= named): hit += 1
        print(f"\nOf those, {lb} patches confined to the class(es) the developer changed: "
              f"**{hit}/{len(both)}** ({100*hit/len(both):.1f}%)")

if __name__ == "__main__":
    main()
