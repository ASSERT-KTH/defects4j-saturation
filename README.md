# Defects4J saturation

**Claude Code with Sonnet 5 produces a test-adequate patch for 851 of the 854 active bugs
in [Defects4J](https://github.com/rjust/defects4j) 3.0.1 — 99.6%.**

This repository contains the harness, the complete per-bug data (patches, agent session
logs, verification output) and the contamination audit for that run.

The headline number is a statement about the *benchmark*, not only about the model.
Defects4J's plausibility criterion — the triggering tests pass and no other developer test
breaks — is now essentially saturated for an agent that can compile and run the test suite
in a loop. What remains discriminative is patch *correctness*, which this data lets you
study: 27.7% of the accepted patches are line-for-line the developer's fix, 62.2% change
the same file(s) by a different route, and 10.1% repair the defect somewhere else entirely.

## Results

| project | bugs | plausible | rate | identical to dev fix | cost | median turns | median min |
|---|---|---|---|---|---|---|---|
| Chart | 26 | 26 | 100.0% | 11 | $3.90 | 10 | 1.3 |
| Cli | 39 | 39 | 100.0% | 7 | $9.64 | 10 | 0.8 |
| Closure | 174 | 174 | 100.0% | 40 | $121.55 | 19 | 5.6 |
| Codec | 18 | 18 | 100.0% | 8 | $5.69 | 10 | 1.1 |
| Collections | 28 | 28 | 100.0% | 3 | $4.61 | 10 | 1.5 |
| Compress | 47 | 47 | 100.0% | 8 | $9.86 | 10 | 1.3 |
| Csv | 16 | 16 | 100.0% | 6 | $2.08 | 8 | 0.7 |
| Gson | 18 | 18 | 100.0% | 13 | $3.14 | 10 | 1.1 |
| JacksonCore | 26 | 25 | 96.2% | 9 | $8.75 | 12 | 1.3 |
| JacksonDatabind | 110 | 110 | 100.0% | 25 | $31.88 | 14 | 4.0 |
| JacksonXml | 6 | 6 | 100.0% | 3 | $1.93 | 14 | 1.9 |
| Jsoup | 93 | 92 | 98.9% | 33 | $26.62 | 11 | 1.0 |
| JxPath | 22 | 22 | 100.0% | 1 | $10.13 | 24 | 2.5 |
| Lang | 61 | 61 | 100.0% | 22 | $11.07 | 9 | 1.7 |
| Math | 106 | 105 | 99.1% | 41 | $37.11 | 11 | 2.9 |
| Mockito | 38 | 38 | 100.0% | 2 | $10.38 | 11 | 4.9 |
| Time | 26 | 26 | 100.0% | 4 | $12.15 | 18 | 2.1 |
| **all** | **854** | **851** | **99.6%** | **236 (27.7%)** | **$310.52** | **12** | **2.8** |

### The three failures

| bug | why |
|---|---|
| `JacksonCore-10` | agent cut off by the 30-minute wall-clock cap; partial patch, 3 relevant tests still fail |
| `Math-66` | agent cut off by the 30-minute wall-clock cap; partial patch, 3 relevant tests still fail |
| `Jsoup-67` | agent stopped on its own after 45 turns; 3 relevant tests still fail |

Two of the three are budget exhaustion rather than repair failure. A longer cap would very
likely push the rate higher, which is the point about saturation.

### Shape of the patches

- 749 of 851 accepted patches touch a single file; 102 touch more than one.
- Median 5 added lines (mean 10.3); largest is `Closure-155` at 134 added lines.
- Median 12 agent turns; p90 35; maximum 241 (`Closure-171`, also the most expensive bug at $12.35).
- 90 bugs were fixed in 6 turns or fewer.
- Median agent time 84 s; p90 333 s.

### Cost and compute

$310.52 at Sonnet 5 list prices ($2/$10 per MTok), mean $0.36 per bug. 7.6M output tokens
against 641.8M cache-read and only 29.9K fresh input tokens — prompt caching carries
essentially all of the context cost. 36.6 h of agent time and 55.5 h of total harness time
(4 workers) over 26.7 h of wall clock, of which roughly 10 h were spent parked on
subscription usage limits.

## Protocol

For each of the 854 bugs, independently:

1. `defects4j checkout -p <P> -v <N>b` into a scratch workspace.
2. **The checkout's `.git` is moved out of the workspace.** It carries the
   `D4J_<P>_<N>_FIXED_VERSION` tag and the full upstream history — that is, the developer
   patch. A fresh, empty git repo replaces it and is used only to diff the agent's edits.
3. Baseline `defects4j compile` and `defects4j test -r`. The triggering test names and the
   real failure output become the task description (`data/<bug>/task.md` is the verbatim
   prompt). The baseline snapshot is taken *after* the build, because some projects' builds
   mutate their own tree (Mockito downloads jars into `compileLib/` and deletes a broken
   Groovy test) and those changes must not be attributed to the agent.
4. `claude -p` runs in the workspace: `claude-sonnet-5`, effort `high`,
   `bypassPermissions`, tools restricted to Bash/Read/Edit/Write — no web access, no
   subagents. It may iterate with `defects4j compile` and `defects4j test` as often as it
   likes. Wall clock capped at 30 min (60 for Closure, JacksonDatabind, Mockito).
5. The agent's diff, restricted to the production source directory, becomes `patch.diff`.
6. **Verification runs on a fresh checkout**, so nothing the agent did to its own
   workspace, test tree or build files can influence the outcome: apply `patch.diff`,
   `defects4j compile`, `defects4j test -r`, then the full developer suite.

A patch is rejected as `TAMPERED` if it changes anything in the test tree, modifies a file
that was tracked at baseline outside the source directory, or adds a build-configuration
file at the repository root. No run was rejected on these grounds.

### Verdicts

| verdict | meaning | n |
|---|---|---|
| `PLAUSIBLE` | compiles; triggering tests pass; no other developer test broken | 851 |
| `TEST_FAIL` | triggering or relevant tests still fail | 3 |
| `REGRESSION` | triggering tests pass but other tests break | 0 |
| `COMPILE_FAIL` | patched version does not compile | 0 |
| `NO_PATCH` | agent changed no production source | 0 |
| `TAMPERED` | touched the test tree or build configuration | 0 |
| `TIMEOUT` | cut off with no patch at all | 0 |

Two verification guards matter for reading these numbers:

- **Flakiness.** A `TEST_FAIL` or `REGRESSION` verdict requires the failure to reproduce on
  a second run of the same suite; only tests failing in both runs count. This was added
  after `Collections-11` was initially scored `REGRESSION` on a
  `TestBoundedBuffer ... Timeout expired` failure unrelated to its patch, tripped by CPU
  load from parallel workers. Re-judged, it is `PLAUSIBLE` with the textbook `readObject`
  fix.
- **Aborted suites.** If the developer suite does not run to completion during
  verification, the bug is recorded as `ERROR`, never as "nothing failed". Every one of the
  854 verification logs carries the `run.dev.tests ... OK` marker.

## Contamination

Defects4J long predates the model's training cutoff, so **memorisation of the developer
fixes cannot be excluded and is not controlled for here.** Read the 99.6% with that in
mind. What *is* controlled is on-host leakage. The agents ran with unrestricted Bash, so
five paths could in principle have handed over the fix:

| channel | sessions that used it |
|---|---|
| `framework/projects/<P>/patches/<N>.src.patch` (the fix itself) | 0 |
| `project_repos/<own project>.git` (upstream history) | 0 |
| the moved-aside `.gitorig` | 0 |
| `defects4j checkout -v <N>f` (the fixed version) | 0 |
| any `D4J_*_FIXED_VERSION` tag | 0 |

`results/contamination-audit.txt` is the output of `harness/bin/audit_contamination.py`,
which greps the tool calls of all 854 sessions; re-run it against `data/` to verify.

One session, `JacksonDatabind-106`, read a **dependency's** published source — `ParserBase.java`
from `jackson-core.git` — while repairing `TreeTraversingParser` in jackson-databind. That is
a dependency's implementation, not the ground truth for its own bug, and it never touched
`jackson-databind.git`. It is reported in the audit for completeness. Six further sessions
unzipped dependency jars (jackson-core, junit bytecode) or read Defects4J's own `*.build.xml`
to run a single test.

## Limitations

- **Plausible is not correct.** 62.2% of accepted patches fix the same file a different way
  than the developer did; those need human review before anyone calls them correct. The
  `identical` / `same-files` / `different` classification in `results/summary.md` is a
  whitespace- and comment-normalised line comparison, not a semantic one.
- **Memorisation is uncontrolled**, as above.
- The agent sees the triggering test *names and failure output*, which is the standard
  Defects4J repair setup but is more information than a developer facing a bug report.
- Single run per bug — no pass@k, no seed variation.
- `dev.patch` in each directory is Defects4J's `<N>.src.patch`, which turns the *fixed*
  version into the *buggy* one; the developer fix is its inverse. `report.py` accounts for
  this when comparing.
- Verification uses the system OpenJDK 11, not the `jdk-11.0.17` build pinned by the
  Defects4J CI. Set `D4J_JAVA_HOME` to that JDK for byte-exact parity.

## Reproducing

Requires Java 11, git, svn, perl with the Defects4J modules, and an authenticated
`claude` CLI.

```bash
./harness/bin/setup.sh                  # pins a private Defects4J at v3.0.1, self-checks Lang-1
source harness/bin/env.sh
./harness/bin/run_all.sh runs/full 4    # all 854 bugs, 4 workers; resumable, safe to Ctrl-C
./harness/bin/run_bug.sh Lang 1 runs/one # a single bug
python3 harness/bin/report.py runs/full # tables + results.csv
python3 harness/bin/audit_contamination.py runs/full
touch runs/full/STOP                    # graceful stop
```

The driver reads the `rate_limit_event` records in each session log and parks the whole
batch until the reported reset when a subscription window is exhausted; those bugs are
requeued and never scored as results.

## Data layout

```
results/results.jsonl        one record per bug: verdict, cost, tokens, turns, timings
results/results.csv          the same, flattened
results/summary.md           report.py output (the tables above)
results/contamination-audit.txt
results/bugs.tsv             the 854 <project>\t<id> pairs
data/<Project>-<id>/
  task.md                    the verbatim prompt the agent received
  patch.diff                 the agent's patch (production sources only)
  dev.patch                  Defects4J's patch (inverse of the developer fix, see above)
  result.json                verdict, cost, tokens, turns, timings, patch stats
  test_before.txt            failing tests + output before repair
  changed_files.txt          every path the agent touched, with git status codes
  session.jsonl.gz           the complete agent session (stream-json)
```

Per-record fields are documented in `results/summary.md`; `session.jsonl.gz` is Claude
Code's `--output-format stream-json` stream, one JSON event per line.

## Licence

Harness and results: MIT (`LICENSE`). `dev.patch`, `task.md` and `test_before.txt` contain
excerpts of the subject projects, which remain under their own licences (mostly
Apache-2.0), redistributed here as Defects4J does.
