# Defects4J saturation

A harness that runs a headless [Claude Code](https://claude.com/claude-code) agent on every
active bug of [Defects4J](https://github.com/rjust/defects4j) 3.0.1 (854 bugs, 17 projects)
and independently verifies each patch it produces.

The repository is organised by **campaign**. A campaign is one prompt variant run over the
whole benchmark; the harness, the verification and the tool restrictions are identical
across campaigns, so their numbers are directly comparable.

## Campaigns

| campaign | what the agent is told | result |
|---|---|---|
| [**perfect-fault-localization**](campaign/perfect-fault-localization) | failing tests, their output, **and the class the defect is in** | **851 / 854 (99.6%)** test-adequate |
| [**no-fault-localization**](campaign/no-fault-localization) | failing tests and their output only | not yet run |

### perfect-fault-localization — TL;DR

- **851 / 854 (99.6%)** patches pass the triggering tests and break no other developer
  test. $319.13 at list prices, median 2.8 min and 12 turns per bug.
- **The prompt names the buggy class**, from Defects4J's own `d4j.classes.modified` — one
  class for 85% of bugs, a **36× median** reduction of the search space an APR tool with
  real fault localization would face. So this is a repair rate *under perfect class-level
  FL*, not a repair rate on Defects4J.
- **Plausible is not correct.** 62.2% of accepted patches repair the same file a different
  way than the developer did.
- **Memorisation is demonstrated, not merely possible.** On one bug the model reproduced the
  developer's fix *and the developer's comments*, byte for byte, from a checkout containing
  neither.
- **A follow-up on the three failures** finds all three are solvable, that none was
  budget-limited, and that a short wall-clock cap suppresses the agent's own signal that it
  is stuck: zero honest failure reports in 854 runs at 30 min, four out of four at 4 h.

### no-fault-localization — planned

Identical in every respect except that the prompt omits the class list. The two templates
differ by exactly four lines:

```
$ diff campaign/perfect-fault-localization/task.md.tmpl campaign/no-fault-localization/task.md.tmpl
18,21d17
< Classes the defect is known to be located in:
<
< __MODIFIED_CLASSES__
<
```

## Protocol

Identical in every campaign. For each of the 854 bugs, independently:

1. `defects4j checkout -p <P> -v <N>b` into a scratch workspace.
2. **The checkout's `.git` is moved out of the workspace.** It carries the
   `D4J_<P>_<N>_FIXED_VERSION` tag and the full upstream history — that is, the developer
   patch. A fresh, empty git repo replaces it and is used only to diff the agent's edits.
3. Baseline `defects4j compile` and `defects4j test -r`. The triggering test names and the
   real failure output are rendered into the campaign's prompt template; the result is
   stored per bug as `data/<bug>/task.md`, so what the agent received is on the record. The
   baseline snapshot is taken *after* the build, because some projects' builds mutate their
   own tree (Mockito downloads jars into `compileLib/` and deletes a broken Groovy test) and
   those changes must not be attributed to the agent.
4. `claude -p` runs in the workspace with `bypassPermissions` and tools restricted to
   Bash/Read/Edit/Write — no web access, no subagents. It may iterate with `defects4j
   compile` and `defects4j test` as often as it likes, under a wall-clock cap. Model,
   effort and cap are campaign parameters; see the campaign's own README.
5. The agent's diff, restricted to the production source directory, becomes `patch.diff`.
6. **Verification runs on a fresh checkout**, so nothing the agent did to its own
   workspace, test tree or build files can influence the outcome: apply `patch.diff`,
   `defects4j compile`, `defects4j test -r`, then the full developer suite. The bar is
   **baseline-relative** — fix every triggering test, and introduce no failure *beyond* the
   set the buggy version already had — and any post-patch failure must reproduce on a second
   run before it counts, so a flaky test cannot sink a patch.

A patch is rejected as `TAMPERED` if it changes anything in the test tree, modifies a file
that was tracked at baseline outside the source directory, or adds a build-configuration
file at the repository root.

### Verdicts

| verdict | meaning |
|---|---|
| `PLAUSIBLE` | compiles; triggering tests pass; no other developer test broken |
| `REGRESSION` | triggering tests pass but other tests break |
| `TEST_FAIL` | triggering or relevant tests still fail |
| `COMPILE_FAIL` | patched version does not compile |
| `NO_PATCH` | agent changed no production source |
| `TAMPERED` | touched the test tree or build configuration — discarded |
| `TIMEOUT` | cut off with no patch at all |
| `USAGE_LIMIT` | subscription usage limit — retried, never counted as a result |
| `BASELINE_FAIL` / `CHECKOUT_FAIL` / `ERROR` | harness or environment problem |

`PLAUSIBLE` means test-adequate, not necessarily correct — the standard APR caveat. Per-campaign
counts are in each campaign's README.

Three verification guards matter for reading any campaign's numbers:

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

## Prompts

Two files make the prompt, and the split is deliberate:

- [`harness/prompts/rules.md`](harness/prompts/rules.md) — the system prompt, **shared by
  every campaign**: edit only the source directory, never weaken a test, no network, no
  repository history, the fix must be general rather than special-cased on the test's
  values, and say so plainly if no real fix is found.
- `campaign/<name>/task.md.tmpl` — the user prompt, **campaign-specific**. This is where the
  campaigns differ, and the only place they differ.

Placeholders: `__PROJECT__`, `__BUG__`, `__SRC_DIR__`, `__TEST_DIR__`, `__TRIGGER_TESTS__`,
`__MODIFIED_CLASSES__`, `__FAILURE_OUTPUT__`. The rendered result is stored verbatim per bug
as `data/<bug>/task.md`, so what each agent actually received is on the record.

## Reproducing

```bash
./harness/bin/setup.sh                 # pins d4j/ to v3.0.1, seeds repos/major/libs, self-checks Lang-1
source harness/bin/env.sh              # D4J_HOME, JAVA_HOME (Java 11), PATH

# one bug, one campaign
CAMPAIGN=perfect-fault-localization ./harness/bin/run_bug.sh Lang 1 runs/smoke

# a whole campaign; <runDir> <parallel workers>, resumable, safe to Ctrl-C
CAMPAIGN=no-fault-localization ./harness/bin/run_all.sh runs/nofl 4

python3 harness/bin/report.py runs/nofl        # summary + results.csv
python3 harness/bin/report_per_bug.py runs/nofl data > RESULTS.md
touch runs/nofl/STOP                           # graceful stop
```

`CAMPAIGN` selects `campaign/<name>/task.md.tmpl` and is recorded in every `result.json`.
`AGENT_MODEL`, `AGENT_EFFORT`, `AGENT_TIMEOUT` and `AGENT_MAX_BUDGET_USD` override the
defaults (`claude-sonnet-5`, `high`, 1800 s, unset).

Analysis scripts, none of which spend anything on the model:

```bash
python3 harness/bin/extract_sessions.py runs/full   # -> sessions.jsonl (telemetry + closing claims)
python3 harness/bin/self_cert.py       runs/full    # agent self-report vs. ground truth
python3 harness/bin/audit_contamination.py runs/full  # on-host leakage audit
python3 harness/bin/report_remaining3.py runs/remaining3
```

**Auth.** Runs used an OAuth subscription. `run_all.sh` reads the `rate_limit_event` records
in each session log; when the 5-hour window is exhausted the batch parks until the reported
reset and the bug is requeued. Prefer `ANTHROPIC_API_KEY` if you want `--max-budget-usd` to
be the real control.

**Java.** Defects4J 3.x requires Java 11. Verification here used the system OpenJDK 11; for
byte-exact parity with the Defects4J CI, install `jdk-11.0.17` from
<https://defects4j.org/downloads/> and point `D4J_JAVA_HOME` at it.

## Repository layout

```
harness/
  bin/                       the harness and the analysis scripts
  prompts/rules.md           the system prompt, shared by all campaigns
  config/batch-settings.json
campaign/<name>/
  README.md                  that campaign's findings
  RESULTS.md                 per-bug table
  prompts/task.md.tmpl       that campaign's prompt
  results/                   run-level records and analyses
  data/<Project>-<id>/       per-bug artefacts, one directory per bug
```

## Licence

Harness and results: MIT (`LICENSE`). `dev.patch`, `task.md` and `test_before.txt` contain
excerpts of the subject projects, which remain under their own licences (mostly
Apache-2.0), redistributed here as Defects4J does.
