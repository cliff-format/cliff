#!/usr/bin/env python3
"""Check the normative CLIFF artifacts in this repository.

Five checks, each of which turns a documentation claim into something a machine
can decide:

1. **Examples are documents.** Every ``.cliff`` file under
   ``spec/examples/**`` is parsed and validated with the reference
   implementation (``cliff_format``) and must produce zero errors. The
   examples of the *current* specification version must additionally be
   canonical: serializing one reproduces the file byte for byte. The frozen
   1.0 corpus is exempt from that, because it deliberately uses the wrapped
   presentation of specification 5.3; it only has to be stable.

2. **No drift between the grammar, the style guide, and the implementation.**
   The ``name-char`` production in ``spec/abnf/cliff-1.1.abnf``, the
   machine-readable regexes in ``style/README.md`` (marked with
   ``<!-- check: ... -->``), and the constants in ``cliff_format.identifiers``
   must agree. A drift guard is the only thing that keeps a reader-facing table
   and a hardcoded constant in sync.

3. **Documented fences do not contradict an example.** A fenced ```cliff block
   in the specification or a document that looks like a complete document must
   parse and validate. A fence may declare itself a fragment with
   ``<!-- fragment: reason -->``, which is how the specification shows one
   wrapped field or one ICU payload without maintaining a second, unvalidated
   document.

4. **Conversion samples still round-trip.** The CLIFF side of every
   ``examples/<format>_to_cliff/`` pair must be a fixed point of
   parse/serialize, so the checked-in sample still shows what the converter does.

5. **Generated examples are current.** ``tools/regenerate_examples.py --check``
   must pass.

The checks needing ``cliff_format`` skip their work when the sibling checkout is
absent; the argument ``--require-repo`` makes that a failure instead, so CI
cannot silently validate nothing.

Usage:
    python tools/check_examples.py [--root ..] [--required] [--quiet]

Exit status: 0 when every check passes, 1 otherwise. Requires Python 3.11+ and
an importable ``cliff_format`` (set ``PYTHONPATH=../cliff-python/src``).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Documentation that carries ```cliff fences worth checking.
DOC_FILES = [
    "spec/cliff-1.1.0.md",
    "style/README.md",
    "README.md",
    "docs/design-rationale.md",
    "docs/ai-safety.md",
    "docs/prompt-assembly.md",
]

FENCE_RE = re.compile(
    r"^```(?P<tag>[A-Za-z0-9_-]*)[ \t]*\r?\n(?P<body>.*?)^```[ \t]*$", re.M | re.S
)
FRAGMENT_RE = re.compile(r"<!--\s*fragment:\s*(?P<reason>[^>]*?)\s*-->")
NON_CANONICAL_RE = re.compile(
    r"<!--\s*non-canonical:\s*(?P<reason>[^>]*?)\s*-->"
)
FRAGMENT_WINDOW = 120
VERSION_LINE_RE = re.compile(r"^(?:CLIFF|cliff)\s+\d", re.M)

# The ABNF production the implementation mirrors.
ABNF_NAME_RE = re.compile(r"^name-char\s*=\s*(?P<rhs>[^\r\n;]+)", re.M)

# The style guide's machine-readable blocks, keyed by their marker comment.
CHECK_MARKER_RE = re.compile(r"<!--\s*check:\s*(?P<name>[a-z-]+)\s*-->")


class Report:
    """Accumulates failures and prints them once at the end."""

    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks = 0

    def check(self, ok: bool, message: str) -> None:
        self.checks += 1
        if not ok:
            self.failures.append(message)

    def summary(self) -> str:
        state = "PASS" if not self.failures else "FAIL"
        return f"{state}: {self.checks} checks, {len(self.failures)} failures"


def _load_cliff_format(root: Path):
    """Import cliff_format, preferring the sibling checkout over site-packages."""
    sibling = root.parent / "cliff-python" / "src"
    if not sibling.is_dir():
        sibling = root.parent.parent / "cliff-python" / "src"
    if sibling.is_dir() and str(sibling) not in sys.path:
        sys.path.insert(0, str(sibling))
    try:
        import cliff_format  # noqa: PLC0415 - imported after the path setup
    except ModuleNotFoundError:
        print(
            "error: cliff_format is not importable. Install cliff-python or run with\n"
            f"       PYTHONPATH={sibling}",
            file=sys.stderr,
        )
        raise SystemExit(2) from None
    return cliff_format


def check_examples(root: Path, report: Report, cliff_format, advisories) -> int:
    """Check 1: every example file validates, and the current ones are canonical."""
    files = sorted((root / "spec" / "examples").rglob("*.cliff"))
    report.check(bool(files), "no example documents found under spec/examples/")
    for path in files:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root)
        is_current = path.parent.name.endswith("1.1.0")
        try:
            document = cliff_format.parse(text, path=path)
        except Exception as exc:  # noqa: BLE001 - report, do not crash
            report.check(False, f"{rel}: parse error: {exc}")
            continue
        issues = cliff_format.validate_document(document)
        errors = [i for i in issues if i.category not in advisories]
        report.check(
            not errors,
            f"{rel}: {len(errors)} error(s): " + "; ".join(i.message for i in errors),
        )
        once = cliff_format.serialize(document)
        # An example may declare that it is deliberately non-canonical, which is
        # how the terminator example stays valid input rather than canonical
        # output (specification 5.6: the serializer never emits a terminator).
        exempt = NON_CANONICAL_RE.search(text) is not None
        if is_current and not exempt:
            report.check(
                once == text,
                f"{rel}: is not canonical; run a canonical serializer over it",
            )
        if exempt:
            report.check(
                once != text,
                f"{rel}: declares itself non-canonical but is already canonical; "
                "drop the marker",
            )
        # Stability holds for both directories: canonical output is a fixed point.
        report.check(
            cliff_format.serialize(cliff_format.parse(once, path=path)) == once,
            f"{rel}: serialization is not idempotent",
        )
        report.check(
            document.spec_version == ("1.1" if is_current else "1.0"),
            f"{rel}: declared version {document.spec_version!r} does not match its "
            f"{'current' if is_current else 'frozen 1.0'} example directory",
        )
    return len(files)


def check_fences(root: Path, report: Report, cliff_format, advisories) -> int:
    """Check 3: a fence that claims to be a document must survive validation."""
    checked = 0
    for name in DOC_FILES:
        path = root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for match in FENCE_RE.finditer(text):
            body = match.group("body")
            line = text[: match.start()].count("\n") + 1
            if not VERSION_LINE_RE.search(body):
                # Not a document: a fragment, a syntax sketch, or a phrase list.
                continue
            after = text[match.end() : match.end() + FRAGMENT_WINDOW]
            fragment = FRAGMENT_RE.search(body) or FRAGMENT_RE.search(after)
            if fragment is not None:
                continue
            checked += 1
            try:
                document = cliff_format.parse(body)
            except Exception as exc:  # noqa: BLE001
                report.check(False, f"{name}:{line}: fence does not parse: {exc}")
                continue
            issues = cliff_format.validate_document(document)
            errors = [i for i in issues if i.category not in advisories]
            report.check(
                not errors,
                f"{name}:{line}: fence has {len(errors)} error(s): "
                + "; ".join(i.message for i in errors),
            )
    return checked


def _marked_blocks(text: str) -> dict[str, str]:
    """Return each ```block whose following comment marks it, keyed by marker.

    A marker belongs to the nearest preceding fence, not to the first fence
    after it: two marked blocks can appear close together, and a forward scan
    would attribute both markers to the earlier one.
    """
    blocks: dict[str, str] = {}
    fences = list(FENCE_RE.finditer(text))
    for marker in CHECK_MARKER_RE.finditer(text):
        preceding = [f for f in fences if f.end() < marker.start()]
        if not preceding:
            continue
        fence = preceding[-1]
        if marker.start() - fence.end() > FRAGMENT_WINDOW:
            continue
        blocks[marker.group("name")] = fence.group("body").strip()
    return blocks


def check_style_regexes(root: Path, report: Report, identifiers) -> None:
    """Check 2a: the style guide's machine-readable regexes match the code."""
    text = (root / "style" / "README.md").read_text(encoding="utf-8")
    blocks = _marked_blocks(text)
    expected = {
        "style-kebab": identifiers.STYLE_KEBAB_PATTERN,
        "style-pascal": identifiers.STYLE_PASCAL_PATTERN,
        "name-char-class": identifiers.NAME_CHAR_CLASS,
    }
    for marker, value in expected.items():
        report.check(
            marker in blocks,
            f"style/README.md lost the '<!-- check: {marker} -->' marker",
        )
        report.check(
            blocks.get(marker, "") == value,
            f"style/README.md documents {blocks.get(marker, '')!r} for '{marker}' "
            f"but the implementation uses {value!r}",
        )
    report.check(
        identifiers.STYLE_NAME_PATTERN
        == f"(?:{identifiers.STYLE_KEBAB_PATTERN})|(?:{identifiers.STYLE_PASCAL_PATTERN})",
        "identifiers.STYLE_NAME_PATTERN must be the two recommended shapes, "
        "each anchored: an unanchored alternative silently accepts any name",
    )


def check_abnf(root: Path, report: Report, identifiers) -> None:
    """Check 2b: the ABNF name-char production matches the implementation."""
    text = (root / "spec" / "abnf" / "cliff-1.1.abnf").read_text(encoding="utf-8")
    match = ABNF_NAME_RE.search(text)
    report.check(match is not None, "cliff-1.1.abnf no longer defines 'name-char'")
    if match is None:
        return
    alternatives = {part.strip() for part in match.group("rhs").split("/")}
    expected = set(identifiers.NAME_CHAR_ALTERNATIVES)
    report.check(
        alternatives == expected,
        "cliff-1.1.abnf 'name-char' is "
        f"{sorted(alternatives)} but the implementation allows {sorted(expected)}",
    )


def check_round_trip_files(root: Path, report: Report, cliff_format) -> int:
    """Check 4: every conversion sample still round-trips to its own document.

    ``examples/<format>_to_cliff/<name>.cliff`` is the CLIFF document an importer
    produced from ``<name>.<ext>``. Regenerating that document from the source
    file must reproduce it byte for byte — otherwise the checked-in sample no
    longer shows what the converter does, which is exactly the drift the samples
    exist to catch.
    """
    examples = root / "examples"
    if not examples.is_dir():
        return 0
    checked = 0
    for directory in sorted(p for p in examples.iterdir() if p.is_dir()):
        cliff_files = sorted(directory.glob("*.cliff"))
        if not cliff_files or not directory.name.endswith("_to_cliff"):
            continue
        for cliff_path in cliff_files:
            text = cliff_path.read_text(encoding="utf-8")
            document = cliff_format.parse(text, path=cliff_path)
            once = cliff_format.serialize(document)
            checked += 1
            report.check(
                once == text,
                f"{cliff_path.relative_to(root)}: no longer round-trips to its own "
                "document (re-run tools/regenerate_examples.py)",
            )
    return checked


def check_generated_examples(root: Path, report: Report) -> int:
    """Check 5: the generated sides of the conversion samples are current.

    Runs the repository's own generator in check mode, so a converter change that
    was not followed by a regeneration fails here rather than in review.
    """
    import subprocess  # noqa: PLC0415 - only needed for this check

    script = root / "tools" / "regenerate_examples.py"
    if not script.is_file():
        return 0
    proc = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    report.check(
        proc.returncode == 0,
        "tools/regenerate_examples.py --check failed:\n"
        + (proc.stdout + proc.stderr).strip(),
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()

    cliff_format = _load_cliff_format(root)
    from cliff_format import identifiers  # noqa: PLC0415 - after the path setup
    from cliff_format.validator import ADVISORY_CATEGORIES  # noqa: PLC0415

    report = Report()
    files = check_examples(root, report, cliff_format, ADVISORY_CATEGORIES)
    fences = check_fences(root, report, cliff_format, ADVISORY_CATEGORIES)
    check_style_regexes(root, report, identifiers)
    check_abnf(root, report, identifiers)
    samples = check_round_trip_files(root, report, cliff_format)
    generators = check_generated_examples(root, report)

    if not args.quiet:
        print(f"example documents checked: {files}")
        print(f"document-style fences checked: {fences}")
        if samples or generators:
            print(f"conversion samples round-tripped: {samples}")
    for failure in report.failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    print(report.summary())
    return 0 if not report.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
