from pathlib import Path
import base64
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_deck import TreeBuilder
from download_controls import (validate_download_nodes, contrast_ratio,
                               check_control_contrast, click_download)

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = base64.b64encode(b"example\n").decode()
ANCHOR = ('<a class="ie-download-btn" download="example.txt" data-download-source="example.txt" '
          'href="data:text/plain;base64,' + PAYLOAD + '" aria-label="Download example.txt" '
          'title="Download example.txt"><img class="ie-download-icon" '
          'src="media/icons/tabler/download.svg" alt=""></a>')


class DownloadPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def check(self, anchor=ANCHOR, heading=True, sid="example"):
        parser = TreeBuilder()
        parser.feed('<section id="' + sid + '">' +
                    ('<h2 class="ie-title-with-download">Title' if heading else '') + anchor +
                    ('</h2>' if heading else '') + '</section>')
        return validate_download_nodes(list(parser.root.iter()), self.root, "index.html")

    def test_official_title_icon_is_accepted(self):
        self.assertEqual(self.check(), [])

    def test_card_is_not_an_official_download_button(self):
        self.assertTrue(any("official" in e for e in self.check(ANCHOR.replace("ie-download-btn", "ie-link-card"))))

    def test_missing_download_attribute_is_rejected(self):
        self.assertTrue(any("filename" in e for e in self.check(ANCHOR.replace('download="example.txt" ', '', 1))))

    def test_new_window_target_is_rejected(self):
        self.assertTrue(any("window" in e for e in self.check(ANCHOR.replace("<a ", '<a target="_blank" ', 1))))

    def test_navigable_href_is_rejected(self):
        bad = ANCHOR.replace("data:text/plain;base64," + PAYLOAD, "example.txt")
        self.assertTrue(any("base64" in e for e in self.check(bad)))

    def test_bare_data_link_cannot_silently_become_a_download(self):
        bad = '<a href="data:text/plain;base64,' + PAYLOAD + '">Download</a>'
        self.assertTrue(any("filename" in e for e in self.check(bad)))

    def test_wrong_icon_is_rejected(self):
        self.assertTrue(any("local download icon" in e for e in self.check(ANCHOR.replace("download.svg", "link.svg"))))

    def test_title_placement_is_required(self):
        self.assertTrue(any("beside a title" in e for e in self.check(heading=False)))

    def test_missing_accessible_label_is_rejected(self):
        self.assertTrue(any("accessible" in e for e in self.check(ANCHOR.replace('aria-label="Download example.txt"', ''))))

    def test_native_action_cannot_be_overridden(self):
        self.assertTrue(any("native" in e for e in self.check(ANCHOR.replace("<a ", '<a onclick="window.open()" ', 1))))

    def test_new_exception_is_rejected(self):
        bad = ANCHOR.replace("<a ", '<a data-download-exception="inline" ', 1)
        self.assertTrue(any("unregistered" in e for e in self.check(bad)))

    def register(self):
        entry = dict(deck="index.html", slide="example", source="example.txt",
                     kind="inline", count=1, reason="Existing inline file reference")
        (self.root / "download-exceptions.json").write_text(json.dumps({"exceptions": [entry]}))

    def test_existing_exception_is_allowed_only_at_its_registered_location(self):
        self.register()
        anchor = ANCHOR.replace('class="ie-download-btn"', 'data-download-exception="inline"')
        self.assertEqual(self.check(anchor, heading=False), [])
        self.assertTrue(any("unregistered" in e for e in self.check(anchor, heading=False, sid="new-slide")))

    def test_exception_count_cannot_expand(self):
        self.register()
        anchor = ANCHOR.replace('class="ie-download-btn"', 'data-download-exception="inline"')
        self.assertTrue(any("expected 1" in e for e in self.check(anchor + anchor)))

    def test_exception_never_waives_no_window_rule(self):
        self.register()
        anchor = ANCHOR.replace('class="ie-download-btn"', 'data-download-exception="inline" target="_blank"')
        self.assertTrue(any("window" in e for e in self.check(anchor, heading=False)))

    def test_contrast_known_values(self):
        self.assertAlmostEqual(contrast_ratio((0, 0, 0), (255, 255, 255)), 21)
        self.assertEqual(contrast_ratio((255, 255, 255), (255, 255, 255)), 1)
        self.assertLess(contrast_ratio((255, 255, 255), (201, 255, 138)), 3)


