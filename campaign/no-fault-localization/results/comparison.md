# perfect-FL vs no-FL

854 vs 854 bugs attempted; 854 in both

- **perfect-FL**: 851/854 plausible (99.6%), $319.13
- **no-FL**: 852/854 plausible (99.8%), $325.19

## Per-bug transitions (854 bugs in both)

| | no-FL solved | no-FL failed |
|---|---|---|
| **perfect-FL solved** | 851 | 0 |
| **perfect-FL failed** | 1 | 2 |

Lost by no-FL: **0**   gained: **1**   net: **+1**

## How no-FL failed

- `TEST_FAIL`: 2

Failed having edited **no file the developer touched** (a localization miss, not a repair miss): **0**
Failed having produced no patch at all: **0**

## Paired cost on the same 854 bugs (mix-independent)

| | perfect-FL | no-FL | delta |
|---|---|---|---|
| cost | $319.13 | $325.19 | +1.9% |
| turns | 15,303 | 16,036 | +4.8% |
| agent seconds | 131,838 | 141,411 | +7.3% |
| cache-read tokens | 662,263,845 | 687,251,212 | +3.8% |
| output tokens | 7,914,837 | 7,958,964 | +0.6% |

### Robust paired statistics

| metric | median ratio | sum ratio | no-FL higher on | p5-p95 | reading |
|---|---|---|---|---|---|
| cost | 1.023 | 1.019 | 464/854 (54%) | 0.52-2.03 | noise |
| turns | 1.000 | 1.048 | 419/854 (49%) | 0.55-1.90 | noise |
| agent seconds | 1.079 | 1.073 | 512/854 (60%) | 0.54-2.25 | **real** |
| cache-read tokens | 1.042 | 1.038 | 473/854 (55%) | 0.43-2.62 | noise |
| output tokens | 1.032 | 1.006 | 462/854 (54%) | 0.47-2.33 | noise |

The ten costliest bugs carry 16% of the paired total, which is why the sum ratio is unstable at partial coverage. A sign test within 7 points of 50% is reported as noise.

Per-project cost ratio:

| project | ratio | perfect-FL | no-FL | n |
|---|---|---|---|---|
| Chart | 1.007 | $3.90 | $3.93 | 26 |
| Cli | 0.796 | $9.64 | $7.68 | 39 |
| Closure | 0.992 | $121.55 | $120.56 | 174 |
| Codec | 0.825 | $5.69 | $4.70 | 18 |
| Collections | 0.843 | $4.61 | $3.89 | 28 |
| Compress | 1.095 | $9.86 | $10.80 | 47 |
| Csv | 1.175 | $2.08 | $2.45 | 16 |
| Gson | 1.062 | $3.14 | $3.33 | 18 |
| JacksonCore | 0.839 | $12.80 | $10.73 | 26 |
| JacksonDatabind | 1.226 | $31.88 | $39.09 | 110 |
| JacksonXml | 1.204 | $1.93 | $2.33 | 6 |
| Jsoup | 1.124 | $26.62 | $29.93 | 93 |
| JxPath | 0.928 | $10.13 | $9.41 | 22 |
| Lang | 0.993 | $11.07 | $11.00 | 61 |
| Math | 1.066 | $41.67 | $44.41 | 106 |
| Mockito | 0.932 | $10.38 | $9.67 | 38 |
| Time | 0.930 | $12.15 | $11.30 | 26 |

## Effort on the 851 bugs both campaigns solved

| | perfect-FL | no-FL |
|---|---|---|
| median turns | 12 | 13 |
| median agent s | 83 | 88 |
| median cache-read tokens | 284,397 | 307,508 |
| median cost | 0.18 | 0.19 |

Of those, no-FL patches confined to the class(es) the developer changed: **807/851** (94.8%)
