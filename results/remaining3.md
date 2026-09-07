# The three bugs that were not solved

851 of the 854 active bugs of Defects4J 3.0.1 got a test-adequate patch from Claude Code
with Sonnet 5 at a 30-minute wall-clock cap. Three did not. This experiment asks whether
they are **budget-limited**, **capability-limited**, or **genuinely hard**, by varying time
and model independently.

## Starting point

| bug | how the run ended | agent patch | developer fix |
|---|---|---|---|
| `JacksonCore-10` | killed at the 1800 s cap (`agent_rc=124`) | +1/−1 in `ByteQuadsCanonicalizer` | **+4/−2**, same file |
| `Math-66` | killed at the 1800 s cap (`agent_rc=124`) | +15/−16 in `BrentOptimizer` | **+11/−22**, same file |
| `Jsoup-67` | stopped on its own, 45 turns, 915 s, $1.61 | +28/−0 in `HtmlTreeBuilder` | **+4/−0**, same file |

Every developer fix is small, in a single file, and in the file the agent was already
editing. None of the three is intrinsically large. But the three failure modes are distinct:

- **`JacksonCore-10` — out of time.** Cut off mid-cleanup on a hash-collision bug, last
  words *"now the file only has the genuine boundary-check fix (line 925)"*, with
  `testCollisionsWithBytesNew187b`, `testShortNameCollisionsDirectNew` and
  `testSyntheticWithBytesNew` still failing.
- **`Math-66` — out of time, and possibly looking in the wrong place.** Cut off at
  *"testQuinticMinStatistics now passes … now let's check the remaining 3 failures"*. The
  developer fix is largely **tolerance constants** (`setAbsoluteAccuracy(1e-11)` → `1E-10`,
  `setRelativeAccuracy(1e-9)` → `1.0e-14`, `setMaxEvaluations(1000)` → `Integer.MAX_VALUE`).
  The agent was rewriting optimiser logic. More time may not help if it never reconsiders
  the class of fix.
- **`Jsoup-67` — wrong fix, confidently self-certified.** Not a budget failure: it stopped
  at 915 s of an 1800 s cap because it believed it was done. It ran a correct `git stash`
  experiment whose output showed the three tests it had broken passing without its patch,
  and reported them as pre-existing environmental failures anyway. See
  [`self-certification.md`](self-certification.md) for the reconstruction. More time will
  not fix this.

## Design

Two factors, one bug at a time, no parallel workers — the main sweep's only flake appeared
under the CPU load of several workers building simultaneously, and two of these three bugs
have timing-sensitive numerical tests.

| condition | model | wall-clock cap | isolates |
|---|---|---|---|
| `T` | `claude-sonnet-5` | 4 h | time alone |
| `M` | `claude-opus-5` | 30 min | model alone |
| `TM` | `claude-opus-5` | 4 h | both |
| `TM+` | `claude-fable-5-1` | 4 h | strongest available |

3 bugs × 4 conditions × **k = 2** repetitions, reported as pass@2 per cell. `k = 2` is the
minimum that distinguishes "solved" from "solved once by luck"; a cell that comes out 1/2 is
re-run to k = 5.

Effort stays `high` throughout, so the model is the only variable in `M` and `TM`.
Everything else — the prompt, the tool restrictions, the `.git` removal that takes the
developer patch out of the agent's reach, and independent verification on a fresh checkout —
is unchanged from the main sweep, so the results are directly comparable.

```bash
./bin/run_remaining3.sh T 2        # condition T, k = 2
python3 bin/report_remaining3.py   # the pass@k table
```

## Results

Conditions `T` and `M` complete (k = 2). `TM` and `TM+` were **not run** — see
"Why `TM` and `TM+` were dropped" below.

| condition | model | cap | JacksonCore-10 | Math-66 | Jsoup-67 |
|---|---|---|---|---|---|
| `T` | claude-sonnet-5 | 4 h | 0/2 (TEST_FAIL) | 0/2 (TEST_FAIL) | **2/2** |
| `M` | claude-opus-5 | 30 min | **2/2** | **2/2** | — |

pass@2 per cell; a non-plausible verdict is named in brackets.

## Cost and effort per cell

