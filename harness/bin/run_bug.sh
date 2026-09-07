#!/bin/bash
# Run one Defects4J bug end to end:
#   checkout -> de-leak -> baseline -> Claude Code (Sonnet 5) -> patch -> independent verify
# Usage: run_bug.sh <Project> <bugId> <runDir>
set -uo pipefail
source "$(dirname "$0")/env.sh"

P="$1"; B="$2"
mkdir -p "$3"
RUNDIR="$(realpath "$3")"
OUT="$RUNDIR/$P-$B"
WORK="$D4J_CLAUDE_ROOT/work/$P-$B.agent"
VERIFY="$D4J_CLAUDE_ROOT/work/$P-$B.verify"
GITORIG="$D4J_CLAUDE_ROOT/work/$P-$B.gitorig"

# A campaign is a prompt variant. `perfect-fault-localization` names the classes the
# developer changed; `no-fault-localization` withholds them. Everything else is identical,
# so campaigns are directly comparable.
CAMPAIGN="${CAMPAIGN:-perfect-fault-localization}"
TASK_TMPL="$D4J_CLAUDE_ROOT/campaign/$CAMPAIGN/task.md.tmpl"
[ -f "$TASK_TMPL" ] || { echo "no such campaign: $CAMPAIGN ($TASK_TMPL)" >&2; exit 2; }
export CAMPAIGN

AGENT_TIMEOUT="${AGENT_TIMEOUT:-1800}"
TEST_TIMEOUT="${TEST_TIMEOUT:-2400}"
case "$P" in
  Closure|JacksonDatabind|Mockito) AGENT_TIMEOUT=$((AGENT_TIMEOUT*2)); TEST_TIMEOUT=$((TEST_TIMEOUT*2));;
esac
# Model, effort and a hard dollar stop are parameters so the same harness can run
# the main sweep and the follow-up conditions. finalize.py reads the same two
# environment variables when it records the run.
export AGENT_MODEL="${AGENT_MODEL:-claude-sonnet-5}"
export AGENT_EFFORT="${AGENT_EFFORT:-high}"
BUDGET_ARG=()
[ -n "${AGENT_MAX_BUDGET_USD:-}" ] && BUDGET_ARG=(--max-budget-usd "$AGENT_MAX_BUDGET_USD")

mkdir -p "$OUT"
FLAKY_NOTE=""
rm -rf "$WORK" "$VERIFY" "$GITORIG"
START=$(date +%s)

log() { echo "[$P-$B] $*" >&2; }
finish() {
  local verdict="$1"; local note="${2:-}"
  # Developer patch kept alongside every result, whatever the verdict, for
  # offline correctness comparison. Copied here rather than earlier so the
  # ground truth is never on disk while the agent is running.
  cp "$D4J_HOME/framework/projects/$P/patches/$B.src.patch" "$OUT/dev.patch" 2>/dev/null || true
  echo "$verdict" > "$OUT/verdict"
  echo "$note"    > "$OUT/note"
  echo "$(( $(date +%s) - START ))" > "$OUT/wallclock_s"
  python3 "$D4J_CLAUDE_ROOT/bin/finalize.py" "$OUT" "$P" "$B" "$RUNDIR"
  rm -rf "$WORK" "$VERIFY" "$GITORIG"
  log "verdict=$verdict $note"
  exit 0
}

# ---------------------------------------------------------------- 1. checkout
if ! timeout 900 defects4j checkout -p "$P" -v "${B}b" -w "$WORK" > "$OUT/checkout.log" 2>&1; then
  finish CHECKOUT_FAIL "defects4j checkout failed"
fi

# ------------------------------------------------- 2. remove the ground truth
# The checkout's .git carries D4J_<P>_<B>_FIXED_VERSION and full upstream
# history, i.e. the developer patch. Move it out of the agent's reach and
# replace it with a fresh repo used only to diff the agent's edits.
mv "$WORK/.git" "$GITORIG" 2>/dev/null || finish CHECKOUT_FAIL "no .git in checkout"
git -C "$WORK" init -q
cat > "$WORK/.git/info/exclude" <<'EOF'
target/
build/
dist/
classes/
out/
bin/classes/
.gradle/
.gradle_local_home/
.m2/
.ivy2/
gradle-app.setting
*.class
*.lock
*.bin
failing_tests
all_tests
*.orig
*.rej
EOF
# ------------------------------------------------------- 3. bug metadata
CFG="$WORK/defects4j.build.properties"
prop() { sed -n "s/^$1=//p" "$CFG" | head -1; }
SRC_DIR=$(prop d4j.dir.src.classes)
TEST_DIR=$(prop d4j.dir.src.tests)
TRIGGER=$(prop d4j.tests.trigger)
MODIFIED=$(prop d4j.classes.modified)
[ -n "$SRC_DIR" ] || finish ERROR "no d4j.dir.src.classes"
echo "$SRC_DIR" > "$OUT/src_dir"; echo "$TEST_DIR" > "$OUT/test_dir"
echo "$TRIGGER" | tr ',' '\n' > "$OUT/trigger_tests"

