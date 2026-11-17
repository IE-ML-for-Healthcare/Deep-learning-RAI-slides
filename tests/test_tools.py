from pathlib import Path
import base64
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_deck  # noqa: E402
import sync_downloads  # noqa: E402


class StaticQATests(unittest.TestCase):
    def test_template_passes_static_qa(self) -> None:
        result = subprocess.run([sys.executable, "scripts/check_deck.py"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_detects_full_stop_in_list_item_and_mixed_variant(self) -> None:
        html = (
            "<div class=\"reveal\"><div class=\"slides\">"
            "<section id=\"s\" class=\"ie-slide ie-light ie-bg-dark-science\">"
            "<div class=\"ie-logo\"><img src=\"logos/ie-scitech-horizontal-light-accent.svg\"></div>"
            "<ul><li>Ends with a dot.</li></ul></section></div></div>"
            "<script src=\"https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reveal.js\"></script>"
            "<script src=\"ie-reveal-fit.js\"></script>"
            "<script>Reveal.initialize({width: 1600, height: 900, margin: 0})</script>"
        )
        tmp = ROOT / "tmp" / "test_deck.html"
        tmp.parent.mkdir(exist_ok=True)
        tmp.write_text(html, encoding="utf-8")
        report = check_deck.Report()
        check_deck.check_deck(tmp, report, {}, is_main=False)
        joined = " ".join(report.errors)
        self.assertIn("full stop", joined)
        self.assertIn("do not combine", joined)
        tmp.unlink()


class TypeScaleTests(unittest.TestCase):
    def test_deck_uses_fixed_px_type_scale(self) -> None:
        report = check_deck.Report()
        check_deck.check_type_scale(report)
        self.assertEqual(report.errors, [])


class TakeawayStandardTests(unittest.TestCase):
    def test_shared_css_carries_the_approved_strip_standard(self) -> None:
        report = check_deck.Report()
        check_deck.check_takeaway_standard(report)
        self.assertEqual(report.errors, [])
        css = (ROOT / "ie-scitech-reveal.css").read_text(encoding="utf-8")
        self.assertIn("background: rgba(255, 255, 255, 0.40) !important", css)
        self.assertIn("background: rgba(255, 255, 255, 0.10) !important", css)

    def test_static_qa_rejects_solid_band_and_inline_strip_styles(self) -> None:
        html = (
            "<div class=\"reveal\"><div class=\"slides\">"
            "<section id=\"s\" class=\"ie-slide ie-light\">"
            "<div class=\"ie-logo\"><img src=\"logos/ie-scitech-horizontal-light-accent.svg\"></div>"
            "<p class=\"ie-band is-solid\">Solid</p>"
            "<p class=\"ie-band\" style=\"background: #000024\">Inline</p></section></div></div>"
            "<script src=\"https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reveal.js\"></script>"
            "<script src=\"ie-reveal-fit.js\"></script>"
            "<script>Reveal.initialize({width: 1600, height: 900, margin: 0})</script>"
        )
        tmp = ROOT / "tmp" / "test_takeaway.html"
        tmp.parent.mkdir(exist_ok=True)
        tmp.write_text(html, encoding="utf-8")
        report = check_deck.Report()
        check_deck.check_deck(tmp, report, {}, is_main=False)
        joined = " ".join(report.errors)
        self.assertIn("is-solid is retired", joined)
        self.assertIn("inline background or border", joined)

    def test_browser_qa_enforces_strip_colours_and_clash_rules(self) -> None:
        source = (ROOT / "scripts" / "check_browser_qa.py").read_text(encoding="utf-8")
        for token in ("want.a", "0.4", "0.1", "clashes with the IE logo", "clashes with the takeaway strip",
                      "key takeaway strip breaks the standard"):
            self.assertIn(token, source)

    def test_browser_qa_enforces_the_grid(self) -> None:
        source = (ROOT / "scripts" / "check_browser_qa.py").read_text(encoding="utf-8")
        for token in ("data-grid-exception", "[96, 84]", "[86, 88, 74]", "does not sit on a gridline",
                      "(n(b.l, 48) && n(b.b, 852))", "grid_strict"):
            self.assertIn(token, source)
        rules = (ROOT / "instructions" / "slide_rules.md").read_text(encoding="utf-8")
        self.assertIn("## Grid", rules)

    def test_browser_qa_enforces_full_bleed_card_media(self) -> None:
        source = (ROOT / "scripts" / "check_browser_qa.py").read_text(encoding="utf-8")
        css = (ROOT / "ie-scitech-reveal.css").read_text(encoding="utf-8")
        rules = (ROOT / "instructions" / "slide_rules.md").read_text(encoding="utf-8")
        for token in ("ie-card--media-bleed", "ie-card-media--full-bleed", "ie-card-overlay--full-width",
                      "equal-overlay card grid has different overlay heights"):
            self.assertIn(token, source)
        for token in ("max-width: none", "max-height: none", "ie-card-grid--equal-overlays"):
            self.assertIn(token, css)
        self.assertIn("Full-bleed media cards", rules)

    def test_grid_exceptions_state_a_reason(self) -> None:
        import re
        deck = (ROOT / "index.html").read_text(encoding="utf-8")
        for reason in re.findall(r'data-grid-exception="([^"]*)"', deck):
            self.assertGreaterEqual(len(reason.split()), 4, reason)


class CssGuardTests(unittest.TestCase):
    def test_title_size_guard_rejects_literal_outlier(self) -> None:
        source = "<style>.reveal .ie-slide.s1 h2 { font-size: 28px; }</style>"
        violations = check_deck.find_css_guard_violations(source)
        self.assertEqual(len(violations["title"]), 1)

    def test_title_size_guard_allows_documented_display_exception(self) -> None:
        source = "<style>/* Display exception: card heading */ .reveal .ie-slide.s1 h2 { font-size: 28px; }</style>"
        violations = check_deck.find_css_guard_violations(source)
        self.assertEqual(violations["title"], [])

    def test_table_and_duplicate_guards_reject_unshared_rules(self) -> None:
        source = (
            "<style>"
            ".reveal .slides section#session-01-x .ie-table { font-size: 20px; }"
            ".duplicate { color: red; } .duplicate { color: red; }"
            "</style>"
        )
        violations = check_deck.find_css_guard_violations(source)
        self.assertEqual(len(violations["table"]), 1)
        self.assertEqual(len(violations["duplicate"]), 1)


class LayoutGuardTests(unittest.TestCase):
    def test_inset_guard_rejects_unlisted_variant_and_uncommented_inset(self) -> None:
        source = (
            '<div class="safe-frame safe-frame--wide"></div>'
            "<style>.reveal .slides section#session-01-x > .safe-frame { top: 10px; }</style>"
        )
        violations = check_deck.find_css_guard_violations(source)
        self.assertEqual(len(violations["inset"]), 2)

    def test_inset_guard_allows_named_variant_and_documented_exception(self) -> None:
        source = (
            '<div class="safe-frame safe-frame--dense"></div>'
            "<style>/* Safe frame exception: needs more height */ "
            ".reveal .slides section#session-01-x > .safe-frame { top: 10px; }</style>"
        )
        violations = check_deck.find_css_guard_violations(source)
        self.assertEqual(violations["inset"], [])

    def test_quote_and_card_guards(self) -> None:
        source = (
            "<style>.reveal .ie-slide.slide-1 .source-quote { font-size: 40px; }"
            "/* Display exception: hero quote */ .reveal .ie-slide.slide-2 .source-quote { font-size: 60px; }"
            ".reveal .ie-slide.s2-x .agenda-card h3 { font-size: 26px; }</style>"
        )
        violations = check_deck.find_css_guard_violations(source)
        self.assertEqual(len(violations["quote"]), 1)
        self.assertEqual(len(violations["card"]), 1)


class StandardsGuardTests(unittest.TestCase):
    def test_fit_scale_width_and_keyrow_shadow_are_rejected(self) -> None:
        source = (
            "<style>.reveal .slides section#s1 .box { width: calc(100% / var(--fit-scale)); }"
            ".reveal .slides section#s1 .t tbody th[scope=\"row\"] { box-shadow: inset 8px 0 0 lime; }"
            ".reveal .ie-slide .ie-table tbody tr.ie-table-key-row th { box-shadow: inset 8px 0 0 lime; }</style>"
        )
        violations = check_deck.find_css_guard_violations(source)
        self.assertEqual(len(violations["fit"]), 1)
        self.assertEqual(len(violations["keyrow"]), 1)

    def test_quote_weight_needs_exception(self) -> None:
        source = "<style>.reveal .ie-slide.slide-1 .ie-quote-emphasis { font-weight: 400; }</style>"
        self.assertEqual(len(check_deck.find_css_guard_violations(source)["quote"]), 1)

    def test_quote_markup_standard(self) -> None:
        bad = (
            '<p class="source-quote">"A <span class="galileo-emphasis">phrase</span>"</p>'
            '<p class="source-attribution">Galileo</p>'
        )
        good = (
            '<p class="source-quote">"A <span class="ie-quote-emphasis">phrase</span>"</p>'
            '<p class="ie-quote-attribution">- Galileo</p>'
        )
        self.assertEqual(len(check_deck.find_markup_guard_violations(bad)), 2)
        self.assertEqual(check_deck.find_markup_guard_violations(good), [])

    def test_one_key_row_per_table(self) -> None:
        two = '<table><tr class="ie-table-key-row"></tr><tr class="ie-table-key-row ie-table-key-row--bold"></tr></table>'
        one = '<table><tr class="ie-table-key-row ie-table-key-row--bold"></tr><tr></tr></table>'
        self.assertEqual(len(check_deck.find_markup_guard_violations(two)), 1)
        self.assertEqual(check_deck.find_markup_guard_violations(one), [])

    def test_pop_ups_must_use_the_shared_tooltip(self) -> None:
        bad = (
            '<div class="maip-result"><span class="maip-fix" role="tooltip">Tip</span></div>'
            '<span class="card-popover">Tip</span>'
            '<p data-tooltip="Tip">Term</p>'
            '<p class="ie-tooltip" data-tooltip="Tip">Term</p>'
        )
        good = (
            '<div class="ie-two-col pattern-tooltip-row">'
            '<p class="ie-band ie-tooltip" tabindex="0" data-tooltip="Tip" aria-label="Term: Tip">Term</p></div>'
        )
        self.assertEqual(len(check_deck.find_markup_guard_violations(bad)), 4)
        self.assertEqual(check_deck.find_markup_guard_violations(good), [])

    def test_speaker_notes_default_is_forbidden(self) -> None:
        import json
        self.assertEqual(json.loads((ROOT / "deck.config.json").read_text(encoding="utf-8"))["speakerNotes"], "forbidden")


class DownloadSyncTests(unittest.TestCase):
    def test_patterns_download_payload_matches_source(self) -> None:
        total, stale, errors = sync_downloads.process(ROOT / "slide_patterns.html", check=True)
        self.assertEqual((stale, errors), (0, []))
        self.assertGreaterEqual(total, 1)

    def test_data_uri_round_trip(self) -> None:
        source = ROOT / "examples" / "downloads" / "example-prompt.md"
        uri = sync_downloads.data_uri(source)
        self.assertTrue(uri.startswith("data:text/markdown;charset=utf-8;base64,"))
        self.assertEqual(base64.b64decode(uri.split(",", 1)[1]), source.read_bytes())


if __name__ == "__main__":
    unittest.main()
