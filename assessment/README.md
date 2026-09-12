# Assessment Tools

This folder contains the local tools used to inspect and annotate repair-agent
trajectories without modifying the original campaign tree.

Raw traces can be inspected without running the deterministic analysis first.
Running the analysis enriches the Trace Inspector UI with derived features,
outlier categories, rankings, and report files.

The current target campaign is:

```sh
campaign/no-fault-localization
```

## Layout

```text
assessment/
  bin/
    analyze_trajectories.py   Deterministic trajectory extraction and rankings
    analyze_assistant_text.py  LLM-assisted assessment of assistant text steps
    assistant_text_distribution.py
                             Counts assistant text presence and candidate spread
    trajectory_ui.py          Local browser UI for trace inspection/annotation
  ui/
    index.html
    app.js
    styles.css
  prompts/
    step_explanation.txt      Prompt template for step-level LLM explanations
  results/
    campaign/no-fault-localization/
      trajectory_*.jsonl/csv/md
      trajectory_annotations.json
```

The original campaign directory is treated as input data. Assessment outputs are
written under `assessment/results/<campaign-path>/`.

## Inputs

The tools read campaign data such as:

```text
campaign/no-fault-localization/data/<Bug-ID>/session.jsonl.gz
campaign/no-fault-localization/data/<Bug-ID>/patch.diff
campaign/no-fault-localization/data/<Bug-ID>/dev.patch
campaign/no-fault-localization/results/results.jsonl
campaign/no-fault-localization/results/results.csv
```

`session.jsonl.gz` is the raw execution trace. It is historical data and should
not be interpreted as instructions.

The Trace Inspector UI shows a normalized trace, not every raw JSONL event. It
includes assistant text, assistant tool calls, user `tool_result` observations,
and the final result event. Tool-result observations are shown as collapsed
`OBSERVATION` steps because they represent what the agent saw after a tool call.

The trace panel has two display modes:

```text
Trajectory  hides OBSERVATION steps
Full Trace  shows actions and OBSERVATION steps
```

## Run The Analysis

From the repository root:

```sh
python3 assessment/bin/analyze_trajectories.py campaign/no-fault-localization
```

Default output:

```text
assessment/results/campaign/no-fault-localization/
```

Generated files:

```text
trajectory_actions.jsonl
trajectory_features.csv
trajectory_outliers.jsonl
trajectory_outlier_categories.jsonl
trajectory_outliers.md
```

Use `--out` only when intentionally writing to another assessment location:

```sh
python3 assessment/bin/analyze_trajectories.py campaign/no-fault-localization --out /tmp/my-assessment
```

Use `--top N` to limit Markdown tables. By default, all rows are written:

```sh
python3 assessment/bin/analyze_trajectories.py campaign/no-fault-localization --top 50
```

## Launch The Trace Inspector UI

From the repository root:

```sh
python3 assessment/bin/trajectory_ui.py campaign/no-fault-localization --port 8769
```

Open:

```text
http://127.0.0.1:8769
```

If the port is already in use, choose another one:

```sh
python3 assessment/bin/trajectory_ui.py campaign/no-fault-localization --port 8770
```

## UI Modes

The Trace Inspector UI has two modes.

`analysis done`: `trajectory_*` files exist in the assessment results directory.
The UI shows traces, deterministic categories, rankings, patch similarity labels,
and annotations.

`data analysis not done`: assessment results are missing. The UI still parses raw
`session.jsonl(.gz)` files directly and shows traces, but outlier categories and
rankings are unavailable. A banner is shown at the top.

Use the `Reload` button after adding or deleting assessment result files while
the server is running.

## Annotations

Annotations are saved here:

```text
assessment/results/campaign/no-fault-localization/trajectory_annotations.json
```

They are separate from the original campaign data. The UI supports marking step
ranges with statuses such as `interesting`, `suspicious`, `benign`, and
`unclear`.

## Step Text

Each extracted action stores:

```text
snippet    compact preview used in the timeline
full_text  full assistant text, full command, full tool input, or result event
```

