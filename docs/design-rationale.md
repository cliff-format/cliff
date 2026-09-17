# CLIFF Design Rationale

This document records **why** CLIFF looks the way it does. It follows the
tradition of the YAML and TOML design documents: every syntax decision has a
recorded reason.

## 1. Why a working format, not an interchange format

XLIFF calls itself an "Interchange File Format": its job is moving data
between tools. CLIFF's job is bigger: **one lossless file for the whole
lifecycle** — extraction, translation, review, delivery. Interchange is one
function of that file, not its identity.

CLIFF is named **Integrated** because it is a working format, not merely an
interchange wrapper, and its README states goals, non-goals, and implementation
artifacts the way TOML, YAML, WHATWG HTML, and GeoJSON do.

## 2. Why line-oriented, not tree-shaped

XLIFF is a tree (`<file><group><unit>...`) and JSON is a tree. Trees are
machine-friendly but hostile to autoregressive LLM editing: a deep edit must
keep every ancestor open and align every closing tag.

CLIFF is a flat sequence of typed lines. The current section sets the context
path; the `<id>` marker starts a record; `key: value` lines attach to the
nearest record positionally, and their indentation carries no meaning.
Inserting, deleting, or rewriting one line can never leave an
unclosed element. The worst realistic failure is a misplaced field, which a
single-pass validator detects without any stack beyond "which entry are we
in".

## 3. Why `[group.path]` sections

- INI-style sections are decades old, unambiguous, and need no closing mark.
- Dotted paths make nesting explicit in every line: `[video]`,
  `[video.advanced]`. No nested brackets, and no ambiguity about where a moved
  line belongs.
- The path participates in the canonical ID
  (`namespace.clan.group-path.entry-id`), satisfying the family → group →
  entry key model without a separate `id` field.

## 4. Why `:` and `=` both, and why canonical is `key: value`

- `key: value` is the CLIFF-native form; `key = value` is what INI/TOML users
  expect and what many humans reflexively type.