| condition | bug | rep | verdict | turns | agent min | cost | patch +/- | vs dev fix |
|---|---|---|---|---|---|---|---|---|
| `T` | JacksonCore-10 | 1 | TEST_FAIL | 90 | 33 | $5.17 | +1/-1 | same-files |
| `T` | JacksonCore-10 | 2 | TEST_FAIL | 214 | 159 | $13.11 | +1/-1 | same-files |
| `T` | Math-66 | 1 | TEST_FAIL | 92 | 27 | $4.59 | +9/-24 | same-files |
| `T` | Math-66 | 2 | TEST_FAIL | 138 | 38 | $7.79 | +6/-17 | same-files |
| `T` | Jsoup-67 | 1 | PLAUSIBLE | 37 | 6 | $0.83 | +49/-7 | different |
| `T` | Jsoup-67 | 2 | PLAUSIBLE | 41 | 11 | $0.98 | +84/-0 | same-files |
| `M` | JacksonCore-10 | 1 | PLAUSIBLE | 15 | 3 | $1.10 | +3/-2 | same-files |
| `M` | JacksonCore-10 | 2 | PLAUSIBLE | 15 | 4 | $1.29 | +2/-1 | same-files |
| `M` | Math-66 | 1 | PLAUSIBLE | 30 | 5 | $1.60 | +12/-27 | same-files |
| `M` | Math-66 | 2 | PLAUSIBLE | 23 | 3 | $1.11 | +9/-23 | same-files |

Total for this experiment: **$37.57** (`~` marks a cost reconstructed from the stream after a wall-clock kill).

## Per-bug summary

- **JacksonCore-10**: solved in 2 of 4 runs — PLAUSIBLE, TEST_FAIL
- **Math-66**: solved in 2 of 4 runs — PLAUSIBLE, TEST_FAIL
- **Jsoup-67**: solved in 2 of 2 runs — PLAUSIBLE

### What condition `T` settles

**Nothing was budget-limited.** Every one of the six runs exited `rc=0` — stopped
voluntarily, well inside the 4-hour cap. The longest used 159 minutes of 240; the median
used 32. Eight times the wall clock of the main sweep changed one of the three outcomes,
and not the two the original `rc=124` kills pointed at.

