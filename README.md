# Defects4J saturation

**Claude Code with Sonnet 5 produces a test-adequate patch for 851 of the 854 active bugs
in [Defects4J](https://github.com/rjust/defects4j) 3.0.1 — 99.6%.**

This repository contains the harness, the complete per-bug data (patches, agent session
logs, verification output) and the contamination audit for that run.

Three analyses accompany it:

- [**Evidence of memorisation**](results/contamination-evidence.md) — one bug where the model
  reproduced the developer's fix *and the developer's comments*, byte for byte, from a
  checkout containing neither. Read the headline with this first.
- [**Agent self-certification**](results/self-certification.md) — 852 assertions of success,
  one of them false, and zero reports of failure in 854 runs.
- [**The three unsolved bugs**](results/remaining3.md) — a follow-up experiment varying
  wall-clock cap and model independently. All three turn out to be solvable; none of the
  four pre-registered predictions held.

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
| Math | 106 | 105 | 99.1% | 41 | $41.67 | 11 | 2.9 |
| Mockito | 38 | 38 | 100.0% | 2 | $10.38 | 11 | 4.9 |
| Time | 26 | 26 | 100.0% | 4 | $12.15 | 18 | 2.1 |
| **all** | **854** | **851** | **99.6%** | **236 (27.7%)** | **$319.13** | **12** | **2.8** |

### The three failures

| bug | why |
|---|---|
| `JacksonCore-10` | agent cut off by the 30-minute wall-clock cap; partial patch, 3 relevant tests still fail |
| `Math-66` | agent cut off by the 30-minute wall-clock cap; partial patch, 3 relevant tests still fail |
| `Jsoup-67` | agent stopped on its own after 45 turns; 3 relevant tests still fail |

Two of the three were cut off at the cap (`agent_rc=124`), which invites reading them as
budget exhaustion. **They are not.** A follow-up experiment
([`results/remaining3.md`](results/remaining3.md)) re-ran all three, varying wall-clock cap
and model independently, k = 2 per cell:

| bug | Sonnet 5, 4 h cap | Opus 5, 30 min cap |
|---|---|---|
| `JacksonCore-10` | 0/2 | **2/2** |
| `Math-66` | 0/2 | **2/2** |
| `Jsoup-67` | **2/2** | not needed |

**All three are solvable, so every one of the 854 bugs has a test-adequate patch from some
run in this study.** Four things in that table are worth more than the headline:

- **Nothing was budget-limited.** All six Sonnet runs at a 4-hour cap exited `rc=0` —
  every one stopped voluntarily, the longest using 159 minutes of 240, the median 32. Eight
  times the wall clock changed exactly one outcome, and not either of the two the `rc=124`
  kills pointed at. On `JacksonCore-10` both reps produced the *byte-identical* one-line
  patch, one of them after a 159-minute, $13.11 run that wrote its own Java search harness
  and ran 14 JVMs in parallel.
- **`Jsoup-67` was a sampling artefact**, not the hard case it looked like. It solves in 6
  and 11 minutes — faster and cheaper than the 15-minute run that failed here. Both
  successful runs rejected the developer's 4-line depth cap for the same different fix: an
  O(1) index of which tags are on the open-elements stack, which is *semantics-preserving*
  where the developer's cap is not.
- **The Opus column is not a capability result.** On `JacksonCore-10` it reproduced the
  developer's comments verbatim — see [Contamination](#contamination). Read it as recall.
- **Short caps suppress the agent's own failure signal.** In 854 runs at 30 minutes the
  agent reported failure **zero** times. At a 4-hour cap it reported failure **4 out of 4**
  times it failed, each time naming the tests left failing and explicitly declining to tune
  constants to force a pass. The two `rc=124` kills were agents cut off *before* they could
  conclude they were stuck — which is precisely what made them look budget-limited.

The two genuinely difficult bugs both reduce, at the margin, to recovering an arbitrary
historical constant to satisfy an assertion on an exact number (`primaryCount() == 564`;
agreement to `1e-13`) — arguably a property of those tests as much as of the defects.

### Shape of the patches

- 749 of 851 accepted patches touch a single file; 102 touch more than one.
- Median 5 added lines (mean 10.3); largest is `Closure-155` at 134 added lines.
- Median 12 agent turns; p90 35; maximum 241 (`Closure-171`, also the most expensive bug at $12.35).
- 90 bugs were fixed in 6 turns or fewer.
- Median agent time 84 s; p90 333 s.

### Cost and compute

$319.13 at Sonnet 5 list prices ($2/$10 per MTok), mean $0.37 per bug. 7.9M output tokens
(63% of them thinking tokens) against 662.3M cache-read and only 30.3K fresh input tokens —
prompt caching carries essentially all of the context cost. 36.6 h of agent time and 55.5 h
of total harness time (4 workers) over 26.7 h of wall clock, of which roughly 10 h were
spent parked on subscription usage limits.

The total was previously reported as $310.52. `JacksonCore-10` and `Math-66` were killed by
`SIGTERM` at the wall-clock cap before the CLI could emit its final `result` event, so their
cost and turn counts were recorded as `0` and `null` — the two most expensive runs in the
sweep were the two missing from the bill. The harness now sends `SIGINT` first with a 60 s
grace period so the CLI can flush, and `finalize.py` falls back to re-summing the
per-message `usage` in the session stream when no result event arrives. Input, cache-read
and cache-write tokens reconstruct exactly (verified against the 852 sessions that kept
their result event: exact on 851, the exception being one session whose log holds two
segments); output tokens are estimated from the stream's running thinking-token counters
plus a fitted tokens-per-character factor, which reproduces per-run cost to a median ratio
of 1.00 (p5 0.98, p95 1.03). The two affected figures are marked `stream_estimate` in
`telemetry_source` and are $4.05 and $4.56.

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
- **Baseline-relative.** A patch must introduce no failure *beyond* the set already failing
  in the buggy version, and must fix the triggering tests. Across all 854 bugs that baseline
  set equals the triggering tests everywhere except `Mockito-24`, which has one pre-existing
  unrelated failure and passed anyway — so the stricter "zero failures" rule the harness
  originally applied changed no verdict. The rule is now asserted explicitly rather than
  left implicit, because "those tests were already failing" is exactly the claim `Jsoup-67`
  made falsely, and it should be answered by the harness's own measurement.

## Contamination

**Memorisation is not a hypothetical here. It is demonstrated for at least one bug.**

The follow-up experiment re-ran `JacksonCore-10` with `claude-opus-5`. It solved the bug
twice out of two, in 3 and 4 minutes, and both runs emitted the developer's fix *including
the developer's two comments, byte for byte*, in a single edit with no iteration:

```diff
         hash += (hash >>> 16); // to xor hi- and low- 16-bits
-        hash ^= (hash >>> 12);
+        hash ^= (hash << 3); // shuffle back a bit
+        hash += (hash >>> 12); // and bit more
```

`grep -rn "shuffle back a bit"` over a fresh `JacksonCore-10b` checkout returns nothing —
the strings are absent from the file and from the whole tree. Informal prose carries no
information the tests or the compiler could supply, so it cannot be re-derived. The
containment below all held: no `.git`, no patches directory, no network, one `git diff`.
The ground truth did not arrive through a tool call.

The parsimonious reading is not "the model memorised Defects4J" but something with wider
reach: `ByteQuadsCanonicalizer._hash` as it ships **in every published jackson-core artefact
since 2015** is in the training data, and this "bug" is a synthetic reversion of the commit
that produced it. Every Defects4J bug is such a reversion, in a widely-used library. A model
that has memorised those libraries as they exist today has effectively been given the answer
key. `JacksonCore-10` is not special in kind — only in being *detectable*, because its fix
happens to carry distinctive prose.

The same test comes out **negative** for `Math-66`, also solved 2/2 by the same model: there
Opus kept the buggy file's own numeric formatting and omitted one of the developer's three
changes as unnecessary, which is what local editing looks like. So the check discriminates
rather than condemning everything. Both cases, with the full verification chain, are in
[`results/contamination-evidence.md`](results/contamination-evidence.md).

**None of this is caught by the audit below**, which greps session tool calls for lookups.
There was no lookup. Read the plausibility figures accordingly: what they measure is further
from "can repair software" than the number suggests, and a memorised patch is by
construction also a *correct* one, which erodes the correctness signal that was supposed to
be what remained.

### On-host leakage, which *is* controlled

The agents ran with unrestricted Bash, so five paths could in principle have handed over the
fix at run time:

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

### A test worth running at scale

The comment check generalises and costs no model spend: for every accepted patch, extract
the comments and string literals it *adds*, and check whether each appears anywhere in the
buggy checkout. Text absent there but present in the developer fix is text the agent could
not have read and did not need to invent. That would turn one demonstrated case into a rate
over 854 bugs. It has **not** been run yet.

## Limitations

- **Plausible is not correct.** 62.2% of accepted patches fix the same file a different way
  than the developer did; those need human review before anyone calls them correct. The
  `identical` / `same-files` / `different` classification in `results/summary.md` is a
  whitespace- and comment-normalised line comparison, not a semantic one.
- **Memorisation is uncontrolled, and demonstrated in at least one case** — see
  [Contamination](#contamination). It is also not independent of the point above: a
  memorised patch is by construction a *correct* one, so recall inflates the
  correctness signal that plausibility was supposed to leave behind.
- The agent sees the triggering test *names and failure output*, which is the standard
  Defects4J repair setup but is more information than a developer facing a bug report.
- Single run per bug in the main sweep — no pass@k, no seed variation. The follow-up
  experiment shows why that matters: `Jsoup-67` is recorded here as a failure and solves
  2/2 on re-run, so **at least one of the three failures is a sampling artefact rather
  than a limit**. The 851 is therefore a slight *under*-estimate of what this
  configuration reaches, and per-bug outcomes near the margin should not be read as
  deterministic. Rep-to-rep variance within a single cell was large: 33 vs 159 minutes and
  3 vs 1 residual failing tests on the same bug and model.
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
results/self-certification.md how often the agent's own closing claim was right
results/contamination-evidence.md the demonstrated memorisation case, and a negative control
results/self-cert.jsonl      per-bug closing claim, its classification and the verdict
results/remaining3.md        the follow-up experiment on the three unsolved bugs
results/contamination-audit.txt
results/bugs.tsv             the 854 <project>\t<id> pairs
data-remaining3/<condition>-r<k>/
  condition.json             model, wall-clock cap, effort, budget for that cell
  results.jsonl              one record per bug in that cell
  <Project>-<id>/            the same per-bug artefacts as data/, plus verdict and note
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
