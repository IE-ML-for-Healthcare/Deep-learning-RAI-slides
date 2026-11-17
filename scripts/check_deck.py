#!/usr/bin/env python3
"""Static QA for IE SciTech Reveal.js repositories. Standard library only.

Run it before and after every change, and before browser QA:

    python scripts/check_deck.py                    # index.html, slide_patterns.html, and docs
    python scripts/check_deck.py --deck index.html  # one deck plus the repository text rules

Errors (exit code 1)
  - Em dash characters in any repository text file
  - Bullet lines or list items that end with a full stop
  - Duplicate ids, missing local assets, relative download links
  - ie-light or ie-dark combined with an ie-bg-* background class
  - Reveal.initialize not set to width 1600, height 900, margin 0, or ie-reveal-fit.js
    loaded before reveal.js
  - Broken course sentinels or session markers (index.html only, when present)
  - Speaker notes when deck.config.json sets "speakerNotes": "forbidden"
  - The is-solid band variant, or an inline background or border on a key takeaway strip
  - A shared stylesheet that no longer carries the approved key takeaway strip standard

Warnings
  - Top-level slides without a stable kebab-case id, or without one .ie-logo
  - Logo accent variant that does not match the section background class
  - Bold markup inside body prose, titles over 12 words
  - Hex colours in inline deck CSS that are not palette tokens
  - Unpinned CDN versions
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_common import ROOT, load_config  # noqa: E402
from download_controls import validate_download_nodes  # noqa: E402

TEXT_SUFFIXES = {".html", ".md", ".css", ".js", ".py", ".yml", ".yaml", ".json", ".sh", ".txt"}
SKIP_PARTS = {".git", "node_modules", ".venv-reveal-qa", "tmp", ".cache", "dist", ".release-tmp", "__pycache__"}
SKIP_NAMES = {"LICENSE-tabler-icons.txt"}
PALETTE = {"#000024", "#000066", "#ffffff", "#fff", "#f7f7f5", "#242424", "#1c1c1c", "#15260f",
           "#c9ff8a", "#9be15d", "#b7e4c7", "#e8e8e8"}
LIGHT_BG = re.compile(r"^(ie-light|ie-bg-light-[\w-]+)$")
DARK_BG = re.compile(r"^(ie-dark|ie-bg-dark-[\w-]+|ie-bg-green-dark-left|ie-compare-dark)$")
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EM_DASH = chr(0x2014)
STRIP_CLASSES = {"ie-band", "ie-takeaway", "deck-takeaway-card", "ie-compare-takeaway", "ie-lr-takeaway-left",
                 "ie-lr-takeaway-right", "ie-lr-takeaway-shared", "ie-process-takeaway", "ie-step-takeaway"}
STRIP_STANDARD = ("rgba(255, 255, 255, 0.40)", "rgba(255, 255, 255, 0.10)", "Key takeaway strip standard".upper())


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text", "line")

    def __init__(self, tag: str, attrs: dict[str, str], parent: "Node | None", line: int) -> None:
        self.tag, self.attrs, self.parent, self.line = tag, attrs, parent, line
        self.children: list[Node] = []
        self.text: list[str] = []

    @property
    def classes(self) -> list[str]:
        return self.attrs.get("class", "").split()

    def iter(self):
        yield self
        for child in self.children:
            yield from child.iter()

    def all_text(self) -> str:
        return "".join(self.text) + "".join(child.all_text() for child in self.children)

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None, 0)
        self.stack = [self.root]
        self.raw_styles: list[str] = []
        self._in_style = False

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {k: (v or "") for k, v in attrs}, self.stack[-1], self.getpos()[0])
        self.stack[-1].children.append(node)
        if tag == "style":
            self._in_style = True
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, {k: (v or "") for k, v in attrs}, self.stack[-1], self.getpos()[0])
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self._in_style:
            self.raw_styles.append(data)
        self.stack[-1].text.append(data)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def repository_files() -> list[Path]:
    try:
        output = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.splitlines()
        files = [ROOT / line for line in output]
    except (OSError, subprocess.CalledProcessError):
        files = [p for p in ROOT.rglob("*") if p.is_file()]
    return [p for p in files if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES
            and not (set(p.relative_to(ROOT).parts) & SKIP_PARTS) and p.name not in SKIP_NAMES]


def check_text_rules(report: Report) -> None:
    fence = re.compile(r"^\s*(```|~~~)")
    bullet = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(?P<body>.+)$")
    for path in repository_files():
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if EM_DASH in line:
                report.error(f"{rel}:{number}: em dash character")
        if path.suffix.lower() == ".md":
            in_code = False
            for number, line in enumerate(text.splitlines(), 1):
                if fence.match(line):
                    in_code = not in_code
                    continue
                match = None if in_code else bullet.match(line)
                if match and match.group("body").rstrip().endswith(".") and not match.group("body").rstrip().endswith(".."):
                    report.error(f"{rel}:{number}: bullet line ends with a full stop")


def local_reference(value: str) -> str | None:
    value = value.strip()
    if not value or value.startswith(("#", "data:", "mailto:", "tel:", "javascript:", "{", "$")):
        return None
    parsed = urlparse(value)
    if parsed.scheme or value.startswith("//"):
        return None
    return unquote(parsed.path) or None


def check_deck(deck: Path, report: Report, config: dict, is_main: bool) -> None:
    rel = deck.relative_to(ROOT).as_posix()
    source = deck.read_text(encoding="utf-8")
    builder = TreeBuilder()
    builder.feed(source)
    root = builder.root
    nodes = list(root.iter())

    seen: dict[str, int] = {}
    for node in nodes:
        node_id = node.attrs.get("id")
        if node_id:
            if node_id in seen:
                report.error(f"{rel}:{node.line}: duplicate id #{node_id} (first on line {seen[node_id]})")
            seen.setdefault(node_id, node.line)

    for node in nodes:
        if "is-solid" in node.classes:
            report.error(f"{rel}:{node.line}: is-solid is retired; every key takeaway strip uses the approved standard")
        if STRIP_CLASSES & set(node.classes) and re.search(r"background|border", node.attrs.get("style", "")):
            report.error(f"{rel}:{node.line}: key takeaway strips must not carry an inline background or border")
    for message in validate_download_nodes(nodes, ROOT, rel):
        report.error(message)
    for node in nodes:
        refs = []
        for attr in ("src", "data-src", "poster"):
            if attr in node.attrs:
                refs.append(node.attrs[attr])
        if node.tag in ("link", "a") and "href" in node.attrs and "download" not in node.attrs:
            refs.append(node.attrs["href"])
        refs += re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", node.attrs.get("style", ""))
        for ref in refs:
            path = local_reference(ref)
            if path and not (deck.parent / path).exists():
                report.error(f"{rel}:{node.line}: missing local asset {ref}")
        if node.tag == "a" and "download" in node.attrs:
            if not node.attrs.get("href", "").startswith("data:"):
                report.error(f"{rel}:{node.line}: download link must be a base64 data: URI (scripts/sync_downloads.py)")
            if "data-download-source" not in node.attrs:
                report.error(f"{rel}:{node.line}: download link needs data-download-source")
    for css in builder.raw_styles:
        for ref in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", css):
            path = local_reference(ref)
            if path and not (deck.parent / path).exists():
                report.error(f"{rel}: missing local asset in inline CSS {ref}")
        for hex_value in set(re.findall(r"#[0-9a-fA-F]{3,8}\b", css)):
            if hex_value.lower() not in PALETTE:
                report.warn(f"{rel}: inline CSS uses non-palette colour {hex_value}; use a token from ie-scitech-reveal.css")
    if is_main:
        check_css_guards(source, report, rel)

    slides_container = next((n for n in nodes if "slides" in n.classes and n.parent is not None
                             and "reveal" in n.parent.classes), None)
    top_sections = [n for n in (slides_container.children if slides_container else []) if n.tag == "section"]
    for section in (n for n in nodes if n.tag == "section"):
        classes = section.classes
        if "ie-slide" not in classes:
            continue
        where = f"{rel}:{section.line} #{section.attrs.get('id', '?')}"
        for node in section.iter():
            if node is not section and node.tag == "section" and node.parent is not section:
                report.error(f"{where}: nested <section> at line {node.line}; Reveal.js counts every section as a slide, use <div> or <article>")
        solid = {"ie-light", "ie-dark"} & set(classes)
        images = [c for c in classes if c.startswith("ie-bg-")]
        if solid and images:
            report.error(f"{where}: do not combine {sorted(solid)} with {images}")
        logos = [c for c in section.children if "ie-logo" in c.classes]
        if len(logos) != 1:
            report.warn(f"{where}: expected exactly one .ie-logo block, found {len(logos)}")
        background = next((c for c in classes if LIGHT_BG.match(c) or DARK_BG.match(c)), None)
        for logo in logos:
            img = next((n for n in logo.iter() if n.tag == "img"), None)
            src = img.attrs.get("src", "") if img else ""
            if background and DARK_BG.match(background) and "light-accent" in src:
                report.warn(f"{where}: light-accent logo on a dark background ({background}); confirm the region beneath it")
            if background and LIGHT_BG.match(background) and "dark-accent" in src:
                report.warn(f"{where}: dark-accent logo on a light background ({background}); confirm the region beneath it")
        if config.get("speakerNotes") == "forbidden":
            for node in section.iter():
                if "notes" in node.classes:
                    report.error(f"{where}: speaker notes are forbidden by deck.config.json")
        for node in section.iter():
            if node.tag in ("h1", "h2"):
                words = len(node.all_text().split())
                if words > 12:
                    report.warn(f"{where}: title has {words} words, keep it under 12")
            if node.tag in ("strong", "b") and any(a.tag in ("p", "li", "td") for a in node.ancestors()):
                report.warn(f"{where}: bold markup inside body prose; use colour or structure for emphasis")
            if node.tag == "li":
                text = " ".join(node.all_text().split())
                if text.endswith(".") and not text.endswith(".."):
                    report.error(f"{where}: list item ends with a full stop: {text[-60:]!r}")

    for section in top_sections:
        section_id = section.attrs.get("id")
        if not section_id:
            report.warn(f"{rel}:{section.line}: top-level slide has no id")
        elif not ID_PATTERN.match(section_id):
            report.warn(f"{rel}:{section.line}: slide id #{section_id} is not kebab-case")

    scripts = [n.attrs.get("src", "") for n in nodes if n.tag == "script" and n.attrs.get("src")]
    reveal_at = next((i for i, s in enumerate(scripts) if s.endswith("reveal.js")), None)
    fit_at = next((i for i, s in enumerate(scripts) if s.endswith("ie-reveal-fit.js")), None)
    if reveal_at is None or fit_at is None or fit_at < reveal_at:
        report.error(f"{rel}: load reveal.js first, then ie-reveal-fit.js")
    for src in scripts + [n.attrs.get("href", "") for n in nodes if n.tag == "link"]:
        if re.search(r"reveal\.js@\d+/", src):
            report.warn(f"{rel}: unpinned CDN version {src}; pin an exact version such as reveal.js@5.2.1")
    init = re.search(r"Reveal\.initialize\(\{(.*?)\}\)", source, re.S)
    if not init:
        report.error(f"{rel}: Reveal.initialize not found")
    else:
        body = init.group(1)
        for key, value in (("width", "1600"), ("height", "900"), ("margin", "0")):
            if not re.search(rf"\b{key}\s*:\s*{value}\b", body):
                report.error(f"{rel}: Reveal.initialize must set {key}: {value}")
        if not re.search(r"\bpdfMaxPagesPerSlide\s*:\s*1\b", body):
            report.warn(f"{rel}: add pdfMaxPagesPerSlide: 1 to Reveal.initialize so print export keeps one page per slide")
        after = source[init.end():]
        if "IERevealFit" in source and not re.search(r"\.then\(\s*function[^{]*\{[^}]*IERevealFit\.fitAll", after, re.S):
            report.error(f"{rel}: call IERevealFit.fitAll() inside Reveal.initialize(...).then(...)")
    if "ie-roadmap" in source and "IEComponents.prepare" not in source:
        report.error(f"{rel}: roadmap slides need IEComponents.prepare() before Reveal.initialize")
    if "data-slide-ref" in source and "IESlideAliases.resolve" not in source:
        report.error(f"{rel}: slide aliases need IESlideAliases.resolve() before Reveal.initialize")

    if is_main and "COURSE SESSION CONTENT START" in source:
        try:
            from release_slice import ReleaseSliceError, parse_source
            parse_source(source)
        except ReleaseSliceError as exc:
            report.error(f"{rel}: session structure: {exc}")


def check_takeaway_standard(report: Report) -> None:
    css = ROOT / "ie-scitech-reveal.css"
    if not css.exists():
        return
    text = css.read_text(encoding="utf-8")
    for token in STRIP_STANDARD:
        if token not in text:
            report.error(f"ie-scitech-reveal.css: the key takeaway strip standard is missing {token!r}")
    block = text[text.find(STRIP_STANDARD[2]):]
    if "!important" not in block:
        report.error("ie-scitech-reveal.css: the key takeaway strip standard must be enforced with !important")


CSS_TABLE_PROPERTIES = {
    "font-family", "font-size", "font-weight", "line-height", "color", "background",
    "background-color", "background-image", "border", "border-color", "border-width",
    "border-style", "border-top", "border-right", "border-bottom", "border-left", "box-shadow",
}
SAFE_FRAME_VARIANTS = ("open", "dense", "full-bleed")
SAFE_FRAME_INSET_PROPERTIES = {"top", "right", "bottom", "left", "inset"}
QUOTE_SELECTOR = re.compile(r"source-quote|source-attribution|ie-quote-(?:text|attribution|emphasis)", re.I)
QUOTE_PARAGRAPH = re.compile(r'<p\s+class="([^"]*)"[^>]*>(.*?)</p>', re.S)
QUOTE_STANDARD_PX = 50
QUOTE_LONG_PX = 30
TITLE_SIZE_TOKENS = ("var(--ie-title-size)", "var(--ie-title-size-compact)")


def _css_strip_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def _css_matching_brace(text: str, opening: int) -> int:
    depth = 1
    quote = None
    index = opening + 1
    while index < len(text):
        if quote:
            if text[index] == "\\":
                index += 2
                continue
            if text[index] == quote:
                quote = None
            index += 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            index = len(text) if end < 0 else end + 2
            continue
        if text[index] in "'\"":
            quote = text[index]
        elif text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return len(text) - 1


def _css_rules(text: str, source: str, base_offset: int = 0) -> list[dict[str, object]]:
    rules: list[dict[str, object]] = []
    cursor = 0
    while cursor < len(text):
        quote = None
        opening = None
        index = cursor
        while index < len(text):
            if quote:
                if text[index] == "\\":
                    index += 2
                    continue
                if text[index] == quote:
                    quote = None
                index += 1
                continue
            if text.startswith("/*", index):
                end = text.find("*/", index + 2)
                index = len(text) if end < 0 else end + 2
                continue
            if text[index] in "'\"":
                quote = text[index]
            elif text[index] == "{":
                opening = index
                break
            index += 1
        if opening is None:
            break
        closing = _css_matching_brace(text, opening)
        raw_selector = text[cursor:opening]
        selector = _css_strip_comments(raw_selector).strip()
        body = text[opening + 1:closing]
        absolute_start = base_offset + cursor
        if selector.startswith("@"):
            rules.extend(_css_rules(body, source, base_offset + opening + 1))
        elif selector:
            comments = list(re.finditer(r"/\*.*?\*/", raw_selector, flags=re.S))
            comment = comments[-1].group(0).strip() if comments else ""
            rules.append({
                "selector": selector,
                "body": body,
                "line": source.count("\n", 0, absolute_start) + 1,
                "comment": comment,
            })
        cursor = closing + 1
    return rules


def _css_declarations(body: str) -> list[tuple[str, str]]:
    clean = _css_strip_comments(body)
    return [(name.strip().lower(), value.strip())
            for name, value in re.findall(r"([\w-]+)\s*:\s*([^;{}]+)", clean)]


def _css_normalize(text: str) -> str:
    return re.sub(r"\s+", " ", _css_strip_comments(text)).strip()


def _css_slide_scoped(selector: str) -> bool:
    clean = _css_normalize(selector)
    return bool(re.search(
        r"\.ie-slide\b|\.(?:session|slide)-[a-z0-9-]+\b|(?:^|[\s>+~,])section(?:[#.][a-z0-9_-]+)?",
        clean, re.I,
    ))


def _css_table_selector(selector: str) -> bool:
    clean = _css_normalize(selector)
    return bool(re.search(
        r"\.[a-z0-9_-]*table\b|(?:^|[\s>+~,])(?:table|thead|tbody|tr|th|td)\b",
        clean, re.I,
    ))


def find_css_guard_violations(source: str) -> dict[str, list[dict[str, object]]]:
    """Return title, table, and duplicate inline-CSS guard violations for a deck."""
    rules: list[dict[str, object]] = []
    for match in re.finditer(r"<style[^>]*>(.*?)</style>", source, flags=re.S | re.I):
        rules.extend(_css_rules(match.group(1), source, match.start(1)))

    title_violations: list[dict[str, object]] = []
    table_violations: list[dict[str, object]] = []
    for rule in rules:
        selector = str(rule["selector"])
        declarations = _css_declarations(str(rule["body"]))
        properties = {name for name, _ in declarations}
        if _css_slide_scoped(selector) and re.search(r"(?<![-\w])h[12](?![-\w])", selector, re.I):
            sizes = [value.lower() for name, value in declarations if name == "font-size"]
            if sizes and (not all(any(token in size for token in TITLE_SIZE_TOKENS) for size in sizes)):
                if not re.search(r"display|exception", str(rule["comment"]), re.I):
                    title_violations.append({"line": rule["line"], "selector": _css_normalize(selector), "sizes": sizes})
        if _css_slide_scoped(selector) and _css_table_selector(selector) and properties & CSS_TABLE_PROPERTIES:
            clean_selector = _css_normalize(selector)
            if re.search(r"\b(?:code|a)\b", clean_selector, re.I):
                continue
            if re.search(r"table\s+exception|semantic .*emphasis", str(rule["comment"]), re.I):
                continue
            table_violations.append({
                "line": rule["line"],
                "selector": clean_selector,
                "properties": sorted(properties & CSS_TABLE_PROPERTIES),
            })

    inset_violations: list[dict[str, object]] = []
    quote_violations: list[dict[str, object]] = []
    card_violations: list[dict[str, object]] = []
    fit_violations: list[dict[str, object]] = []
    keyrow_violations: list[dict[str, object]] = []
    for rule in rules:
        selector = _css_normalize(str(rule["selector"]))
        properties = {name for name, _ in _css_declarations(str(rule["body"]))}
        comment = str(rule["comment"])
        if not _css_slide_scoped(selector):
            continue
        if any(re.search(r"\.safe-frame$", part.strip()) for part in selector.split(",")) and properties & SAFE_FRAME_INSET_PROPERTIES:
            if not re.search(r"safe frame exception", comment, re.I):
                inset_violations.append({"line": rule["line"], "selector": selector})
        if QUOTE_SELECTOR.search(selector) and re.search(r"\.ie-slide\.[\w-]+|section[#.]|#[\w-]+", selector) and properties & {"font-size", "font-weight", "font-style"} and not re.search(r"display exception", comment, re.I):
            quote_violations.append({"line": rule["line"], "selector": selector})
        for name, value in _css_declarations(str(rule["body"])):
            if name in {"width", "height", "min-width", "max-width"} and "--fit-scale" in value:
                fit_violations.append({"line": rule["line"], "selector": selector})
        if re.search(r"(?:^|[\s,])(?:th|tr|td)\b|\bth\[", selector) and any(name == "box-shadow" and "inset" in value for name, value in _css_declarations(str(rule["body"]))) and "ie-table-key-row" not in selector:
            keyrow_violations.append({"line": rule["line"], "selector": selector})
        if re.search(r"\.agenda-card\b", selector) and "font-size" in properties:
            card_violations.append({"line": rule["line"], "selector": selector})
    for match in re.finditer(r"safe-frame--([a-z-]+)", source):
        if match.group(1) not in SAFE_FRAME_VARIANTS:
            inset_violations.append({"line": source.count("\n", 0, match.start()) + 1, "selector": match.group(0)})

    by_rule: dict[tuple[str, str], list[int]] = {}
    for rule in rules:
        key = (_css_normalize(str(rule["selector"])), _css_normalize(str(rule["body"])))
        by_rule.setdefault(key, []).append(int(rule["line"]))
    duplicate_violations = [
        {"selector": selector, "lines": lines}
        for (selector, _body), lines in by_rule.items()
        if len(lines) > 1
    ]
    return {"title": title_violations, "table": table_violations, "duplicate": duplicate_violations,
            "inset": inset_violations, "quote": quote_violations, "card": card_violations,
            "fit": fit_violations, "keyrow": keyrow_violations}


def find_markup_guard_violations(source: str) -> list[str]:
    """Quote, table, and pop-up markup standards: lime emphasis, dash-prefixed attribution, one key row per table, shared ie-tooltip only."""
    messages: list[str] = []
    body = re.sub(r"<style[^>]*>.*?</style>|<script[^>]*>.*?</script>", "", source, flags=re.S | re.I)
    for match in QUOTE_PARAGRAPH.finditer(body):
        classes = match.group(1).split()
        inner = match.group(2)
        line = source.count("\n", 0, source.find(match.group(0))) + 1 if match.group(0) in source else 0
        if "source-quote" in classes or "ie-quote-text" in classes:
            for span in re.finditer(r'<span\s+class="([^"]*)"', inner):
                if span.group(1).split() != ["ie-quote-emphasis"]:
                    messages.append(f"line {line}: quote emphasis must use the shared ie-quote-emphasis class, found {span.group(1)!r}")
        if "source-attribution" in classes or "ie-quote-attribution" in classes:
            text = re.sub(r"<[^>]+>", "", inner).strip()
            if not text.startswith("- "):
                messages.append(f"line {line}: quote attribution must start with a dash and a space, found {text!r}")
    for tag in re.finditer(r"<[a-zA-Z][^>]*>", body):
        markup = tag.group(0)
        classes = (re.search(r'\sclass="([^"]*)"', markup) or [None, ""])[1].split()
        line = body.count("\n", 0, tag.start()) + 1
        custom = [c for c in classes if c != "ie-tooltip" and re.search(r"(^|-)(tooltip|popover|hovercard)$", c)]
        if 'role="tooltip"' in markup or custom:
            messages.append(f"body line {line}: hover or focus pop-ups must use the shared ie-tooltip pattern, found {custom or 'role=tooltip'}")
        if "data-tooltip=" in markup and "ie-tooltip" not in classes:
            messages.append(f"body line {line}: data-tooltip needs the shared ie-tooltip class")
        if "ie-tooltip" in classes and not ('tabindex="0"' in markup and "aria-label=" in markup and "data-tooltip=" in markup):
            messages.append(f"body line {line}: ie-tooltip needs tabindex=\"0\", data-tooltip, and aria-label")
    for table in re.finditer(r"<table\b.*?</table>", body, flags=re.S | re.I):
        if len(re.findall(r'<tr\s+class="[^"]*\bie-table-key-row\b', table.group(0))) > 1:
            messages.append("a table has more than one ie-table-key-row, highlight one row only")
    return messages


def check_css_guards(source: str, report: Report, rel: str) -> None:
    violations = find_css_guard_violations(source)
    for item in violations["title"]:
        report.error(f"{rel}:{item['line']}: slide title font-size {item['sizes']} is not a shared title token: {item['selector']}")
    for item in violations["table"]:
        report.error(f"{rel}:{item['line']}: slide-scoped table styling {item['properties']}: {item['selector']}")
    for item in violations["inset"]:
        report.error(f"{rel}:{item['line']}: safe-frame inset outside the named variants {SAFE_FRAME_VARIANTS} needs a Safe frame exception comment: {item['selector']}")
    for item in violations["quote"]:
        report.error(f"{rel}:{item['line']}: slide-scoped quote font-size needs a Display exception comment or the shared quote class: {item['selector']}")
    for item in violations["card"]:
        report.error(f"{rel}:{item['line']}: slide-scoped agenda card font-size, use ie-agenda-stack: {item['selector']}")
    for item in violations["fit"]:
        report.error(f"{rel}:{item['line']}: never size a box with var(--fit-scale), ie-reveal-fit.js already compensates width and height so content spans margin to margin: {item['selector']}")
    for item in violations["keyrow"]:
        report.error(f"{rel}:{item['line']}: highlight a table row with the shared ie-table-key-row class, not a scoped inset shadow: {item['selector']}")
    for message in find_markup_guard_violations(source):
        report.error(f"{rel}: {message}")
    for item in violations["duplicate"]:
        report.error(f"{rel}:{item['lines'][0]}: duplicate identical CSS rule on lines {item['lines']}: {item['selector']}")


def check_type_scale(report: Report) -> None:
    """Fixed px type scale on the 1600 x 900 canvas: no vw or vh units in CSS."""
    for name in ("ie-scitech-reveal.css", "index.html", "slide_patterns.html"):
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        css = text if name.endswith(".css") else "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.S))
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        hits = re.findall(r"[:(,\s]-?\d*\.?\d+(?:vw|vh|vmin|vmax)\b", css)
        if hits:
            report.error(f"{name}: {len(hits)} viewport unit value(s) found, use fixed px on the 1600 x 900 canvas")
    shared = ROOT / "ie-scitech-reveal.css"
    if shared.exists():
        text = shared.read_text(encoding="utf-8")
        for token in ("--ie-title-size:", "--ie-title-size-compact:", "--ie-lead-size:", "ie-logo-tr", "ie-logo-br"):
            if token not in text:
                report.error(f"ie-scitech-reveal.css: type scale or logo variant {token!r} is missing")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--deck", action="append", help="deck HTML to check; repeatable")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args()
    config = load_config()
    report = Report()
    check_text_rules(report)
    check_takeaway_standard(report)
    check_type_scale(report)
    decks = args.deck or [d for d in ("index.html", "slide_patterns.html") if (ROOT / d).exists()]
    for deck in decks:
        check_deck((ROOT / deck).resolve(), report, config, is_main=Path(deck).name == "index.html")
    for warning in report.warnings:
        print(f"WARN  {warning}")
    for error in report.errors:
        print(f"FAIL  {error}")
    failed = bool(report.errors) or (args.strict and bool(report.warnings))
    print(f"Static QA {'FAILED' if failed else 'PASSED'} ({len(report.errors)} failures, {len(report.warnings)} warnings)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