# ------------------------------------------------------- 4. baseline build/test
if ! timeout "$TEST_TIMEOUT" defects4j compile -w "$WORK" > "$OUT/compile_before.log" 2>&1; then
  finish BASELINE_FAIL "buggy version does not compile"
fi
timeout "$TEST_TIMEOUT" defects4j test -r -w "$WORK" > "$OUT/test_before.log" 2>&1
cp "$WORK/failing_tests" "$OUT/test_before.txt" 2>/dev/null || : > "$OUT/test_before.txt"
BEFORE_FAIL=$(grep -c "^--- " "$OUT/test_before.txt" 2>/dev/null || true); BEFORE_FAIL=${BEFORE_FAIL:-0}
if [ "$BEFORE_FAIL" -eq 0 ]; then
  finish BASELINE_FAIL "no failing test in the buggy version"
fi

# The bar a patch has to clear, stated explicitly: fix every triggering test and
# introduce no failure BEYOND the ones the buggy version already had. So the
# allowed post-patch failure set is  baseline failures \ triggering tests  --
# in practice empty for all but a handful of bugs, but asserted rather than
# assumed.
grep '^--- ' "$OUT/test_before.txt" | sed 's/^--- //' | sort -u > "$OUT/.before_names"
grep -v '^$' "$OUT/trigger_tests" | sort -u > "$OUT/.trigger_names"
comm -23 "$OUT/.before_names" "$OUT/.trigger_names" > "$OUT/allowed_failures.txt"
rm -f "$OUT/.before_names" "$OUT/.trigger_names"

# Snapshot AFTER the baseline build: several projects' builds mutate the tree
# themselves (Mockito downloads jars into compileLib/ and drops a broken Groovy
# test), and those side effects must not be attributed to the agent.
git -C "$WORK" add -A -- . >/dev/null 2>&1
git -C "$WORK" -c user.email=harness@local -c user.name=harness commit -q -m baseline >/dev/null 2>&1
if ! git -C "$WORK" rev-parse HEAD >/dev/null 2>&1; then finish ERROR "baseline commit failed"; fi

# ------------------------------------------------------------- 5. build prompt
python3 - "$OUT" "$P" "$B" "$SRC_DIR" "$TEST_DIR" "$TRIGGER" "$MODIFIED" "$TASK_TMPL" <<'PY'
import sys, pathlib
out, proj, bug, src, tst, trig, mod, tmpl = sys.argv[1:9]
tpl = pathlib.Path(tmpl).read_text()
fail = pathlib.Path(out, "test_before.txt").read_text()
# keep the prompt bounded: the failure report can be huge for some bugs
if len(fail) > 12000:
    fail = fail[:12000] + "\n... (truncated)\n"
tests = "\n".join("  - " + t for t in trig.split(",") if t)
classes = "\n".join("  - " + c for c in mod.split(",") if c) or "  (not specified)"
txt = (tpl.replace("__PROJECT__", proj).replace("__BUG__", bug)
          .replace("__SRC_DIR__", src).replace("__TEST_DIR__", tst)
          .replace("__TRIGGER_TESTS__", tests)
          .replace("__MODIFIED_CLASSES__", classes)
          .replace("__FAILURE_OUTPUT__", fail.strip()))
pathlib.Path(out, "task.md").write_text(txt)
PY
[ -s "$OUT/task.md" ] || finish ERROR "prompt rendering failed"

