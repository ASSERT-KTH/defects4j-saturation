# Positive evidence of memorisation

The main run's caveat was the standard one: Defects4J predates the model's training
cutoff, so memorisation of the developer fixes "cannot be excluded and is not controlled
for". The follow-up experiment produced something stronger than a caveat — a case where
memorisation is not merely possible but demonstrated, with a tell that can be checked
mechanically.

## The finding

`JacksonCore-10` was one of three bugs the main sweep did not solve. Re-run with
`claude-opus-5` at the original 30-minute cap, it was solved twice out of two, in 3 and 4
minutes, 15 turns each. Both runs emitted this:

```diff
         hash += (hash >>> 16); // to xor hi- and low- 16-bits
-        hash ^= (hash >>> 12);
+        hash ^= (hash << 3); // shuffle back a bit
+        hash += (hash >>> 12); // and bit more
         return hash;
```

The two added lines are the developer's fix. **So are the two comments, byte for byte.**

Code can be re-derived. `// shuffle back a bit` and `// and bit more` cannot: they are
informal prose, they carry no information the compiler or the tests could supply, and
nothing in the task constrains their wording. Reproducing both exactly, in the right order,
attached to the right statements, is not inference.

## Ruling out the alternatives

The strings are absent from everything the agent could read. In a fresh
`defects4j checkout -p JacksonCore -v 10b`:

```
$ grep -c "shuffle back a bit" src/main/java/.../ByteQuadsCanonicalizer.java
0
$ grep -rn "shuffle back a bit" .          # the entire checkout
(no output)
```

The buggy `_hash` is a single uncommented line at 984:

```java
        hash += (hash >>> 16); // to xor hi- and low- 16-bits
        hash ^= (hash >>> 12);
        return hash;
```

The agent's whole session is 14 tool calls: read the class, read three test files, one
`defects4j compile`, one throwaway harness under `/tmp`, three `Edit`s, two test runs, one
`git diff`. Checked against that log:

- **No `.git` access.** The harness moves the checkout's `.git` — which carries the
  `D4J_JacksonCore_10_FIXED_VERSION` tag and full upstream history — out of the workspace
  before the agent starts, and replaces it with an empty repo. The agent's only git command
  was `git diff`.
- **No access to `framework/projects/*/patches/`**, where Defects4J keeps the reference
  patches. Zero matches in the log.
- **No network.** `WebSearch` and `WebFetch` are in `--disallowed-tools`. The only URLs in
  the entire session are five occurrences of `http://www.cse.yorku.ca/~oz/hash.html`, which
  is a pre-existing comment on line 970 of the buggy file — read, not fetched.
- **No search.** The hash function was changed in a **single `Edit`**, first attempt, no
  iteration:

  ```
  old='hash += (hash >>> 16); // to xor hi- and low- 16-bits\n        hash ^= (hash >>> 12);\n        return hash;'
  new='hash += (hash >>> 16); // to xor hi- and low- 16-bits\n        hash ^= (hash << 3); // shuffle back a bit\n        hash += (hash >>> 12); // and bit more\n        return hash;'
  ```

For contrast, `claude-sonnet-5` at a 4-hour cap wrote its own Java search program, ran 14
JVMs in parallel, and reported testing "well over a billion candidate replacement formulas
(varying shift amounts, add/xor/multiply combinations, seed placement, known avalanche
constants…)" without finding a two-operation expression that was inside its stated search
space. It never produced the comments either.

## What this is, and is not, evidence of

It is not evidence that the agent cheated at run time. Every containment measure in the
harness held; there was nothing to catch. The ground truth did not arrive through a tool
call, it arrived in the weights.

The most parsimonious reading is not "this model memorised Defects4J". It is that
`ByteQuadsCanonicalizer._hash` as it exists **in every published jackson-core artefact since
2015** is in the training data, and `JacksonCore-10` is a synthetic reversion of the commit
that produced it. That generalises past this one bug, and it is the structural problem:

> Every Defects4J bug is a reversion of a real commit in a widely-used open-source library.
> A model that has memorised those libraries as they ship today has, in effect, been handed
> the answer key.

`JacksonCore-10` is not special in kind. It is special only in being *detectable*, because
its fix happens to carry distinctive prose. A fix consisting purely of code — which is most
of them — leaves no comparable trace.

## The other bug tells a different story

Applied to `Math-66`, solved 2/2 by the same model in the same condition, the same test
comes out negative. The developer fix changes three constructor constants; Opus changed two
of them, and the *formatting* is the tell running the other way:

| | developer wrote | buggy file had | Opus wrote |
|---|---|---|---|
| absolute accuracy | `1e-11` | `1E-10` | `1E-11` |
| relative accuracy | `1e-9` | `1.0e-14` | `1.0e-9` |

Opus kept the file's local style — uppercase `1E-`, the redundant `.0` in `1.0e-` — and
changed only the digits. Reciting the developer's line would have produced `1e-11` and
`1e-9`. This is what editing the text in front of you looks like. It also left
`setMaxEvaluations(Integer.MAX_VALUE)` alone where the developer wrote `1000`, and still
passed the full suite — so it did not reproduce the developer's change set, it produced a
smaller one that suffices.

Independent support that these values are *derivable*: `claude-sonnet-5`, which never
solved this bug, nonetheless recovered `1E-11` on its own and said how —

> I verified this by reproducing the exact (bit-identical) hardcoded expected value in
> `MultiStartUnivariateRealOptimizerTest::testQuinticMin` once this constant was corrected.

Against that, Opus changed both constants in one edit with no experimentation, and `1e-9` is
an arbitrary value five orders of magnitude from the `1.0e-14` in the file. **The evidence
for `Math-66` is genuinely ambiguous** and is left that way here. The formatting argues for
derivation; the one-shot correctness of two arbitrary constants argues for recall.

The useful conclusion is that the comment test **discriminates**: run over these four
solved-by-Opus runs it flags one bug and clears the other, rather than condemning
everything. That is what makes it worth running at scale.

## What this means for the numbers

- The `M` condition's headline — Opus 5 solving two bugs that Sonnet 5 could not solve with
  eight times the wall clock — **cannot be read as a capability result.** For
  `JacksonCore-10` the parsimonious explanation is recall. The experiment's stated success
  criterion for this condition ("capability matters at the margin… the strongest argument
  that the benchmark still discriminates between models") is not supported by this evidence.
- The plausibility figure is not wrong, but what it measures is further from "can repair
  software" than the number suggests. Patch *correctness* was already the remaining signal;
  this narrows it again, because a memorised patch is by construction correct.
- `bin/audit_contamination.py` cannot detect this. It greps session tool calls for lookups,
  and there was no lookup.

## A test worth running at scale

The check generalises and costs no model spend. For every accepted patch, extract the
comments and string literals it *adds*, and ask whether each appears anywhere in the buggy
checkout. Anything absent there but present in the developer fix is text the agent could not
have read and did not need to invent.

That converts one anecdote into a rate over 854 bugs, and it is a lower bound by
construction: it can only catch fixes whose developer version carried distinctive
non-code text.

Not run yet — see the open questions at the end of [`remaining3.md`](remaining3.md).

## Reproducing this case

```bash
# 1. the comments are nowhere in anything the agent could read
defects4j checkout -p JacksonCore -v 10b -w /tmp/jc10
grep -rn "shuffle back a bit" /tmp/jc10                 # no output

# 2. but the agent emitted them
cat data-followup/M-r1/JacksonCore-10/patch.diff
zcat data-followup/M-r1/JacksonCore-10/session.jsonl.gz | grep -c "shuffle back a bit"
# 3   (the Edit call, plus the two stream events that echo it)

# 3. and its only git command was the final diff
zcat data-followup/M-r1/JacksonCore-10/session.jsonl.gz \
  | grep -o '"command":"[^"]*git [^"]*"' | sort -u
# "command":"git diff"
```

Both `M` reps show the same thing; `M-r2` is the independent replication.
