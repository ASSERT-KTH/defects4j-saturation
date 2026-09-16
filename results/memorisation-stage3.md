# Stage 3 — was the phrase assemblable from readable text?

phrases: 39, bugs: 32


## Ranked by how much of the phrase was actually readable

- **strong** — phrase of 6+ words, at most 3 readable: **9 phrases / 8 bugs**
- moderate — phrase of 6+ words, 4-5 readable: 9 phrases / 9 bugs
- short phrases (under 6 words), where this metric is unreliable in both directions: 20
- weak — most of the phrase was readable: 1

### Strong

- **Csv-2** — `Index for header '%s' is %d but CSVRecord only has %d values!`
  longest readable fragment: `header` (1 words, 6 chars, 8%)
- **Jsoup-26** — `frameset documents won't have a body. the clean doc will have empty body.`
  longest readable fragment: `have a` (2 words, 6 chars, 15%)
- **Gson-8** — `Abstract class can't be instantiated! Class name: `
  longest readable fragment: `Abstract` (1 words, 8 chars, 14%)
- **Gson-8** — `Interface can't be instantiated! Interface name: `
  longest readable fragment: `Interface` (1 words, 9 chars, 17%)
- **Lang-35** — `Array and element cannot both be null`
  longest readable fragment: `and element` (2 words, 11 chars, 29%)
- **Closure-151** — `Prints the compiler version to stderr.`
  longest readable fragment: `the compiler` (2 words, 12 chars, 33%)
- **Jsoup-58** — `because we only look at the body, but we start from a shell, make sure there's nothing in the head`
  longest readable fragment: `the body, but` (3 words, 13 chars, 15%)
- **Time-8** — `Positive hours must not have negative minutes: `
  longest readable fragment: `must not have` (3 words, 13 chars, 43%)
- **Jsoup-7** — `will always be available as created above if not existent`
  longest readable fragment: `will always be` (3 words, 14 chars, 30%)
### Moderate

- **Jsoup-19** — `if it could not be made abs, run as-is to allow custom unknown protocols`
  longest readable fragment: `could not be made` (4 words, 17 chars, 29%)
- **Lang-11** — `) must be greater than start (`
  longest readable fragment: `must be greater than` (4 words, 20 chars, 57%)
- **Jsoup-83** — `NOTE: out of spec, but clear (spec has this as a part of the attribute name)`
  longest readable fragment: `out of spec, but clear` (5 words, 22 chars, 31%)
- **Lang-12** — `The chars array must not be empty`
  longest readable fragment: `array must not be empty` (5 words, 23 chars, 71%)
- **JacksonCore-14** — `Trying to release buffer smaller than original`
  longest readable fragment: `Trying to release buffer` (4 words, 24 chars, 57%)
- **Jsoup-11** — `:not(selector) subselect must not be empty`
  longest readable fragment: `subselect must not be empty` (5 words, 27 chars, 83%)
- **JacksonDatabind-77** — `Illegal type (%s) to deserialize: prevented for security reasons`
  longest readable fragment: `prevented for security reasons` (4 words, 30 chars, 44%)
- **JacksonDatabind-78** — `Illegal type (%s) to deserialize: prevented for security reasons`
  longest readable fragment: `prevented for security reasons` (4 words, 30 chars, 44%)
- **JacksonCore-18** — `Attempt to write plain `java.math.BigDecimal` (see JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN) with illegal scale (%d): needs to be between [-%d, %d]`
  longest readable fragment: `Attempt to write plain `java.math.BigDecimal`` (5 words, 45 chars, 29%)

### Short phrases — judge these on context, not on this metric

- Jsoup-42 — `skip disabled form inputs` (readable: `skip`, 4 chars)
- JacksonXml-6 — ` bytes (out of ` (readable: `bytes`, 5 chars)
- JacksonXml-6 — `Too few bytes available: missing ` (readable: `bytes`, 5 chars)
- Lang-11 — `Parameter end (` (readable: `end (`, 5 chars)
- JacksonCore-10 — `shuffle back a bit` (readable: `back a`, 6 chars)
- Jsoup-56 — `PUBLIC or SYSTEM` (readable: `PUBLIC`, 6 chars)
- Lang-35 — `Arguments cannot both be null` (readable: `be null`, 7 chars)
- JacksonCore-10 — `and bit more` (readable: `bit more`, 8 chars)
- Lang-37 — `No, so rethrow original` (readable: `original`, 8 chars)
- Lang-9 — `Failed to parse \"` (readable: `Failed to`, 9 chars)
- Compress-37 — `blank line in header` (readable: `blank line`, 10 chars)
- Compress-12 — `Error detected parsing the header` (readable: `parsing the`, 11 chars)
- Compress-28 — `Truncated TAR archive` (readable: `TAR archive`, 11 chars)
- Jsoup-7 — `dupes, move contents to master` (readable: `contents to`, 11 chars)
- Lang-37 — ` in an array of ` (readable: `in an array`, 11 chars)
- Jsoup-93 — `browsers don't submit these` (readable: `don't submit`, 12 chars)
- Time-9 — `Hours out of range: ` (readable: `out of range:`, 13 chars)
- Cli-30 — `Default option wasn't defined` (readable: `Default option`, 14 chars)
- Cli-39 — `Unable to find file: ` (readable: `Unable to find`, 14 chars)
- Compress-41 — `Unexpected record signature: 0X%X` (readable: `Unexpected record`, 17 chars)