# ------------------------------------------------------------- 6. run the agent
log "launching claude (timeout ${AGENT_TIMEOUT}s)"
AGENT_START=$(date +%s)
# SIGINT first, not SIGTERM: the CLI traps INT and flushes its final `result`
# event (turns, cost, tokens). SIGKILL only after a 60 s grace period.
( cd "$WORK" && timeout --signal=INT --kill-after=60 "$AGENT_TIMEOUT" \
    claude -p "$(cat "$OUT/task.md")" \
      --model "$AGENT_MODEL" \
      --effort "$AGENT_EFFORT" \
      "${BUDGET_ARG[@]}" \
      --permission-mode bypassPermissions \
      --output-format stream-json --verbose \
      --append-system-prompt "$(cat "$D4J_CLAUDE_ROOT/prompts/rules.md")" \
      --disallowed-tools WebSearch WebFetch Task Workflow Skill ToolSearch \
        CronCreate CronDelete CronList SendMessage RemoteTrigger ScheduleWakeup \
        DesignSync EnterWorktree ExitWorktree TaskOutput TaskStop ListAgents \
        NotebookEdit ReportFindings \
      --settings "$D4J_CLAUDE_ROOT/config/batch-settings.json" \
      --strict-mcp-config \
      --setting-sources project \
      --no-session-persistence \
) > "$OUT/claude.jsonl" 2> "$OUT/claude.err"
AGENT_RC=$?
echo $(( $(date +%s) - AGENT_START )) > "$OUT/agent_s"
echo "$AGENT_RC" > "$OUT/agent_rc"
printf '%s\n' "$AGENT_MODEL" > "$OUT/agent_model"
printf '%s\n' "$AGENT_TIMEOUT" > "$OUT/agent_timeout_s"

if grep -qiE "usage limit|rate.?limit(ed)? |too many requests|overloaded_error" "$OUT/claude.err" "$OUT/claude.jsonl" 2>/dev/null; then
  if ! grep -q '"subtype":"success"' "$OUT/claude.jsonl" 2>/dev/null; then
    finish USAGE_LIMIT "claude reported a usage/rate limit"
  fi
fi
[ "$AGENT_RC" -eq 124 ] && TIMED_OUT=1 || TIMED_OUT=0

# ------------------------------------------------------------- 7. extract patch
git -C "$WORK" add -A -- . >/dev/null 2>&1
git -C "$WORK" diff --cached HEAD -- "$SRC_DIR" > "$OUT/patch.diff" 2>/dev/null
git -C "$WORK" diff --cached HEAD --name-status > "$OUT/changed_files.txt" 2>/dev/null

# Tampering. Only three things count, so that build scratch created by the
# agent's own `defects4j compile/test` runs never triggers a false positive:
#   a) any change at all inside the test tree
#   b) modification/deletion of any file that was tracked at baseline and lives
#      outside the production source directory (build files, resources, ...)
#   c) a build-configuration file added at the repository root
if [ -n "$TEST_DIR" ] && grep -qE "^[A-Z]+	${TEST_DIR}/" "$OUT/changed_files.txt"; then
  finish TAMPERED "modified the test tree"
fi
if awk -F'\t' -v src="$SRC_DIR" '$1 ~ /^[MD]/ && index($2, src "/") != 1 {print; found=1} END{exit !found}' \
     "$OUT/changed_files.txt" > "$OUT/tamper.txt"; then
  finish TAMPERED "modified $(wc -l < "$OUT/tamper.txt") tracked file(s) outside $SRC_DIR"
fi
if grep -qE "^A	(build\.xml|pom\.xml|build\.gradle|maven-build\.xml|\.defects4j\.config|[^/]*\.properties)$" "$OUT/changed_files.txt"; then
  finish TAMPERED "added a build-configuration file"
fi
if [ ! -s "$OUT/patch.diff" ]; then
  [ "$TIMED_OUT" -eq 1 ] && finish TIMEOUT "agent timed out with no patch"
  finish NO_PATCH "agent produced no source change"
fi

# --------------------------------------------- 8. independent verification
if ! timeout 900 defects4j checkout -p "$P" -v "${B}b" -w "$VERIFY" > "$OUT/verify_checkout.log" 2>&1; then
  finish ERROR "verification checkout failed"
fi
if ! git -C "$VERIFY" apply --whitespace=nowarn "$OUT/patch.diff" > "$OUT/apply.log" 2>&1; then
  if ! patch -p1 -d "$VERIFY" -f -s < "$OUT/patch.diff" >> "$OUT/apply.log" 2>&1; then
    finish ERROR "patch does not apply to a clean checkout"
  fi
fi
if ! timeout "$TEST_TIMEOUT" defects4j compile -w "$VERIFY" > "$OUT/compile_after.log" 2>&1; then
  finish COMPILE_FAIL "patched version does not compile"
fi
timeout "$TEST_TIMEOUT" defects4j test -r -w "$VERIFY" > "$OUT/test_rel.log" 2>&1
cp "$VERIFY/failing_tests" "$OUT/test_rel.txt" 2>/dev/null || : > "$OUT/test_rel.txt"
if ! grep -q "run.dev.tests).*OK" "$OUT/test_rel.log" || [ ! -s "$VERIFY/all_tests" ]; then
  finish ERROR "relevant test suite did not run to completion during verification"
