# CLIFF Style Guide

- **Document:** CLIFF Style Guide
- **Applies to:** CLIFF 1.0 and 1.1 documents, and the tools that write them
- **Status:** Informative. Recommended, not required.
- **Normative references:** [spec/cliff-1.1.0.md](../spec/cliff-1.1.0.md) (the format),
  [spec/abnf/cliff-1.1.abnf](../spec/abnf/cliff-1.1.abnf) (the grammar)
- **Machine-readable:** the patterns in §2.1 and §2.3 are checked against the reference
  implementation by `tools/check_examples.py`

---

## 1. Background

### 1.1 Scope of this guide

This guide defines the **recommended** spelling of identifiers, files, and lines in a
CLIFF document. It is not part of the specification and it is not enforced by the
format's validator: a document that violates every rule below is still a valid CLIFF
document, and a tool that rejects one is broken, not strict.

The guide is written for the people and programs that *produce* CLIFF files:

- **translators and localization engineers** hand-authoring or reviewing a clan;
- **tool authors** whose importer must invent identifiers where the source format had
  none, and whose exporter must choose a file name;
- **prompt authors** writing instructions for a model that edits CLIFF files.

If you are writing a validator, read the specification instead. If you are writing a
document, read this.

### 1.2 Goals of this guide

1. **Optimize for the reader, not the writer.** A clan is read far more often than it
   is written — by the next translator, by a reviewer, and by a model with a context
   window. A name costs the writer one keystroke and the reader every time it appears.
2. **Keep one spelling per file.** Mixed habits inside one document are the failure
   this guide exists to prevent: a reader cannot tell a deliberate difference from a
   typo, and a diff shows churn where nothing changed.
3. **Never break a translation match key.** An identifier is the key a translation
   memory, an engine manifest, or a downstream resource is already using. Renaming one
   to tidy it discards the translation attached to it. This rule outranks every other
   rule in the guide.
4. **Be consistent with the surrounding project.** When a project already has a naming
   habit, follow it. Consistency is a good tiebreaker when there is no technical reason
   to choose otherwise, and a project's existing habit *is* a technical reason.
5. **Prefer the auditable choice.** A spelling that a script can check is worth more
   than one that merely looks right, because a script keeps checking it after everyone
   who chose it has moved on.

### 1.3 How to read this guide

Each rule states the requirement, then **Why:** the failure it prevents, then
**Decision:** what to do. Follow the requirement; read the reasoning when you are
about to make an exception.

Rules use the words **must**, **should**, and **may** to mean "required by this guide",
"recommended by this guide", and "left to the project". None of them mean "required by
the format" — only the specification can say that.

### 1.4 What this guide does not decide

- **Which characters are legal.** The specification does: `A-Z a-z 0-9 _ -`, never
  `.`, case-sensitive ([specification §5.5](../spec/cliff-1.1.0.md)).
- **Tag spellings.** `type`, `emotion`, `status`, and `variant` are closed
  vocabularies with fixed spelling ([specification §12](../spec/cliff-1.1.0.md)).
  There is no style question here, which is why §3 is short.
- **Whether a key may be quoted.** The specification forbids it: a key is a bare
  name, and quoting one is a validity error ([specification
  §6.1](../spec/cliff-1.1.0.md)). A tolerant parser may accept a quoted key as the
  documented relaxation of [Appendix C.2.7](../spec/cliff-1.1.0.md) and report the
  repair, which is a conformance option rather than a recommendation, so this
  guide says nothing about it either way.
- **Field order within an entry**, beyond the recommendation in §6.3.
- **Anything about a document's meaning.** Translation choices are the project's, not
  this guide's.

---

## 2. Identifiers

### 2.1 Choosing an identifier shape

> **Rule:** Use **lowercase kebab-case** or **PascalCase** for every identifier
> (namespace, clan, group path segment, entry id). Use one of the two per file. Do not
> use underscores, and do not mix the two shapes.

