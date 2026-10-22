# Version Control Policy

This document defines the English-only version control policy for the CLIFF specification
repository. It follows the CLIFF organisation convention: English Conventional Commits, a
protected `main` release branch, a protected `dev` integration branch, annotated repository
tags and an English changelog.

## 1. Branches and pull requests

- `main` is the release branch. It is protected, always releasable, and receives merges only
  from `dev`.
- `dev` is the integration branch. It is protected, always buildable, and receives work through
  pull requests.
- Work branches start from `dev`:
  - `feature/<slug>` for features;
  - `fix/<slug>` for fixes;
  - `docs/<slug>`, `test/<slug>`, `refactor/<slug>`, `ci/<slug>`, `build/<slug>`,
    `chore/<slug>`, `perf/<slug>` or `style/<slug>` for the corresponding work;
  - `prototype/<slug>` for disposable experiments. Prototype code is not merged; reimplement it
    on `dev`.
- Work pull requests target `dev`. Release pull requests target `main` and merge `dev` into
  `main`.
- Branch names are lowercase ASCII with hyphen-separated words.
- Pull request titles use the same format as commit subjects.
- Merge commits are allowed; the `dev` to `main` release merge must be a merge commit, so
  `main` is not linear.
- Do not squash a release merge. Preserve the integration history.
- Delete a work branch after merge.
- `main` and `dev` prohibit direct pushes. A pull request must pass review and the repository
  checks before merge.

## 2. Commits

Format:

~~~text
[AI] type(scope): English description

English body explaining why and what changed.
~~~

- `[AI]` is optional. It is required for AI-generated or automated commits.
- `type` is one of: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `style`,
  `chore`, `build`, `ci`, `revert`.
- The description is imperative English, at most 72 characters, and does not end with a period.
- A commit contains one logical change.
- All version control artifacts are English. They must not contain Chinese, Japanese, Korean or
  other CJK text.

## 3. Versions and tags

- Releases follow Semantic Versioning. CLIFF specification releases use annotated tags
  `vX.Y.Z` with the message `cliff X.Y.Z`.
- Tags are created only on `main`, after the release merge from `dev`. Never tag `dev` or a
  work branch.
- The specification version and its normative changes are recorded in `CHANGELOG.md`.

## 4. Release process

1. Ensure `dev` is stable and the specification examples are consistent.
2. On `dev`, update the specification, examples and `CHANGELOG.md`.
3. Open a release pull request from `dev` to `main` and run the full review.
4. Merge with a merge commit. Do not squash the release merge.
5. On `main`, create the annotated tag `vX.Y.Z` and publish a GitHub Release.
6. No package is published from this repository.

## 5. Enforcement

- Branch protection requires pull requests, blocks direct pushes, force pushes and branch deletion,
  and applies to administrators.
- This repository has no always-run CI check at present. Review, the specification
  examples and the local consistency checks are the merge gate.
- Reviewers run the repository's local checks before approving a merge.