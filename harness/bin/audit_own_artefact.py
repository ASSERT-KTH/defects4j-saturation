"""Audit the sixth leakage channel: the project's own published artefacts.

~/.m2, ~/.gradle and ~/.ivy2 hold released jars of the very projects Defects4J
bugs come from. A jar at a version after the fix contains the fixed bytecode, so
decompiling it is ground-truth access even though no repository, patch file or
network was touched.
"""
import json, pathlib, re, sys

OWN = {"JacksonCore":"jackson-core", "JacksonDatabind":"jackson-databind",
       "JacksonXml":"jackson-dataformat-xml", "Gson":"gson",
       "Compress":"commons-compress", "Codec":"commons-codec", "Csv":"commons-csv",
       "Lang":"commons-lang", "Collections":"commons-collections", "Cli":"commons-cli",
       "Math":"commons-math", "JxPath":"commons-jxpath", "Jsoup":"jsoup",
       "Time":"joda-time", "Mockito":"mockito", "Closure":"closure-compiler",
       "Chart":"jfreechart"}
CACHE = re.compile(r"\.m2|\.gradle|\.ivy2|/repository/")
EXTRACT = re.compile(r"\b(unzip|jar\s+[xtf]+|javap|cfr|procyon|jd-cli|strings)\b")
HUNT = re.compile(r"\bfind\b[^|;]*-i?name[^|;]*\.jar")

def scan(f, own):
    hunts=[]; reads=[]
    seen=set()
    for line in open(f, errors="replace"):
        line=line.strip()
        if not line.startswith("{"): continue
        try: ev=json.loads(line)
        except: continue
        if ev.get("type")!="assistant": continue
        m=ev.get("message") or {}
        for i,b in enumerate(m.get("content") or []):
            k=(m.get("id"), b.get("id") or i)
            if k in seen: continue
            seen.add(k)
            if b.get("type")!="tool_use": continue
            c=str((b.get("input") or {}).get("command") or "")
            if not c: continue
            if HUNT.search(c) and own in c.lower(): hunts.append(c)
            # reading the project's own artefact from a cache, not from target/
            if own in c and CACHE.search(c) and EXTRACT.search(c) and "target/" not in c:
                reads.append(c)
    return hunts, reads

import sys
RUNS = sys.argv[1:] or ["runs/full", "runs/nofl"]
rows=[]
for run in RUNS:
    for d in sorted(pathlib.Path(run).iterdir()):
        f=d/"claude.jsonl"
        if not f.is_file(): continue
        proj=d.name.rsplit("-",1)[0]
        own=OWN.get(proj)
        if not own: continue
        h,r = scan(f, own)
        if h or r:
            v=(d/"verdict").read_text().strip() if (d/"verdict").is_file() else "?"
            rows.append((run, d.name, v, len(h), len(r), (r or h)[0]))
reads = [r for r in rows if r[4]]
hunts = [r for r in rows if not r[4]]
print(f"# Sixth leakage channel: the project's own published artefacts\n")
print(f"Sessions that EXTRACTED or decompiled their own project's cached jar: "
      f"**{len(reads)}** -- these are ground-truth access.\n")
for run,b,v,nh,nr,ex in reads:
    print(f"- **{b}** [{run.split('/')[-1]}] verdict={v}, {nr} read(s)")
    print(f"  `{' '.join(ex.split())[:180]}`")
print(f"\nSessions that only SEARCHED for such a jar without reading one: {len(hunts)}")
print("Most are looking for junit/hamcrest to build a test classpath, which is benign;\n"
      "a search that finds nothing is not access. Listed for completeness:\n")
for run,b,v,nh,nr,ex in hunts:
    print(f"- {b} [{run.split('/')[-1]}] {v}")
