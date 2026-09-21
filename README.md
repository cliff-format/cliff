<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="logos/cliff-wordmark-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="logos/cliff-wordmark-light.svg">
    <img alt="CLIFF: The Contextual Localization Integrated File Format"
         src="logos/cliff-wordmark-light.svg"
         width="50%">
  </picture>

  <p align="center">The Contextual Localization Integrated File Format.</p>

  <p align="center">
    <a href="spec/cliff-1.1.0.md">Specification</a> •
    <a href="style/">Style guide</a> •
    <a href="docs/">Documentation</a> •
    <a href="CONTRIBUTING.md">Contributing</a>
  </p>
</div>


## Overview

CLIFF is a Contextual Localization Integrated File Format, a line-oriented, context-first working file for the whole localization lifecycle. It is designed for both human translators and LLM workflows, solving the usual trade-off between machine-friendly syntax and complete context. CLIFF avoids multi-line closing tags and keeps token cost low, while carrying context from family to group to entry and standardizing tags, widths, and ICU support.

All text in this specification is normative unless otherwise labeled.

## Example

Here is a minimal CLIFF file:

```cliff
CLIFF 1.1
namespace: demo
clan: settings
source-language: en-US
target-language: zh-CN

[Video]
type: label

<Resolution>
source: "Resolution"
target: "分辨率"
type: noun
status: final
```

The four header fields `namespace`, `clan`, `source-language`, and `target-language` are required. Each entry has a stable ID, `source`, `type`, and `status`; group metadata is inherited by entries. Identifiers may use uppercase, digits, `_`, and `-`, are case-sensitive, and are never rewritten by a parser. See the [specification](spec/cliff-1.1.0.md) for the complete syntax.

## Why CLIFF?

CLIFF is built for the whole translation lifecycle and for LLM-driven translation workflows. It addresses common pain points of traditional localization formats:

- **AI-safe syntax**: No multi-line open/close pairs; every construct is a line, so a model or human can add, move, or delete lines without breaking the document.
- **Context-first**: One file is one clan with family-level `info`/`standard`/`dependency`, inherited group context, and per-entry context; translators never work in the dark.
- **Enforced attributes**: Closed, validator-enforced vocabularies for `type`, `emotion`, and `status` turn vague inputs into typed data; `type` and `status` are required on every entry, and `emotion` defaults from `type`.
- **Low token cost**: Short lowercase keys, minimal structural punctuation, no repeated open/close tags, and no per-entry braces make CLIFF cheaper to send to LLMs.
- **Full ICU support**: Unicode MessageFormat MF1 and MF2 are preserved verbatim inside strings; the dialect is auto-detected.
- **Human- and machine-friendly**: Markdown-like readability, tolerant `:` / `=` assignment, an optional trailing `,` / `;`, single-pass parser, and normative ABNF grammar.
- **Your identifiers, your names**: 1.1 defines which characters an identifier may use and stops there — casing, word joining, and file naming are a project style decision ([style guide](style/README.md)), not a conformance requirement.
- **Strict and tolerant parsing**: a strict parser rejects everything the grammar rejects, while a documented tolerant mode ([Appendix C](spec/cliff-1.1.0.md)) repairs the format errors a model actually makes — without ever guessing missing data — and reports every repair.

See the [comparison](docs/comparison.md) and [design rationale](docs/design-rationale.md) for full details.

## Measured evidence

CLIFF claims are not editorial: the separate [cliff-test](https://github.com/cliff-format/cliff-test)
project measures the format against XLIFF, PO, Fluent, JSON, YAML, CSV, Android
and iOS on the same corpus, the same model and the same context payload
(960 real translation calls, 16 documents, 392 entries, public raw evidence and
computed review data):

- **Token cost** — carrying the same context payload, CLIFF's document is the
  smallest of the ten: 47 499 tokens against 52 753 for yaml-cliff and 140 693 for
  csv — 11.1% and 196.2% more than CLIFF respectively, the report's `vs CLIFF`
  column being the other format's excess rather than CLIFF's saving. CLIFF's
  **prompt**, however, is the most expensive in the plain arm and the third most
  expensive in the context arm, because it is the only format whose prompt carries a
  specification block: 2 925 tokens per call, the specification compressed to its
  rules.
- **Context fidelity** — 100% round-trip retention vs 97.6% (PO loses header
  title/info/standard) and 67.3% (plain JSON), over 2 464 context facts and at
  0.00 repairs per round trip.
- **Quality** — on the segments a format delivers, translation quality is identical
  (the format does not change the model): the chrF++ of the answers that parse spans
  53.3–55.7 across all ten formats. *Delivered* is part of the claim — in the
  context arm CLIFF failed 4 of its 48 answers and XLIFF 2.1 failed 10 — and CLIFF's
  advantage is that the context payload is structurally guaranteed and survives
  editing.
- **Single-pass rewrite validity** — asked to translate a whole file in one pass,
  CLIFF returns a valid file in **91.7%** of answers in both arms. Read that column
  within a format's own row rather than across formats: CLIFF's answers are checked by
  the official validator, the strictest checker in the comparison, while the other
  nine only have to parse under theirs. Under those laxer checkers csv's bare arm came
  in at 89.6% and XLIFF 2.1's context arm at 79.2%. After twelve
  sequential model edits of the same file CLIFF is still valid **100.0%** of the time
  bare and **86.1%** context, against XLIFF 2.1's 71.4% / 77.8%.

Summary: [BENCHMARK.md](https://github.com/cliff-format/cliff-test/blob/main/BENCHMARK.md) • public data bundle:
[benchmark/clarion-2026-09-21](https://github.com/cliff-format/cliff-test/tree/main/benchmark/clarion-2026-09-21) •
reference implementation: [cliff-python](https://github.com/cliff-format/cliff-python).

## Contributing

CLIFF follows a specification-first workflow. Contributions are welcome in the normative specification, ABNF grammar, reference validator, conformance fixtures, and documentation.

- Open an issue or pull request with the proposed change.
- Add conformance fixtures before changing the validator or grammar.
- Keep the ABNF grammar and specification in sync.
- Use the `x-` prefix for provisional extension fields until they become standard.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

CLIFF is released under the MIT License, in the same spirit as TOML, YAML, and XLIFF. The format may be freely implemented. See [LICENSE](LICENSE) for the full license text.

The CLIFF logo is Copyright © 2026 CLIFF contributors and is also licensed under the MIT License. See [logos/README.md](logos/README.md).

## Wiki / Documentation

This README is only a starting point. The normative details and extended design material live in the repository:

- [Specification](spec/cliff-1.1.0.md) — the complete normative definition of CLIFF 1.1.
- [CLIFF 1.0](spec/cliff-1.0.0.md) — the superseded but still true 1.0 definition; every 1.0 document is a valid 1.1 document.
- [ABNF grammar](spec/abnf/cliff-1.1.abnf) — the machine-readable normative grammar.
- [Style guide](style/README.md) — recommended identifier and file naming (informative, not enforced).
- [Design rationale](docs/design-rationale.md) — why the syntax is designed this way.
- [AI safety](docs/ai-safety.md) — how CLIFF stays safe under LLM editing.
- [Prompt assembly](docs/prompt-assembly.md) — recommended prompting pattern for translation models.
- [Comparison](docs/comparison.md) — detailed comparison with other localization formats.
- [Implementations](docs/implementations.md) — implementation registry and conformance levels.
- [Standards library](references/standards-library.md) — external standards that CLIFF reuses.
