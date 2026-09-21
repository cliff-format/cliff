# CLIFF 1.1.0 — Contextual Localization Integrated File Format

- **Version:** 1.1.0
- **File extension:** `.cliff`
- **Media type:** `text/vnd.cliff` (provisional, unregistered)
- **Encoding:** UTF-8 (BOM optional), LF preferred, CRLF accepted
- **Normative grammar:** [abnf/cliff-1.1.abnf](abnf/cliff-1.1.abnf)
- **Supersedes:** [cliff-1.0.0.md](cliff-1.0.0.md) — 1.1 is a relaxation of 1.0; every 1.0-conforming document is 1.1-conforming
- **Recommended style:** [../style/README.md](../style/README.md) (informative, not normative)
- **License:** MIT

> CLIFF is the Contextual Localization Integrated File Format. CLIFF is not an
> interchange wrapper around other formats: it is the single lossless
> **working format** for the whole localization lifecycle.

All text in this specification is normative unless otherwise labeled.

---

## 1. Introduction

CLIFF is a **line-oriented, context-first data format for translators**. One
file describes one translation family (`clan`): a coherent body of content
such as all settings text of an application, one act of a game story, a film's
subtitles, or one product catalog.

A CLIFF file carries enough context natively — situation, content type,
emotion, glossary dependencies, translation standards, and width limits — that
a translator (human or LLM) never has to translate in the dark. It is designed
to support **faithfulness, expressiveness, and elegance** ("信达雅", also called the three elements of translation)
throughout the lifecycle: extraction, translation, review, and delivery all
use the same lossless file.

CLIFF is designed for two consumers whose needs usually conflict:

1. **Human translators and localization engineers**, who need rigor,
   type-checkable metadata, fixed vocabularies, and interoperability with
   XLIFF, PO, and Fluent toolchains.
2. **Large language models**, which edit text autoregressively and must never
   corrupt structure by producing unbalanced tags or brackets.

The format therefore uses **only line-local syntax**: every construct is one
line; there are no multi-line open/close pairs in the structural grammar.
Required, closed-set metadata (`type`, `emotion`, `status`) is "enforced
orchestration": it makes translation inputs explicit instead of implicit,
which measurably improves LLM translation quality.

## 2. Goals and objectives

CLIFF exists to:

1. Provide **one lossless, self-contained file format** for the entire
   translation lifecycle — extraction, machine/human translation, review,
   delivery — instead of an interchange-only wrapper (XLIFF) or a runtime
   message format.
2. Put **context first**: situation, content type, emotion, glossary
   dependencies, and translation standards are first-class data, never
   comments, so "faithfulness, expressiveness, and elegance" is an actionable
   target rather than a slogan.
3. Be **optimized for LLM translation workflows**: minimal token cost,
   edit-safe line-local syntax, and enforced structured attributes.
4. Be **easy for humans to read and write**: markdown-like surface habits,
   tolerant `:` / `=` assignment, generous but deterministic whitespace rules,
   and instantly recognizable groups and entries.
5. Be **easy for machines to parse**: a single-pass line parser, an ABNF
   grammar, a reference validator, and a JSON-shaped data model. No parser
   needs a document-level stack.
6. Reuse **existing standards** instead of inventing new ones: BCP 47, XLIFF
   concepts, Unicode MessageFormat (MF1/MF2), UAX #11 display widths, CLDR.
7. **Let each project name its own identifiers.** 1.1 defines which characters
   an identifier may contain and stops there; casing and word-joining habits
   are a project style decision ([../style/README.md](../style/README.md)),
   not a conformance requirement.

### 2.1 Non-goals

- CLIFF is **not a runtime localization engine format**. It is an authoring,
  working, and delivery format; runtimes should consume compiled resources.
- CLIFF does **not store translation memories, revision history, engine
  confidence, dates, or authors**. Those are tool-chain/VCS data.
- CLIFF does **not define UI**. It defines data.
- CLIFF is **not a general serialization format** (unlike YAML/JSON). It has a
  fixed translation data model with a closed field vocabulary.
- CLIFF does **not define a naming convention** for identifiers or files. It
  defines the character set, the uniqueness rules, and the style guide that
  projects are recommended to follow.

## 3. Quick example

```cliff
CLIFF 1.1
namespace: demo
clan: settings
source-language: en-US
target-language: zh-CN
title: "Demo application settings"
info: "End-user UI strings of the demo app; shown in the settings screen."
standard: "Keep UI terms short; do not translate product names."
dependency: ["../shared/terms.zh-CN.cliff", "docs/style-guide.md"]

[video]
context: "Video settings screen."
type: label
emotion: [objective]
max-width: 12

<resolution>
source: "Resolution"
target: "分辨率"
type: noun
emotion: [objective]
status: final

<Fullscreen>
source: "Fullscreen"
target: "全屏"
type: noun
status: reviewed
context: "Toggle label on the video settings screen."
```

The same file is valid for humans (tolerant `=` and whitespace, optional
trailing `,` / `;`) and is canonicalized by any serializer to the form above.

## 4. Conformance

A conforming CLIFF 1.1 document:

1. Is a valid UTF-8 text stream.
2. Matches the grammar in [abnf/cliff-1.1.abnf](abnf/cliff-1.1.abnf) after the
   lexical pre-pass in §5.
3. Satisfies every semantic constraint in §6–§14.

A **strict validator** MUST reject documents that fail syntactic or semantic
constraints. A **tolerant parser** MAY accept unknown `x-` extension keys and
issue warnings; a tolerant parser MAY additionally apply the documented
relaxations of Appendix C, in which case it MUST report every repair it made.

The words MUST, MUST NOT, SHOULD, and MAY are used as in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Normative text is written so
that a conformance suite can decide it: every requirement below states who must
do what, under which condition, and what a violation is observable as.

## 5. Lexical structure

### 5.1 Characters and encoding

Documents are UTF-8 encoded. A leading byte-order mark (U+FEFF) is permitted
and ignored. Unpaired surrogates are invalid. Unicode normalization form is
not enforced; writers SHOULD emit NFC.

### 5.2 Lines

The preferred line ending is LF (`\n`). CRLF is accepted and treated as LF.
A bare CR is invalid.

### 5.3 Whitespace

- Space is U+0020 and tab is U+0009.
- **Tolerant grammar:** leading/trailing whitespace is permitted on version,
  section, entry, field, blank, and comment lines, and around `:` / `=` and
  inside single-line lists. Whitespace never changes meaning, and indentation
  carries no meaning at all: fields may be written flat, with no indentation
  under their entry, exactly like INI and TOML. Blank lines are likewise
  insignificant and may appear anywhere.
- **Canonical form:** no leading or trailing whitespace; exactly one space
  after `key:`; one space between list items; fields written flat with a
  blank line before each entry and each section for readability.
- **Wrapped continuation presentation:** when a long value is wrapped across
  physical lines for human-readable presentation, continuation lines SHOULD be
  indented so their opening quote or bracket aligns with the opening quote or
  bracket of the field value. Indentation remains non-semantic.
- Tabs or spaces are allowed inside quoted strings only as escaped (`\t`) or
  literal U+0020 characters; raw tabs are invalid inside strings and between
  tokens.
- Blank lines contain only whitespace and are ignored anywhere.

### 5.4 Comments

```cliff
# A full-line comment.
# Leading whitespace is allowed.
```

- A comment line starts with optional whitespace followed by `#`.
- There are **no inline comments**. `#` inside a quoted string or after a
  value is data or an error, never a comment.
- Comments are **developer notes only**. They MUST NOT carry information a
  translator needs; a translator MUST be able to delete every comment without
  losing translation context.
- Parsers MUST NOT preserve comments in the data model.

### 5.5 Names and tags

