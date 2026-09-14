# CLIFF AI Safety Model

This document describes how CLIFF 1.0 protects against the dominant LLM
editing failure modes and how to test it.

## 1. Failure modes of existing formats

| Failure | JSON | XML/XLIFF | PO | YAML |
| --- | --- | --- | --- | --- |
| Unclosed structural braces/tags | fatal | fatal | n/a | fatal |
| Mismatched closing-tag order | fatal | fatal | n/a | n/a |
| Unbalanced quotes in nested text | fatal | fatal | entry damage | fatal |
| Comments/data confusion | n/a | comments rare | **fatal by design** | comments are data |
| Indentation changes meaning | n/a | n/a | n/a | **fatal** |
| Free-form tag drift (`sad` vs `Sadness`) | n/a | n/a | n/a | n/a |
| Whitespace changes meaning | n/a | n/a | n/a | possible |

## 2. CLIFF 1.0 guarantees

For every structural construct, the following invariants hold:

1. **Line locality.** A section, entry, field, or list never continues onto
   another line. Deleting any line cannot unbalance the document.
2. **No structural `{ }` or `< >`.** Braces appear only as ICU payload inside
   quoted strings; angle brackets are never structural.
3. **Single-line brackets only.** `[section]` and `[item, item]` close on the
   same line. A validator needs no document-level stack to detect an unclosed
   list.
4. **Quotes only for strings.** IDs and tags are unquoted lowercase names, so
   a model never has to balance quotes around identifiers.
5. **Marker-anchored entries.** `<id>` is recognized by its single-line
   marker, not by column position, so accidental re-indentation is not
   fatal.
6. **Closed vocabularies.** Invalid `type`/`emotion`/`status` values are hard
   errors, turning silent quality bugs into loud, one-line-fixable errors.
7. **Inert comments.** A model may freely rewrite or delete `#` lines without
   touching data.
8. **Whitespace-insensitive structure.** `:` / `=`, indentation width, and
   surrounding spaces never change meaning; canonical serialization removes
   the difference. (YAML's opposite choice is the cautionary tale.)

## 3. Editing model

CLIFF assumes the worst-case editor: an autoregressive model that may replace
an arbitrary text span with a plausible alternative.

| Edit | Result |
| --- | --- |
| Change a `source`/`target` string | Local; valid if quotes/escapes/ICU balance survive |
| Add a field under an entry | Valid if the key is known and the value types correctly |
| Move an entry to another section | Valid; its canonical ID changes and the validator reports the move |
| Re-indent an entry or field | Valid (whitespace carries no meaning) |
| Use `=` instead of `:` | Valid (equivalent separators) |
| Delete a section line | Entries attach to the previous section; validator reports the new IDs |
| Delete a closing bracket of `[section]` | Invalid on **that line only** |
| Invent `type: Nown` or `emotion: [Sadness]` | Single-line vocabulary error listing the allowed values |
| Break ICU `{...}` inside a string | Local brace-balance error; file structure remains intact |

No edit can produce a document that is silently unbalanced from line 500
onward.

## 4. What the validator must report

Every CLIFF error MUST include:

- line number;
- error category (`syntax`, `semantic`, `vocabulary`, `icu`, `id`,
  `extension`, `warning`);
- the offending line text;
- for vocabulary errors: the allowed values;
- for canonical-ID errors: the two conflicting IDs.

This lets an AI agent make a single corrective edit instead of guessing.

## 5. Prompt-safe presentation

When sending CLIFF to a model:

- delete comments (developer-only);
- keep the header (it is the prompt's context);
- for each batch, include the section header and its group metadata;
- include the `dependency` paths and, when available, the referenced
  glossary entries relevant to the batch;
- never pretty-print into another structure (do not wrap in JSON).

CLIFF is already the shape a model should edit: context lines first, then the
translation lines.

## 6. Robustness test protocol

The edit-robustness suite in `cliff-test` applies 100 real, model-style edits
to a baseline file and validates after every edit:

- rename and reorder entries;
- re-indent entries and fields;
- add/remove optional fields;
- mutate fixed tags toward near-misses (`final` → `Final`, `noun` → `nouns`);
- switch separators and whitespace widths;
- insert/delete comment lines;
- rewrite ICU strings;
- move group metadata;
- duplicate section paths and entry ids.

Acceptance: when the edit intent is valid, **100% of the edited files must
remain valid**; deliberately invalid changes must each be caught by a precise
error. The protocol lives in
[cliff-test/tests/edit-robustness/](https://github.com/cliff-format/cliff-test/tests/edit-robustness/).