#!/usr/bin/env python3
"""Select and run validation from the actual diff, without weakening slide checks.

    python scripts/validate_changes.py                 # staged, unstaged and untracked
    python scripts/validate_changes.py --base main     # also include branch changes
    python scripts/validate_changes.py --slides <ids>   # include specific slides
    python scripts/validate_changes.py --full          # full local regression
    python scripts/validate_changes.py --plan          # inspect selection without running
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from html import unescape
import json
import os
import posixpath
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import unquote, urlsplit

from check_commit_scope import CSS_ID_RE, STYLE_RE, css_rules, split_top_level
from qa_common import ROOT

TOKENS = re.compile(r"<!--.*?-->|<script\b.*?</script\s*>|<style\b.*?</style\s*>|<(/?)section\b([^>]*)>", re.I | re.S)
ID = re.compile(r'''\bid\s*=\s*["']([^"']+)["']''', re.I)
ATTR = re.compile(r'''\b(?:src|href|poster|data-src|data-background(?:-(?:image|video|iframe))?|data-download-source)\s*=\s*["']([^"']+)["']''', re.I)
URL = re.compile(r'''url\(\s*["']?([^\s)'" ]+)["']?\s*\)''', re.I)
SHARED = {"scripts/download_controls.py", "download-exceptions.json", "ie-scitech-reveal.css", "ie-reveal-fit.js", "slide-aliases.js", "deck.config.json",
          "requirements-qa.txt", "environment.yml", "scripts/qa_common.py", "scripts/check_browser_qa.py"}
TESTS = {"scripts/download_controls.py": ["test_download_controls"], "download-exceptions.json": ["test_download_controls"], "scripts/check_deck.py": ["test_tools"], "scripts/sync_downloads.py": ["test_tools"],
         "scripts/check_commit_scope.py": ["test_commit_scope", "test_validate_changes"],
         "scripts/check_browser_qa.py": ["test_tools", "test_browser_qa"],
         "scripts/validate_changes.py": ["test_validate_changes"],
         "scripts/release_slice.py": ["test_release_slice"]}


@dataclass
class Plan:
    files: list[str]
    slides: list[str] = field(default_factory=list)
    full_browser: bool = False
    gallery: bool = False
    static: bool = False
    downloads: bool = False
    roster: bool = False
    tests: list[str] = field(default_factory=list)
    full_tests: bool = False
    reasons: list[str] = field(default_factory=list)


def deck_parts(html: str) -> tuple[dict[str, str], str]:
    """Keep exact section text, ignoring only line-ending differences."""
    html = html.replace("\r\n", "\n").replace("\r", "\n")
    sections, outside, depth, start, end, sid = {}, [], 0, 0, 0, ""
    for match in TOKENS.finditer(html):
        if match.group(2) is None:
            continue
        if not match.group(1):
            if depth == 0:
                start = match.start()
                found = ID.search(match.group(2))
                sid = found.group(1) if found else ""
                outside.append(html[end:start])
            depth += 1
        elif depth:
            depth -= 1
            if depth == 0:
                if not sid or sid in sections:
                    raise ValueError("Slide ids are missing or duplicated; use full validation")
                sections[sid] = html[start:match.end()]
                end = match.end()
    if depth:
        raise ValueError("Unbalanced sections; use full validation")
    outside.append(html[end:])
    shell = STYLE_RE.sub("", "".join(outside))
    shell = re.sub(r"<!--.*?-->|<title\b.*?</title\s*>", "", shell, flags=re.I | re.S)
    shell = re.sub(r">\s+<", "><", shell)
    return sections, re.sub(r"\s+", " ", shell).strip()


def css_impact(old: str, new: str, ids: set[str]) -> tuple[set[str], bool]:
    def rules(html):
        return [rule for css in STYLE_RE.findall(html) for rule in css_rules(css)]
    old_rules, new_rules = rules(old), rules(new)
    before, after = Counter(old_rules), Counter(new_rules)
    changes = (before - after) + (after - before)
    common = before & after
    def common_order(sequence):
        remaining, result = common.copy(), []
        for rule in sequence:
            if remaining[rule]:
                result.append(rule)
                remaining[rule] -= 1
        return result
    if common_order(old_rules) != common_order(new_rules):
        changes.update(common)
    imports = lambda html: re.findall(r"@(?:import|charset|namespace)\b[^;]*;", "\n".join(STYLE_RE.findall(html)))
    if imports(old) != imports(new):
        return set(), True
    affected = set()
    for selector, _ in changes:
        # Attribute values and feature-query conditions are not slide anchors
        if re.search(r"@(?:supports|scope|keyframes)\b|\\", selector):
            return affected, True
        selector = re.sub(r"\[[^\]]*\]", "", selector)
        # Only a positive slide-id anchor proves a rule is local
        selector = re.sub(r":(?:is|where)\((#[\w-]+(?:\s*,\s*#[\w-]+)*)\)",
                          lambda m: m.group(1).replace(",", " "), selector)
        for part in split_top_level(selector):
            anchors = set(CSS_ID_RE.findall(part)) & ids
            if not anchors or re.search(r":[\w-]+\(|[+~]", part):
                return affected, True
            affected.update(anchors)
    return affected, False


def local_refs(text: str) -> set[str]:
    refs = set()
    values = ATTR.findall(text) + URL.findall(text)
    values += re.findall(r'''@import\s*["']([^"']+)["']''', text, flags=re.I)
    for srcset in re.findall(r'''\bsrcset\s*=\s*["']([^"']+)["']''', text, flags=re.I):
        values.extend(item.strip().split()[0] for item in srcset.split(",") if item.strip())
    for value in values:
        url = urlsplit(unescape(value))
        if not url.scheme and not url.netloc and url.path:
            refs.add(posixpath.normpath(unquote(url.path)))
    return refs


def css_dependencies(root: Path, css_files: set[str]) -> set[str]:
    """Follow local stylesheet imports, resolving assets relative to each sheet."""
    pending, seen, assets = list(css_files), set(), set()
    root = root.resolve()
    while pending:
        relative = pending.pop()
        path = (root / relative).resolve()
        if path in seen or not path.is_relative_to(root) or not path.is_file():
            continue
        seen.add(path)
        for ref in local_refs(path.read_text(encoding="utf-8")):
            resolved = (path.parent / ref).resolve()
            if not resolved.is_relative_to(root):
                continue
            dependency = resolved.relative_to(root).as_posix()
            assets.add(dependency)
            if resolved.suffix.lower() == ".css":
                pending.append(dependency)
    return assets


def make_plan(files: list[str], old: str, new: str, full: bool = False, shared_assets: set[str] | None = None,
              gallery_assets: set[str] | None = None, available_tests: set[str] | None = None) -> Plan:
    plan = Plan(sorted(set(files)))
    try:
        before, old_shell = deck_parts(old)
        after, new_shell = deck_parts(new)
    except ValueError as exc:
        before, after, old_shell, new_shell = {}, {}, "", ""
        plan.full_browser = True
        plan.reasons.append(str(exc))
    ids = set(before) | set(after)
    affected = set()
    for path in plan.files:
        if path in (gallery_assets or set()):
            plan.gallery = True
            plan.reasons.append(f"Pattern gallery dependency changed: {path}")
        if path == "index.html":
            affected.update(sid for sid in ids if before.get(sid) != after.get(sid))
            scoped, shared_css = css_impact(old, new, ids)
            affected.update(scoped)
            if old_shell != new_shell or shared_css:
                plan.full_browser = True
                plan.reasons.append("Deck runtime, shared inline style or outer structure changed")
            if list(before) != list(after):
                def neighbours(order, sid):
                    if sid not in order:
                        return ()
                    i = order.index(sid)
                    return tuple(order[max(0, i - 1):i + 2])
                for sid in ids:
                    if neighbours(list(before), sid) != neighbours(list(after), sid):
                        affected.add(sid)
                plan.reasons.append("Slide order changed: include affected boundaries")
        elif path in SHARED or path.startswith(("logos/", "backgrounds/")) or Path(path).suffix in {".css", ".js"}:
            plan.full_browser = plan.gallery = True
            plan.reasons.append(f"Shared rendering dependency changed: {path}")
        elif path == "slide_patterns.html":
            plan.gallery = True
        else:
            referenced = {sid for sid, section in after.items() if path in local_refs(section)}
            affected.update(referenced)
            if referenced:
                plan.reasons.append(f"Validate consumers of changed asset or download: {path}")
            elif path in local_refs(old) | local_refs(new) | (shared_assets or set()) or (path.startswith("media/") and path in old + new):
                plan.full_browser = plan.gallery = True
                plan.reasons.append(f"Dependency has no provable slide scope: {path}")
        if path.startswith("scripts/") or path.startswith(".githooks/") or path == "requirements-qa.txt":
            if path in TESTS:
                plan.tests.extend(TESTS[path])
            else:
                plan.full_tests = True
        elif path.startswith("tests/test_") and path.endswith(".py"):
            plan.tests.append(Path(path).stem)
        if path == "groups.csv" or path == "scripts/sync_group_roster.py":
            plan.roster = True
    # Removed sections need a structural check, not an invalid browser id
    plan.slides = sorted(affected & set(after))
    plan.static = bool(affected or plan.full_browser or plan.gallery or plan.tests or plan.full_tests)
    plan.downloads = plan.static
    if full:
        plan.full_browser = plan.gallery = plan.static = plan.downloads = plan.roster = plan.full_tests = True
        plan.reasons.append("Full regression explicitly requested")
    if "test_template_standards" in (available_tests or set()) and (
            plan.full_browser or "scripts/check_deck.py" in plan.files or "slide_patterns.html" in plan.files):
        plan.tests.append("test_template_standards")
    plan.tests = sorted(set(plan.tests))
    return plan


def git(*args: str) -> str:
    result = subprocess.run(["git", "--no-optional-locks", *args], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


def qa_python() -> tuple[str, dict[str, str]]:
    """Reuse this clone's existing environment, including its linked worktrees."""
    expected = re.search(r"^playwright==([^\s]+)", (ROOT / "requirements-qa.txt").read_text(encoding="utf-8"), re.M)
    if expected is None:
        raise RuntimeError("requirements-qa.txt must pin a Playwright version")
    roots = [ROOT] + [Path(line[9:]) for line in git("worktree", "list", "--porcelain").splitlines()
                      if line.startswith("worktree ")]
    candidates = [os.environ.get("IE_QA_PYTHON", "")]
    for root in roots:
        candidates += [str(root / folder / suffix) for folder in (".venv-reveal-qa", ".venv-reveal-qa-native")
                       for suffix in ("Scripts/python.exe", "bin/python")]
    candidates.append(sys.executable)
    for candidate in dict.fromkeys(candidates):
        if not candidate or not Path(candidate).is_file():
            continue
        try:
            probe = subprocess.run([candidate, "-c", "from pathlib import Path; from importlib.metadata import version; "
                                    f"assert version('playwright') == {expected.group(1)!r}; "
                                    "from playwright.sync_api import sync_playwright; "
                                    "p=sync_playwright().start(); ok=Path(p.chromium.executable_path).is_file(); p.stop(); "
                                    "raise SystemExit(0 if ok else 1)"], capture_output=True, timeout=20)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.returncode == 0:
            env = os.environ.copy()
            if not env.get("IE_QA_CDN_MIRROR"):
                for root in roots:
                    mirror = root / ".cache/cdn-mirror"
                    if (mirror / "node_modules").is_dir():
                        env["IE_QA_CDN_MIRROR"] = str(mirror)
                        break
            return candidate, env
    raise RuntimeError("No ready QA environment with the pinned Playwright version in this clone or its worktrees. "
                       "Run bash scripts/setup_browser_qa.sh once")


