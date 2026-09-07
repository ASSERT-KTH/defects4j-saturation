# Campaign: no fault localization

**Not yet run.**

Identical to [`perfect-fault-localization`](../perfect-fault-localization) in every respect
— same harness, same model and effort, same wall-clock caps, same tool restrictions, same
independent verification on a fresh checkout — except that the prompt does **not** tell the
agent which class the defect is in.

The agent gets the failing test names and their real failure output, and nothing else. It
has to localize the defect itself.

## Why

The perfect-FL campaign reached 851/854, but its prompt named the buggy class, taken from
Defects4J's `d4j.classes.modified`: one class for 85% of bugs, a **36× median** reduction of
the search space an APR tool with real fault localization would face. That number is
therefore a repair rate *under perfect class-level fault localization*, and the size of the
advantage is unknown.

This campaign measures it. The delta between the two is the contribution of fault
localization to the headline.

## The only difference

```
$ diff campaign/perfect-fault-localization/prompts/task.md.tmpl \
       campaign/no-fault-localization/prompts/task.md.tmpl
18,21d17
< Classes the defect is known to be located in:
<
< __MODIFIED_CLASSES__
<
```

Four lines. Everything else — including the `__MODIFIED_CLASSES__` value the harness
computes — is unchanged; the value is simply never rendered into the prompt.

## Running it

```bash
source harness/bin/env.sh
CAMPAIGN=no-fault-localization ./harness/bin/run_all.sh runs/nofl 4
```

Expect roughly the same order of cost as the perfect-FL campaign ($319 at list prices), plus
whatever extra exploration the agents do to find the defect themselves — reading more files
raises cache-read tokens, which dominated the first campaign's bill.
