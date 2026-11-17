#!/usr/bin/env python3
"""Validate and slice the continuous Reveal.js deck by slide selection

The deck keeps every session between COURSE SESSION CONTENT sentinels and
paired SESSION NN markers. Cutoffs use the overall Reveal.js slide number.
See instructions/release_pipeline.md.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


COURSE_START = "<!-- COURSE SESSION CONTENT START -->"
COURSE_END = "<!-- COURSE SESSION CONTENT END -->"
SESSION_MARKER = re.compile(r"<!-- SESSION (\d{2}) (START|END) -->")
REVEAL_INIT = "Reveal.initialize({"
ALIAS_RESOLVE_CALL = re.compile(r"^[ \t]*IESlideAliases\.resolve\(\);", re.MULTILINE)
PDF_CONFIG = "\n      pdfSeparateFragments: false,"
PAGE_LIMIT = re.compile(r"\bpdfMaxPagesPerSlide\s*:\s*1\b")
PAGE_LIMIT_CONFIG = "\n      pdfMaxPagesPerSlide: 1,"
CUTOFF_PATTERN = re.compile(r"([0-9]+)(?:/([0-9]+))?")
RANGE_PATTERN = re.compile(r"([0-9]+) - ([0-9]+)/([0-9]+)")
SLIDE_REF_PATTERN = re.compile(r"data-slide-ref\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
VOID_ELEMENTS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)


class ReleaseSliceError(ValueError):
    """Raised when the slide release contract is invalid"""


@dataclass(frozen=True)
class SlideBlock:
    number: int
    start: int
    end: int
    element_id: str | None
    heading: str | None


@dataclass(frozen=True)
class SessionBlock:
    number: int
    start: int
    end: int


@dataclass(frozen=True)
class DeckStructure:
    course_end_start: int
    slides: tuple[SlideBlock, ...]
    sessions: tuple[SessionBlock, ...] = ()


@dataclass(frozen=True)
class SlideCutoff:
    raw: str
    numerator: int
    denominator: int | None
    start: int = 1
    explicit_range: bool = False

    @property
    def end(self) -> int:
        return self.numerator

    @property
    def count(self) -> int:
        return self.end - self.start + 1


@dataclass(frozen=True)
class ReleaseInputs:
    source_total: int
    publish: SlideCutoff
    pdf: SlideCutoff | None


@dataclass
class _Element:
    tag: str
    start: int
    attrs: dict[str, str]
    classes: frozenset[str]
    is_slides_container: bool = False
    is_top_level_slide: bool = False
    end: int | None = None


class _HeadingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._heading_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._heading_depth:
            self._heading_depth += 1
        elif tag.lower() in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_depth = 1

    def handle_endtag(self, tag: str) -> None:
        if self._heading_depth:
            self._heading_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._heading_depth:
            self._chunks.append(data)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self._chunks)).strip()


class _SlideHTMLParser(HTMLParser):
    """Track HTML element boundaries without rewriting the source markup"""

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.text = text
        self.line_offsets = [0]
        for line in text.splitlines(keepends=True):
            self.line_offsets.append(self.line_offsets[-1] + len(line))
        self.stack: list[_Element] = []
        self.slides_container_candidates: list[_Element] = []
        self.slide_elements: list[_Element] = []
        self.non_direct_sections: list[int] = []
        self.nested_sections: list[int] = []

    def token_offset(self) -> int:
        line, column = self.getpos()
        if line < 1 or line > len(self.line_offsets):
            raise ReleaseSliceError("Could not resolve an HTML token position")
        return self.line_offsets[line - 1] + column

    def end_offset(self, start: int) -> int:
        end = self.text.find(">", start)
        if end < 0:
            raise ReleaseSliceError("Malformed HTML contains an unterminated tag")
        return end + 1

    @staticmethod
    def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {name.lower(): value or "" for name, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        start = self.token_offset()
        raw = self.get_starttag_text()
        if raw is None:
            raise ReleaseSliceError(f"Could not read the <{tag}> start tag")
        attributes = self.attrs_dict(attrs)
        classes = frozenset(attributes.get("class", "").split())
        has_reveal_ancestor = any("reveal" in element.classes for element in self.stack)
        is_slides_container = "slides" in classes and has_reveal_ancestor
        element = _Element(
            tag=tag,
            start=start,
            attrs=attributes,
            classes=classes,
            is_slides_container=is_slides_container,
        )

        if is_slides_container:
            self.slides_container_candidates.append(element)

        if tag == "section":
            containing_slides = [
                candidate for candidate in self.stack if candidate.is_slides_container
            ]
            if containing_slides:
                if any(candidate.tag == "section" for candidate in self.stack):
                    self.nested_sections.append(start)
                elif self.stack[-1] is not containing_slides[-1]:
                    self.non_direct_sections.append(start)
                else:
                    element.is_top_level_slide = True

        if tag not in VOID_ELEMENTS:
            self.stack.append(element)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "section":
            raise ReleaseSliceError(
                "Unsupported self-closing <section>; Reveal slides must be complete top-level elements"
            )

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in VOID_ELEMENTS:
            return
        start = self.token_offset()
        if not self.stack:
            return

        matching_index = next(
            (index for index in range(len(self.stack) - 1, -1, -1) if self.stack[index].tag == tag),
            None,
        )
        if matching_index is None:
            return
        if tag == "section":
            if any(element.tag == "section" for element in self.stack[matching_index + 1 :]):
                line, column = self.getpos()
                raise ReleaseSliceError(
                    f"Malformed HTML at line {line}, column {column}: a nested "
                    "<section> must close before its parent"
                )
        elif any(element.tag == "section" for element in self.stack[matching_index + 1 :]):
            line, column = self.getpos()
            raise ReleaseSliceError(
                f"Malformed HTML at line {line}, column {column}: an element inside "
                f"<section> closes its ancestor </{tag}>"
            )

        element = self.stack[matching_index]
        del self.stack[matching_index:]
        element.end = self.end_offset(start)
        if element.is_top_level_slide:
            self.slide_elements.append(element)

    def finish(self) -> None:
        try:
            self.close()
        except Exception as error:
            if isinstance(error, ReleaseSliceError):
                raise
            raise ReleaseSliceError(f"Could not parse the deck HTML: {error}") from error
        if any(element.tag == "section" for element in self.stack):
            raise ReleaseSliceError("Unclosed <section> element in the deck HTML")


def _scan_slides(text: str) -> tuple[int, int, tuple[SlideBlock, ...]]:
    parser = _SlideHTMLParser(text)
    try:
        parser.feed(text)
        parser.finish()
    except ReleaseSliceError:
        raise
    except Exception as error:
        raise ReleaseSliceError(f"Could not parse the deck HTML: {error}") from error

    if len(parser.slides_container_candidates) != 1:
        raise ReleaseSliceError(
            "Expected exactly one .reveal .slides container, found "
            f"{len(parser.slides_container_candidates)}"
        )
    if parser.nested_sections:
        raise ReleaseSliceError(
            "Unsupported vertical Reveal slides: nested <section> elements were found "
            "inside a top-level slide; flatten the deck before releasing"
        )
    if parser.non_direct_sections:
        raise ReleaseSliceError(
            "Unsupported Reveal structure: every slide <section> must be a direct child "
            "of .reveal .slides"
        )

    container = parser.slides_container_candidates[0]
    if container.end is None:
        raise ReleaseSliceError("The .reveal .slides container is not closed")

    slides: list[SlideBlock] = []
    for number, element in enumerate(parser.slide_elements, start=1):
        if element.end is None:
            raise ReleaseSliceError(f"Slide {number} is not closed")
        markup = text[element.start : element.end]
        heading = _heading_from_markup(markup)
        slides.append(
            SlideBlock(
                number=number,
                start=element.start,
                end=element.end,
                element_id=element.attrs.get("id") or None,
                heading=heading,
            )
        )

    if not slides:
        raise ReleaseSliceError("No top-level Reveal slide sections were found")
    return container.start, container.end, tuple(slides)


def _heading_from_markup(markup: str) -> str | None:
    parser = _HeadingParser()
    try:
        parser.feed(markup)
        parser.close()
    except Exception:
        return None
    heading = parser.text
    if not heading:
        return None
    return heading[:160]


def slide_identity(slide: SlideBlock) -> str:
    if slide.element_id:
        return f"id={slide.element_id}"
    if slide.heading:
        return f"heading={slide.heading}"
    return "unknown"


def exact_marker_positions(text: str, marker: str, label: str) -> tuple[int, int]:
    positions = [match.start() for match in re.finditer(re.escape(marker), text)]
    if len(positions) != 1:
        raise ReleaseSliceError(f"Expected exactly one {label}, found {len(positions)}")
    start = positions[0]
    return start, start + len(marker)


def parse_source(text: str) -> DeckStructure:
    (
        slides_container_start,
        slides_container_end,
        slides,
    ) = _scan_slides(text)
    course_start_start, course_start_end = exact_marker_positions(
        text, COURSE_START, "course START sentinel"
    )
    course_end_start, course_end_end = exact_marker_positions(
        text, COURSE_END, "course END sentinel"
    )
    if course_start_end >= course_end_start:
        raise ReleaseSliceError("Course sentinels are reversed or overlap")
    if not (
        slides_container_start < course_start_start
        and course_end_end < slides_container_end
    ):
        raise ReleaseSliceError("Course sentinels must be inside the .reveal .slides container")

    inner_start = course_start_end
    inner_end = course_end_start
    marker_matches = [
        match
        for match in SESSION_MARKER.finditer(text)
        if inner_start <= match.start() < inner_end
    ]
    all_marker_matches = list(SESSION_MARKER.finditer(text))
    if len(marker_matches) != len(all_marker_matches):
        raise ReleaseSliceError("A session marker exists outside the course sentinels")
    if not marker_matches:
        raise ReleaseSliceError("No session markers were found between the course sentinels")
    if any(
        not (slides_container_start < match.start() < slides_container_end)
        for match in marker_matches
    ):
        raise ReleaseSliceError("A session marker exists outside the .reveal .slides container")

    sessions: list[SessionBlock] = []
    open_session: tuple[int, int] | None = None
    for match in marker_matches:
        number = int(match.group(1))
        kind = match.group(2)
        if kind == "START":
            if open_session is not None:
                raise ReleaseSliceError(
                    f"SESSION {number:02d} START appears before SESSION "
                    f"{open_session[0]:02d} END"
                )
            open_session = (number, match.start())
        else:
            if open_session is None:
                raise ReleaseSliceError(f"SESSION {number:02d} END has no matching START")
            if open_session[0] != number:
                raise ReleaseSliceError(
                    f"SESSION {number:02d} END does not match SESSION "
                    f"{open_session[0]:02d} START"
                )
            sessions.append(
                SessionBlock(number=number, start=open_session[1], end=match.end())
            )
            open_session = None

    if open_session is not None:
        raise ReleaseSliceError(f"SESSION {open_session[0]:02d} START has no matching END")

    numbers = [session.number for session in sessions]
    if len(numbers) != len(set(numbers)):
        duplicates = sorted(number for number in set(numbers) if numbers.count(number) > 1)
        formatted = ", ".join(f"{number:02d}" for number in duplicates)
        raise ReleaseSliceError(f"Duplicate session marker pairs found: {formatted}")
    if numbers != sorted(numbers):
        raise ReleaseSliceError("Session numbers are not in ascending order")

    for slide in slides:
        if not (course_start_end <= slide.start and slide.end <= course_end_start):
            raise ReleaseSliceError(
                f"Slide {slide.number} is outside the course content sentinels"
            )
        owners = [
            session
            for session in sessions
            if session.start <= slide.start and slide.end <= session.end
        ]
        if len(owners) != 1:
            raise ReleaseSliceError(
                f"Slide {slide.number} must belong to exactly one complete session marker block"
            )

    return DeckStructure(
        course_end_start=course_end_start,
        slides=slides,
        sessions=tuple(sessions),
    )


def parse_cutoff(value: str, label: str, source_total: int) -> SlideCutoff:
    match = CUTOFF_PATTERN.fullmatch(value)
    if not match:
        raise ReleaseSliceError(
            f"{label} must be an integer N or N/T with no whitespace, got {value!r}"
        )
    numerator = int(match.group(1))
    denominator = int(match.group(2)) if match.group(2) is not None else None
    if numerator < 1 or numerator > source_total:
        hint = ""
        if numerator > source_total:
            hint = (
                " Use the overall Reveal.js slide number, not a session number, "
                "slide id, or session-slide shorthand."
            )
        raise ReleaseSliceError(
            f"{label} numerator must be from 1 through the source total "
            f"({source_total}), got {numerator}.{hint}"
        )
    if denominator is not None and denominator != source_total:
        raise ReleaseSliceError(
            f"{label} denominator {denominator} does not match the actual source "
            f"slide total {source_total}"
        )
    return SlideCutoff(raw=value, numerator=numerator, denominator=denominator)


def parse_pdf_selection(value: str, label: str, source_total: int) -> SlideCutoff:
    range_match = RANGE_PATTERN.fullmatch(value)
    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))
        denominator = int(range_match.group(3))
        if start < 1:
            raise ReleaseSliceError(
                f"{label} range start must be from 1 through the source total "
                f"({source_total}), got {start}"
            )
        if end < 1:
            raise ReleaseSliceError(
                f"{label} range end must be from 1 through the source total "
                f"({source_total}), got {end}"
            )
        if start > end:
            raise ReleaseSliceError(
                f"{label} range start {start} cannot exceed range end {end}"
            )
        if end > source_total:
            raise ReleaseSliceError(
                f"{label} range end must be from 1 through the source total "
                f"({source_total}), got {end}"
            )
        if denominator != source_total:
            raise ReleaseSliceError(
                f"{label} denominator {denominator} does not match the actual source "
                f"slide total {source_total}"
            )
        return SlideCutoff(
            raw=value,
            numerator=end,
            denominator=denominator,
            start=start,
            explicit_range=True,
        )
    return parse_cutoff(value, label, source_total)


def validate_inputs(
    source_text: str, through_text: str, pdf_text: str | None
) -> ReleaseInputs:
    structure = parse_source(source_text)
    source_total = len(structure.slides)
    publish = parse_cutoff(through_text, "publish_through_slide", source_total)
    if pdf_text in (None, ""):
        pdf = None
    else:
        pdf = parse_pdf_selection(pdf_text, "pdf_through_slide", source_total)
        if pdf.end > publish.numerator:
            raise ReleaseSliceError(
                f"pdf_through_slide ({pdf.raw}) cannot exceed "
                f"publish_through_slide ({publish.raw})"
            )
    return ReleaseInputs(source_total=source_total, publish=publish, pdf=pdf)


def add_pdf_config(text: str) -> str:
    count = text.count(REVEAL_INIT)
    if count != 1:
        raise ReleaseSliceError(
            f"Expected exactly one safe Reveal.initialize target, found {count}"
        )
    if "pdfSeparateFragments:" in text:
        raise ReleaseSliceError("Generated HTML already contains PDF-only configuration")
    # Decks normally set pdfMaxPagesPerSlide: 1 themselves, because the canvas is fixed
    extra = PDF_CONFIG if PAGE_LIMIT.search(text) else PDF_CONFIG + PAGE_LIMIT_CONFIG
    return text.replace(REVEAL_INIT, REVEAL_INIT + extra, 1)


def reconstruct(text: str, structure: DeckStructure, cutoff: SlideCutoff) -> str:
    if cutoff.start == 1 and cutoff.end == len(structure.slides):
        return text
    if cutoff.start == 1:
        last_included = structure.slides[cutoff.end - 1]
        return text[: last_included.end] + "\n\n" + text[structure.course_end_start :]

    _, course_start_end = exact_marker_positions(
        text, COURSE_START, "course START sentinel"
    )
    selected_slides = structure.slides[cutoff.start - 1 : cutoff.end]
    selected_markup_parts: list[str] = []
    for session in structure.sessions:
        session_slides = [
            slide
            for slide in selected_slides
            if session.start <= slide.start and slide.end <= session.end
        ]
        if not session_slides:
            continue
        session_start = SESSION_MARKER.match(text, session.start)
        session_end = (
            SESSION_MARKER.search(text, session_start.end(), session.end)
            if session_start is not None
            else None
        )
        if session_start is None or session_end is None:
            raise ReleaseSliceError(
                f"Could not resolve SESSION {session.number:02d} markers for range output"
            )
        selected_markup_parts.append(text[session_start.start() : session_start.end()])
        selected_markup_parts.extend(
            text[slide.start : slide.end] for slide in session_slides
        )
        selected_markup_parts.append(text[session_end.start() : session_end.end()])
    if not selected_markup_parts:
        selected_markup_parts = [
            text[slide.start : slide.end] for slide in selected_slides
        ]
    selected_markup = "\n\n".join(selected_markup_parts)
    return (
        text[:course_start_end]
        + "\n\n"
        + selected_markup
        + "\n\n"
        + text[structure.course_end_start :]
    )


def add_range_alias_fallback(
    text: str,
    source_text: str,
    source_structure: DeckStructure,
    cutoff: SlideCutoff,
) -> str:
    selected_slides = source_structure.slides[cutoff.start - 1 : cutoff.end]
    selected_ids = {
        slide.element_id for slide in selected_slides if slide.element_id is not None
    }
    source_markup_by_id = {
        slide.element_id: source_text[slide.start : slide.end]
        for slide in source_structure.slides
        if slide.element_id is not None
    }
    fallback_markup: dict[str, str] = {}
    for slide in selected_slides:
        markup = source_text[slide.start : slide.end]
        reference = SLIDE_REF_PATTERN.search(markup)
        if reference is None:
            continue
        target = reference.group(1)
        if target not in selected_ids and target in source_markup_by_id:
            fallback_markup[target] = base64.b64encode(
                source_markup_by_id[target].encode("utf-8")
            ).decode("ascii")

    if not fallback_markup:
        return text

    resolver_calls = list(ALIAS_RESOLVE_CALL.finditer(text))
    if len(resolver_calls) != 1:
        raise ReleaseSliceError(
            f"Expected exactly one IESlideAliases.resolve() call, found {len(resolver_calls)}"
        )

    fallback_json = json.dumps(fallback_markup, separators=(",", ":"))
    fallback_script = """    (function () {
        var fallbackMarkup = %s;
        var decodeUtf8 = function (encoded) {
          var binary = window.atob(encoded);
          var bytes = new Uint8Array(binary.length);
          var index;
          for (index = 0; index < binary.length; index += 1) {
            bytes[index] = binary.charCodeAt(index);
          }
          return new TextDecoder("utf-8").decode(bytes);
        };
        var originalResolve = window.IESlideAliases && window.IESlideAliases.resolve;
        if (typeof originalResolve !== "function") {
          throw new Error("IE Slide Aliases resolver is unavailable");
        }
        window.IESlideAliases.resolve = function () {
          var slides = document.querySelector(".reveal .slides");
          if (!slides) {
            throw new Error("Reveal slides container is unavailable");
          }
          var staged = [];
          var stagedTargets = Object.create(null);
          Array.prototype.forEach.call(
            document.querySelectorAll("section[data-slide-ref]"),
            function (alias) {
              if (alias.__ieSlideAliasResolved) return;
              var target = alias.getAttribute("data-slide-ref");
              var encoded = target && fallbackMarkup[target];
              if (!encoded || document.getElementById(target) || stagedTargets[target]) {
                return;
              }
              var fragment = document.createRange().createContextualFragment(decodeUtf8(encoded));
              var source = fragment.firstElementChild;
              if (
                !source ||
                source.tagName.toLowerCase() !== "section" ||
                source.id !== target
              ) {
                throw new Error("Invalid range alias fallback for #" + target);
              }
              slides.appendChild(source);
              staged.push(source);
              stagedTargets[target] = true;
            }
          );
          try {
            return originalResolve();
          } finally {
            staged.forEach(function (source) {
              if (source.parentNode) source.parentNode.removeChild(source);
            });
          }
        };
    }());