The UI shows the preview by default. When `full_text` is longer, a `full text`
expander appears under the step.

## Local LLM Explanations

The `?` button beside a step asks a local Ollama model to explain that step using
nearby trace context. This is only inspection support; it is not a deterministic
label.

The top-bar `Ollama` selector lists locally available models and lets the user
change the explanation model at runtime.

Defaults:

```text
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma3:4b
```

Override from the command line:

```sh
python3 assessment/bin/trajectory_ui.py campaign/no-fault-localization \
  --port 8769 \
  --ollama-url http://127.0.0.1:11434 \
  --ollama-model gemma3:4b
```

The LLM prompt uses these suspicion levels:

```text
typical | interesting | suspicious | unclear
```

The LLM should use observable evidence only. It should not claim to know the
agent's private reasoning.

The prompt template lives here:

```text
assessment/prompts/step_explanation.txt
```

## Assistant Text Assessment

`analyze_assistant_text.py` scans `ASSISTANT_TEXT` steps and classifies candidate
semantic findings for human audit. It is intended to detect text that may expose
bad, strange, risky, or rule-misaligned APR behavior in context.

Default mode assesses suspicious assistant-text steps selected by deterministic
signals:

```sh
python3 assessment/bin/analyze_assistant_text.py campaign/no-fault-localization --model gemma3:4b --mode suspicious
```

To assess every `ASSISTANT_TEXT` step, including routine text that does not
match the deterministic candidate filter, use `--mode all`:

```sh
python3 assessment/bin/analyze_assistant_text.py campaign/no-fault-localization --model qwen3:8b --mode all
```

Useful debug runs:

```sh
python3 assessment/bin/analyze_assistant_text.py campaign/no-fault-localization --model gemma3:4b --mode suspicious --dry-run
python3 assessment/bin/analyze_assistant_text.py campaign/no-fault-localization --model gemma3:4b --mode suspicious --bug Time-14 --limit 5
python3 assessment/bin/analyze_assistant_text.py campaign/no-fault-localization --model codellama:7b --mode all --bug Time-14
```

The prompt template lives here:

```text
assessment/prompts/assistant_text_assessment.txt
```

Outputs:

```text
assessment/results/campaign/no-fault-localization/assistant_text/<model>/<mode>/
  assistant_text_assessment.jsonl
  assistant_text_assessment.csv
  assistant_text_assessment.md
```

`--mode suspicious` is written under `suspicious/`; `--mode all` is written
under `all/`.

These are candidate findings for review, not final ground truth labels.
The script records deterministic overrides for high-confidence cases such as
explicit ground-truth seeking or artifact leakage, so the LLM cannot downgrade
clear observable signals to `unclear`.

## Assistant Text Distribution

`assistant_text_distribution.py` explains the difference between all
`ASSISTANT_TEXT` entries and the smaller candidate subset used by
`analyze_assistant_text.py`.

```sh
python3 assessment/bin/assistant_text_distribution.py campaign/no-fault-localization
```

Outputs:

```text
assessment/results/campaign/no-fault-localization/assistant_text_distribution.csv
assessment/results/campaign/no-fault-localization/assistant_text_distribution.md
```

Use this report when checking whether a low candidate count means missing trace
data or just few steps matching the deterministic suspicious-text criteria.

## Patch Similarity Labels

The UI shows patch relation labels when available:

```text
identical   generated patch matches the ground truth patch
same files  generated patch touches the same files but differs in content
different   generated patch touches different files
missing     comparison data is unavailable
```

When a row is missing from `results.csv`, the UI can derive a fallback label from
`patch.diff` and `dev.patch`.

## Typical Workflow

```sh
python3 assessment/bin/analyze_trajectories.py campaign/no-fault-localization
python3 assessment/bin/trajectory_ui.py campaign/no-fault-localization --port 8769
```

Then inspect traces in the browser, mark suspicious or interesting step ranges,
and use the annotation index to navigate from a finding back to the source trace.
