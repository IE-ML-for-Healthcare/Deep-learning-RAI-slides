#!/usr/bin/env python3
"""Commit scope guard for the deck. Standard library only.

Rule: a commit that changes a slide in index.html must name that slide in its message.

A slide counts as changed when its top-level <section> differs, or when a CSS rule
scoped to its id (a selector containing #<id>) differs. Whitespace, comments and
line endings are ignored. Name a slide by writing its id anywhere in the message,
or add a trailer such as:

    Slides: topic-one-overview, topic-two-detail
    Slides: all (reflow after the shared stylesheet change)

Why: a whole-file copy from a stale worktree reverts other agents' slides without
any merge conflict. Such a commit changes slides its message does not name, so it
fails here, locally in the agent-branch commit-msg hook and in pull-request CI.
Direct commits on main are exempt from message policy, but still run product QA.

Usage
    python scripts/check_commit_scope.py --commit-msg .git/COMMIT_EDITMSG   # hook mode
    python scripts/check_commit_scope.py --range main..HEAD                  # CI and manual
    python scripts/check_commit_scope.py --range main..HEAD --list           # show slides per commit

Limits: JavaScript and class-only CSS changes are not slide-scoped, so they are not
checked. Commits older than this script are never judged in range mode.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import Counter

DECK = "index.html"
SCRIPT = "scripts/check_commit_scope.py"

TOKEN_RE = re.compile(
    r"<script\b.*?</script\s*>|<style\b.*?</style\s*>|<(/?)section\b([^>]*)>",
    re.I | re.S,
)
ID_ATTR_RE = re.compile(r"""\bid\s*=\s*["']([^"']+)["']""", re.I)
STYLE_RE = re.compile(r"<style\b[^>]*>(.*?)</style\s*>", re.I | re.S)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
CSS_ID_RE = re.compile(r"#(-?[A-Za-z_][\w-]*)")
ALL_RE = re.compile(r"^\s*Slides:\s*all\s*\((.+)\)\s*$", re.I | re.M)
ALL_REASON_MIN = 8


def normalise(text: str) -> str:
    text = re.sub(r"\s+", " ", text.replace("\r\n", "\n").replace("\r", "\n")).strip()
    return re.sub(r">\s+<", "><", text)


def split_sections(html: str) -> dict[str, str]:
    """Return {slide id: normalised markup} for top-level sections."""
    html = HTML_COMMENT_RE.sub("", html)
    slides: dict[str, str] = {}
    depth = 0
    start = 0
    slide_id = ""
    unnamed = 0
    for match in TOKEN_RE.finditer(html):
        if match.group(2) is None:  # script or style block, skipped for depth
            continue
        closing = bool(match.group(1))
        if not closing:
            if depth == 0:
                start = match.start()
                found = ID_ATTR_RE.search(match.group(2))
                if found:
                    slide_id = found.group(1)
                else:
                    unnamed += 1
                    slide_id = f"(slide without id, position {unnamed})"
            depth += 1
        elif depth > 0:
            depth -= 1
            if depth == 0:
                slides[slide_id] = normalise(html[start:match.end()])
    return slides


def css_rules(css: str, context: str = "") -> list[tuple[str, str]]:
    """Flatten CSS into (selector with at-rule context, normalised body) pairs."""
    css = CSS_COMMENT_RE.sub("", css)
    rules: list[tuple[str, str]] = []
    position = 0
    while True:
        open_at = css.find("{", position)
        if open_at == -1:
            break
        prelude = normalise(css[position:open_at])
        depth = 1
        index = open_at + 1
        while index < len(css) and depth:
            if css[index] == "{":
                depth += 1
            elif css[index] == "}":
                depth -= 1
            index += 1
        body = css[open_at + 1:index - 1]
        if prelude.startswith("@") and "{" in body:
            rules.extend(css_rules(body, f"{context}{prelude} "))
        else:
            rules.append((f"{context}{prelude}", normalise(body)))
        position = index
    return rules


def split_top_level(selector: str) -> list[str]:
    """Split a selector list on commas that are outside parentheses."""
    parts, depth, current = [], 0, ""
    for char in selector:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += char
    parts.append(current.strip())
    return parts


def project(selector: str, slide_id: str, ids: set[str]) -> str:
    """Reduce a selector to the part that targets one slide.

    Slides often share a rule, for example :is(#a, #b, #c) .card. Adding or removing
    a neighbour must not count as a change to this slide, so other slide ids and
    their commas are dropped from the projection.
    """
    own = re.compile(rf"#{re.escape(slide_id)}(?![\w-])")
    kept = [part for part in split_top_level(selector) if own.search(part)]
    text = ", ".join(kept)
    # Only ids present in this selector can affect its projection. Iterating all
    # deck ids recompiles thousands of irrelevant regexes on a large deck.
    neighbours = (set(CSS_ID_RE.findall(text)) & ids) - {slide_id}
    for other in sorted(neighbours, key=len, reverse=True):
        pattern = re.escape(other)
        text = re.sub(rf"\s*,\s*#{pattern}(?![\w-])", "", text)
        text = re.sub(rf"#{pattern}(?![\w-])\s*,\s*", "", text)
    return re.sub(r":(?:is|where)\(\s*(#[\w-]+)\s*\)", r"\1", text)


def scoped_css(html: str, ids: set[str]) -> dict[str, Counter]:
    """Return {slide id: multiset of CSS rules whose selector mentions #id}."""
    buckets: dict[str, Counter] = {}
    for block in STYLE_RE.findall(HTML_COMMENT_RE.sub("", html)):
        for selector, body in css_rules(block):
            mentioned = {m for m in CSS_ID_RE.findall(selector) if m in ids}
            for slide_id in mentioned:
                key = f"{project(selector, slide_id, ids)} {{ {body} }}"
                buckets.setdefault(slide_id, Counter())[key] += 1
    return buckets


def changed_slides(old: str | None, new: str | None) -> list[str]:
    """Return sorted ids of slides added, removed, or modified between two decks."""
    old_sections = split_sections(old) if old else {}
    new_sections = split_sections(new) if new else {}
    ids = set(old_sections) | set(new_sections)
    old_css = scoped_css(old, ids) if old else {}
    new_css = scoped_css(new, ids) if new else {}
    changed = set()
    for slide_id in ids:
        if old_sections.get(slide_id) != new_sections.get(slide_id):
            changed.add(slide_id)
        elif old_css.get(slide_id, Counter()) != new_css.get(slide_id, Counter()):
            changed.add(slide_id)
    return sorted(changed)


def clean_message(message: str) -> str:
    return "\n".join(line for line in message.splitlines() if not line.startswith("#"))


def uncovered(ids: list[str], message: str) -> list[str]:
    """Return changed ids that the message does not cover."""
    message = clean_message(message)
    allowed = ALL_RE.search(message)
    if allowed and len(allowed.group(1).strip()) >= ALL_REASON_MIN:
        return []
    return [
        slide_id for slide_id in ids
        if not re.search(rf"(?<![\w-]){re.escape(slide_id)}(?![\w-])", message)
    ]


def report(ids: list[str], missing: list[str], label: str) -> str:
    shown = ", ".join(missing[:12]) + (f" and {len(missing) - 12} more" if len(missing) > 12 else "")
    return (
        f"commit scope: {label} changes {len(ids)} slide(s) in {DECK} "
        f"but its message does not name: {shown}\n"
        "  If you meant to change them, add a trailer to the message, for example:\n"
        f"    Slides: {', '.join(missing[:3])}\n"
        "  If you did not, your index.html is probably a stale copy. Do not copy files between\n"
        "  worktrees. Merge the latest main into your branch, redo only your own change, and\n"
        "  commit again. For a deliberate deck-wide change, add: Slides: all (<reason>)"
    )


def git(*args: str) -> str | None:
    result = subprocess.run(
        ["git", "--no-optional-locks", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return result.stdout if result.returncode == 0 else None


def check_commit_msg(path: str) -> int:
    if git("rev-parse", "-q", "--verify", "MERGE_HEAD"):
        return 0  # merge commits are reviewed through their parents
    with open(path, encoding="utf-8", errors="replace") as handle:
        message = handle.read()
    amend = "amend" in os.environ.get("GIT_REFLOG_ACTION", "")
    base = "HEAD~1" if amend else "HEAD"
    old = git("show", f"{base}:{DECK}")
    new = git("show", f":{DECK}")
    if new is None or old == new:
        return 0
    ids = changed_slides(old, new)
    missing = uncovered(ids, message)
    if missing:
        print(report(ids, missing, "this commit"), file=sys.stderr)
        return 1
    return 0


def intro_commit() -> str | None:
    out = git("log", "--diff-filter=A", "--format=%H", "-1", "--", SCRIPT)
    return (out or "").strip() or None


def check_range(spec: str, list_only: bool) -> int:
    base = spec.split("..")[0] if ".." in spec else spec
    if not base or set(base) == {"0"} or git("rev-parse", "-q", "--verify", f"{base}^{{commit}}") is None:
        print(f"commit scope: base '{base}' is not available, nothing to check")
        return 0
    commits = (git("rev-list", "--reverse", "--no-merges", spec) or "").split()
    intro = intro_commit()
    failures = 0
    for commit in commits:
        if intro and subprocess.run(
            ["git", "--no-optional-locks", "merge-base", "--is-ancestor", intro, commit],
            capture_output=True,
        ).returncode != 0:
            continue  # older than the guard, never judged
        old = git("show", f"{commit}^:{DECK}")
        new = git("show", f"{commit}:{DECK}")
        if old == new or new is None:
            continue
        ids = changed_slides(old, new)
        message = git("log", "-1", "--format=%B", commit) or ""
        missing = uncovered(ids, message)
        short = commit[:7]
        if list_only:
            print(f"{short}: {', '.join(ids) if ids else '(no slide changes)'}"
                  + (f"  UNNAMED: {', '.join(missing)}" if missing else ""))
        if missing:
            failures += 1
            if not list_only:
                print(report(ids, missing, f"commit {short}"), file=sys.stderr)
    if failures:
        return 1
    print(f"commit scope: {len(commits)} commit(s) checked, all slide changes are named")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--commit-msg", metavar="FILE", help="hook mode: message file of the commit in progress")
    mode.add_argument("--range", metavar="BASE..HEAD", help="check every commit in a range")
    parser.add_argument("--list", action="store_true", help="with --range, print slides per commit")
    args = parser.parse_args(argv)
    if args.commit_msg:
        return check_commit_msg(args.commit_msg)
    return check_range(args.range, args.list)


if __name__ == "__main__":
    sys.exit(main())