**Why:**

- A single shape makes the id space greppable: `grep -r '<panel-options' file.cliff`
  answers a question in one command when the shape is predictable, and does not when
  the file contains `panel-options`, `panelOptions`, and `panel_options` for three
  different entries.
- Mixed shapes are indistinguishable from typos in review. A reviewer cannot tell
  whether `SaveSlot` next to `save-slot` is a deliberate new entry or a rename that
  went wrong — and in CLIFF those are two *different* entries, so the mistake is
  silent.
- Both shapes survive the specification's character set, so either choice is legal;
  committing to one is what buys the benefit.

**Decision:** prefer kebab-case. It is the shape the specification's own examples and
the reference implementation's generated identifiers use, so it is the shape a reader
is most likely to have seen before. Choose PascalCase instead when the identifiers come
from a system that already spells them that way (an engine's resource names, a
generated manifest) — in that case preserving the source spelling is rule 1.3 in §1.2,
and it outranks this preference.

The two recommended shapes, as a machine-readable pattern:

```text
^[a-z0-9]+(-[a-z0-9]+)*$
```
<!-- check: style-kebab -->

```text
^[A-Z][A-Za-z0-9]*$
```
<!-- check: style-pascal -->

The identifier character set that any style must stay inside. This is the
specification's rule, not this guide's; it is printed here so the two documents can be
compared mechanically:

```text
[A-Za-z0-9_-]
```
<!-- check: name-char-class -->

Acceptable:

```cliff
namespace: ironforge-rpg
clan: act3-strings

[Video.Advanced]
<fullscreen>
<SaveSlot_2>
```

Not recommended, though valid:

```cliff
namespace: IronForge_RPG
clan: act3_strings

[Video.advanced]
<save-slot>
```

The second example has no defect a validator would report. It mixes a
PascalCase namespace with a snake_case clan, an `Advanced` and an `advanced` group
segment, and two id shapes — which is exactly the state from which a rename silently
deletes a translation.

### 2.2 Identifiers are match keys

> **Rule:** Never change an identifier because the source text changed, the wording
> improved, or the spelling looks nicer. Change it only as a deliberate,
> reviewed rename that carries the translation with it.

**Why:** The identifier, not the source string, is what a translation memory matches
on ([specification §10.3](../spec/cliff-1.1.0.md)). Renaming an entry orphans its
existing translation: the next run sees a new key with no translation and either
reports it as untranslated or machine-translates it again. Neither failure is visible
in a diff of the document.

**Decision:** when a rename is genuinely required, do it in one commit that also
updates the translation memory, the engine's key manifest, and any `reference` paths.
Report the rename to whoever maintains the downstream keys.

### 2.3 Names that are not identifiers

> **Rule:** Do not apply this guide to `type`, `emotion`, `status`, or `variant`.
> Their spelling is fixed by the specification.

**Why:** A style guide cannot offer a choice where the format offers none. The value of
a closed vocabulary is that a near-miss is reported loudly; an "accepted alias"
destroys exactly that property, and a validator that accepted `Final` for `final` could
no longer tell a typo from an intent.

**Decision:** write tags as bare lowercase words: `status: final`, `type: noun`,
`emotion: [objective]`. Never quote them. See
[specification §5.5 and §12](../spec/cliff-1.1.0.md) for the vocabularies.

### 2.4 Shortening an identifier

> **Rule:** Keep the part of a name that carries meaning, and omit what the surrounding
> path already says.

**Why:** An entry id sits inside a group path, and both sit inside a clan. Repeating
the group in the entry wastes the reader's attention and lengthens every line:

```cliff
[video.advanced]

# Redundant: every entry in this group is a video setting.
<video-advanced-fullscreen>

# Clear: the path already says "video.advanced".
<fullscreen>
```