CLIFF 1.1 separates two kinds of bare word. They are different rules because
they answer different questions: a **name** answers "what is this thing
called" (chosen by the project), a **tag** answers "which of the fixed values
is this" (chosen by this specification).

A **name** is an ASCII identifier used for keys, entry IDs, group paths, and
the `namespace` / `clan` header values:

```
name      = name-char *name-char
name-char = ALPHA / DIGIT / "_" / "-"
```

- The character set is exactly: ASCII uppercase letters (`A`–`Z`), ASCII
  lowercase letters (`a`–`z`), ASCII digits (`0`–`9`), underscore (`_`), and
  hyphen (`-`). It is deliberately slightly wider than a conventional
  programming-language identifier: `InvSwordIron`, `inv_sword_iron`,
  `inv-sword-iron`, `Resolution`, and `200` are all names.
- A name MUST contain at least one character. An empty name (`<>`, `[]`) is a
  syntax error.
- A name MUST NOT contain a dot (`.`). The dot is the separator of group paths
  and of canonical IDs (§10.1); forbidding it inside names is what keeps
  `namespace.clan.group-path.entry-id` unambiguous in both directions.
- Names are **case-sensitive**: `Resolution` and `resolution` are two
  different identifiers and two different entries.
- A name MAY begin with a digit, a hyphen, or an underscore (`200`, `_x`,
  `x-` are names). A parser MUST NOT impose a stricter rule than the
  production above; a project that wants a narrower habit follows the style
  guide instead of expecting the validator to enforce it.
- **No case folding, no normalization.** A parser MUST NOT lowercase,
  upper-case, or kebab-case an identifier it read. The identifier is the
  translation match key (§10.3); silently rewriting it would break every
  translation memory that already uses it.

A **tag** is the value of a fixed-vocabulary field (`type`, `emotion`,
`status`, `variant`). Tags are **not** relaxed by 1.1:

```
tag-name = %x61-7A *( %x61-7A / DIGIT / "-" )
```

Tags are lowercase kebab-case ASCII words drawn from the closed sets in §12 and
§13. `type: noun` and `status: final` are tags; `type: Noun` is an invalid tag
and a validator MUST report it as a vocabulary error. Tags stay narrow on
purpose: a closed vocabulary that tolerates spelling variants is not closed, and
the whole value of `type`/`status` is that a near-miss is loud (§12).

A **string** is a single-line string delimited by either double quotes or
single quotes. Both delimiters share identical semantics; the canonical
serializer always emits double quotes:

```cliff
"Resolution"
"Anvil says: \"That is a fine blade.\""
'Anvil says: "That is a fine blade."'
"Line one\nLine two"
```

Recognized escapes:

| Escape | Character | Valid in |
| --- | --- | --- |
| `\"` | U+0022 | double-quoted strings |
| `\'` | U+0027 | single-quoted strings |
| `\\` | U+005C | both |
| `\n` | U+000A | both |
| `\r` | U+000D | both |
| `\t` | U+0009 | both |

All other characters — including `#`, `{`, `}`, `<`, `>`, `[`, `]`, `:`, `=`,
`,`, `;`, and non-ASCII Unicode scalar values — may appear literally inside
strings, except that the closing delimiter itself must be escaped (an
unescaped `"` ends a double-quoted string; an unescaped `'` ends a single-quoted
one). A string MUST NOT contain a raw newline, raw tab, or unescaped control
character. Unknown escape sequences are errors. Note that English apostrophes
(`It's`) are fine inside double-quoted strings and must be written `\'`
inside single-quoted strings.

A **path string** (used by `dependency` and `reference`) is an ordinary quoted
string holding a relative POSIX-style path such as `"../shared/terms.zh-CN.cliff"`
or `"docs/style-guide.md"`. Forward slashes SHOULD be used; consumers MUST
resolve paths safely (see §19).

### 5.6 Line terminators

A version, blank, comment, section, entry, or field line MAY end with **at most
one** optional terminator character, `,` (U+002C) or `;` (U+003B), before any
trailing whitespace:

```cliff
namespace: demo,
[Video];
context: "Video settings.", 
```

Rules:

- A terminator carries **no meaning**. It never separates, joins, changes, or
  truncates anything: the line means exactly what it would mean without it.
- Stripping is defined on the **closing quote**: the terminator is recognized
  only after the whole line's value has been consumed, so a `,` or `;` inside a
  quoted string is ordinary payload. `source: "a,b;"` has the value `a,b;`.
  Likewise the trailing comma inside a list (`emotion: [calm,]`) is the
  list's own optional trailing comma (§6.1) and not a line terminator.
- **At most one** terminator is permitted. `;;`, `,,`, and `, ;` are syntax
  errors, and so is any other trailing punctuation. Accepting one is
  leniency for hand authors and for models that reflexively punctuate;
  accepting a run of them would make the boundary between value and
  punctuation undecidable.
- Writers SHOULD NOT emit terminators, and the canonical serializer MUST NOT
  (§17.6). They exist so that a human or model habit does not become a
  validity error.
- Because the terminator is not part of any value, a parser MUST discard it
  before classifying the line, and MUST NOT report it as a repair.

## 6. Syntax

A CLIFF document contains, in order:

1. A mandatory version line.
2. Header fields.
3. Zero or more sections.

```abnf
cliff-file    = version-line *header-line *section
version-line = *WSP %s"CLIFF" SP ( %s"1.0" / %s"1.1" ) *WSP [ terminator ] *WSP LF
```

The version line MUST be the first non-blank, non-comment line. `CLIFF` and the
version number are case-sensitive; `cliff 1.1` is invalid. The canonical
spelling is exactly `CLIFF 1.1`. A `CLIFF 1.1` implementation MUST accept both
`CLIFF 1.0` and `CLIFF 1.1`, because 1.1 is a pure relaxation of 1.0: every
1.0-conforming document is also 1.1-conforming, and a version-line rewrite
would break that guarantee for no benefit. Implementations MUST reject major
versions they do not support, and MUST reject a minor version they do not
implement (`CLIFF 1.2`, `CLIFF 2.0`) with a message naming the supported
versions.

### 6.1 Fields

```abnf
field-line   = *WSP field *WSP [ terminator ] *WSP LF *continuation-line
field        = key *WSP ( "=" / ":" ) *WSP value
value        = string-value / list / integer / name / language-tag
string-value = string *( *WSP string )
list         = "[" *WSP [ list-items ] *WSP "]"
list-items   = list-item *( *WSP "," *WSP list-item ) *WSP [ "," ]
list-item    = string / integer / name / language-tag
key          = name
```

Rules:

- **Two separators, one meaning.** `key: value` and `key = value` are
  equivalent. The separator is the first `=` or `:` outside a quoted string.
- **Canonical form is `key: value`** — no space before the colon, exactly one
  space after it. Tolerant parsers accept any whitespace around either
  separator.
- **Adjacent strings, C-style, across physical lines.** Any scalar string
  field (`source`, `target`, `title`, `info`, `standard`, `context`,
  `reviewer`, …) MAY continue onto following physical lines as additional
  quoted strings — the continuation lines repeat neither the key nor the
  separator, and may be indented to align under the opening quote:

  ```cliff
  info: "CLIFF is a translator-optimized, context-first data format for"
        "localization. It provides one lossless working file for the whole"
        "translation lifecycle — extraction, translation, review, delivery —"
        "and carries enough native context for faithful, expressive, elegant"
        "translation."
  ```

  Adjacent string literals are concatenated **verbatim, with no inserted
  character** — exactly like C. Writers own any spaces: include a trailing
  space at the end of a line, or a leading space at the start of the next,
  when the text needs one; CJK text typically needs none:

  ```cliff
  info: "CLIFF（Contextual Localization Integrated File Format，读作“cliff”）是一种"
        "面向翻译员优化的语境本地化数据格式。它为整个翻译生命周期（抽取、"
        "翻译、审校、交付）提供单一的无损工作文件格式，并原生提供充足语境"
  ```

  This works for `source` and `target` too; the semantic value is identical
  to one long single-line string, and ICU payloads are preserved. Validators
  apply brace-balance and width checks to the **concatenated** value.

