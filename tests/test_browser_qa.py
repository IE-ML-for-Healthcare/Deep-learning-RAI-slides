from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_browser_qa import select_slides, scoped_locator  # noqa: E402


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.slides = [dict(id="a"), dict(id="b"), dict(id="alias", ref="a"), dict(id="other", ref="b")]

    def test_canonical_edit_also_checks_aliases(self):
        self.assertEqual([s["id"] for s in select_slides(self.slides, {"a"})], ["a", "alias"])

    def test_alias_only_edit_stays_local(self):
        self.assertEqual([s["id"] for s in select_slides(self.slides, {"alias"})], ["alias"])

    def test_no_selection_preserves_full_default_for_continuous_integration(self):
        self.assertEqual(select_slides(self.slides, set()), self.slides)

    def test_full_with_screenshot_ids_still_checks_every_slide(self):
        self.assertEqual(select_slides(self.slides, {"a"}, full=True), self.slides)

    def test_typo_does_not_produce_a_false_pass(self):
        with self.assertRaisesRegex(ValueError, "Unknown slide ids: typo"):
            select_slides(self.slides, {"typo"})

    def test_full_mode_also_rejects_unknown_screenshot_ids(self):
        with self.assertRaises(ValueError):
            select_slides(self.slides, {"typo"}, full=True)

    def test_scoped_functional_selectors_include_the_section_itself(self):
        class Page:
            def locator(self, selector):
                return selector
        selector = scoped_locator(Page(), "section.ie-roadmap", ["a"])
        self.assertIn('section[id="a"]', selector)
        self.assertIn('section[id="a"] *', selector)


if __name__ == "__main__":
    unittest.main()