**Decision:** avoid abbreviations that a reader outside your project would not know,
and never abbreviate by deleting letters inside a word
(`scr-resolution` for `screen-resolution`). Widely known initialisms are fine as a
unit: `hdmi-1-input`, `usb-c-port`. Prefer a longer name that a new translator can read
over a short one that needs a legend.

### 2.5 Generated identifiers

> **Rule:** A tool that writes CLIFF may normalize the identifiers it invents, and must
> report every identifier it rewrites.

**Why:** An importer is the one place a tool legitimately chooses a style, because the
source format had no CLIFF identifier to preserve. It is also the one place a silent
rename destroys data, since the imported keys may already exist in a translation
memory.

**Decision:** keep identifiers that are already valid CLIFF names as they are, even when
they do not follow §2.1 — `InvSwordIron` and `bad_id` are valid names, and rewriting
one is a data loss. Apply the normalization of
[specification Appendix C.3](../spec/cliff-1.1.0.md) only to identifiers that contain a
character the format forbids, and emit a report line for each one. Disambiguate
collisions with a numeric suffix rather than dropping an entry.

---

## 3. Tags

> **Rule:** Tags are written bare, lowercase, and unquoted. They are never the subject
> of a style decision.

**Why:** quoted and unquoted spellings of the same tag would give one field two shapes,
which is the ambiguity the format rejects on purpose
([specification §6.1.1](../spec/cliff-1.1.0.md)).

**Decision:** `status: final`, not `status: "final"`, not `status: Final`. In a list,
`emotion: [objective]`, not `emotion: ["objective"]`, and not `emotion: objective` —
list-typed fields keep their brackets even for a single item.

---

## 4. Files and directories

### 4.1 File name

> **Rule:** Name the file after the clan and the target language, in one of the two
> shapes the specification recommends.

**Why:** The file name is the first thing a reader, a build script, and a language-pack
job sees. A file called `strings.cliff` in a directory of two hundred files tells none
of them what it contains; `<clan>.<target-language>.cliff` tells all three.

**Decision:**

- Folder layout, for a project with more than one target language:

  ```text
  <target-language>/<clan>.cliff        zh-CN/settings.cliff
  ```

- Flat layout, for a single-language project or a small tool:

  ```text
  <clan>.<target-language>.cliff        settings.zh-CN.cliff
  ```

Spell `<clan>` exactly as the `clan` header value, including its case. Spell
`<target-language>` as the BCP 47 tag in canonical casing (`en-US`, `zh-Hant-TW`).

A generated or reprocessed file that deliberately breaks the shape is acceptable. Name
it for what it is — `corpus.cliff`, `settings.merged.cliff` — rather than bending the
convention into something that almost matches.

### 4.2 One clan per file

> **Rule:** One clan is one file. Do not split a clan across files, and do not merge
> two clans into one.

**Why:** The clan is the unit of review, of delivery, and of translation context: its
header carries the family `info` and `standard` that every entry in it is translated
against. Splitting the clan splits that context, and the second file's translator no
longer sees it.

**Decision:** when two clans share context, share it with `dependency`, not by merging.
When one clan is too large to translate in one pass, split the *work* (batch by
section), not the *file*.

### 4.3 Directory is the language boundary

> **Rule:** In a multi-language project, one directory per language, named by the BCP 47
> tag. Do not nest language directories inside clan directories, or the reverse.

**Why:** A directory boundary is a boundary for `git checkout`, for CI path filters, and
for zipping a language pack. Real teams deliver a language, not a clan, so the directory
should be the thing they hand over.

**Decision:**

```text
project/
├── en-US/          # or the source language
│   ├── act3.cliff
│   └── settings.cliff
└── zh-CN/
    ├── act3.cliff
    └── settings.cliff
```

### 4.4 The header stays authoritative

> **Rule:** Never let the file name carry information the header does not also carry.

