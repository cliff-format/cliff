# Contributing to CLIFF

CLIFF is an open format specification. Contributions are welcome in the same
spirit as YAML and TOML: clear, conservative, and testable.

This repository contains the **specification only**. Test suites, the
reference validator, and the token benchmark live in the separate
[cliff-test](https://github.com/cliff-format/cliff-test) project; interoperability tools may be separate
projects as well.

## What we need

1. **Issues** — ambiguity reports, parser edge cases, and real-world
   localization scenarios CLIFF handles poorly.
2. **Spec changes** — small, motivated changes to `spec/cliff-1.1.0.md` with a
   corresponding update to:
   - `spec/abnf/cliff-1.1.abnf`
   - `spec/examples/cliff-1.1.0/`
   - `docs/design-rationale.md`
3. **Reference-library updates** — standards, emotion tags, and status tags in
   `references/`.
4. **Style-guide changes** — identifier and file naming recommendations in
   `style/README.md`. Style is informative, so it can move faster than the
   specification; keep it consistent with `spec/cliff-1.1.0.md` §5.5 and §11.

## Change rules

- Field names are standardized American English words. Adding a field is a
  normative change and needs a use case from at least two translation
  scenarios.
- Fixed tag sets (`type`, `emotion`, `status`, `variant`) are intentionally
  closed. Additions require the proposed word, its exact definition, and a
  translation-guidance row in `references/`.
- Do not introduce multi-line structural constructs. This is the core
  invariant of the format.
- Keep the two kinds of bare word distinct: a **name** (identifiers, keys, group
  segments) answers "what is this called" and is the project's choice; a
  **tag** answers "which fixed value is this" and is this specification's
  choice. Widening `name` further is a lexical change; adding a value to a
  closed tag set goes through `references/`.
- Identifier *style* belongs in `style/README.md`, not in the grammar. Do not
  turn a recommended spelling into a validity rule.
- Keep the identifier character set, the ABNF `name` production, and
  `style/README.md`'s machine-readable regexes in sync; the drift-guard test in
  the reference implementation reads both.
- Spec changes that affect validation must be accompanied by a matching change
  in the `cliff-test` validator and fixtures.

## Release and version policy

- 1.x releases must stay **relaxations**: a document valid under an earlier 1.x
  specification must remain valid under every later one. If a change would
  reject a previously valid document, it is a major-version change, not a 1.x
  change.
- The version line accepts every implemented 1.x minor version; the canonical
  serializer emits the current one. State the supported versions in the
  diagnostic when rejecting an unimplemented one.
- Update `CHANGELOG.md` with every normative change, marking relaxations and any
  behavior a strict implementation will now report differently.

## License

All contributions are under the MIT License. By submitting a contribution you
agree to license it under that license.