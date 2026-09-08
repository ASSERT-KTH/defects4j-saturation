# Campaign: no fault localization

**Claude Code with Sonnet 5 produces a test-adequate patch for 851 of 853 active bugs of
[Defects4J](https://github.com/rjust/defects4j) 3.0.1 — 99.8% — when it is told only which
tests fail, and has to find the defect itself.**

The companion [`perfect-fault-localization`](../perfect-fault-localization) campaign, whose
prompt named the class the defect was in, scored 851/854 (99.6%). This campaign exists
because that disclosure was a real methodological flaw: the prompt handed over
ground-truth fault localization at class granularity, one class for 85% of bugs, a **36×
median** reduction of the search space an APR tool with real fault localization faces.

## The answer: withholding it changed nothing

## Per-bug transitions (854 bugs in both)

| | no-FL solved | no-FL failed |
|---|---|---|
| **perfect-FL solved** | 851 | 0 |
| **perfect-FL failed** | 1 | 2 |

Lost by no-FL: **0**   gained: **1**   net: **+1**


**No bug was lost.** Not one bug that the perfect-FL agent solved became unsolvable without
the class name. One bug went the other way (`Jsoup-67`, which perfect-FL failed by
sampling noise). The two that failed in both campaigns failed for the same reason both
times.

**There were no localization failures at all:**

- Failed having edited no file the developer touched: **0**
- Failed having produced no patch: **0**
- Accepted patches confined to the class the developer changed: **807/851 (94.8%)** —
  found unaided, and stable within half a point from bug 100 onward

Both failures found the right file by themselves and then ran out of wall clock:

| bug | perfect-FL | no-FL | localization |
|---|---|---|---|
| `JacksonCore-10` | TEST_FAIL, rc=124 | TEST_FAIL, rc=124 | found `ByteQuadsCanonicalizer` unaided |
| `Math-66` | TEST_FAIL, rc=124 (0/2 even at a 4 h cap) | TEST_FAIL, rc=124 | found `BrentOptimizer` unaided |

`JacksonCore-10` needs a specific hash-mixing expression; `Math-66` needs three constructor
constants. Both agents were sitting in exactly the right file when the clock ran out.
Localization was never the bottleneck on either.

## What it cost

### Robust paired statistics

| metric | median ratio | sum ratio | no-FL higher on | p5-p95 | reading |
|---|---|---|---|---|---|
| cost | 1.023 | 1.019 | 464/854 (54%) | 0.52-2.03 | noise |
| turns | 1.000 | 1.048 | 419/854 (49%) | 0.55-1.90 | noise |
| agent seconds | 1.079 | 1.073 | 512/854 (60%) | 0.54-2.25 | **real** |
| cache-read tokens | 1.042 | 1.038 | 473/854 (55%) | 0.43-2.62 | noise |
| output tokens | 1.032 | 1.006 | 462/854 (54%) | 0.47-2.33 | noise |


Only one metric survives a sign test: **wall-clock time, median ratio 1.079, higher on 60%
of bugs.** Cost (54%), turns (49%), cache-read tokens (55%) and output tokens (54%) are
indistinguishable from a coin flip.

Do not read the sum ratios. Per-bug ratios span roughly 0.5–2.0 and the ten costliest bugs
carry 16% of the total, so a sum swings on which expensive Closure bugs happen to be in
scope — during this campaign the interim sum ratio for cost wandered between 0.97 and 1.02
while the median never moved off 1.02. That is why the table reports both and labels its own
conclusions.

## Effort on the 851 bugs both campaigns solved

| | perfect-FL | no-FL |
|---|---|---|
| median turns | 12 | 13 |
| median agent s | 83 | 88 |
| median cache-read tokens | 284,397 | 307,508 |
| median cost | 0.18 | 0.19 |

Of those, no-FL patches confined to the class(es) the developer changed: **807/851** (94.8%)

**So finding the defect yourself costs about 8% more wall-clock time and nothing else.**
It is measurably more work — a few more turns, a little longer — but the extra searching is
cheap next to the repair, and it buys the same result.

## What that says about Defects4J

The disclosure was a flaw worth fixing and it barely mattered, which is itself the finding:
**Defects4J's triggering tests already point at the defect.** A failing test name, a stack
trace and an assertion message localize a bug to one class about 95% of the time for an
agent that can read the tree. Naming the class adds almost nothing on top.

That is a statement about the benchmark, not about the model. It also means the perfect-FL
number was not inflated in the way the critique implied — but "not inflated" was not
knowable without running this, and the two campaigns differ by exactly four lines of prompt.

## Configuration

| | |
|---|---|
| model | `claude-sonnet-5`, effort `high` |
| prompt | [`prompts/task.md.tmpl`](prompts/task.md.tmpl) + the shared [`harness/prompts/rules.md`](../../harness/prompts/rules.md) |
| wall-clock cap | 30 min (60 for Closure, JacksonDatabind, Mockito) |
| runs per bug | 1 |
| tools | Bash, Read, Edit, Write — no web, no subagents |
| wall clock | 27 h, 4 workers, 21 usage-limit parks |
| agent time | 39.2 h |
| cost | **$324.58** over the 853 counted bugs ($325.19 including the excluded `Time-14`) |

The only difference from the perfect-FL campaign:

```
$ diff campaign/perfect-fault-localization/prompts/task.md.tmpl \
       campaign/no-fault-localization/prompts/task.md.tmpl
18,21d17
< Classes the defect is known to be located in:
<
< __MODIFIED_CLASSES__
<
```

`__MODIFIED_CLASSES__` is still computed by the harness; it is simply never rendered into
the prompt. Each bug's `data/<bug>/task.md` is the verbatim prompt the agent received, so
what was withheld is on the record rather than a claim.

## One excluded bug

`Time-14` is excluded, which is why the denominator is 853. The agent ran
`find / -iname "joda-time-*.jar"`, decompiled the class under repair out of a **pre-fix
(2.9.4)** and a **post-fix (2.12.5)** release, and diffed the bytecode. That is
ground-truth access through a channel the harness did not audit — the project's own
published jars in `~/.m2`. Full account, including the session that found the same jars and
declined to use them, in
[`results/contamination-own-artefact.md`](results/contamination-own-artefact.md).

The perfect-FL campaign was audited with the same detector and is clean (0 reads), so its
851/854 stands. The agent now runs with those caches masked
(`harness/bin/sandbox_caches.sh`), which neither completed campaign had.

## Self-certification

Of 854 sessions, 850 asserted success and **none of those assertions was wrong** — better
than perfect-FL, where one was false (`Jsoup-67`). Three made no claim about test outcomes;
one was killed at the cap before reporting.

The agent again reported failure in its own voice **zero** times, replicating the
perfect-FL result and reinforcing that this is a property of the 30-minute cap rather than
of the model: at a 4-hour cap it reported failure 4 times out of 4. See
[`../perfect-fault-localization/results/self-certification.md`](../perfect-fault-localization/results/self-certification.md).

## Data layout

```
prompts/task.md.tmpl                    the campaign's prompt template
results/results.jsonl                   one record per bug (Time-14 carries "excluded")
results/results.csv                     the same, flattened
results/summary.md                      per-project tables
results/comparison.md                   generated perfect-FL vs no-FL comparison
results/contamination-own-artefact.md   the sixth leakage channel, and the exclusion
results/self_cert.jsonl                 per-bug closing claim and its classification
RESULTS.md                              per-bug table
data/<Project>-<id>/                    per-bug artefacts, as in the other campaign
```

## Reproducing

```bash
source harness/bin/env.sh
CAMPAIGN=no-fault-localization ./harness/bin/run_all.sh runs/nofl 4
python3 harness/bin/compare_campaigns.py runs/full runs/nofl \
        --label-a perfect-FL --label-b no-FL
python3 harness/bin/audit_own_artefact.py runs/nofl
```