**Why:** Files are renamed, copied into working directories, attached to tickets, and
generated by tools. The header travels with the content; the name often does not. A
document whose identity exists only in its name is anonymous the moment someone pastes
it into a chat window.

**Decision:** fill in `namespace`, `clan`, `source-language`, and `target-language` even
when the file name already says what they would say. Authoring plugins should do this
automatically. A file-name mismatch is a warning in CLIFF 1.1 and never an invalidity;
fix it for tidiness, not to make the document valid.

---

## 5. Group paths

### 5.1 Shape and depth

> **Rule:** Write the complete dotted path on every section line, keep depth to what a
> reader can hold in mind, and use one segment shape per file.

**Why:** Each line carries its own full path so that a moved line never becomes
ambiguous ([specification §6.2](../spec/cliff-1.1.0.md)). Deep nesting spends that
benefit on paths nobody can remember, and a group two levels deeper than its neighbours
usually means the entry belonged to the shallower group.

**Decision:** two or three levels is typical (`[video]`, `[video.advanced]`). Beyond
that, check whether the extra level is a real distinction or a filing habit:

```cliff
# Reasonable
[video]
[video.advanced]
[video.advanced.color]

# Probably a filing habit, not a distinction
[video.advanced.color.gamma.curve]
```

### 5.2 Ordering

> **Rule:** Order sections the way a reader navigates the product, and keep related
> sections adjacent.

**Why:** Section order is authored order and it is preserved by serializers
([specification §17.3](../spec/cliff-1.1.0.md)). A clan whose sections follow the
settings screen a user actually sees is reviewable top to bottom; one in alphabetical
order is not.

**Decision:** mirror the UI or the document's own structure. Put high-traffic, short
groups first, and keep prose-like content (dialogue, narration) away from label-like
content so a reviewer can hold one register at a time.

---

## 6. Lines and fields

### 6.1 Do not write a trailing `,` or `;`

> **Rule:** Do not end a line with a terminator.

**Why:** CLIFF 1.1 accepts one trailing `,` or `;` on any line, because hand authors and
models punctuate reflexively and rejecting a whole file over one comma is a bad trade
([specification §5.6](../spec/cliff-1.1.0.md)). Accepting it is not the same as
recommending it: the character means nothing, it invites a second one (`;;` is a syntax
error), and it makes every diff noisier.

**Decision:** write `key: value`. If a generator's output carries terminators, strip
them on the way in rather than teaching the next reader that they are normal.

### 6.2 Separators and spacing

> **Rule:** Use `key: value`. Do not use `key = value`, do not put a space before the
> colon, and do not align values in a column.

**Why:** `=` is tolerated input for INI and TOML habits, but the canonical form is
`:` — and a file that mixes the two gives a reviewer two things to check that mean
one thing. Aligned values, in a format where a long value is a quoted string of
arbitrary length, produce diffs in which one edit rewrites every line.

**Decision:** one space after the colon, no trailing whitespace, one space between
list items.

### 6.3 Field order within an entry

> **Rule:** Write the entry's fields in a stable order: `source`, `target`, `type`,
> `emotion`, `status`, then the optional context-bearing fields (`context`,
> `max-width`, `reference`, `reviewer`).

**Why:** A reviewer comparing two entries scans the same position for the same fact.
When `status` moves around, the eye has to search for it, and a misplaced `target` is
easier to miss next to an unrelated field.

**Decision:** the order above matches the specification's field tables (§8) and what the
reference serializer emits, so a file written this way does not churn the first time a
tool rewrites it.

### 6.4 Flat fields, blank-line separation

> **Rule:** Write fields flat, at the same indentation as the `<id>` marker. Put one
> blank line before each section and each entry.

**Why:** Indentation carries no meaning in CLIFF ([specification §5.3](../spec/cliff-1.1.0.md)),
so indented fields buy nothing and cost a class of editing mistakes: a model that
re-indents half a block, or an editor that reflows it, produces a diff that looks
structural but is not. The blank line does carry reading value — it is the paragraph
break between entries.

