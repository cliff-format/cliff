# CLIFF Implementations

This page registers CLIFF 1.0 implementations and their conformance level, in
the style of the TOML and YAML implementation lists. To list a project, open
a PR adding it here with a link and the conformance row it passed.

## Conformance levels

| Level | Requirement |
| --- | --- |
| **Validator** | Parses the ABNF grammar and enforces every semantic constraint of the specification; reports line-numbered, categorized errors. |
| **Parser** | Tolerant parser: accepts valid documents and ignores unknown `x-` fields with warnings. |
| **Serializer** | Produces canonical CLIFF 1.0 (§17 Serialization), including the file name convention. |
| **Converter** | Bidirectional mapping to another format (XLIFF, PO, Fluent, JSON, CSV), documented lossy conversions. |

## Reference implementation

| Project | Language | Level | Notes |
| --- | --- | --- | --- |
| [cliff-python](https://github.com/cliff-format/cliff-python) (cliff-python) | Python 3.11+ | Validator, Parser, Serializer, Converter | MIT, zero runtime dependencies, 3 319 LOC; bidirectional converters for XLIFF, PO, Fluent, JSON, YAML, CSV, Android, iOS |
| [cliff-test/tools/cliff_validator.py](https://github.com/cliff-format/cliff-test/tools/cliff_validator.py) | Python 3.11+ | Validator, Serializer (test helpers) | Reference validator used by the conformance fixtures |

## Test and benchmark tooling

| Project | Location |
| --- | --- |
| Conformance fixtures (valid/invalid) | [cliff-test/tests/fixtures](https://github.com/cliff-format/cliff-test/tests/fixtures) |
| Token benchmark | [cliff-test/tools/token_benchmark.py](https://github.com/cliff-format/cliff-test/tools/token_benchmark.py) |
| Edit robustness protocol | [cliff-test/tests/edit-robustness](https://github.com/cliff-format/cliff-test/tests/edit-robustness) |
| Translation quality corpus | [cliff-test/tests/quality](https://github.com/cliff-format/cliff-test/tests/quality) |
| **CLARION benchmark** (format-vs-format) | [cliff-test/BENCHMARK.md](https://github.com/cliff-format/cliff-test/BENCHMARK.md) — summary with graphs of the measured evidence + public data bundle |
| Benchmark data bundle (raw + computed) | [cliff-test/benchmark/clarion-2026-09-02](https://github.com/cliff-format/cliff-test/benchmark/clarion-2026-09-02) |
| Benchmark tooling | [cliff-test/tools/audit_report.mjs](https://github.com/cliff-format/cliff-test/tools/audit_report.mjs) (audit + unified metrics), [cliff-test/tools/qe_score.py](https://github.com/cliff-format/cliff-test/tools/qe_score.py) (reference-free QE), [cliff-test/tools/package_benchmark.py](https://github.com/cliff-format/cliff-test/tools/package_benchmark.py) (public bundle) |

## Third-party implementations

None registered yet. Please submit a PR with a fixture-suite result.