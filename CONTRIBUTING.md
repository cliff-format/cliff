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
2. **Spec changes** — small, motivated changes to
   `spec/cliff-1.0.0.md` with a corresponding update to:
   - `spec/abnf/cliff-1.0.abnf`
   - `spec/examples/`
   - `docs/design-rationale.md`
3. **Reference-library updates** — standards, emotion tags, and status tags in
   `references/`.

## Change rules

- Field names are standardized American English words. Adding a field is a
  normative change and needs a use case from at least two translation
  scenarios.
- Fixed tag sets (`type`, `emotion`, `status`, `variant`) are intentionally
  closed. Additions require the proposed word, its exact definition, and a
  translation-guidance row in `references/`.
- Do not introduce multi-line structural constructs. This is the core
  invariant of the format.
- Spec changes that affect validation must be accompanied by a matching change
  in the `cliff-test` validator and fixtures.

## License

All contributions are under the MIT License. By submitting a contribution you
agree to license it under that license.