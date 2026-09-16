#!/usr/bin/env python3
"""Look for text an agent could not have read and did not need to invent.

Channel 0 of leakage.md -- the model's training data -- has no mitigation, so
the only thing left is to measure it. Code can be re-derived from the tests and
the surrounding source. Prose cannot: a comment carries no information the
compiler or the test suite could supply, and nothing in the task constrains its
wording. So when an agent's patch ADDS a comment or string literal that

  (a) appears in the developer's fix, and
  (b) appears nowhere in the buggy version the agent was given,

that text came from somewhere other than the task. `JacksonCore-10` is the
worked example: `// shuffle back a bit` and `// and bit more`, byte for byte.

Two stages, because verifying (b) properly needs a checkout per bug:

  stage 1 (free)      screen every bug using dev.patch alone. Defects4J's
                      <N>.src.patch turns FIXED into BUGGY, so its '-' lines are
                      the developer's additions and its '+' and context lines are
                      text the buggy version already had.
  stage 2 (checkouts) for flagged bugs only, confirm the text appears nowhere in
                      the whole buggy tree -- not just outside the patch hunk.

Usage:
  audit_memorisation.py <runDir> [<runDir> ...]           # stage 1
  audit_memorisation.py <runDir> --verify [--workdir DIR] # stage 1 + stage 2
"""
import json, pathlib, re, subprocess, sys, collections

# A comment or a string literal, with its delimiters stripped.
LINE_COMMENT  = re.compile(r"//\s*(.+?)\s*$")
BLOCK_COMMENT = re.compile(r"/\*+\s*(.+?)\s*\*+/")
STAR_LINE     = re.compile(r"^\s*\*\s*(.+?)\s*$")       # javadoc continuation
STRING_LIT    = re.compile(r'"((?:[^"\\]|\\.){4,})"')   # >=4 chars: skip "", " ", "x"

# Prose worth testing. Anything that is really code, punctuation or a bare
# identifier can be re-derived and is dropped.
CODEY = re.compile(r"[;{}]|\breturn\b|\bif\s*\(|&&|\|\||->|=>|\+\+|\w+\(\)|"
                   r"\w\.\w+\(|\b(int|void|final|static|public|private)\b")

def is_prose(t):
    """Distinctive natural-language text, as opposed to code or boilerplate."""
    if len(t) < 12:                      return False   # too short to be distinctive
    if len(t.split()) < 3:               return False   # needs to read as a phrase
    if re.fullmatch(r"[\W_]+", t):       return False
    if CODEY.search(t):                  return False   # a code fragment, not prose
    # mostly letters and spaces, or it is punctuation-heavy machinery
    letters = sum(c.isalpha() or c.isspace() for c in t)
    if letters / len(t) < 0.8:           return False
    return True

def texts(lines):
    """Comments and string literals in a set of diff lines, as normalised prose."""
    out = set()
    for l in lines:
        body = l[1:]
        for rx in (LINE_COMMENT, BLOCK_COMMENT, STAR_LINE):
            for m in rx.finditer(body):
                t = " ".join(m.group(1).split())
                if is_prose(t):
                    out.add(t)
        for m in STRING_LIT.finditer(body):
            t = m.group(1)
            if is_prose(t):
                out.add(t)
    return out

def sides(path):
    add, rem, ctx = [], [], []
    try:
        for l in path.read_text(errors="replace").splitlines():
            if l.startswith("+++") or l.startswith("---") or l.startswith("diff "):
                continue
            if l.startswith("+"):   add.append(l)
            elif l.startswith("-"): rem.append(l)
            elif l.startswith(" "): ctx.append(l)
    except OSError:
        pass
    return add, rem, ctx

def screen(bugdir):
    """-> (candidates, agent_prose_count) for one bug."""
    p, d = bugdir / "patch.diff", bugdir / "dev.patch"
    if not (p.is_file() and d.is_file() and p.stat().st_size):
        return set(), 0
    a_add, _, _          = sides(p)
    d_add, d_rem, d_ctx  = sides(d)      # dev.patch is FIXED -> BUGGY
    agent   = texts(a_add)               # what the agent wrote
    devfix  = texts(d_rem)               # what the developer's fix adds
    already = texts(d_add) | texts([" " + l[1:] for l in d_ctx])   # already in the buggy file
    return (agent & devfix) - already, len(agent)

def verify(project, bug, phrases, workdir):
    """Confirm the phrases appear nowhere in the buggy checkout."""
    w = pathlib.Path(workdir) / f"{project}-{bug}.memaudit"
    subprocess.run(["rm", "-rf", str(w)], check=False)
    r = subprocess.run(["defects4j", "checkout", "-p", project, "-v", f"{bug}b", "-w", str(w)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    confirmed = []
    for t in phrases:
        hit = subprocess.run(["grep", "-rqF", t, str(w)], capture_output=True)
        if hit.returncode != 0:          # absent from the entire buggy tree
            confirmed.append(t)
    subprocess.run(["rm", "-rf", str(w)], check=False)
    return confirmed

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_verify = "--verify" in sys.argv
    workdir = "/tmp"
    if "--workdir" in sys.argv:
        workdir = sys.argv[sys.argv.index("--workdir") + 1]

    flagged, scanned, with_prose = [], 0, 0
    for run in args:
        for d in sorted(pathlib.Path(run).iterdir()):
            if not (d / "patch.diff").is_file():
                continue
            v = (d / "verdict").read_text().strip() if (d / "verdict").is_file() else "?"
            scanned += 1
            cand, n_prose = screen(d)
            if n_prose:
                with_prose += 1
            if cand:
                flagged.append((run, d.name, v, sorted(cand)))

    print("# Memorisation audit: text the agent could not have read\n")
    print(f"patches scanned: {scanned}")
    print(f"  of which the agent's patch adds any prose at all: {with_prose}")
    print(f"  flagged by stage 1 (prose shared with the developer fix, absent "
          f"from the patch context): **{len(flagged)}**\n")
    for run, bug, v, cand in flagged:
        print(f"- **{bug}** [{pathlib.Path(run).name}] ({v})")
        for t in cand:
            print(f"    - `{t}`")

    if do_verify and flagged:
        print("\n## Stage 2 — confirmed absent from the whole buggy checkout\n")
        for run, bug, v, cand in flagged:
            project, num = bug.rsplit("-", 1)
            got = verify(project, num, cand, workdir)
            if got is None:
                print(f"- {bug}: checkout failed, unverified")
            elif got:
                print(f"- **{bug}** ({v}) — {len(got)}/{len(cand)} confirmed:")
                for t in got:
                    print(f"    - `{t}`")
            else:
                print(f"- {bug}: none confirmed (all present somewhere in the buggy tree)")

if __name__ == "__main__":
    main()
