# Defects4J x Claude Code (Sonnet 5) — perfect fault localization

854 bugs attempted

| project | n | plausible | rate | identical | test_fail | compile_fail | no_patch | other | cost_usd | med_turns | med_min |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Chart | 26 | 26 | 100.0% | 11 | 0 | 0 | 0 | 0 | 3.90 | 10 | 1.3 |
| Cli | 39 | 39 | 100.0% | 7 | 0 | 0 | 0 | 0 | 9.64 | 10 | 0.8 |
| Closure | 174 | 174 | 100.0% | 40 | 0 | 0 | 0 | 0 | 121.55 | 19 | 5.6 |
| Codec | 18 | 18 | 100.0% | 8 | 0 | 0 | 0 | 0 | 5.69 | 10 | 1.1 |
| Collections | 28 | 28 | 100.0% | 3 | 0 | 0 | 0 | 0 | 4.61 | 10 | 1.5 |
| Compress | 47 | 47 | 100.0% | 8 | 0 | 0 | 0 | 0 | 9.86 | 10 | 1.3 |
| Csv | 16 | 16 | 100.0% | 6 | 0 | 0 | 0 | 0 | 2.08 | 8 | 0.7 |
| Gson | 18 | 18 | 100.0% | 13 | 0 | 0 | 0 | 0 | 3.14 | 10 | 1.1 |
| JacksonCore | 26 | 25 | 96.2% | 9 | 1 | 0 | 0 | 0 | 12.80 | 12 | 1.3 |
| JacksonDatabind | 110 | 110 | 100.0% | 25 | 0 | 0 | 0 | 0 | 31.88 | 14 | 4.0 |
| JacksonXml | 6 | 6 | 100.0% | 3 | 0 | 0 | 0 | 0 | 1.93 | 14 | 1.9 |
| Jsoup | 93 | 92 | 98.9% | 33 | 1 | 0 | 0 | 0 | 26.62 | 11 | 1.0 |
| JxPath | 22 | 22 | 100.0% | 1 | 0 | 0 | 0 | 0 | 10.13 | 24 | 2.5 |
| Lang | 61 | 61 | 100.0% | 22 | 0 | 0 | 0 | 0 | 11.07 | 9 | 1.7 |
| Math | 106 | 105 | 99.1% | 41 | 1 | 0 | 0 | 0 | 41.67 | 11 | 2.9 |
| Mockito | 38 | 38 | 100.0% | 2 | 0 | 0 | 0 | 0 | 10.38 | 11 | 4.9 |
| Time | 26 | 26 | 100.0% | 4 | 0 | 0 | 0 | 0 | 12.15 | 18 | 2.1 |
| **ALL** | 854 | 851 | 99.6% | 236 | 3 | 0 | 0 | 0 | 319.13 | 12 | 2.8 |

## Verdict breakdown

- PLAUSIBLE: 851
- TEST_FAIL: 3

Agent hit the wall-clock cap on 2 bug(s): JacksonCore-10, Math-66

## Patch similarity to the developer fix (plausible patches)

- identical: 236
- same-files: 529
- different: 86

Total list-price cost: $319.13   tokens in/out/cache-read: 30,264/7,914,837/662,263,845

CSV: results/results.csv