**`Jsoup-67` was variance, not a capability ceiling — 2/2.** It solves in 6 and 11 minutes,
faster and cheaper than the 15-minute run that failed in the main sweep. The pre-experiment
reading of this bug ("more time will not fix this; it stopped because it believed it was
done") was right that budget was not the issue and wrong about the conclusion: the bug is
comfortably within reach, and the main sweep simply drew a bad sample.

Both successful runs independently rejected the developer's fix and converged on the same
different one. The developer caps the open-elements scope search at 100 entries
(`MaxScopeSearchDepth`, +4 lines). Both agent runs instead built an O(1) index of which tag
names are currently on the stack, so `inSpecificScope` returns early when no target tag is
open anywhere — rep 1 by routing every mutation through `push`/`pop` (+49/−7, spilling into
`HtmlTreeBuilderState.java`), rep 2 more cleanly via a `TagCountingStack extends
ArrayList<Element>` that overrides `add`/`remove`/`set` (+84/−0, confined to the one file
the developer also touched). Worth noting for any correctness discussion: the agents' fix is
**semantics-preserving** — a tag absent from the stack cannot be in scope — whereas the
developer's depth cap genuinely changes behaviour for stacks deeper than 100. `report.py`
scores these `different` and `same-files`; neither label captures that the larger patch is
the more conservative one.

**`JacksonCore-10` — 0/2, and the extra budget bought nothing.** Both reps produced the
*byte-identical* one-line patch, `_spilloverEnd >= (_hashSize << 3)`, which is semantically
exactly half the developer fix. Rep 1 reached it in 33 minutes; rep 2 took 159 minutes and
$13.11, wrote its own Java search harness, ran 14 JVMs in parallel searching for the missing
hash-mixing function — and ended at the same one line, having cleaned up every trace of the
instrumentation.

Rep 2 did localise the remaining half precisely, and proved the code cannot satisfy the
tests as written:

> I proved mathematically (and confirmed by direct execution) that the current
> `calcHash(int q1)` single-quad hash function cannot possibly produce the
> primary/secondary/tertiary/spill-over counts these tests assert — e.g. for
> `testShortNameCollisionsDirectNew` the current hash only yields 384 distinct buckets among
> the 700 test inputs, while the test requires `primaryCount() == 564`, which is
> mathematically impossible with the current formula regardless of any growth/rehash tuning.
> **So `calcHash(int q1)` is a real defect.**

It then reported searching "well over a billion candidate replacement formulas (varying
shift amounts, add/xor/multiply combinations, seed placement, known avalanche constants, and
the rehash growth threshold in tandem)" without success. **That claim does not hold up.** The
developer's replacement is `hash ^= (hash << 3); hash += (hash >>> 12);` — two operations,
shifts of 3 and 12, one xor and one add — squarely inside the space as described. The
session log also shows the agent fighting breakage in its own harness ("my earlier `sed`
only replaced the constructor signature line, not this instantiation"). The likely reading
is a faulty search rather than an inadequate search space: the agent aimed the right tool at
the right target and its own coverage claim is not reliable. The search itself was not
independently reproduced here.

**`Math-66` — 0/2, and rep 2 came within one constant.** Rep 1 left 3 of 4 triggering tests
failing; rep 2 left 1. The developer fix is a structural refactor *plus* three constructor
constants. Both reps got the refactor essentially right (semantically equivalent: they test
`getGoalType() == GoalType.MAXIMIZE` where the developer threads an `isMinim` boolean).
Rep 2 additionally found `setAbsoluteAccuracy(1E-10)` → `1E-11`, the developer's exact
value, and verified it by reverse-engineering:

> **Wrong default absolute accuracy.** The default `absoluteAccuracy` was `1E-10`; it should
> be `1E-11`. I verified this by reproducing the exact (bit-identical) hardcoded expected
> value in `MultiStartUnivariateRealOptimizerTest::testQuinticMin` once this constant was
> corrected.

The two it missed are `setMaxEvaluations(Integer.MAX_VALUE)` → `1000` and
`setRelativeAccuracy(1.0e-14)` → `1e-9`. The second is what the last failing test needs, and
it is the counterintuitive one: the fix *loosens* relative accuracy by five orders of
magnitude while tightening absolute accuracy.

**The `Math-66` diagnostic arm is cancelled.** It was designed to add the hint *"the defect
may lie in numerical tolerances or iteration limits rather than in the algorithm"*, to
separate "cannot find it" from "never considered that class of fix". Rep 2 answers that
without the hint: it named "wrong default absolute accuracy" as a root cause and confirmed
it numerically. The agent considered the class and found part of it, so the hint has nothing
left to test.

**Both unsolved bugs now reduce to recovering an arbitrary historical constant** — a
bit-mixing expression, and a relative-accuracy value — in order to satisfy assertions on
exact numbers (`primaryCount() == 564`; agreement to `1e-13`). That is a property of the
tests as much as of the defects, and it is worth stating before asking whether a stronger
model helps: what is being measured at this margin is search for a specific magic value, not
program repair in the usual sense.

**Rep-to-rep variance is large.** 33 vs 159 minutes on the same bug, $4.59 vs $13.11, 3 vs 1
residual failures. `k = 2` supports the qualitative claims above (nothing is budget-limited;
`Jsoup-67` is reachable) but is too thin for a defensible pass rate on any cell.

### What condition `M` settles — and what it does not

Opus 5 at the **original 30-minute cap** solved both remaining bugs, 2/2 each, in 3-5
minutes and 15-30 turns, for $5.10 across all four runs. On the face of it that is the
cleanest possible model effect: Sonnet 5 failed both 0/2 with eight times the wall clock,
one of those runs spending 159 minutes and $13.11 on a 14-JVM parallel search.

**That reading does not survive contact with the patches.** Both Opus runs on
`JacksonCore-10` reproduced the developer's fix *including the developer's two comments,
byte for byte*, in a single `Edit` with no iteration:

```diff
         hash += (hash >>> 16); // to xor hi- and low- 16-bits
-        hash ^= (hash >>> 12);
+        hash ^= (hash << 3); // shuffle back a bit
+        hash += (hash >>> 12); // and bit more
```

Those comments appear nowhere in the buggy checkout — not in the file, not anywhere in the
tree. They carry no information the tests or the compiler could supply. The harness held
(no `.git`, no patches directory, no network, one `git diff`); the ground truth did not come
through a tool call, it came from the weights. The full verification chain, and why the same
test comes out *negative* for `Math-66`, is in
[`contamination-evidence.md`](contamination-evidence.md).

So the plan's success criterion for this condition — *"`M` cracks something `T` does not →
capability matters at the margin… strongest argument that the benchmark still discriminates
between models"* — **is not supported.** For `JacksonCore-10` the parsimonious explanation
is recall, not capability. For `Math-66` the evidence is ambiguous and left that way: Opus
preserved the buggy file's own numeric formatting (`1E-11`, `1.0e-9` rather than the
developer's `1e-11`, `1e-9`) and omitted one developer change as unnecessary, which is what
local editing looks like — but it fixed two arbitrary constants in one shot with no
experimentation, which is not.

The measured result stands: **all 854 bugs of Defects4J 3.0.1 now have a test-adequate
patch from some run in this study.** What that number licenses you to conclude about repair
ability is a separate question, and narrower than it looks.

### Why `TM` and `TM+` were dropped

`TM` (Opus 5, 4 h) and `TM+` (Fable 5.1, 4 h) were budgeted at roughly $150-420 combined and
were not run, for two reasons:

1. **No headroom to measure.** `M` solved both bugs in 3-5 minutes of a 30-minute cap. A
   4-hour cap cannot show anything a 30-minute cap did not; there was no run anywhere in
   this experiment that exhausted its budget.
2. **The question changed.** `TM`/`TM+` were designed to separate capability from time. With
   memorisation demonstrated on one of the two bugs, spending Fable-tier rates to watch a
   stronger model recall the same commit faster would produce a number that reads as a
   capability finding and is not one. `TM+`'s stated criterion — "Defects4J plausibility is
   saturated outright for frontier agents" — is already answered by `M` at a twelfth of the
   price, with the same caveat attached.

### Self-certification, in contrast to the main sweep

All four failing runs reported their failure plainly, in their own voice — a section headed
"What I could not fix" or "Not fixed", naming the tests left failing and why, and in every
case explicitly declining to tune constants to force a pass. Rep 2 of `JacksonCore-10`:

> Since I can't verify a genuine, non-hacky fix, I'm leaving `calcHash(int q1)` unchanged
> rather than guessing and risking a value that merely happens to pass by coincidence.

Across the 854 runs of the main sweep at a 30-minute cap, the agent reported failure **zero**
times. At a 4-hour cap it reported failure **4 out of 4** times it failed. The short cap was
not only losing fixes; it was suppressing the agent's own signal that it was stuck — both
`rc=124` kills in the main sweep died mid-work, which is precisely what made them look
budget-limited. See [`self-certification.md`](self-certification.md).

## The predictions, scored

The four criteria were written before any run. None came out as expected.

| predicted | actual |
|---|---|
| **`T` alone cracks `JacksonCore-10` and `Math-66`** → the 99.6% is partly a wall-clock artefact, and the 30-minute cap becomes the headline caveat | **Wrong.** `T` cracked neither. It cracked `Jsoup-67`, the bug expected to be immune to more time. Nothing was budget-limited: all six `T` runs exited `rc=0`, median 32 minutes of 240. |
| **`M` cracks something `T` does not** → capability matters at the margin; the strongest argument that the benchmark still discriminates between models | **Happened, but does not mean this.** `M` cracked both, at the *30-minute* cap. On `JacksonCore-10` it reproduced the developer's comments verbatim, so the parsimonious explanation is recall. The criterion is not supported. |
| **Nothing cracks `Jsoup-67`** → a genuinely hard case whose failure is over-editing plus false self-certification, not search budget | **Wrong.** Solved 2/2 in 6 and 11 minutes, faster and cheaper than the run that failed. The original failure was a bad sample. The false self-certification was real, but it was not a property of the bug. |
| **`TM+` cracks all three** → plausibility saturated outright for frontier agents, only correctness remains as a signal | **Not run, and unnecessary.** Every bug was already solved by `T` or `M`. The conclusion holds — all 854 have a test-adequate patch — but it arrived at a twelfth of the projected cost, and with a contamination caveat the criterion did not anticipate. |

Two findings the design did not anticipate at all:

- **Short caps suppress the agent's own failure signal.** Zero honest failure reports in 854
  runs at 30 minutes; four out of four at 4 hours. The two `rc=124` kills that made these
  bugs look budget-limited were agents cut off *before* they could conclude they were stuck.
- **Memorisation is demonstrable, not just possible**, and detectable through added comments
  that cannot exist in the buggy checkout. See
  [`contamination-evidence.md`](contamination-evidence.md).

## Caveats

- Runs bill against an OAuth subscription rather than an API key, so a 4 h agent cap can
  collide with a 5 h usage window. The harness parks the batch at a window reset and
  requeues the bug, which means an interrupted run is discarded and repeated rather than
  resumed. Wall-clock cost is therefore higher and less predictable than the token cost.
- `--max-budget-usd 25` is passed per run as a hard stop.
- Cost for any run killed at the cap is reconstructed from the session stream and marked
  `~` in the table below; see the telemetry note in the top-level README.

## Open questions

- **Run the comment test over all 854 accepted patches.** For each, extract the comments and
  string literals the patch *adds* and check whether they appear anywhere in the buggy
  checkout. Text absent there but present in the developer fix is text the agent could not
  have read. This costs no model spend and would turn one demonstrated case into a rate. It
  is a lower bound by construction — it can only catch fixes whose developer version carried
  distinctive non-code text.
- **Whether `JacksonCore-10` and `Math-66` should count as repair failures at all.** Both
  reduce, at the margin, to recovering an arbitrary historical constant in order to satisfy
  an assertion on an exact number (`primaryCount() == 564`; agreement to `1e-13`). That is
  arguably a property of those tests rather than of the defects. Reclassifying benchmark
  bugs is not something this study does unilaterally.
- **`k = 2` does not support a per-cell pass rate.** It supports the qualitative claims here
  (nothing was budget-limited; `Jsoup-67` is reachable; Opus solves both stragglers) but
  rep-to-rep variance was large — 33 vs 159 minutes and 3 vs 1 residual failures on the same
  bug and model. No cell came out 1/2, so the plan's escalation trigger to k = 5 never fired.