class RenderedDownloadTests(unittest.TestCase):
    """Actual Chromium regressions, including deliberately broken variants."""
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
        css = (ROOT / "ie-scitech-reveal.css").read_text(encoding="utf-8")
        cls.css = css[css.index(":root {"):css.index("}", css.index(":root {"))+1]
        cls.css += css[css.index("/* Official title-side file download control, pattern-27 */"):]
        cls.svg = base64.b64encode((ROOT / "media/icons/tabler/download.svg").read_bytes()).decode()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 800, "height": 400}, accept_downloads=True)
        self.page = self.context.new_page()
        self.addCleanup(self.context.close)

    def fixture(self, background="white", dark=False, extra_css="", onclick=""):
        anchor = ANCHOR.replace("media/icons/tabler/download.svg", "data:image/svg+xml;base64," + self.svg)
        if dark:
            anchor = anchor.replace('class="ie-download-btn"', 'class="ie-download-btn ie-download-btn--dark"')
        if onclick:
            anchor = anchor.replace("<a ", '<a onclick="' + onclick + '" ', 1)
        self.page.set_content('<style>' + self.css + extra_css +
                              '</style><div class="reveal"><section class="ie-slide" style="background:' +
                              background + ';padding:40px"><h2 class="ie-title-with-download">Save' +
                              anchor + '</h2></section></div>')
        control = self.page.locator("a[download]")
        control.locator("img").evaluate("i=>i.decode()")
        return control

    def test_light_and_dark_surfaces_pass_in_all_states(self):
        for background, dark in (("white", False), ("rgb(36,36,36)", True)):
            with self.subTest(background=background):
                errors = []
                ratios = check_control_contrast(self.page, self.fixture(background, dark), "fixture", errors)
                self.assertEqual(errors, [])
                self.assertEqual(len(ratios), 3)
                self.assertGreaterEqual(min(ratios), 3)

    def test_wrong_dark_treatment_on_light_surface_fails(self):
        errors = []
        check_control_contrast(self.page, self.fixture("white", True), "fixture", errors)
        self.assertTrue(any("normal" in e and "below" in e for e in errors), errors)

    def test_wrong_light_treatment_on_dark_surface_fails(self):
        errors = []
        check_control_contrast(self.page, self.fixture("black", False), "fixture", errors)
        self.assertTrue(any("normal" in e and "below" in e for e in errors), errors)

    def test_hover_regression_is_detected(self):
        errors = []
        bad = ".ie-download-btn:hover .ie-download-icon {filter:brightness(0) invert(1)!important}"
        check_control_contrast(self.page, self.fixture(extra_css=bad), "fixture", errors)
        self.assertTrue(any("hover" in e and "below" in e for e in errors), errors)

    def test_real_gradient_background_is_measured(self):
        errors = []
        check_control_contrast(self.page, self.fixture("linear-gradient(90deg,white,rgb(230,230,230))", True), "fixture", errors)
        self.assertTrue(any("below" in e for e in errors), errors)

    def test_made_up_button_geometry_is_detected(self):
        errors = []
        bad = ".ie-download-btn {width:80px!important}"
        check_control_contrast(self.page, self.fixture(extra_css=bad), "fixture", errors)
        self.assertTrue(any("geometry" in e for e in errors), errors)

    def test_partly_invisible_icon_on_split_background_fails(self):
        errors = []
        split = ".ie-download-btn {background:linear-gradient(90deg,white 50%,black 50%)!important}"
        check_control_contrast(self.page, self.fixture(extra_css=split), "fixture", errors)
        self.assertTrue(any("normal" in e and "below" in e for e in errors), errors)

    def test_title_gap_is_enforced(self):
        errors = []
        bad = ".ie-title-with-download {gap:30px!important}"
        check_control_contrast(self.page, self.fixture(extra_css=bad), "fixture", errors)
        self.assertTrue(any("title gap" in e for e in errors), errors)

    def test_actual_download_has_exact_name_and_contents(self):
        errors = []
        valid = click_download(self.page, self.fixture(), b"example\n", "example.txt", errors, "fixture")
        self.assertTrue(valid, errors)
        self.assertEqual(errors, [])

    def test_a_download_that_also_opens_a_window_fails(self):
        errors = []
        control = self.fixture(onclick="window.open('about:blank')")
        self.assertFalse(click_download(self.page, control, b"example\n", "example.txt", errors, "fixture"))
        self.assertTrue(any("another tab or window" in e for e in errors), errors)

    def test_a_download_that_also_navigates_fails(self):
        errors = []
        control = self.fixture(onclick="setTimeout(()=>location.hash='moved',0)")
        self.assertFalse(click_download(self.page, control, b"example\n", "example.txt", errors, "fixture"))
        self.assertTrue(any("navigated" in e for e in errors), errors)

    def test_saved_bytes_are_compared_with_the_source(self):
        errors = []
        self.assertFalse(click_download(self.page, self.fixture(), b"wrong", "example.txt", errors, "fixture"))
        self.assertTrue(any("bytes" in e for e in errors), errors)

    def test_same_url_reload_is_still_rejected(self):
        errors = []
        control = self.fixture(onclick="setTimeout(()=>location.reload(),10)")
        self.assertFalse(click_download(self.page, control, b"example\n", "example.txt", errors, "fixture"))
        self.assertTrue(any("navigated" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