- **List continuation lines.** A list field (`emotion`, `dependency`,
  `reference`, …) may continue on following physical lines as bare lists —
  again no repeated key, and may be indented to align under the opening
  bracket:

  ```cliff
  dependency: ["../terms/terms.zh-CN.cliff"]
              ["docs/act3-script.md", "docs/style-guide.md"]
  ```

  Each `[...]` still opens and closes on the same physical line, so no
  bracket pair ever spans lines. The effective list is the ordered
  concatenation of all fragments. Strings inside a list never continue
  across lines.

- **Continuation rules (strings and lists alike).**

  - A continuation line is a line whose only tokens are quoted strings (for
    a string field) or a single list (for a list field), optionally
    surrounded by whitespace:

    ```abnf
    continuation-line = *WSP ( string-value / list ) *WSP [ terminator ] *WSP LF
    ```

    It attaches to the immediately preceding field; a blank or comment line
    ends the continuation.
  - An orphan continuation line (no preceding compatible field) is a syntax
    error with a line number.
  - The canonical serializer always emits one normalized line per field
    (single string, or one merged list); wrapped forms are a tolerant,
    human-facing presentation that parsers MUST accept and serializers MAY
    normalize away.
  - `\n` inside a string is the only way to produce an actual line break in
    the text value itself.
- A **list** is single-line, may be empty, MAY have one trailing comma, and
  MUST NOT nest another list. List items are strings, integers, names, or
  language tags — never another list.
- **List-typed fields are always written as lists.** `emotion`,
  `dependency`, and `reference` MUST use the `[...]` form even when they
  hold exactly one item (`emotion: [neutral]`, `reference: ["src/ui.cpp:12"]`).
  A bare scalar in a list-typed field is a validity error; there is no
  single-item shorthand. This keeps the value's type readable from the line
  itself and keeps writers from drifting between two spellings of one field.
  (A tolerant parser MAY accept the bare form as a documented relaxation —
  Appendix C.2.1 — in which case it MUST report the repair.)
- **Tags are never quoted.** A scalar value that is a tag (§5.5) is written as
  a bare lowercase word (`status: final`, `type: noun`, `emotion: [calm]`).
  Quoting one turns it into a string and is a validity error. Only text values
  are quoted. (A tolerant parser MAY accept a quoted tag — Appendix C.2.3.)
- **No repeated fields.** Every key MAY appear at most once per scope
  (header, group, entry). Duplicates are validity errors. There is no
  "repeatable field" concept; multi-value data is expressed with lists or
  continuation lines.
- **Trailing `,` / `;`.** A field line may end with one optional terminator
  (§5.6). It does not make the field repeatable, does not continue anything,
  and carries no meaning.
- Unknown keys are **extension fields**. They MUST start with `x-`
  (e.g. `x-engine: "..."`). Strict validators MUST warn about unknown keys and
  MUST NOT reject them. Extension fields are never inherited.

### 6.1.1 The two rules writers get wrong

Every other rule in this section is either obvious or forgiving. These two are
neither, they are the two a hand author or a language model violates first, and
a validator rejects both:

| Wrong | Right | Why |
| --- | --- | --- |
| `emotion: "calm"` | `emotion: [calm]` | a tag is a bare word, and `emotion` is list-typed |
| `emotion: calm` | `emotion: [calm]` | list-typed fields keep their brackets even for one item |
| `type: "label"` | `type: label` | tags are never quoted |
| `status: "final"` | `status: final` | tags are never quoted |
| `reference: "src/ui.cpp:12"` | `reference: ["src/ui.cpp:12"]` | `reference` is list-typed |
| `dependency: "terms.zh-CN.cliff"` | `dependency: ["terms.zh-CN.cliff"]` | `dependency` is list-typed |

The rule behind both rows is one sentence: **the shape of the value tells you
its type, so the shape is not optional.** Brackets mean a list, quotes mean
text, and a bare word means a tag or an identifier. A reader, a diff, and a
validator can all determine the type of a field from the line alone, and no
writer has to remember which fields "also accept" a shorthand.

The three list-typed fields are `emotion`, `dependency` and `reference`.
There are no others, and there is no single-item shorthand for any of them.

### 6.2 Sections and groups

```abnf
section-line = *WSP "[" group-path "]" *WSP [ terminator ] *WSP LF
group-path   = name *( "." name )
```

- A section declares the **current group path** for all following entries
  until the next section or end of file.
- Nesting is expressed by path, never by nested brackets:
  `[video]`, then `[video.advanced]`. Each line carries the complete path, so
  a moved line never becomes ambiguous.
- **Human-friendly layout.** Section lines MAY be indented to *display* the
  nesting depth — two spaces per level, purely cosmetic — and the parser MUST
  ignore that indentation (the path itself remains authoritative):

  ```cliff
  [video]
  context: "Video settings."

  [video.advanced]
  context: "Advanced video settings."
  ```

  Top-level sections SHOULD sit at column 0, nested sections MAY be indented
  two spaces per depth as an optional visual cue, and a blank line SHOULD
  separate every section and every entry. Because there are no closing tags,
  a reader navigates exactly like a Markdown heading outline: the bracket
  path is the heading, the blank line is the paragraph break, and the `<id>`
  marker is the list anchor. Tool UIs SHOULD render groups as a tree from the
  dotted path; serializers MUST never invent a closing marker.
- Section path segments are names (§5.5) and therefore contain no `.`.
- A section path MUST be unique in the file.
- A section line MAY end with one optional `,` or `;` terminator (§5.6).
- Empty groups are permitted.

### 6.3 Group metadata (inherited context)

Immediately after a section line and before the first entry line, a section
MAY contain **group metadata fields**. Only these keys are permitted:

`context`, `type`, `emotion`, `max-width`

Group metadata is inherited by every entry in the section (see §9). Group
metadata lines are written flat like any field; their position before the
first entry line identifies them. Once the first entry line appears, any
later field belongs to that entry until the next section.

### 6.4 Entries

```abnf
entry-line = *WSP "<" name ">" *WSP [ terminator ] *WSP LF
```

- `<resolution>` starts a translation entry; the entry id is the name inside
  the angle brackets, written as a bare name or, equivalently for a tolerant
  parser, as a quoted string (Appendix C.2.4). Angle brackets have exactly one
  structural use in CLIFF: this single-line entry marker. There is no closing
  `</...>` tag, and `<`/`>` inside strings remain ordinary payload characters.
- The entry id is a **name** (§5.5): uppercase letters, digits, `_` and `-` are
  permitted; `.` is not. The id is case-sensitive, so `<Save>` and `<save>` are
  two distinct entries. A parser MUST NOT normalize the id it read.
- Entry lines MAY be re-indented by models; the marker itself is
  authoritative. A terminator MAY follow the closing `>` (§5.6):
  `<resolution>,`
- Entry fields are written flat, with no required indentation; attachment is
  positional (they follow their entry line until the next entry or section
  line). A blank line before each entry is the recommended visual separator.
  Indented entry fields remain valid as tolerant input, but they are not the
  canonical form.
- `source`, `type` (direct or inherited), and `status` are required.
  `target` is optional.
- An `entry-id` MUST be unique within the file.

## 7. Header fields

Header fields appear after the version line and before the first section.