""" % fallback_json
    insert_at = resolver_calls[0].start()
    return text[:insert_at] + fallback_script + text[insert_at:]


def validate_output(
    output_text: str,
    source_text: str,
    source_structure: DeckStructure,
    cutoff: SlideCutoff,
    pdf_config: bool = False,
) -> None:
    _, _, output_slides = _scan_slides(output_text)
    expected_slides = source_structure.slides[cutoff.start - 1 : cutoff.end]
    if len(output_slides) != cutoff.count:
        raise ReleaseSliceError(
            f"Generated output contains {len(output_slides)} slides, expected "
            f"{cutoff.count}"
        )

    expected_markup = [source_text[slide.start : slide.end] for slide in expected_slides]
    actual_markup = [output_text[slide.start : slide.end] for slide in output_slides]
    if actual_markup != expected_markup:
        for index, (expected, actual) in enumerate(
            zip(expected_markup, actual_markup), start=1
        ):
            if expected != actual:
                source_number = cutoff.start + index - 1
                raise ReleaseSliceError(
                    f"Generated slide {index} does not match source slide {source_number}"
                )
        raise ReleaseSliceError("Generated slide sequence does not match the source cutoff")

    if output_text.count(COURSE_START) != 1 or output_text.count(COURSE_END) != 1:
        raise ReleaseSliceError("Generated output must retain one course sentinel pair")
    required_closings = (REVEAL_INIT, "</script>", "</body>", "</html>")
    missing = [item for item in required_closings if item not in output_text]
    if missing:
        raise ReleaseSliceError(
            "Generated output is missing required closing markup: " + ", ".join(missing)
        )
    if output_text.count(REVEAL_INIT) != 1:
        raise ReleaseSliceError("Generated output must retain exactly one Reveal.initialize call")
    if pdf_config:
        if output_text.count("pdfSeparateFragments: false,") != 1:
            raise ReleaseSliceError("PDF fragment configuration was not inserted exactly once")
        if len(PAGE_LIMIT.findall(output_text)) != 1:
            raise ReleaseSliceError("PDF page configuration was not inserted exactly once")
    elif "pdfSeparateFragments:" in output_text:
        raise ReleaseSliceError("PDF-only configuration is not allowed in public HTML")


def _print_validation(inputs: ReleaseInputs, structure: DeckStructure, machine: bool) -> None:
    publish_last = structure.slides[inputs.publish.numerator - 1]
    first_excluded = (
        structure.slides[inputs.publish.numerator]
        if inputs.publish.numerator < inputs.source_total
        else None
    )
    if machine:
        print(f"source_total={inputs.source_total}")
        print(f"publish_request={inputs.publish.raw}")
        print(f"publish_numerator={inputs.publish.numerator}")
        print(f"publish_denominator={inputs.publish.denominator or ''}")
        print(f"publish_padded={inputs.publish.numerator:03d}")
        print(f"last_included={inputs.publish.numerator} | {slide_identity(publish_last)}")
        if first_excluded is None:
            print("first_excluded=none")
        else:
            print(f"first_excluded={first_excluded.number} | {slide_identity(first_excluded)}")
        print(f"pdf_wanted={'true' if inputs.pdf is not None else 'false'}")
        print(f"pdf_request={inputs.pdf.raw if inputs.pdf is not None else 'skipped'}")
        print(f"pdf_start={inputs.pdf.start if inputs.pdf is not None else ''}")
        print(f"pdf_end={inputs.pdf.end if inputs.pdf is not None else ''}")
        print(f"pdf_count={inputs.pdf.count if inputs.pdf is not None else ''}")
        print(
            f"pdf_selected_count={inputs.pdf.count if inputs.pdf is not None else ''}"
        )
        print(f"pdf_numerator={inputs.pdf.end if inputs.pdf is not None else ''}")
        print(
            f"pdf_padded_start={inputs.pdf.start:03d}"
            if inputs.pdf is not None
            else "pdf_padded_start="
        )
        print(
            f"pdf_padded_end={inputs.pdf.end:03d}"
            if inputs.pdf is not None
            else "pdf_padded_end="
        )
        print(
            f"pdf_padded={inputs.pdf.end:03d}" if inputs.pdf is not None else "pdf_padded="
        )
        print(
            f"pdf_denominator={inputs.pdf.denominator if inputs.pdf is not None and inputs.pdf.denominator is not None else ''}"
        )
        return

    print(f"Validated source deck: {inputs.source_total} slides")
    print(f"Publish request: {inputs.publish.raw}")
    print(f"Published: slides 1-{inputs.publish.numerator}")
    print(f"Last included: {inputs.publish.numerator} | {slide_identity(publish_last)}")
    if first_excluded is None:
        print("First excluded: none")
    else:
        print(f"First excluded: {first_excluded.number} | {slide_identity(first_excluded)}")
    if inputs.pdf is None:
        print("PDF: skipped")
    else:
        print(f"PDF request: {inputs.pdf.raw}")
        print(f"PDF: slides {inputs.pdf.start}-{inputs.pdf.end}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--through-slide")
    parser.add_argument("--pdf-through-slide")
    parser.add_argument("--pdf-config", action="store_true")
    parser.add_argument("--validate-inputs", action="store_true")
    parser.add_argument(
        "--machine",
        action="store_true",
        help="Print key=value validation fields for workflow output handling",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.validate_inputs:
            if args.source is None or args.through_slide is None:
                raise ReleaseSliceError(
                    "--validate-inputs requires --source and --through-slide"
                )
            if args.out is not None or args.pdf_config:
                raise ReleaseSliceError(
                    "--validate-inputs does not accept --out or --pdf-config"
                )
            source_text = args.source.read_text(encoding="utf-8")
            source_structure = parse_source(source_text)
            inputs = validate_inputs(
                source_text, args.through_slide, args.pdf_through_slide
            )
            _print_validation(inputs, source_structure, args.machine)
            return 0

        if args.machine:
            raise ReleaseSliceError("--machine is permitted only with --validate-inputs")
        if args.pdf_through_slide is not None:
            raise ReleaseSliceError(
                "--pdf-through-slide is permitted only with --validate-inputs"
            )
        if args.through_slide is None:
            raise ReleaseSliceError("--through-slide is required when generating output")
        if args.source is None or args.out is None:
            raise ReleaseSliceError("--source and --out are required when generating output")

        source_text = args.source.read_text(encoding="utf-8")
        source_structure = parse_source(source_text)
        cutoff_parser = parse_pdf_selection if args.pdf_config else parse_cutoff
        cutoff = cutoff_parser(
            args.through_slide, "through-slide", len(source_structure.slides)
        )
        output_text = reconstruct(source_text, source_structure, cutoff)
        # Aliases whose canonical slide falls outside the selection, in either
        # a cumulative cutoff or an explicit range, get a staged fallback copy
        output_text = add_range_alias_fallback(
            output_text, source_text, source_structure, cutoff
        )
        if args.pdf_config:
            output_text = add_pdf_config(output_text)
        validate_output(
            output_text,
            source_text,
            source_structure,
            cutoff,
            pdf_config=args.pdf_config,
        )

        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output_text, encoding="utf-8", newline="")
        written = args.out.read_text(encoding="utf-8")
        validate_output(
            written,
            source_text,
            source_structure,
            cutoff,
            pdf_config=args.pdf_config,
        )
        print(f"Source slides: {len(source_structure.slides)}")
        print(f"Selected slides: {cutoff.start}-{cutoff.end}")
        print(f"Output: {args.out}")
        print(f"Bytes: {args.out.stat().st_size}")
        return 0
    except (OSError, ReleaseSliceError) as error:
        print(f"release_slice error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
