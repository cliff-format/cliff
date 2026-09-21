# Changelog

CLIFF is versioned as 1.1.0. See the Git history for the complete record of changes.

## 1.1.0 — 2026

CLIFF 1.1 is a **pure relaxation** of CLIFF 1.0: every 1.0-conforming document is
also 1.1-conforming, and no 1.0 requirement was removed or narrowed. A 1.0-only
validator will reject the new liberties, which is exactly why the version line
exists (§21).

### Changed

- **Identifiers are wider and are no longer a style rule.** `name` becomes
  `[A-Za-z0-9_-]+` (uppercase, digits, `_`, `-`; `.` still forbidden because it
  separates group paths and canonical ID components). Lowercase kebab-case is no
  longer enforced by the grammar; it moves to the style guide. Identifiers stay
  case-sensitive and must not be case-folded by a parser (§5.5, §10.1).
- **Tags stay closed and lowercase.** A new `tag-name` production states it
  explicitly: `type`, `emotion`, `status`, and `variant` values remain lowercase
  kebab-case words from their closed vocabularies (§5.5, §12, §13).
- **File layout and file naming are recommendations.** The layout/header
  consistency check of §11.3 drops from MUST to SHOULD and is reported as a
  **warning** by default; an implementation may offer an explicit opt-in strict
  mode for projects that keep the convention mandatory (§11, §21).

### Added

- **Clarification to the identifier relaxation (Appendix C.2.5): markup is not an
  identifier.** The relaxation applies to an identifier that **begins with a name
  character** (ignoring surrounding whitespace), or that uses the quoted form of
  C.2.4. A pair of angle brackets that encloses anything else — a stray closing tag
  `</terms>`, or `<.hidden>` — is **not an entry marker**, and C.5 rejects the line
  with a located, categorized error. A tolerant parser MUST NOT manufacture an entry,
  a group or an identifier out of markup, because that invents data the document does
  not contain; the same rule governs the first segment of a group path inside `[...]`.
  The limit was found by a measured model behaviour: a corpus of answers in which the
  model closes what it opens (`</terms>` after its glossary) produced documents that
  the reading normalized into an entry named `terms` (C.3 step 4 replaces the slash,
  step 6 strips it) and then failed on `entry 'terms' is missing required field
  'source'` — an entry the answer never had, with a diagnostic that pointed at the
  invented entry instead of at the stray line. The empty-name case is unchanged: an
  identifier that is empty or whitespace-only still takes the fallback name of C.3
  step 7. Strict parsing is untouched, and the ABNF's semantic-constraint block now
  states the limit as well, so it reaches a prompt that injects that block.
- **Relaxation: a quoted key** (Appendix C.2.7). A field line written
  `"context": "…"` — or with single quotes, or with `=` — is now a permitted
  tolerant deviation: the quotes are removed, a `name-quote` repair is reported,
  and the enclosed text is then read as a key under exactly the scope rules a
  bare key faces. **Nothing is widened.** The key sets are unchanged, so a quoted
  word that is not a legal key in that scope is still an unknown-key error
  (§C.5) and a quoted `status` in a group is still a scope error; the enclosed
  text must be a `name` (§5.5), with no escapes processed, so a parser is never
  asked to guess where the key ends. The relaxation is decided before the
  continuation rules: a line whose first token is a quoted name followed by `:`
  or `=` is a field line, while a line of quoted strings only remains a
  continuation. A serializer still emits keys bare (§Serialization), so the
  relaxed form cannot spread. The rationale, including the two neighbouring
  designs that were rejected, is in `docs/design-rationale.md` §5b.
  **No clause was added to §6.1**: a quoted key already fails the grammar
  (`key = name`, §5.5), and §6.1 states rules only where the grammar leaves a gap
  — which is why "tags are never quoted" and "list-typed fields are always
  written as lists" exist there and this does not.
- **Optional line terminator** (`, ` or `;`) at the end of any line, at most one,
  meaning nothing and never emitted by a canonical serializer. It is recognized
  only after the line's closing quote or bracket, so a `,` or `;` inside a string
  is payload (§5.6).
- **`style/README.md`** — the informative style guide for identifier and file
  naming, with the machine-readable recommended shapes and the reasons the rules
  moved out of the normative grammar.
- **Appendix C — tolerant parsing**, normative for any tool that advertises it:
  the seven permitted relaxations, the deterministic identifier-normalization
  algorithm, collision handling, the repairs that are forbidden (a tolerant
  parser must not guess missing data, vocabulary, or structure), and the
  requirement that every repair be reported and that the result still be valid
  under the strict grammar.
- **Enumerated resource limits** (§19): file size, line length, decoded string
  length, group path segment count, list length, and entry count, enforced
  identically in strict and tolerant modes.

### Compatibility

- **A strict implementation reports nothing differently for a quoted key.** Strict
  mode still rejects it, with the same rejection as before; only a tool that
  advertises tolerant parsing accepts it, and it must report the repair. A
  tolerant parser built before this change refuses the form, so a document that
  relies on it is not portable to an older tolerant implementation — the form is
  input only, and canonical output is unchanged.
- Both `CLIFF 1.0` and `CLIFF 1.1` version lines are accepted by a 1.1
  implementation; a canonical serializer emits `CLIFF 1.1` for new documents and
  preserves the declared version when round-tripping an existing one.
- Documents that follow `style/README.md` remain valid under the 1.0 grammar, so a
  project that must interoperate with 1.0-only tooling can keep one set of bytes
  for both.