| Key | Type | Required | Repeatable | Meaning |
| --- | --- | --- | --- | --- |
| `namespace` | name | **required** | no | Namespace segment of canonical IDs |
| `clan` | name | **required** | no | Family segment; one file = one clan |
| `source-language` | BCP 47 tag | **required** | no | Source language |
| `target-language` | BCP 47 tag | **required** | no | Target language |
| `version` | string | no | no | Project or source-content version the translations correspond to, e.g. `"1.4.2"`; not the CLIFF spec version |
| `variant` | `standard` / `glossary` | no (default `standard`) | no | File variant; see §13 |
| `title` | string | no | no | Short human-readable family description |
| `info` | string | no | no | Family-level information; may continue across lines (§6.1) |
| `standard` | string | no | no | Translation standards/policies; may continue across lines (§6.1) |
| `dependency` | list of path strings | no | no | Relative paths of prerequisite files (glossaries, style guides, source docs) |

`namespace`, `clan`, `source-language`, and `target-language` are all
required. Authoring plugins and editors SHOULD fill them in automatically, so
hand authors never type them. The file is therefore self-describing no matter
where it travels; the file layout (§11) is a delivery convention that SHOULD
agree with the header, never a substitute for it.

`namespace` and `clan` are names (§5.5): mixing case, using `_`, or starting
with a digit is permitted and is NOT a validity error. A project that wants a
uniform habit follows [../style/README.md](../style/README.md).

