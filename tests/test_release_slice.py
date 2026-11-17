from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release_slice import (  # noqa: E402
    ReleaseSliceError,
    add_range_alias_fallback,
    parse_cutoff,
    parse_pdf_selection,
    parse_source,
    reconstruct,
)


def deck(body: str, resolver: bool = True) -> str:
    script = "    IESlideAliases.resolve();\n" if resolver else ""
    return (
        "<html><body><div class=\"reveal\"><div class=\"slides\">\n"
        "<!-- COURSE SESSION CONTENT START -->\n"
        f"{body}\n"
        "<!-- COURSE SESSION CONTENT END -->\n"
        "</div></div>\n<script>\n"
        f"{script}"
        "    Reveal.initialize({ width: 1600 });\n</script>\n</body></html>\n"
    )


THREE_SLIDES = (
    "<!-- SESSION 01 START -->\n"
    "<section id=\"a\"><h2>A</h2></section>\n"
    "<section id=\"b\"><h2>B</h2></section>\n"
    "<!-- SESSION 01 END -->\n"
    "<!-- SESSION 02 START -->\n"
    "<section id=\"c\" data-slide-ref=\"a\"></section>\n"
    "<!-- SESSION 02 END -->"
)


class ParseCutoffTests(unittest.TestCase):
    def test_accepts_valid_cutoff(self) -> None:
        cutoff = parse_cutoff("101/108", "publish_through_slide", 108)
        self.assertEqual((cutoff.numerator, cutoff.denominator), (101, 108))

    def test_explains_session_style_mistake(self) -> None:
        with self.assertRaisesRegex(ReleaseSliceError, "not a session number"):
            parse_cutoff("1014/108", "publish_through_slide", 108)

    def test_rejects_denominator_mismatch(self) -> None:
        with self.assertRaises(ReleaseSliceError):
            parse_cutoff("10/99", "publish_through_slide", 108)

    def test_range_requires_spaces_around_hyphen(self) -> None:
        with self.assertRaises(ReleaseSliceError):
            parse_pdf_selection("5-8/10", "pdf_through_slide", 10)
        selection = parse_pdf_selection("5 - 8/10", "pdf_through_slide", 10)
        self.assertEqual((selection.start, selection.end), (5, 8))


class StructureTests(unittest.TestCase):
    def test_template_index_is_release_ready(self) -> None:
        structure = parse_source((ROOT / "index.html").read_text(encoding="utf-8"))
        self.assertGreater(len(structure.slides), 0)

    def test_template_defers_pdf_only_configuration_to_release_tooling(self) -> None:
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("pdfSeparateFragments:", source)

    def test_rejects_slide_outside_session(self) -> None:
        body = "<!-- SESSION 01 START -->\n<!-- SESSION 01 END -->\n<section id=\"x\"></section>"
        with self.assertRaises(ReleaseSliceError):
            parse_source(deck(body))

    def test_rejects_descending_sessions(self) -> None:
        body = (
            "<!-- SESSION 02 START -->\n<section id=\"a\"></section>\n<!-- SESSION 02 END -->\n"
            "<!-- SESSION 01 START -->\n<section id=\"b\"></section>\n<!-- SESSION 01 END -->"
        )
        with self.assertRaises(ReleaseSliceError):
            parse_source(deck(body))


class AliasFallbackTests(unittest.TestCase):
    def test_range_alias_gets_staged_canonical_copy(self) -> None:
        text = deck(THREE_SLIDES)
        structure = parse_source(text)
        cutoff = parse_pdf_selection("3 - 3/3", "pdf", 3)
        output = add_range_alias_fallback(reconstruct(text, structure, cutoff), text, structure, cutoff)
        self.assertIn("fallbackMarkup", output)

    def test_cumulative_forward_alias_gets_staged_copy(self) -> None:
        body = (
            "<!-- SESSION 01 START -->\n"
            "<section id=\"a\" data-slide-ref=\"c\"></section>\n"
            "<section id=\"b\"><h2>B</h2></section>\n"
            "<section id=\"c\"><h2>C</h2></section>\n"
            "<!-- SESSION 01 END -->"
        )
        text = deck(body)
        structure = parse_source(text)
        cutoff = parse_cutoff("2", "publish", 3)
        output = add_range_alias_fallback(reconstruct(text, structure, cutoff), text, structure, cutoff)
        self.assertIn("fallbackMarkup", output)

    def test_resolver_call_is_required_when_fallback_needed(self) -> None:
        text = deck(THREE_SLIDES, resolver=False)
        structure = parse_source(text)
        cutoff = parse_pdf_selection("3 - 3/3", "pdf", 3)
        with self.assertRaises(ReleaseSliceError):
            add_range_alias_fallback(reconstruct(text, structure, cutoff), text, structure, cutoff)


if __name__ == "__main__":
    unittest.main()