- Accepting both costs a parser one token of lookahead ("first `=` or `:`
  outside a string") and costs nothing in ambiguity, because keys are
  lowercase names that never contain either character.
- Surrounding whitespace is tolerated for hand-written files, but the
  canonical serializer always emits `key: value` with exactly one space. This
  keeps determinism for machines while being forgiving to humans — the YAML
  lesson applied in the opposite direction: YAML paid a huge complexity price
  for permissive whitespace, so CLIFF permits whitespace only where it cannot
  change meaning.
- Long values may wrap across physical lines as C-style adjacent quoted
  strings for any scalar string field (`source`, `target`, `info`,
  `standard`, `context`, …), concatenated verbatim with no inserted
  character; `\n` remains the only real line break. List fields may wrap as
  bare single-line lists that merge in order, so no bracket pair ever spans
  lines. Continuation lines may be indented to align with the opening
  quote/bracket so wrapped values remain easy to scan. Repeated fields are
  rejected outright — every key appears at most once per scope — so
  "multi-line" always means continuation, never duplicate keys. Text blocks
  are deliberately rejected.

## 5. Why identifiers have a character set but no style rule

CLIFF 1.0 restricted all names to lowercase kebab-case everywhere: keys, IDs,
group segments, and fixed tags. The reason was real:

- LLMs drift between `InvSwordIron`, `inv_sword_iron`, and `inv-sword-iron`,
  silently breaking translation-memory keys.
- Case-sensitive uniqueness checks then produce duplicate keys with identical
  meaning.

CLIFF 1.1 keeps the concern and splits the answer.

**What the format decides** is the character set and the identity rules: a name
may use ASCII letters, digits, `_`, and `-`, must contain at least one
character, must not contain `.`, and is case-sensitive and **never rewritten by
a parser**:

```
name-char = ALPHA / DIGIT / "_" / "-"
```

**What the project decides** is style: kebab-case, PascalCase, or the mixed
habits an existing engine manifest already uses. `style/README.md` records the
recommendation; nothing enforces it.

Two things convinced us the 1.0 rule was backwards:

1. **An identifier is a translation match key, not a display string.** It is
   the string a translation memory, an engine manifest, or a downstream
   resource already uses. When a project imports `Menu.Button.Save` from an
   engine, or keeps a glossary called `TheBlockOfGrass`, enforcing CLIFF's
   spelling means *rewriting the keys* — and a rewritten key is a lost
   translation. The format was making a style decision on behalf of data that
   already had one.
2. **The drift problem is a recommendation's job.** Consistency is still worth
   having within a file, and a style guide plus an opt-in lint (`--style`)
   delivers it without turning a cosmetic choice into a parse error. A
   validator that rejects `bad_id` cannot also be the validator for a project
   whose ids came from Android resource names.

What did **not** relax is equally deliberate. Fixed-vocabulary tags (`type`,
`emotion`, `status`, `variant`) stay lowercase kebab-case words from closed
sets. Those are not identifiers a project chooses; they are slots this
specification defines, and a closed set that tolerates `Final` next to `final`
is not closed (§12).

`.`, however, stays forbidden inside a name even though it is a natural
separator for dotted keys imported from i18n JSON. The dot is the separator of
group paths and of canonical IDs, and a name that could contain one would make
`namespace.clan.group.entry-id` ambiguous in both directions — the identity
model is the one thing this format cannot make fuzzy. Importers fold a dotted
key into a group path, or replace the dot; both are reported.

Language tags remain BCP 47 and keep their own casing rules, because they are
not names.

## 5a. Why one optional trailing `,` or `;` is standard but not canonical

Hand authors and models punctuate reflexively. In 1.0, one stray comma at the
end of a line rejected the whole document, which is a bad trade: the comma
carries no information, and the error costs a full validation round trip.

1.1 therefore makes at most one trailing `,` or `;` legal on every line, with
three deliberate boundaries:

- **One, not many.** `;;`, `,,`, and `, ;` stay errors. Accepting a run would
  make the boundary between a value and punctuation undecidable, and
  "decidable" is the property the format is selling.
- **Only after the closing quote or bracket.** The terminator is recognized
  when the line's value has been consumed, so `source: "a,b;"` keeps its value
  intact. A separator that can appear inside data and also terminate it is
  exactly the kind of ambiguity §4 avoids.
- **Never canonical.** The serializer does not emit it, so it cannot spread
  through a file by copy-paste. Accepting input liberally while writing
  canonically is the same posture as `key = value`. It is also why the style
  guide tells writers not to use it: legal is not the same as recommended.

## 6. Why the recommended layout is `<target-language>/<clan>.cliff`

- A large project has many clans and many languages. Unreal Engine's
  convention — one folder per language — makes the **delivery boundary** the
  **directory boundary**: the Japanese team checks out and ships `ja-JP/`,
  the Spanish team `es-ES/`, CI diffs stay inside one folder, and a language
  pack is the folder itself. The flat layout (`settings.zh-CN.cliff`) would
  put hundreds of mixed files in one directory.
- The flat name `<clan>.<target-language>.cliff` remains valid for
  single-language projects and small tools; the two layouts resolve to the
  same two facts (clan, target language) and conflict is a warning.
- The header is authoritative: `namespace`, `clan`, `source-language`, and
  `target-language` are all required, and authoring plugins/editors fill them
  in automatically. The layout is a delivery convention that SHOULD agree with
  the header; it never supplies missing header values. Files get renamed,
  moved, and pasted, so the header keeps the file self-describing.
- **Why the mismatch is a warning and not an error (1.1).** The layout is a
  convenience for humans and CI, not a property of the data. A file copied into
  a working directory, attached to a ticket, or written by a generator has lost
  its name without losing a single fact — the header still carries all four
  identity fields. Reporting a mismatch as an error made the *file's location*
  a conformance requirement, which is the one thing a self-describing format
  should not need. A project that wants it enforced turns on an explicit strict
  mode, so the choice is visible instead of implied.
- `source-language` and `target-language` must be valid BCP 47 tags; a
  per-entry language exception belongs in that entry's `context`, not in the
  header.

## 7. Why the header is small and generic

CLIFF keeps a small, generic header:

- identity (`namespace`, `clan`, `source-language`, `target-language`,
  `variant`) — all four identity/language fields are required, and authoring
  plugins/editors fill them in automatically;
- `title` — one short family description;
- `info` — free prose for anything the whole family needs to know (setup,
  audience, characters, domain);
- `standard` — translation policy lines;
- `dependency` — a list of relative paths to prerequisite glossaries and
  reference documents.

Terminology lives in a dedicated `variant: glossary` file. Structured
per-text attributes (`type`, `emotion`, `status`) live on the entry where they
belong. This matches the XLIFF 2.2 approach of optional modules and keeps the
core generic.

## 8. Why `type` is required and closed

Translation quality depends on knowing *what* is being translated: an isolated
noun, a UI label, narration, a pun. Free text ("kind of text") drifts; a
closed 26-tag set does not.

`type` is required per entry but inheritable from the group, so a screen of
labels pays the cost once. The closed set is deliberately split into three
families — word-level, phrase-level, text/function-level — because they map to
different translation strategies (dictionary lookups, term management, and
discourse translation).

## 9. Why `emotion` defaults follow `type`

Requiring `emotion` on every entry would add tokens without adding
information: a settings label is objective by default, and a line of dialogue
is neutral until annotated. CLIFF therefore:

- adds `objective` (informational default) and `mechanical` (robot delivery)
  to the emotion vocabulary;
- defaults non-speech types to `objective` and speech types (`dialogue`,
  `monologue`, `idiom`) to `neutral`;
- lets an explicit `emotion` always override the default.

## 10. Why `status` is required

`status` drives the whole lifecycle and is meaningless when guessed. A
required, explicit state removes the "which phase is this file in" ambiguity
that a default status created. The four tags — `initial`, `translated`,
`reviewed`, `final` — are identical to the XLIFF 2.x state model; `initial`
means "no target text yet" (extraction state) and is the only status that may
omit `target`. The cost is one short line per entry.

## 11. Why `speaker`/`listener`/`scene` are not fields

Speaker, listener, and scene are useful for game dialogue but not universal,
and an optional field would be skipped by developers exactly as often as a
free-text field. CLIFF folds attribution into `context` prose and does not
define a structured speaker field: when `type` is `dialogue`/`monologue`, the
model already knows someone is speaking, and `context` carries who.
Machine-readable identity can be reconstructed by tools from the canonical ID
and group path when needed.

## 12. Why there is no `format` field

MessageFormat dialect is a property of each string, and strings already
declare themselves:

1. MF2 markers (`{{`, `}}`, `.match`, `.input`, `.local`) → MF2;
2. else `{...}` → MF1;
3. else plain text.

A `format` field duplicates that information and drifts (the field says `mf1`
while the string is plain). Auto-detection is deterministic and removes a
whole class of consistency errors. MF2 is the preferred dialect for new
content; MF1 remains accepted.

## 13. Why ICU lives inside strings

Modern localization needs plurals, selects, and placeholders. CLIFF does not
re-encode ICU as XML-like elements; it stores MF1/MF2 verbatim in quoted
strings and validates brace balance. A broken ICU expression is a local
string error, never document corruption, because `{` and `}` only appear
inside quoted strings.

## 14. Why `max-width` counts display cells

`"OK"` and `"确定"` are both two characters but two vs. four rendered cells.
UI overflow bugs are about rendered width, so CLIFF measures UAX #11 display
cells: Latin/digit/halfwidth = 1, CJK/fullwidth/emoji = 2, combining marks = 0.

## 15. Why comments are inert

PO's fatal flaw is carrying structured data (`#:`, `#,`, `#|`, `#.`) inside
comment syntax: a tool that strips comments destroys references. In CLIFF, `#`
is only a full-line developer note; every translator-relevant fact is a field.
A translator can be handed a file with all comments deleted and lose nothing.

## 16. Fields deliberately omitted

| Omitted field | Reason |
| --- | --- |
| `engine`, model name | Tool-chain metadata, not translation data |
| `confidence` | Runtime quality signal, not an interchange property |
| `date`, `author` | Filesystem/VCS metadata |
| `previous-source`/`previous-target` | VCS/diffing is the system of record |
| translation-memory data | Belongs in a TM database |
| `msgid_plural`/`msgstr[n]` | ICU MessageFormat replaces plural arrays |
| segment-level markup (`<mrk>`, `<ph>`) | ICU placeholders carry the same information without structural tags |
| `format` | Auto-detected per string (this document §12; spec §14) |
| `term` header lines | Handled by `variant: glossary` files referenced via `dependency` |
| `character`, `genre`, `audience`, `setting`, `register` | Folded into generic `info` prose |

## 17. How nested groups stay readable without closing tags

A tree format pays for nesting with closing delimiters; CLIFF pays with a
flatter look. The mitigation is a **Markdown-style outline**:

- `[group]` is the heading; the dotted path shows the depth.
- A blank line before every section and entry is the paragraph break.
- `<id>` is the list anchor; fields are flat, and indentation carries no
  meaning (INI/TOML style).
- Canonical serializers MAY indent nested section lines by two spaces per
  path depth — a purely cosmetic cue, because the path on the line remains
  authoritative and the parser ignores the indentation:

  ```cliff
  [video]
  context: "Video settings."

  [video.advanced]
  context: "Advanced video settings."
  ```

There is no closing marker to forget, and a reader never has to scan upward
to find one. Tool UIs render the dotted path as a tree; the file itself stays
flat and line-local.

## 18. Why the spec and tests are separate repositories

Following TOML (spec vs `toml-test`) and WHATWG (standard vs test suites),
the normative specification lives in `cliff/` while the reference validator,
fixtures, benchmarks, and quality rubrics live in `cliff-test/`. The
specification says *what*; the test project says *how well*.

The style guide lives **inside** the specification repository (`style/`) even
though it is informative. The split between normative and informative material
is a labelling question, not a repository question: the two documents must
agree about the character set, the canonical form, and the recommended shapes,
and the drift-guard test in the reference implementation reads both. Putting
them in one repository makes that agreement enforceable in one commit;
splitting them would make the style guide the one document most likely to go
stale without anyone noticing.