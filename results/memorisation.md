# Measuring channel 0: text the agent could not have read

[`leakage.md`](../leakage.md) lists six ways the ground truth could reach an
agent. Five are on-host and were blocked or audited. The sixth — the model's
training data — has no mitigation, so the only thing left is to measure it.

This is the sweep that measures it, over **1,718 patches** from both campaigns
and the follow-up experiment. It cost no model spend.

## The idea

Code can be re-derived. The tests, the stack traces and the surrounding source
constrain it, and two people fixing the same defect often write the same lines.

**Prose cannot.** A comment carries no information the compiler or the test suite
could supply, and nothing in the task constrains its wording. So when an agent's
patch *adds* a comment or string literal that

1. also appears in the developer's fix, and
2. appears nowhere in the buggy version the agent was given,

that text came from somewhere other than the task.

## Three stages

| stage | question | cost | survivors |
|---|---|---|---|
| 1 | does the agent's added prose also appear in the developer's fix, and not in the patch context? | free | 93 of 1,718 patches |
| 2 | is it absent from the **entire** buggy checkout, tests included? | 93 checkouts | 32 bugs |
| 3 | could it have been **assembled** from readable fragments? | 32 checkouts | see below |

Stage 2 matters because stage 1 flags a lot of noise: license headers that appear
in hundreds of files in the same repo (`Closure-169` alone contributed 22), and
error messages that a test asserts verbatim. Those all vanish against a whole-tree
grep. 21 of the 93 were eliminated this way.

Stage 3 matters because "absent verbatim" is not the same as "unavailable". A test
asserting a substring —

```java
assertTrue(e.getMessage().contains("Truncated TAR"))
```

— leaves the full phrase absent from the tree while handing the agent most of it.
So for every surviving phrase, stage 3 finds the longest contiguous word sequence
of it that *is* present somewhere in the buggy tree.

## The metric, and a mistake worth recording

The first version of stage 3 scored each phrase by the **fraction** of it that was
readable, and flagged anything under a third. That rule gave a **false negative on
the known positive control**: `JacksonCore-10`'s `and bit more` scored 67%, because
the two-word English fragment `bit more` occurs by chance somewhere in a large
tree. `shuffle back a bit` scored 50% on `back a`.

The fraction is the wrong statistic alone. What matters is the **absolute size** of
the longest readable fragment: one or two short words is coincidence; five words
and twenty-plus characters is the agent having genuinely read most of the phrase.
Results are therefore reported in tiers rather than collapsed into a verdict, and
short phrases are called out as a class this metric cannot judge in either
direction.

## Result

Of 39 phrases across 32 bugs surviving stage 2:

- **strong — 9 phrases across 8 bugs.** Six words or more, with at most three
  words readable anywhere in the tree.
- moderate — 9 phrases across 9 bugs. Six words or more, four to five readable.
- short phrases (under six words) — 20, unjudgeable by this metric.
- weak — 1, most of the phrase was readable.

The strong tier:

| bug | phrase the agent wrote | longest readable fragment |
|---|---|---|
| `Csv-2` | `Index for header '%s' is %d but CSVRecord only has %d values!` | `header` (6 chars) |
| `Gson-8` | `Abstract class can't be instantiated! Class name: ` | `Abstract` (8 chars) |
| `Gson-8` | `Interface can't be instantiated! Interface name: ` | `Interface` (9 chars) |
| `Jsoup-26` | `frameset documents won't have a body. the clean doc will have empty body.` | `have a` (6 chars) |
| `Lang-35` | `Array and element cannot both be null` | `and element` (11 chars) |
| `Closure-151` | `Prints the compiler version to stderr.` | `the compiler` (12 chars) |
| `Jsoup-58` | `because we only look at the body, but we start from a shell, make sure there's nothing in the head` | `the body, but` (13 chars) |
| `Time-8` | `Positive hours must not have negative minutes: ` | `must not have` (13 chars) |
| `Jsoup-7` | `will always be available as created above if not existent` | `will always be` (14 chars) |

`Jsoup-26`, `Jsoup-58` and `Jsoup-7` are the most striking: informal lowercase
developer comments, 10 to 20 words long, reproduced with at most three words of
readable overlap. Nothing in the task constrains how a comment is phrased.

## `JacksonCore-10` — why it is still the clearest case

It does not appear in the strong tier, because both its phrases are under six
words. Its strength was never this metric:

```diff
         hash += (hash >>> 16); // to xor hi- and low- 16-bits
-        hash ^= (hash >>> 12);
+        hash ^= (hash << 3); // shuffle back a bit
+        hash += (hash >>> 12); // and bit more
```

**Two** comments, both matching the developer exactly, in the right order,
attached to the right statements, alongside the correct code — emitted in a
**single edit with no iteration**, in a session of 14 tool calls. The conjunction
is the evidence, not any one phrase. Detail:
[`contamination-evidence.md`](../campaign/perfect-fault-localization/results/contamination-evidence.md).

For contrast, `claude-sonnet-5` spent 159 minutes and $13.11 on the same bug
searching ~400 M candidate formulas and never found it —
[the brute-force case study](../campaign/perfect-fault-localization/results/remaining3.md#case-study-a-self-built-brute-force-search-that-could-not-win).

## What this does and does not establish

**It establishes** that recall of developer text is not a one-off. At least 8 bugs
carry text the agent could not have read and did not need to invent, and the
`JacksonCore-10` conjunction makes at least 9.

**It is a lower bound, by construction.** The method can only see fixes whose
developer version carried distinctive non-code text. Of 1,718 patches, only 587
add any prose at all — the other 1,131 are pure code and are **invisible to this
test**. A low count means *rarely detectable*, not *rarely happening*.

**It does not establish** that these patches are wrong, or that the plausibility
rates are inflated. All 8 strong-tier bugs are `PLAUSIBLE`: the patches work. The
point is narrower and worse — a memorised patch is by construction also a
*correct* one, so recall erodes precisely the correctness signal that plausibility
was supposed to leave behind.

**It says nothing about the other 1,131 patches**, which is most of them.

## Reproducing

```bash
# stage 1 only (free)
python3 harness/bin/audit_memorisation.py runs/full runs/nofl

# stages 1 + 2 (a checkout per flagged bug)
python3 harness/bin/audit_memorisation.py runs/full runs/nofl --verify \
  > results/memorisation-audit.txt

# stage 3 (a checkout per confirmed bug)
python3 harness/bin/audit_memorisation_stage3.py results/memorisation-audit.txt \
  > results/memorisation-stage3.md

# re-rank without re-checking out
python3 harness/bin/audit_memorisation_stage3.py --reclassify results/memorisation-stage3.json
```

Stored output: [`memorisation-audit.txt`](memorisation-audit.txt) (stages 1–2),
[`memorisation-stage3.md`](memorisation-stage3.md) and
[`memorisation-stage3.json`](memorisation-stage3.json) (stage 3).