**Decision:**

```cliff
[video]
context: "Video settings screen."
type: label

<resolution>
source: "Resolution"
target: "分辨率"
type: noun
status: final
```

### 6.5 Section indentation is optional

> **Rule:** A section line may be indented two spaces per path depth as a visual cue.
> Do not rely on it, and do not indent anything else.

**Why:** The indentation is cosmetic and the parser ignores it; the path on the line is
authoritative ([specification §6.2](../spec/cliff-1.1.0.md)). It helps a reader see the
outline, and it becomes a liability the moment someone believes it defines nesting.

**Decision:** indent section lines only, or not at all. Both are fine; be consistent
within a file.

### 6.6 Quoting

> **Rule:** Use double quotes for text values. Use single quotes only when the value
> contains more double quotes than single quotes.

**Why:** Both delimiters mean the same thing and the serializer emits double quotes
([specification §5.5](../spec/cliff-1.1.0.md)). Picking the delimiter by content keeps
the number of escapes down, which is where hand-written strings actually break.

**Decision:** `target: "Anvil says: \"That is a fine blade.\""` is correct and
double-quoted; a value that is mostly quoted English may read better in single quotes:
`context: 'The label reads "Save as…"'`.

### 6.7 Wrapping a long value

> **Rule:** A long value may be wrapped as adjacent quoted strings, with continuation
> lines aligned under the opening quote.

**Why:** CLIFF has no text blocks ([specification §6.1](../spec/cliff-1.1.0.md)), and
the wrapped form keeps the value and its continuation visibly one field. Adjacent
strings concatenate verbatim, so the writer owns the spaces — the single most common
mistake in a wrapped value is a missing trailing space at a line break.

**Decision:**

```cliff
info: "CLIFF is a translator-optimized, context-first data format for"
      "localization. It provides one lossless working file for the whole"
      "translation lifecycle."
```

Write a trailing space at the end of a line, or a leading space at the start of the
next, whenever the text needs one. CJK text usually needs neither. Do not wrap a value
that fits on one line: the wrapped form is for readability, and a two-line value that
would fit in eighty columns costs the reader a join.

### 6.8 One field, one line

> **Rule:** Write each key at most once per scope. To hold several values, use a list or
> a continuation line.

**Why:** CLIFF has no repeatable fields, and a duplicate key is a validity error
([specification §6.1](../spec/cliff-1.1.0.md)). This is the rule a model breaks most
often when asked to "add another reference", which is why §6.9 exists.

**Decision:**

```cliff
# Correct: one list holds both paths.
reference: ["src/ui.cpp:12", "docs/ui.md"]

# Wrong: two reference fields, which is a duplicate key.
reference: ["src/ui.cpp:12"]
reference: ["docs/ui.md"]
```

### 6.9 Lists keep their brackets

> **Rule:** Write list-typed fields (`emotion`, `dependency`, `reference`) as lists,
> even for one item.

**Why:** The shape of the value tells the reader its type
([specification §6.1.1](../spec/cliff-1.1.0.md)). A single-item shorthand would give one
field two spellings, and a tool that has to accept both eventually emits both.

**Decision:** `emotion: [objective]`, `dependency: ["../terms/terms.zh-CN.cliff"]`,
`reference: ["src/ui.cpp:12"]`.

### 6.10 Comments

> **Rule:** Use `#` full-line comments for developer notes only. Never put translation
> context in a comment.

**Why:** A translator must be able to delete every comment without losing context
([specification §5.4](../spec/cliff-1.1.0.md)); a fact a translator needs is a field,
not a note. Anything in a comment is invisible to the person the document is for.

**Decision:** use comments for tooling hints, temporary notes, and explanations aimed at
a maintainer. Move everything a translator would need into `context`, `standard`, or
`info`.

---

## 7. Header