def run_check(name: str, command: list[str], out: Path, env: dict) -> dict:
    start = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    log = result.stdout + result.stderr
    (out / f"{name}.log").write_text(log, encoding="utf-8")
    elapsed = round(time.perf_counter() - start, 3)
    print(f"{'PASS' if result.returncode == 0 else 'FAIL'} {name}: {elapsed:.3f} s", flush=True)
    if result.returncode:
        print(log)
    return {"name": name, "seconds": elapsed, "exit_code": result.returncode, "command": command}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default="HEAD", help="compare this commit with current files, including untracked files")
    parser.add_argument("--slides", default="", help="extra slide ids; cannot narrow shared-change validation")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--plan", action="store_true", help="print the plan without running checks")
    parser.add_argument("--out", default="tmp/validation")
    args = parser.parse_args()
    started = time.perf_counter()
    files = [p for p in git("diff", "--name-only", "--no-renames", "-z", args.base, "--").split("\0") if p]
    files += [p for p in git("ls-files", "--others", "--exclude-standard", "-z").split("\0") if p]
    old = git("show", f"{args.base}:index.html")
    new = (ROOT / "index.html").read_text(encoding="utf-8")
    gallery_assets = local_refs((ROOT / "slide_patterns.html").read_text(encoding="utf-8"))
    css_files = {ref for ref in local_refs(old) | local_refs(new) | gallery_assets if ref.endswith(".css")}
    shared_assets = css_dependencies(ROOT, css_files | {"ie-scitech-reveal.css"})
    available_tests = {path.stem for path in (ROOT / "tests").glob("test_*.py")}
    plan = make_plan(files, old, new, args.full, shared_assets, gallery_assets, available_tests)
    plan.slides = sorted(set(plan.slides) | {s.strip() for s in args.slides.split(",") if s.strip()})
    if plan.slides:
        plan.static = plan.downloads = True
    print(json.dumps(asdict(plan), indent=2), flush=True)
    if args.plan:
        return 0
    out = (ROOT / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    jobs = [("diff", ["git", "--no-optional-locks", "diff", "--check", args.base, "--"])]
    py, env = sys.executable, os.environ.copy()
    if plan.static:
        jobs.append(("static", [py, "scripts/check_deck.py"]))
    if plan.downloads:
        jobs.append(("downloads", [py, "scripts/sync_downloads.py", "--check"]))
    if plan.roster:
        jobs.append(("roster", [py, "scripts/sync_group_roster.py", "--check"]))
    if plan.full_tests:
        jobs.append(("tests", [py, "-m", "unittest", "discover", "-s", "tests"]))
    elif plan.tests:
        jobs.append(("tests", [py, "-m", "unittest", *["tests." + m for m in plan.tests]]))
    if args.base != "HEAD":
        jobs.append(("commit-scope", [py, "scripts/check_commit_scope.py", "--range", f"{args.base}..HEAD"]))
    if plan.full_browser or plan.slides or plan.gallery:
        browser_py, env = qa_python()
        print(f"Reusing QA Python: {browser_py}", flush=True)
        if plan.full_browser or plan.slides:
            command = [browser_py, "scripts/check_browser_qa.py", "--strict", "--out", str(out / "deck")]
            if plan.slides:
                command += ["--slides", ",".join(plan.slides), "--screenshots", "listed"]
            else:
                command += ["--screenshots", "none"]
            if plan.full_browser:
                command += ["--full"]
            jobs.append(("browser-deck", command))
        if plan.gallery:
            jobs.append(("browser-gallery", [browser_py, "scripts/check_browser_qa.py", "--deck", "slide_patterns.html",
                                            "--full", "--screenshots", "none", "--out", str(out / "gallery")]))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda job: run_check(*job, out, env), jobs))
    summary = {"base": args.base, "plan": asdict(plan), "results": results,
               "elapsed_seconds": round(time.perf_counter() - started, 3)}
    (out / "validation_report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Validation: {summary['elapsed_seconds']:.3f} s; report: {out / 'validation_report.json'}")
    return int(any(result["exit_code"] for result in results))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Validation FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
