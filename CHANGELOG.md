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

- **Optional line terminator** (`, ` or `;`) at the end of any line, at most one,
  meaning nothing and never emitted by a canonical serializer. It is recognized
  only after the line's closing quote or bracket, so a `,` or `;` inside a string
  is payload (§5.6).
- **`style/README.md`** — the informative style guide for identifier and file
  naming, with the machine-readable recommended shapes and the reasons the rules
  moved out of the normative grammar.
- **Appendix C — tolerant parsing**, normative for any tool that advertises it:
  the six permitted relaxations, the deterministic identifier-normalization
  algorithm, collision handling, the repairs that are forbidden (a tolerant
  parser must not guess missing data, vocabulary, or structure), and the
  requirement that every repair be reported and that the result still be valid
  under the strict grammar.
- **Enumerated resource limits** (§19): file size, line length, decoded string
  length, group path segment count, list length, and entry count, enforced
  identically in strict and tolerant modes.

### Compatibility

- Both `CLIFF 1.0` and `CLIFF 1.1` version lines are accepted by a 1.1
  implementation; a canonical serializer emits `CLIFF 1.1` for new documents and
  preserves the declared version when round-tripping an existing one.
- Documents that follow `style/README.md` remain valid under the 1.0 grammar, so a
  project that must interoperate with 1.0-only tooling can keep one set of bytes
  for both.
