#!/usr/bin/env python3
"""Regenerate or verify base64 download payloads in Reveal.js decks.

Every download control is an anchor with a `download` filename, a
`data-download-source` repository path, and an `href` holding the full file as
a base64 `data:` URI, so the file saves correctly over `file://` and HTTP.

    python scripts/sync_downloads.py            # rewrite stale payloads
    python scripts/sync_downloads.py --check    # fail if any payload is stale
    python scripts/sync_downloads.py deck.html  # limit to specific files

Only the `href` attribute value changes; the rest of the HTML is untouched.
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECKS = ("index.html", "slide_patterns.html")
ANCHOR = re.compile(r"<a\b[^>]*\bdata-download-source\s*=\s*\"[^\"]*\"[^>]*>", re.IGNORECASE | re.DOTALL)
SOURCE = re.compile(r"\bdata-download-source\s*=\s*\"([^\"]*)\"", re.IGNORECASE)
HREF = re.compile(r"(\bhref\s*=\s*\")([^\"]*)(\")", re.IGNORECASE)
DOWNLOAD = re.compile(r"\bdownload\s*=\s*\"([^\"]+)\"", re.IGNORECASE)

MEDIA_TYPES = {
    ".md": "text/markdown;charset=utf-8",
    ".txt": "text/plain;charset=utf-8",
    ".csv": "text/csv;charset=utf-8",
    ".json": "application/json",
    ".py": "text/x-python;charset=utf-8",
    ".ipynb": "application/x-ipynb+json",
}


def media_type(path: Path) -> str:
    return MEDIA_TYPES.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def data_uri(path: Path) -> str:
    return f"data:{media_type(path)};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def process(deck: Path, check: bool) -> tuple[int, int, list[str]]:
    text = deck.read_text(encoding="utf-8")
    errors: list[str] = []
    stale = 0
    total = 0

    def fix(match: re.Match[str]) -> str:
        nonlocal stale, total
        tag = match.group(0)
        total += 1
        source_ref = SOURCE.search(tag).group(1)
        if not DOWNLOAD.search(tag):
            errors.append(f"{deck.name}: anchor for {source_ref!r} has no download filename")
            return tag
        source = (ROOT / source_ref).resolve()
        if ROOT not in source.parents or not source.is_file():
            errors.append(f"{deck.name}: download source not found inside the repository: {source_ref}")
            return tag
        expected = data_uri(source)
        href = HREF.search(tag)
        if href is None:
            errors.append(f"{deck.name}: anchor for {source_ref!r} has no href")
            return tag
        if href.group(2) == expected:
            return tag
        stale += 1
        return tag[: href.start(2)] + expected + tag[href.end(2):]

    updated = ANCHOR.sub(fix, text)
    if not check and updated != text and not errors:
        deck.write_text(updated, encoding="utf-8", newline="")
    return total, stale, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("decks", nargs="*", help="HTML files, default: index.html and slide_patterns.html")
    parser.add_argument("--check", action="store_true", help="report stale payloads without writing")
    args = parser.parse_args()
    decks = [Path(d).resolve() for d in args.decks] or [ROOT / d for d in DEFAULT_DECKS if (ROOT / d).exists()]
    failed = False
    for deck in decks:
        total, stale, errors = process(deck, args.check)
        for error in errors:
            print(f"ERROR {error}")
        failed = failed or bool(errors) or (args.check and stale > 0)
        verb = "stale" if args.check else "updated"
        print(f"{deck.name}: {total} download controls, {stale} {verb}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
