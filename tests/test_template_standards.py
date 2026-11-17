"""Cross-course guards for the shared template standards. Standard library only."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_deck  # noqa: E402

CSS = (ROOT / "ie-scitech-reveal.css").read_text(encoding="utf-8")
BROWSER_QA = (ROOT / "scripts" / "check_browser_qa.py").read_text(encoding="utf-8")
COMPONENTS = (ROOT / "ie-components.js").read_text(encoding="utf-8")
GALLERY = (ROOT / "slide_patterns.html").read_text(encoding="utf-8")
COURSE_CLASS = re.compile(r"^(s\d+[a-z]*|session|slide-\d+|gp\d+|f)-")


def css_strip_lists():
    return [set(c.strip().lstrip(".") for c in group.split(","))
            for group in re.findall(r":is\((\.ie-band,[^)]*)\)", CSS)]


class StripRegistryTests(unittest.TestCase):
    def test_static_browser_and_css_registries_match(self):
        browser = re.search(r"const STRIP = '([^']+)'", BROWSER_QA).group(1)
        browser_set = set(c.strip().lstrip(".") for c in browser.split(","))
        self.assertEqual(browser_set, check_deck.STRIP_CLASSES)
        lists = css_strip_lists()
        self.assertTrue(lists, "no strip standard block found in the stylesheet")
        for group in lists:
            self.assertEqual(group, check_deck.STRIP_CLASSES)

    def test_registry_holds_no_course_specific_class(self):
        for name in check_deck.STRIP_CLASSES:
            self.assertIsNone(COURSE_CLASS.match(name), name)
        self.assertIn("ie-takeaway", check_deck.STRIP_CLASSES)

    def test_shared_stylesheet_has_no_slide_id_selectors(self):
        self.assertNotRegex(CSS, r"section#(session|slide)-\d")


class ImageModalTests(unittest.TestCase):
    def test_stylesheet_ships_modal_and_click_cue(self):
        for hook in (".ie-image-modal-trigger::after", ".ie-image-modal.is-active",
                     ".ie-image-modal-img", ".ie-image-modal-trigger-icon",
                     "html.print-pdf .ie-image-modal"):
            self.assertIn(hook, CSS)
        self.assertIn('content: "CLICK FOR IMAGE"', CSS)

    def test_components_wire_the_modal(self):
        self.assertIn("function initImageModals", COMPONENTS)
        self.assertIn("initImageModals(deck)", COMPONENTS)
        for event in ('"Escape"', '"Enter"', '" "', "slidechanged"):
            self.assertIn(event, COMPONENTS)

    def test_gallery_example_points_at_its_dialog(self):
        trigger = re.search(r'class="ie-band ie-image-modal-trigger"[^>]*aria-controls="([^"]+)"', GALLERY)
        self.assertIsNotNone(trigger)
        self.assertIn(f'id="{trigger.group(1)}" class="ie-image-modal"', GALLERY)


class BrandTableTests(unittest.TestCase):
    def test_brand_table_pattern_and_styles(self):
        for hook in (".ie-table-brand-cell", ".ie-table-brand-link", ".ie-table-brand-name"):
            self.assertIn(hook, CSS)
        self.assertIn('id="pattern-31-brand-table"', GALLERY)

    def test_brand_links_open_safely(self):
        for link in re.findall(r'<a class="ie-table-brand-link"[^>]*>', GALLERY):
            self.assertIn('target="_blank"', link)
            self.assertIn('rel="noopener noreferrer"', link)
            self.assertIn("aria-label=", link)


if __name__ == "__main__":
    unittest.main()
