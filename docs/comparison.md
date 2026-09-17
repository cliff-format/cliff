# CLIFF vs. Common Translation Formats

## Property table

| Property | CLIFF 1.1 | XLIFF 2.1/2.2 | GNU PO | JSON | CSV | Fluent | YAML | TOML |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Structural nesting | flat, line-local | deep, paired tags | flat | deep, braces/brackets | flat | flat-ish (select blocks) | indentation | sections + arrays |
| Closing delimiters at structure level | none (brackets close on one line) | `</...>` everywhere | none | `}`/`]` | none | `}` for select variants | none (indentation) | `]`, `}` |
| Per-entry context | first-class + inheritable | available via `<meta>` | `#.` comments (lossy) | ad hoc | missing | attributes/comments | ad hoc | ad hoc |
| Required content typing (`type`) | ✅ 26 closed tags | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Fixed emotion tags | ✅ 23 tags | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Fixed status tags | ✅ 4 tags, required | ✅ `state` | fuzzy only | ❌ | ❌ | ❌ | ❌ | ❌ |
| ICU MessageFormat | ✅ verbatim MF1/MF2, auto-detected | payload available | partial (plural) | payload available | problematic | own `select` syntax | payload available | payload available |
| Stable source-independent ID | ✅ | ✅ | ❌ (`msgid` = source) | schema-dependent | ❌ | ✅ | schema-dependent | schema-dependent |
| Glossary as data | ✅ `variant: glossary` files + `dependency` | ✅ glossary module (2.2 Part 2) | external | ad hoc | none | `-term` | ad hoc | ad hoc |
| Comment safety | comments inert; data is data | comments are data | **comments carry data** | no comments | no comments | comments are data | comments are data | comments are data |
| Human readability | high | low | medium | medium | low | medium-high | high | high |
| Per-entry LLM token overhead | low | very high | medium | high | low but no context | low-medium | medium | medium |
| Ecosystem tooling (today) | new | mature | mature | universal | universal | mature (Mozilla) | universal | mature |

## Token overhead (relative, structural only)

For a 20-entry UI translation set carrying equivalent semantics:

| Format | Structural tokens (approx.) | Notes |
| --- | --- | --- |
| CLIFF 1.1 | 1× | keys only where information exists |
| CSV (minimal, lossy) | 0.8–1× | loses context, nesting, lists |
| CSV (context-preserving) | ~3× | repeats family/group context per row |
| PO | 1.4–1.5× | comments-as-data plus msgid/msgstr duplication |
| Fluent | 1.1–1.4× | line-oriented but `term`/attribute/select overhead |
| YAML/TOML | 1.3–1.8× | indentation or array brackets |
| JSON | 2.5–2.7× | brackets, quotes, commas per nesting level |
| XLIFF 2.1/2.2 | 2.5–3× | open+close tag per element |

Measured benchmark output is produced by the separate
[cliff-test](https://github.com/cliff-format/cliff-test) project
(`cliff-test/tools/token_benchmark.py`) and written to
`cliff-test/tests/benchmark/report.md`.

## Why not extend one of the existing formats?

- **XLIFF** has the right data model (and 2.2 Part 2 adds the glossary
  module), but its surface syntax is hostile to AI editing. CLIFF borrows its
  concepts (`file/group/unit`, `source/target`, `state`, glossary) and removes
  the paired-tag syntax.
- **PO** is flat and cheap but encodes data in comments and uses source text
  as the identity key.
- **JSON** is universal but structurally fragile under LLM edits, with high
  quote/brace noise.
- **CSV** is cheap but has no grouping, error-prone escaping, and context
  columns degrade into free text.
- **Fluent** is a strong line-oriented runtime/authoring format, but it is
  message-focused rather than workflow-focused: no status model, no canonical
  project IDs, and its `select` is not ICU.
- **YAML/TOML** are good general data languages, but neither defines a
  translation data model; CLIFF's fixed fields *are* the model.

## Interoperability positioning

CLIFF is a **working hub**, not a runtime replacement:

```
XLIFF 2.1/2.2 ⇄ CLIFF 1.1 ⇄ PO / Fluent / JSON / CSV / XLSX (via tools)
```

Normative mappings are specified in
[../spec/cliff-1.1.0.md](../spec/cliff-1.1.0.md) §18.