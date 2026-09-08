# Defects4J x Claude Code (Sonnet 5) — no fault localization

853 bugs attempted

Excluded from every figure below:

- **Time-14** (PLAUSIBLE) — contaminated: agent located and decompiled joda-time 2.9.4 and 2.12.5 from ~/.m2 and diffed the pre- and post-fix bytecode of the class under repair; see results/contamination-own-artefact.md

| project | n | plausible | rate | identical | test_fail | compile_fail | no_patch | other | cost_usd | med_turns | med_min |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Chart | 26 | 26 | 100.0% | 11 | 0 | 0 | 0 | 0 | 3.93 | 10 | 1.5 |
| Cli | 39 | 39 | 100.0% | 12 | 0 | 0 | 0 | 0 | 7.68 | 10 | 0.9 |
| Closure | 174 | 174 | 100.0% | 36 | 0 | 0 | 0 | 0 | 120.56 | 20 | 5.8 |
| Codec | 18 | 18 | 100.0% | 8 | 0 | 0 | 0 | 0 | 4.70 | 11 | 1.5 |
| Collections | 28 | 28 | 100.0% | 3 | 0 | 0 | 0 | 0 | 3.89 | 8 | 1.5 |
| Compress | 47 | 47 | 100.0% | 9 | 0 | 0 | 0 | 0 | 10.80 | 10 | 1.5 |
| Csv | 16 | 16 | 100.0% | 8 | 0 | 0 | 0 | 0 | 2.45 | 8 | 0.8 |
| Gson | 18 | 18 | 100.0% | 10 | 0 | 0 | 0 | 0 | 3.33 | 11 | 1.1 |
| JacksonCore | 26 | 25 | 96.2% | 9 | 1 | 0 | 0 | 0 | 10.73 | 13 | 1.2 |
| JacksonDatabind | 110 | 110 | 100.0% | 23 | 0 | 0 | 0 | 0 | 39.09 | 17 | 4.5 |
| JacksonXml | 6 | 6 | 100.0% | 3 | 0 | 0 | 0 | 0 | 2.33 | 15 | 2.5 |
| Jsoup | 93 | 93 | 100.0% | 33 | 0 | 0 | 0 | 0 | 29.93 | 11 | 1.2 |
| JxPath | 22 | 22 | 100.0% | 2 | 0 | 0 | 0 | 0 | 9.41 | 22 | 2.1 |
| Lang | 61 | 61 | 100.0% | 13 | 0 | 0 | 0 | 0 | 11.00 | 9 | 1.6 |
| Math | 106 | 105 | 99.1% | 45 | 1 | 0 | 0 | 0 | 44.41 | 11 | 3.0 |
| Mockito | 38 | 38 | 100.0% | 6 | 0 | 0 | 0 | 0 | 9.67 | 12 | 4.0 |
| Time | 25 | 25 | 100.0% | 4 | 0 | 0 | 0 | 0 | 10.69 | 16 | 2.2 |
| **ALL** | 853 | 851 | 99.8% | 235 | 2 | 0 | 0 | 0 | 324.58 | 13 | 2.9 |

## Verdict breakdown

- PLAUSIBLE: 851
- TEST_FAIL: 2

Agent hit the wall-clock cap on 2 bug(s): JacksonCore-10, Math-66

## Patch similarity to the developer fix (plausible patches)

- identical: 235
- same-files: 519
- different: 97

Total list-price cost: $324.58   tokens in/out/cache-read: 31,796/7,943,000/686,097,382

CSV: results/results.csv