### 7.1 Fill every required field, in the canonical order

> **Rule:** Write `namespace`, `clan`, `source-language`, `target-language`, then
> `version`, `variant`, `title`, `info`, `standard`, `dependency`.

**Why:** This is the order the canonical serializer emits
([specification §17.2](../spec/cliff-1.1.0.md)), so a file written this way does not
churn when a tool touches it.

### 7.2 Write the family's context once, in the header

> **Rule:** Put anything true of the whole clan in `info` or `standard`. Do not repeat
> it on every entry.

**Why:** Repetition drifts: the fifth entry's copy of a policy line says something
slightly different from the first, and now there are two policies. The header is also
the part of the prompt a model reads first.

**Decision:** `info` for setup, audience, characters, and domain; `standard` for
policies a translation must follow ("preserve proper nouns", "keep labels under the
declared max-width"); `context` on a group or entry for what is true of that text.

### 7.3 `dependency` holds paths, and relative ones

> **Rule:** Use relative POSIX paths with forward slashes, and reference real files.

**Why:** Dependencies are resolved against the file's own directory
([specification §16](../spec/cliff-1.1.0.md)), so they survive a repository move;
absolute paths do not. A dangling dependency is the most common defect in a
hand-written header, and nothing in the document reports it.

**Decision:** `dependency: ["../terms/terms.zh-CN.cliff", "docs/style-guide.md"]`. Check
that each path resolves before committing.

### 7.4 The glossary is a deliverable, not a reflex

> **Rule:** Create a `variant: glossary` file when terminology recurs or a naming
> decision would otherwise be made twice. Do not create one by default.

**Why:** A glossary that exists but holds invented or unused renderings is worse than no
glossary: it is a file to maintain that contradicts the translation
([specification §13.2.2](../spec/cliff-1.1.0.md)).

**Decision:** when you record a term decision while translating, record it in the
glossary for that clan and add a `dependency` to it from the `standard` file. When a
clan has no recurring terminology, ship no glossary.

---

## 8. Working with a project that has its own style

> **Rule:** When a project already has a naming habit that differs from §2, follow the
> project. Record the deviation and why.

**Why:** The guide is a default for projects that have no answer, not an argument
against a project that has one. An engine whose resource keys are `Menu.Button.Save`
has already made the decision, and the cost of overriding it is a rewritten key
manifest plus every translation memory entry that referenced it.

**Decision:** adopt one of the two recommended shapes when you are starting a clan from
nothing. When you are importing or extending one, keep the existing shape. Note the
choice in the clan's `standard` or `info` line so the next translator does not
re-litigate it.

---

## 9. Checking a document against this guide

Style is opt-in, so check it explicitly rather than expecting a validator to do it:

```bash
cliff_format validate --style path/to/file.cliff
```

`--style` reports style deviations as warnings (category `style`) and exits `0` when the
document has no errors — the document is valid CLIFF either way. To enforce this guide
in one project's CI, treat a non-empty `--style` report as a failure *in that project's
own pipeline*. Do not add it to a shared validator: another project is entitled to a
different style, and a format whose validator enforced one project's habit would have
made the mistake CLIFF 1.1 removed.

Reviewers should treat a `--style` finding as a conversation, not a defect. The one
finding worth blocking on is a rename of an existing identifier (§2.2), because that
loses a translation.

---

## 10. Compatibility

> **Rule:** If a clan must be readable by a CLIFF 1.0-only tool, follow §2.1 and §4.1
> exactly.

**Why:** CLIFF 1.0 required lowercase kebab-case identifiers and a matching file name.
CLIFF 1.1 relaxed both, so a document that follows this guide is valid under **both**
grammars and can be handed to either toolchain without a second copy.

**Decision:** for a mixed-toolchain project, use kebab-case identifiers, the folder or
flat file name from §4.1, and no terminators. That is the intersection of the two
specifications and the whole of this guide.