fi
REL_FAIL=$(grep -c '^--- ' "$OUT/test_rel.txt" 2>/dev/null || true); REL_FAIL=${REL_FAIL:-0}
if [ "$REL_FAIL" -ne 0 ]; then
  # Confirm before judging: some developer tests are timing-sensitive and flake
  # under the load of several workers building in parallel. Only failures that
  # reproduce on a second run count.
  timeout "$TEST_TIMEOUT" defects4j test -r -w "$VERIFY" > "$OUT/test_rel2.log" 2>&1
  cp "$VERIFY/failing_tests" "$OUT/test_rel2.txt" 2>/dev/null || : > "$OUT/test_rel2.txt"
  grep '^--- ' "$OUT/test_rel.txt"  2>/dev/null | sed 's/^--- //' | sort -u > "$OUT/.r1"
  grep '^--- ' "$OUT/test_rel2.txt" 2>/dev/null | sed 's/^--- //' | sort -u > "$OUT/.r2"
  comm -12 "$OUT/.r1" "$OUT/.r2" > "$OUT/failing_stable_raw.txt"; rm -f "$OUT/.r1" "$OUT/.r2"
  comm -23 "$OUT/failing_stable_raw.txt" "$OUT/allowed_failures.txt" > "$OUT/failing_stable.txt"
  STABLE=$(wc -l < "$OUT/failing_stable.txt")
  if [ "$STABLE" -ne 0 ]; then
    finish TEST_FAIL "$STABLE relevant test(s) still failing"
  fi
  if [ -s "$OUT/failing_stable_raw.txt" ]; then
    FLAKY_NOTE=" ($(wc -l < "$OUT/failing_stable_raw.txt") pre-existing baseline failure(s) unchanged)"
  else
    FLAKY_NOTE=" (a flaky relevant test failed on the first run only)"
  fi
fi
timeout "$TEST_TIMEOUT" defects4j test -w "$VERIFY" > "$OUT/test_full.log" 2>&1
cp "$VERIFY/failing_tests" "$OUT/test_after.txt" 2>/dev/null || : > "$OUT/test_after.txt"
# Guard against a silently aborted suite being read as "nothing failed".
if ! grep -q "run.dev.tests).*OK" "$OUT/test_full.log" || [ ! -s "$VERIFY/all_tests" ]; then
  finish ERROR "full test suite did not run to completion during verification"
fi
FULL_FAIL=$(grep -c '^--- ' "$OUT/test_after.txt" 2>/dev/null || true); FULL_FAIL=${FULL_FAIL:-0}
if [ "$FULL_FAIL" -ne 0 ]; then
  # Same flakiness guard as above: a regression must reproduce to count.
  timeout "$TEST_TIMEOUT" defects4j test -w "$VERIFY" > "$OUT/test_full2.log" 2>&1
  cp "$VERIFY/failing_tests" "$OUT/test_after2.txt" 2>/dev/null || : > "$OUT/test_after2.txt"
  if ! grep -q "run.dev.tests).*OK" "$OUT/test_full2.log"; then
    finish ERROR "full test suite did not run to completion on the confirmation run"
  fi
  grep '^--- ' "$OUT/test_after.txt"  2>/dev/null | sed 's/^--- //' | sort -u > "$OUT/.f1"
  grep '^--- ' "$OUT/test_after2.txt" 2>/dev/null | sed 's/^--- //' | sort -u > "$OUT/.f2"
  comm -12 "$OUT/.f1" "$OUT/.f2" > "$OUT/regressions_raw.txt"; rm -f "$OUT/.f1" "$OUT/.f2"
  # Same baseline-relative rule. The baseline was measured with `test -r`, so
  # the allowed set only covers relevant tests; a pre-existing failure outside
  # the relevant set would still be counted, as it was before this change.
  comm -23 "$OUT/regressions_raw.txt" "$OUT/allowed_failures.txt" > "$OUT/regressions.txt"
  STABLE=$(wc -l < "$OUT/regressions.txt")
  if [ "$STABLE" -ne 0 ]; then
    finish REGRESSION "$STABLE test(s) broken elsewhere in the suite"
  fi
  if [ -s "$OUT/regressions_raw.txt" ]; then
    FLAKY_NOTE="$FLAKY_NOTE ($(wc -l < "$OUT/regressions_raw.txt") pre-existing baseline failure(s) unchanged in the full suite)"
  else
    FLAKY_NOTE="$FLAKY_NOTE (a flaky test failed on the first full run only)"
  fi
fi

finish PLAUSIBLE "all developer tests pass$FLAKY_NOTE"
