#!/usr/bin/env python3
"""Regenerate the embedded group roster used by the group and student picker.

The picker (`.s-picker` in ie-scitech-reveal.css, `initGroupPicker` in
index.html) reads its data from a JSON script tag embedded directly in the
deck, so the deck has zero runtime dependency on an external file and keeps
working over `file://`:

    <!-- GROUP ROSTER DATA START -->
    <script type="application/json" id="ie-group-roster">
    ...generated JSON, and nothing else...
    </script>
    <!-- GROUP ROSTER DATA END -->

Source of truth: `groups.csv` in the repository root, the raw group-members
export downloaded from the university system, unmodified. Columns used:
"Group Code", "First Name", "Last Name". Blank rows (a group with an empty
seat) are skipped. The group number is the trailing digits of the group
code, for example "New_gc_Group_gc_1" becomes group 1. Each student is
displayed as their first given name plus the initial of their first
surname, for example "Nicolas O.".

    python scripts/sync_group_roster.py             # rewrite the embedded roster
    python scripts/sync_group_roster.py --check      # fail if the deck is stale
    python scripts/sync_group_roster.py --source groups.csv --deck index.html

To use a new roster for a new course or a new group set: replace
groups.csv with the new export (same column headers) and rerun this script.
No manual reformatting is needed.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "groups.csv"
DEFAULT_DECKS = ("slide_patterns.html",)  # change to your course deck once you copy the picker into it

START = "<!-- GROUP ROSTER DATA START -->"
END = "<!-- GROUP ROSTER DATA END -->"
BLOCK = re.compile(
    re.escape(START)
    + r'(\s*<script type="application/json" id="ie-group-roster">)(.*?)(</script>\s*)'
    + re.escape(END),
    re.DOTALL,
)


def group_number(group_code: str) -> str:
    match = re.search(r"(\d+)\s*$", group_code)
    if not match:
        raise ValueError(f"cannot read a group number from group code: {group_code!r}")
    return match.group(1)


def display_name(first: str, last: str) -> str:
    first_token = first.strip().split()[0].title() if first.strip() else ""
    last_token = last.strip().split()[0] if last.strip() else ""
    initial = f"{last_token[0].upper()}." if last_token else ""
    return f"{first_token} {initial}".strip()


def load_roster(source: Path) -> list[dict[str, str]]:
    roster: list[dict[str, str]] = []
    with source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"Group Code", "First Name", "Last Name"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{source.name}: missing expected column(s): {', '.join(sorted(missing))}")
        for row in reader:
            code = (row.get("Group Code") or "").strip()
            first = (row.get("First Name") or "").strip()
            last = (row.get("Last Name") or "").strip()
            if not code or (not first and not last):
                continue  # blank placeholder seat in the export
            roster.append({"group": group_number(code), "name": display_name(first, last)})
    if not roster:
        raise SystemExit(f"{source.name}: no students found, nothing to embed")
    return roster


def build_payload(roster: list[dict[str, str]]) -> str:
    groups = sorted({int(entry["group"]) for entry in roster})
    payload = {"groupCount": len(groups), "students": roster}
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def process(deck: Path, payload: str, check: bool) -> tuple[bool, list[str]]:
    text = deck.read_text(encoding="utf-8")
    errors: list[str] = []
    match = BLOCK.search(text)
    if not match:
        errors.append(f"{deck.name}: GROUP ROSTER DATA markers not found, add the picker markup first")
        return False, errors

    current_payload = match.group(2).strip()
    if current_payload == payload:
        return False, errors

    if not check:
        replacement = f"{match.group(1)}\n{payload}\n{match.group(3)}"
        text = text[: match.start(1)] + replacement + text[match.end(3):]
        deck.write_text(text, encoding="utf-8", newline="")
    return True, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="roster CSV, default: groups.csv")
    parser.add_argument("--deck", action="append", dest="decks", help="deck to update, default: index.html")
    parser.add_argument("--check", action="store_true", help="report a stale roster without writing")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    if not source.is_file():
        print(f"ERROR roster source not found: {source}")
        return 1

    roster = load_roster(source)
    payload = build_payload(roster)
    decks = [Path(d).resolve() for d in args.decks] if args.decks else [ROOT / d for d in DEFAULT_DECKS if (ROOT / d).exists()]

    failed = False
    for deck in decks:
        stale, errors = process(deck, payload, args.check)
        for error in errors:
            print(f"ERROR {error}")
        failed = failed or bool(errors) or (args.check and stale)
        verb = "stale" if args.check and stale else ("updated" if stale else "already current")
        print(f"{deck.name}: {len(roster)} students, {len({e['group'] for e in roster})} groups, {verb}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