`source-language` and `target-language` MUST be valid
[BCP 47](https://www.rfc-editor.org/rfc/bcp/bcp47.txt) language tags.
Comparisons of language tags are case-insensitive per BCP 47. Strict
validators SHOULD validate tags per RFC 5646; a validator MAY use a
documented permissive envelope (letters/digits/hyphens) for well-formedness
while still rejecting invalid constructs such as underscores. When a single
entry uses another language (an Italian idiom in an English file, say), that
fact belongs in the entry's `context`, not in the header.

`info` carries free-form family description prose: conversation setup,
audience, characters, or domain. Only `title`, `info`, and `standard` carry
family prose, because everything else that matters per entry is structured
data on the entry itself.

`version` records the project or source-content version the translations were
made against (the source revision is the one workflow fact that no
translation can be verified without). Creation/modification timestamps and
author names belong to version control, not to the file; tools that need them
out of band MAY use `x-created` / `x-modified` extensions.

Example:

```cliff
CLIFF 1.1
namespace: IronForge-RPG
clan: game
source-language: zh-CN
target-language: en-US
version: "1.4.2"
title: "IronForge RPG — Act 3"
info: "The mountain city of IronForge, one week after the siege." "Anvil is a warm, plain-spoken dwarf blacksmith. Captain Mei is formal in public, warm to friends."
standard: "Preserve proper nouns; localize idioms for humor." "Keep UI labels under the declared max-width."
dependency: ["../terms/ironforge.terms.en-US.cliff", "docs/act3-script.md"]
```

## 8. Entry fields

The **entry ID** is not a field: it is the name in the `<id>` entry marker.
This saves two quote tokens per entry and keeps the ID the only thing an entry
is anchored by.

| Key | Type | Required | Repeatable | Inherited from group | Meaning |
| --- | --- | --- | --- | --- | --- |
| `source` | string | **required** | no | no | Source-language text; may contain ICU |
| `target` | string | no | no | no | Target-language text; may contain ICU |
| `type` | type tag | **required (direct or inherited)** | no | **yes** | Content/grammatical type of the text; see §12.1 |
| `emotion` | emotion list | no | no | **yes** | Emotion/delivery tags; default depends on `type`; see §12.2 |
| `status` | status tag | **required** | no | no | Translation status; see §12.3 |
| `context` | string | no | no | **yes** | Situation of this entry; group value then entry value are joined; may continue across lines (§6.1) |
| `max-width` | integer > 0 | no | no | **yes** | Maximum rendered display width in cells |
| `reference` | list of path strings | no | no | no | Source references, e.g. code or document locations. Always a list, even for one item; may continue as bare lists (§6.1) |
| `reviewer` | string | no | no | no | Latest human reviewer identifier |

Additional `x-` extension keys are permitted under the rule of §6.1.

Notes:

- `target` is optional so extraction and translation phases share one format.
  A writer MUST set `target` before declaring `status: translated`,
  `reviewed`, or `final`.
- `emotion` is optional because its default is derived from `type`. Writing it
  explicitly is still encouraged for dialogue and idioms. When written, it is
  always a list — `emotion: [neutral]`, never `emotion: neutral` (§6.1).
- **`speaker`, `listener`, and `scene` are not CLIFF fields.** When `type` is
  `dialogue`/`monologue`, the translator already knows someone is speaking;
  *who* is speaking belongs in `context` (e.g. `context: "Anvil speaks to the
  player at the forge."`). CLIFF deliberately does not provide an optional
  structured speaker field: an optional field would be ignored exactly as
  often as `context` is, while adding schema surface without adding
  guarantees.
- There is **no `format` field.** MessageFormat dialect is auto-detected; see
  §14.

## 9. Group inheritance

For an entry `E` in section path `G`:

- `context`: the effective context is the group `context` value followed by
  the entry `context` value, joined with a single space when both exist.
- `type`: the entry value overrides the group value; at least one of the two
  MUST exist.
- `emotion`: the entry value overrides the group value. Lists do not merge.
- `max-width`: the entry value overrides the group value.
- All other entry fields are never inherited.

```cliff
[video]
context: "Video settings screen."
type: label
emotion: [objective]
max-width: 12

<resolution>
source: "Resolution"
target: "分辨率"
status: final

<brightness>
source: "Brightness"
target: "亮度"
max-width: 8
status: reviewed
```

## 10. Canonical identifiers, keys, and engine adaptation

### 10.1 Names and uniqueness

- `namespace`, `clan`, group path segments, and entry IDs are names (§5.5) and
  MUST NOT contain `.`. The character set is `A–Z a–z 0–9 _ -`; casing,
  underscores, leading digits, and leading or trailing hyphens are all
  permitted and are not errors.
- Casing is significant, not conventional: a validator MUST NOT treat
  `Save` and `save` as the same entry, and MUST NOT fold either.
- The canonical ID of an entry in section `G` is:

```
namespace.clan.G.entry-id
```

Example: `namespace: demo`, `clan: settings`, section `[video.advanced]`,
entry `resolution` → `demo.settings.video.advanced.resolution`. With
`namespace: IronForge-RPG`, section `[Video.Advanced]`, entry `Fullscreen` →
`IronForge-RPG.game.Video.Advanced.Fullscreen`.

- Canonical IDs MUST be unique within the file. They SHOULD be unique within a
  translation project; tools SHOULD reject collisions across files.
- Writers SHOULD choose stable, human-readable IDs and MUST NOT change them
  merely because the source text changed. The ID is the translation match key.
- Writers SHOULD follow the project's style guide for the *shape* of an ID
  (see [../style/README.md](../style/README.md)). Style is a recommendation:
  a validator MUST NOT reject a document because its IDs are PascalCase,
  snake_case, or mixed.

### 10.2 Duplicate entry IDs — parser behavior

A duplicate `entry-id` (and therefore a duplicate canonical ID) is a
**validity error**. A strict validator MUST reject the file and report:

- the line number and text of each conflicting `entry` line,
- both conflicting canonical IDs,
- the error category `id`.

A tolerant parser MUST NOT silently overwrite one entry with the other; it
MUST surface the same error. This is deliberate: silent last-wins behavior is
exactly how translation data gets lost, and a one-line error is cheaper than a
missing string at runtime. A tolerant parser MAY apply the documented
disambiguation of Appendix C.2.5, which renames the later entry and reports the
rename — never silently.

### 10.3 Key vs ID

| Concept | CLIFF term | Meaning |
| --- | --- | --- |
| Entry ID | `<id>` entry marker | The stable, human-readable identifier inside the file. It is part of the canonical ID and is the translation match key. |
| Translation key | canonical ID | The globally unique key a tool uses to look up a unit across files, glossaries, and translation memories: `namespace.clan.group.entry`. |
| Engine key | (mapping) | The string an engine or runtime resource uses at run time (a hash, a path, a numeric index). It is NOT stored in CLIFF. |

CLIFF deliberately has **no separate `key` field**: two identity systems in one
file would drift. If an engine cannot use the canonical ID directly, the
converter owns the mapping and may emit it out of band (a `.map.json` or the
engine's own resource format). A hash ID may be *globally unique*, but it is
meaningless to a reviewer and brittle to regenerate; CLIFF keeps meaningful
IDs in the file and lets engines keep their hashes in their own resources.

Because 1.1 permits mixed case, an importer that must fold foreign identifiers
(e.g. a JSON key `InvSwordIron` into an ID) SHOULD preserve the source spelling
when it is already a valid name, and MUST report any identifier it had to
rewrite.

### 10.4 Game-engine and app adaptation

| Engine / pipeline | What it wants | CLIFF adapter rule |
| --- | --- | --- |
| Minecraft / lang files | flat `key=value` | flatten canonical ID → `namespace.clan.group.entry` (or a configured prefix + `group.entry`); preserve the key on re-import so IDs stay stable |
| Unreal (Localization Dashboard) | `namespace, key` inside culture folders | map canonical ID → UE `namespace`/`key` (e.g. namespace = `clan`, key = `group.entry`); `target-language` selects the culture folder |
| Unity (I2 Localization / string tables) | `term` = key | use canonical ID as the term; entry `type` can drive gender/plural handling |
| Godot / CSV importer | `key, source, target` columns | key column = canonical ID |
| Web/i18n JSON (i18next etc.) | nested or dotted keys | flatten to dotted canonical ID, or nest `namespace.clan.group` then `entry` |

Converters MUST keep the mapping deterministic in both directions so
re-extraction and re-import do not regenerate keys. A converter that folds case
MUST do so only when the target format requires it, and MUST report every
renamed identifier.

## 11. File layout and naming

The layout and the file name are **recommendations**, not conformance
requirements of CLIFF 1.1. A document is valid no matter what its file is
called or which directory holds it; the header (§7) is what identifies it. The
guidance below is what projects SHOULD do, and it is restated in
[../style/README.md](../style/README.md).

### 11.1 Folder layout (recommended)

```
<target-language>/<clan>.cliff
```

Examples: `zh-CN/settings.cliff`, `en-US/act3.cliff`, `ja-JP/terms.cliff`.

This is the **recommended layout** for projects with more than one target
language. It follows the Unreal Engine convention of one directory per
language: a Japanese translation team checks out and delivers `ja-JP/`, the
Spanish team `es-ES/`, CI jobs scope their diffs to one directory, and a
language pack is simply that directory zipped. A large project with many
clans therefore reads as "one folder per language, one file per clan" instead
of hundreds of mixed files in one directory.

### 11.2 Flat layout (allowed for small projects)

```
<clan>.<target-language>.cliff
```

Examples: `settings.zh-CN.cliff`, `act3.en-US.cliff`, `terms.zh-Hant-TW.cliff`.

The flat layout is convenient for single-language repositories and small
tools; it remains fully valid. A single-language project is never forced to
create a language folder.

### 11.3 Consistency rules (checked as recommendations)

The header is authoritative: `namespace`, `clan`, `source-language`, and
`target-language` are required fields (§7). The layout is a delivery
convention that SHOULD agree with the header; it never supplies missing header
values, and a mismatch never makes a document invalid.

- `<clan>` in a file name SHOULD be spelled exactly as the `clan` header value,
  and `<target-language>` SHOULD be the BCP 47 tag of the target language in
  canonical casing (`en-US`, `zh-Hant-TW`); comparison is case-insensitive.
- A validator SHOULD check the layout against the header and report a
  **warning** when they disagree. A validator MAY offer an opt-in strict mode
  that reports the same finding as an error, for projects that keep the
  convention mandatory in their own CI. Which mode applies MUST be explicit,
  never accidental.

  1. **Folder candidate:** if the file's immediate parent directory name is a
     language tag whose primary subtag is 2–3 letters, optionally followed by
     `-` subtags of letters/digits (e.g. `en`, `ja-JP`, `zh-Hant-TW`), the
     directory SHOULD equal the header `target-language` (case-insensitive) and
     the file name (minus `.cliff`) SHOULD equal the header `clan`. Directory
     names that merely look word-like (`valid`, `quality`) are not language
     tags.
  2. **File-name candidate:** otherwise, a file name matching
     `<clan>.<target-language>.cliff` SHOULD equal the header values.
  3. If both candidates exist, both SHOULD agree with the header and with each
     other.
  4. A file whose name and parent directory do not match either shape is still
     valid when the four required header fields are present (e.g. a generated
     file such as `corpus.cliff`); the layout check simply does not apply.
  5. Any mismatch is reported as a **warning** in the default mode described
     above.
- Editors and plugins SHOULD create files in the folder layout when a project
  has more than one target language, and in the flat layout otherwise.

## 12. Fixed vocabularies

Fixed tag sets are **closed**. Values not listed below are validity errors.
Closed sets exist so an AI cannot silently invent a slightly different tag and
so tooling can type-check every field. Tag values are lowercase kebab-case
(`tag-name`, §5.5) — a differently-cased spelling of a listed value
(`Final`, `NOUN`) is a vocabulary error, not an alias.

### 12.1 Type tags (`type`)

`type` classifies the grammatical or functional kind of text. Definitions and
translation guidance: [references/content-types.md](../references/content-types.md).

Word-level:

```
noun, verb, adjective, adverb, pronoun, numeral, preposition, conjunction,
particle, interjection, proper-noun
```

Phrase-level:

```
noun-phrase, verb-phrase, adjective-phrase, adverb-phrase, fixed-phrase, idiom
```

Text/function-level:

```
sentence, description, narration, dialogue, monologue, prompt, label,
subtitle, accessibility-cue
```

- `fixed-phrase` covers compound names and fixed multi-word terms such as
  "The Block of Grass"; `proper-noun` covers named entities.
- `narration` is story/voice-over narration; `dialogue` is spoken exchange;
  `monologue` is a character's inner thought.
- `prompt` is UI guidance or tooltip text; `label` is a short UI label or
  menu item.
- `accessibility-cue` is a caption shown for accessibility, e.g. a
  sound-effect cue for deaf/hard-of-hearing viewers ("[door creaks]").
- `type` is required per entry, but may be inherited from the group to keep
  token cost low for homogeneous sections.

### 12.2 Emotion tags (`emotion`)

`emotion` accepts one or more of the 23 tags defined in
[references/emotion-tags.md](../references/emotion-tags.md):

```
neutral, objective, mechanical,
joyful, sad, angry, fearful, surprised, curious, disgusted,
anxious, calm, playful, serious, urgent, romantic, hopeful,
grateful, formal, informal, polite, rude, nostalgic
```

The value is always a list, one or more tags long: `emotion: [neutral]`,
`emotion: [surprised, playful]`. A bare tag (`emotion: neutral`) is a
validity error (§6.1).

Defaults (when `emotion` is omitted):

| Effective `type` | Default emotion |
| --- | --- |
| `dialogue`, `monologue`, `idiom` | `[neutral]` |
| every other type | `[objective]` |

- `objective` = matter-of-fact, informational (narration, labels, nouns).
- `mechanical` = deliberately emotionless machine/robot delivery; use it
  explicitly, it is never a default.
- Explicit `emotion` always overrides the default.

### 12.3 Status tags (`status`)

`status` is required on every entry and is identical to the XLIFF 2.x state
model:

```
initial, translated, reviewed, final
```

| Tag | Meaning |
| --- | --- |
| `initial` | No target text yet (extraction state) |
| `translated` | Target text exists; not yet human-reviewed |
| `reviewed` | Target text has passed review |
| `final` | Locked for release |

State machine and constraints: [references/status-tags.md](../references/status-tags.md).
`translated`, `reviewed`, and `final` require a `target` field; `target` may
be omitted only with `status: initial`.

## 13. Variants: standard and glossary

`variant` selects the file's specialized shape. The grammar is identical for
both variants; only semantics change.

### 13.1 `standard` (default)

A translation-unit file. It MUST have at least one entry.

### 13.2 `glossary`

A **terminology file**: canonical translations of dedicated terms, compound
nouns, fixed phrases, and idioms (e.g. "The Block of Grass").

A glossary is a normal CLIFF document. It differs from a `standard` file in one
way only: **every entry is a term, not a segment of running text**. The grammar,
the field vocabulary and the validation rules are identical.

#### 13.2.1 Shape

- Header: `variant: glossary`.
- Each entry holds one term: `source` = source term, `target` = canonical
  translation, `type` = its grammatical kind, `status` = workflow state.
- `type` SHOULD be one of the term-level tags: `noun`, `verb`, `adjective`,
  `adverb`, `pronoun`, `numeral`, `preposition`, `conjunction`, `particle`,
  `interjection`, `proper-noun`, `noun-phrase`, `verb-phrase`,
  `adjective-phrase`, `adverb-phrase`, `fixed-phrase`, `idiom`. A strict
  validator warns for other types.
- `target` SHOULD be present; a strict validator warns when it is missing.
- `context` SHOULD record **why** this rendering was chosen, because a term
  without its reason is re-litigated at every review.
- The `clan` of a glossary SHOULD be the clan it serves with the suffix
  `-terms` (`settings` → `settings-terms`), so the file name follows §11
  without a new convention: `settings-terms.zh-CN.cliff`, or
  `zh-CN/settings-terms.cliff` in the folder layout. A glossary shared by a
  whole project SHOULD use the clan `terms`.
- Term files are referenced from `standard` files via `dependency`, e.g.
  `dependency: ["../terms/terms.zh-CN.cliff"]`.

#### 13.2.2 Lifecycle: a glossary is produced, not only consumed

Most projects do not start with a glossary. Terminology decisions are made
**while translating** — the first time a product name, a character name, a
recurring interface word or a domain term has to be rendered — and they are
lost unless they are written down at that moment.

CLIFF therefore treats the glossary as a **deliverable of translation**, not
merely as an input to it:

1. A translator (human or machine) that makes a term decision while translating
   a `standard` file SHOULD record it in a `variant: glossary` file for that
   clan, creating the file when it does not exist.
2. A translation task MAY therefore be answered with **two documents**: the
   translated `standard` file and the glossary file. Producing a glossary is
   never a violation of a "return one file" instruction; producing an empty or
   invented glossary is a defect.
3. A term belongs in the glossary when it recurs, names something (product,
   feature, character, place, faction), is a fixed phrase or idiom, or was a
   judgement call another translator could reasonably decide differently. A
   sentence that occurs once does not belong in a glossary.
4. **A glossary is not always warranted, and MUST NOT be created reflexively.**
   The default is no glossary. It is warranted when the family's `standard` or
   `info` asks for terminology consistency or a naming policy, when the clan is
   large enough that a term recurs across entries, or when a naming judgement
   would otherwise be re-made differently by the next translator. A short file
   of a few dozen strings whose terms occur once needs none, and producing one
   there adds a file to maintain without adding a decision to remember.
5. The rendering recorded MUST be the rendering actually used in the translated
   file. A glossary that disagrees with its own translation is worse than none.
6. When merging into an existing glossary, an entry whose `status` is
   `reviewed` or `final` MUST NOT be overwritten. A conflicting proposal is
   reported to a human, not applied.
7. The `standard` file SHOULD gain a `dependency` entry pointing at the
   glossary, so every later translation of that clan receives the decisions
   automatically.

#### 13.2.3 Why this belongs in the format

Terminology consistency is the failure mode of every large localization
project, and the usual remedies live outside the file: a spreadsheet, a
translation-memory server, a reviewer's memory. Because a CLIFF glossary is an
ordinary CLIFF document, it is validated by the same validator, diffed by the
same tools, reviewed in the same pull request, and attached by one
`dependency` line. That is what makes "the glossary is part of the working
file set" true in practice rather than in principle.

```cliff
CLIFF 1.1
namespace: studio
clan: terms
source-language: zh-CN
target-language: en-US
variant: glossary
title: "Studio terminology"
standard: "Canonical translations; dialect-specific files may override."

[items]
type: noun-phrase

<BlockOfGrass>
source: "草方块"
target: "The Block of Grass"
type: fixed-phrase
status: final
context: "Minecraft-style building block; the article must be preserved."
```

## 14. ICU MessageFormat support

CLIFF stores ICU MessageFormat syntax **verbatim** inside `source` and
`target` strings. It is payload, never CLIFF structure.

- MessageFormat 1: `{count, plural, ...}`, `{gender, select, ...}`.
- MessageFormat 2: `.input`, `.local`, `.match`, and `{{...}}` placeholders.
  MF2 is the preferred dialect for new content (it is stable in CLDR 47); MF1
  remains accepted for legacy content.

There is **no `format` field**. Tools MUST auto-detect the dialect per string:

1. If the string contains MF2 syntax markers (`{{`, `}}`, `.match`, `.input`,
   `.local`), it is MF2.
2. Else if it contains `{...}`, it is MF1.
3. Else it is plain text.

Validators MUST verify brace balance in any string containing `{` or `}` and
SHOULD reject obviously malformed ICU. A broken ICU expression is a local
string error, never a document-level corruption.

## 15. Display width (`max-width`)

`max-width` is the maximum number of **display cells** of the rendered target
text, not a character count.

| Character class (UAX #11) | Cells |
| --- | --- |
| East Asian Wide (`W`) or Fullwidth (`F`) | 2 |
| East Asian Narrow (`Na`), Neutral (`N`), Halfwidth (`H`) | 1 |
| East Asian Ambiguous (`A`) | 1 |
| Combining marks (Mn, Mc, Me), variation selectors, zero-width characters | 0 |
| Emoji with default emoji presentation | 2 |
| An emoji ZWJ sequence, counted once as a whole | 2 |

Width is counted over **rendered glyphs**, not over code points. A character
that carries default emoji presentation, or a text-presentation symbol
followed by variation selector 16 (U+FE0F), occupies 2 cells. An emoji ZWJ
sequence renders as a single glyph and therefore counts **2 cells in total**,
not 2 cells per member: `"👩‍💻"` (U+1F469 U+200D U+1F4BB) is 2 cells, because
the ZWJ and the joined members contribute nothing beyond the one glyph they
form.

Examples: `"分辨率"` = 6 cells, `"OK"` = 2 cells, `"OK 分辨率"` = 9 cells,
`"👩‍💻"` = 2 cells, `"e\u0301"` = 1 cell.

The constraint applies to the **rendered** target. For ICU messages, tools
MUST evaluate each variant with representative argument values.

## 16. Dependencies

`dependency` is a single-line list of quoted **relative paths**, resolved
against the directory containing the file:

- prerequisite CLIFF families — commonly `variant: glossary` term files;
- non-CLIFF reference material (markdown scripts, style guides, design docs).

```cliff
dependency: ["../terms/terms.zh-CN.cliff", "docs/act3-script.md"]
```

Paths use `/` separators. `..` is permitted. Consumers MUST treat paths as
untrusted and resolve them inside the project sandbox (see §19). A translator
or LLM given a file SHOULD also be given the referenced files.

## 17. Serialization (canonical form)

A canonical serializer MUST:

1. Emit `CLIFF 1.1` as the first line when it is writing a new document. When
   it is round-tripping a document that declared `CLIFF 1.0`, it MUST preserve
   the declared version rather than silently upgrading the file's declared
   spec version.
2. Emit the four required header fields `namespace`, `clan`,
   `source-language`, `target-language`, then `version` (when present),
   `variant` (only when `glossary`), `title`, `info`, `standard`,
   `dependency` in that order.
3. Emit sections and entries in authored order (order is contextual).
4. Put one blank line before each section and before each entry. Section
   lines MAY be indented per path depth as an optional human cue, but
   indentation carries no meaning.
5. Emit entry fields and group metadata flat, with no indentation.
6. Use `key: value` with exactly one space after the colon; no trailing
   whitespace; single spaces inside lists. **A canonical serializer MUST NOT
   emit a trailing `,` or `;` terminator (§5.6)**, even when the input carried
   one: the terminator is tolerated input, never canonical output.
7. Emit identifiers exactly as the data model holds them. A canonical
   serializer MUST NOT change the case, add or remove `_`, or otherwise
   "tidy" an identifier; if a project wants a canonical identifier style, that
   is a separate, opt-in normalization step (see
   [../style/README.md](../style/README.md)), not part of CLIFF
   serialization.
8. Use LF line endings, UTF-8 without BOM, and the minimum escaping necessary.
9. A serializer that also chooses a file name SHOULD place the file at
   `<target-language>/<clan>.cliff` when the project has more than one target
   language, and MAY use the flat name `<clan>.<target-language>.cliff` for
   single-language projects (§11).

## 18. Interoperability

CLIFF is a working format; converters to/from other formats are expected but
need not be lossless in the other direction.

| CLIFF 1.1 | XLIFF 2.1/2.2 | gettext PO | Fluent |
| --- | --- | --- | --- |
| file | `<xliff>` with one `<file>` | one `.po` file | one `.ftl` resource |
| `namespace`/`clan` | project metadata + `<file original>` | header metadata | resource naming |
| section path | nested `<group id>` | `msgctxt` convention | grouping by file |
| entry | `<unit id>` | `msgid` block | message / term |
| `source` / `target` | `<source>` / `<target>` | `msgid` / `msgstr` | value |
| `type` | `<metaGroup category>` or ITS metadata | extracted-comment convention | attribute |
| `emotion` | annotations metadata | `#.` comment (lossy) | attribute |
| `status` | `state` attribute | fuzzy flag subset | not applicable |
| `context` | `<metadata>` + ITS | `#.` (lossy) | comment/attribute |
| glossary | XLIFF 2.2 glossary module (`variant: glossary`) | external glossary | term with attributes |
| ICU in strings | inline payload | inline | Fluent select/placeholders |

Converters from PO MUST materialize PO metadata comments into explicit CLIFF
fields (`reference`, `context`). Converters from XLIFF SHOULD preserve
`<group>` nesting as dotted section paths and SHOULD map XLIFF 2.2 glossary
modules to `variant: glossary` files. Converters SHOULD preserve an identifier
that is already a valid CLIFF name (§5.5) verbatim, and MUST report every
identifier they had to rewrite to fit the target format.

## 19. Security considerations

- CLIFF documents may contain arbitrary strings; consumers MUST treat them as
  untrusted data and MUST NOT evaluate them (except an explicitly requested
  ICU formatter).
- Strings may contain literal `<` and `>`; UI layers must escape HTML as
  usual.
- `dependency` and `reference` paths are attacker-controlled. Resolve them
  inside an explicit project root and reject escapes outside it.
- Implementations MUST enforce resource limits so a hostile or corrupt
  document cannot exhaust memory or time. The limits MUST apply in both strict
  and tolerant modes, MUST be documented by the implementation, and MUST be
  configurable. At minimum an implementation MUST bound:
  - the file size,
  - the length of a single line,
  - the length of a single decoded string,
  - the number of path segments in a group path,
  - the number of items in a list,
  - the number of entries in a document.
  A document that exceeds a limit MUST be rejected with a diagnostic that
  carries the line number and names the limit and the observed value, never
  truncated silently.

## 20. Extension fields

Unknown keys are permitted only as `x-` prefixed names, at header, group, and
entry level. Extensions:

- MUST be ignored by parsers that do not understand them;
- MUST never be inherited;
- MUST NOT change the meaning of standard fields;
- are warned about by strict validators.

A future minor revision may promote a widely used `x-` field into the core
only if it is generic and has a fixed vocabulary.

## 21. Versioning

The version line declares the supported specification series: `CLIFF 1.0` and
`CLIFF 1.1` both identify the 1.x series; this specification document is
1.1.0. Implementations MUST reject major versions they do not support and MUST
reject a 1.x minor version they do not implement.

1.1 is a **pure relaxation** of 1.0. Every document that conforms to
[cliff-1.0.0.md](cliff-1.0.0.md) also conforms to this specification; 1.1 adds
no new requirement that a previously valid document can violate. Concretely:

| Area | 1.0 | 1.1 |
| --- | --- | --- |
| Identifier character set (`name`) | `[a-z][a-z0-9-]*` | `[A-Za-z0-9_-]+`, no `.` |
| Tag spelling (`tag-name`) | lowercase kebab-case | unchanged |
| Line terminators | none | one optional trailing `,` / `;` (§5.6) |
| File layout and file name | MUST agree with the header | SHOULD agree; mismatch is a warning by default (§11.3) |
| Version line | `CLIFF 1.0` only | `CLIFF 1.0` or `CLIFF 1.1` |
| Resource limits | required, unspecified | required and enumerated (§19) |
| Identifier style | enforced by the grammar | recommended only ([../style/README.md](../style/README.md)) |

Because the relaxation is one-directional, a 1.0-only validator will reject
1.1 documents that use the new liberties; that is expected, and it is why the
version line exists. Implementations that must interoperate with 1.0-only
tooling SHOULD follow the style guide, which stays inside the 1.0 grammar.

## Appendix A. Normative references

- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — Key words for use in RFCs
- [BCP 47 / RFC 5646](https://www.rfc-editor.org/rfc/bcp/bcp47.txt) — Tags for Identifying Languages
- [XLIFF 2.1](https://docs.oasis-open.org/xliff/v2.1/os/xliff-core-v2.1-os.html) — XML Localisation Interchange File Format
- [XLIFF 2.2 Part 2: Extended](https://docs.oasis-open.org/xliff/xliff-core/v2.2/cs01/xliff-extended-v2.2-cs01-part2.html) — glossary and annotations modules
- [Unicode TR35 Part 9 — MessageFormat](https://www.unicode.org/reports/tr35/tr35-messageFormat.html)
- [Unicode UAX #11 — East Asian Width](https://www.unicode.org/reports/tr11/)
- [Unicode CLDR](https://cldr.unicode.org/)
- [GNU gettext PO Files](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html)
- [Fluent 1.0](https://projectfluent.org/) — localization system for natural-sounding translations
- [RFC 5234](https://www.rfc-editor.org/rfc/rfc5234) — ABNF
- [RFC 7405](https://www.rfc-editor.org/rfc/rfc7405) — Case-sensitive strings in ABNF

## Appendix B. Data model (informative)

```
file ── header: namespace, clan, source-language, target-language,
│                version, variant, title, info, standard, dependency
├── [a] ── metadata: context, type, emotion, max-width
│   ├── <entry-id> ── source, target, type, emotion, status,
│   │                 context, max-width, reference, reviewer
│   └── ...
└── [a.b] ...
```

The JSON-shaped model is intentionally representable by any tool:
`{header, groups: [{path, metadata, entries: [...]}]}`. Canonical ID
`namespace.clan.group-path.entry-id` is the join key across files, tools, and
translation memories.

## Appendix C. Tolerant parsing (normative)

Cliff 1.1 defines a **tolerant parsing mode** for one specific consumer: an
automated translation pipeline that must not lose a translation because a model
punctuated a line differently. This appendix is normative for any tool that
advertises tolerant parsing, so that two independent tolerant parsers agree.

### C.1 Relationship to strict parsing

- Tolerant parsing is a **superset of the strict grammar**: every document that
  parses strictly also parses tolerantly, and produces the same data model.
- Strict parsing is unchanged by this appendix. A tool MUST be able to run in
  strict mode, and strict mode MUST reject everything the strict grammar
  rejects.
- Tolerant parsing is **not** a new surface syntax: it does not change the
  ABNF, does not introduce a construct that a strict parser must learn, and
  introduces no multi-line structure. Its output is always a document that is
  valid under the strict grammar.
- Tolerant parsing is **opt-in**. A parser MUST NOT apply it by default, and
  the mode in effect MUST be observable by the caller.

### C.2 Permitted relaxations

A tolerant parser MAY accept the following seven deviations. For each, the
required result and the required diagnostic are given.

1. **A list-typed field written as a bare scalar.**
   Trigger: `emotion: objective`, `dependency: "../shared/terms.zh-CN.cliff"`,
   `reference: "src/ui.cpp:12"`.
   Result: the value is treated as a one-item list; if the scalar is quoted,
   the quotes are removed and the text is the item; if the scalar is a
   comma-separated series, each comma-separated item is one list item.
   Diagnostic: category `list-shape`, with the line and both spellings.

2. **A field repeated in one scope.**
   Trigger: the same key twice under one header, group, or entry.
   Result: a scalar string field is concatenated in source order using the
   C-style rule of §6.1 (no inserted character); a list field is extended in
   source order using the list-continuation rule of §6.1. The effective value
   is therefore identical to what the equivalent continuation lines would have
   produced.
   Diagnostic: category `field-repeat`, naming the key and every line it
   appeared on.

3. **A quoted tag.**
   Trigger: `status: "final"`, `emotion: ["calm"]`, `type: 'label'`.
   Result: the quotes are removed and the enclosed word is validated against
   the closed vocabulary of §12 exactly as a bare tag would be. The vocabulary
   remains closed: a value outside it is an error (§C.5), and so is a value
   whose only correction would be a spelling guess.
   Diagnostic: category `tag-quote`.

4. **A quoted entry ID.**
   Trigger: `<"resolution">`, `<'resolution'>`.
   Result: identical to the bare form `<resolution>`. Angle brackets retain
   exactly one structural use (§6.4) and there is still no closing tag.
   Diagnostic: category `name-quote`.

5. **An identifier containing a reserved character.**
   Trigger: an entry ID, group segment, `namespace`, or `clan` that contains a
   character outside `name-char` (§5.5) — for example a space, `&`, `/`, `+`,
   or a dot that was meant as a path separator.
   Result: the identifier is normalized by the algorithm in §C.3, and the
   canonical ID is then subject to §C.4.
   Diagnostic: category `name-normalized`, carrying the original and the
   normalized identifier.

6. **A version line that differs in spelling only.**
   Trigger: `CLIFF 1.1.0`, `cliff 1.1`, `CLIFF 1.1 `.
   Result: the document is read as the corresponding minor version. The
   version number is not guessed from content.
   Diagnostic: category `version`.

7. **A quoted key.**
   Trigger: `"context": "…"`, `'status': final`, `"source" = "Sign in"`.
   Result: the quotes are removed and the enclosed text is read as the key,
   under exactly the scope rules a bare key faces. The enclosed text MUST be a
   `name` (§5.5): escape sequences are not processed, and a character outside
   `name-char` is not accepted. **The key sets are unchanged.** A quoted word
   that is not a legal key in that scope is an unknown key and therefore an
   error (§C.5); the quotes never make an unknown key legal, and never move a
   key into a scope that does not allow it.
   Diagnostic: category `name-quote`, with the line and both spellings.

Relaxation 7 is decided before the continuation rules of §6.1: a line whose
first non-whitespace token is a quoted name followed, after optional whitespace,
by `:` or `=`, is a field line. A line that instead consists only of quoted
strings is still a continuation line. The relaxation applies to header, group
metadata and entry fields; the version line, section lines and entry lines carry
no key and are unaffected. Nothing about the strict grammar changes, because there
was never a rule to change: a quoted key is not a `name` (§5.5) and §6.1 states no
case in which the quotes would be well formed, so §6.1 needs no clause about them
and this appendix adds none. The repair's result is identical to the bare key, so
the canonical form of §Serialization is unchanged as well: a serializer emits keys
bare, and the quoted form exists only as an input relaxation.

Relaxations deliberately **not** in this list: trailing `,` / `;` (that is
standard syntax since 1.1, §5.6, and MUST NOT be reported as a repair), bare
`entry <id>` / `entry: <id>` legacy markers, a list that spans lines, and any
messy-but-recoverable line (see §C.5).

### C.3 Identifier normalization

A tolerant parser MUST normalize an identifier that violates §5.5 with this
deterministic procedure, and no other:

1. Apply Unicode NFKC normalization.
2. Strip leading and trailing whitespace.
3. Replace every run of whitespace with a single `-`.
4. Replace every character that is neither whitespace nor `name-char` (§5.5)
   with `-`.
5. Collapse a run of `-` into a single `-`.
6. Strip leading and trailing `-`.
7. If the result is empty, use the scope's fallback name (`entry`, `group`,
   `ns`, `clan`).

The procedure MUST be applied to a **violating** identifier only. An identifier
that is already a valid name MUST be preserved byte-for-byte even when it does
not match the recommended style: `bad_id`, `BadID`, and `200` are left alone,
because style is a recommendation (§10.1), not a repair. Two runs of the same
tolerant parser on the same input MUST produce the same identifiers.

### C.4 Collision handling

After normalization, group paths and canonical IDs (`§10.1`) MUST be unique.
A tolerant parser MUST NOT resolve a collision by dropping or overwriting data
(§10.2). It MUST either:

- resolve it deterministically by appending `-2`, `-3`, … to the later
  identifier until the canonical ID is unique, keeping the counter
  monotonic across the document, and report a `id-collision` diagnostic naming
  both entries and both final IDs; or
- reject the document with the duplicate-ID error of §10.2.

The implementation MUST offer both behaviors and MUST document which one is
the default.

### C.5 Repairs that are forbidden

Tolerant parsing exists to preserve information, not to guess it. A tolerant
parser MUST reject, with a located and categorized error, at least:

- a missing `source`, `status`, or effective `type`;
- a `status` that contradicts the presence or absence of `target` (§12.3);
- an unbalanced ICU brace inside a string;
- a tag outside its closed vocabulary (§12), including a near-miss spelling;
- an unknown non-`x-` key;
- a line that is neither a field, a section, an entry marker, a continuation,
  a comment, nor blank (a malformed field line MUST NOT be silently discarded
  as if it were a comment);
- a document that exceeds a resource limit (§19);
- a version line whose version the implementation does not implement.

### C.6 Output guarantee and observability

- A document produced by tolerant parsing, when serialized canonically (§17),
  MUST be accepted by the strict grammar with zero errors. Fixing the input is
  the point; if the repair cannot achieve that, it must not be applied.
- Every repair and every rejection MUST be reported with a line number, a
  category, a human-readable message, and — for repairs — the original and the
  resulting value. Reporting is not optional: an unreported repair is
  indistinguishable from data loss, which is the failure this mode exists to
  prevent.
- A tool MUST NOT use tolerant parsing where strict consistency is required
  (for example, a source-of-truth check in CI); it MUST be able to select
  strict mode.
