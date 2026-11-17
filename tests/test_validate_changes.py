from pathlib import Path
import sys
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_changes import css_dependencies, deck_parts, make_plan, qa_python  # noqa: E402


def deck(copy="Alpha", css="#a .card { padding: 4px; }", script="start()"):
    return (f"<html><head><style>{css}</style></head><body><div class='reveal'><div class='slides'>"
            f"<section id='a'><h2>{copy}</h2><img src='media/a.png'>"
            "<a data-download-source='media/prompt.md' href='data:text/plain;base64,eA=='>Download</a></section>"
            "<section id='b'><h2>Beta</h2><img src='media/b.png'></section>"
            "<section id='c' data-slide-ref='a'></section>"
            f"</div></div><script>{script}</script></body></html>")


class SelectionTests(unittest.TestCase):
    def test_copy_edit_runs_slide_checks_without_unrelated_tooling_tests(self):
        plan = make_plan(["index.html"], deck(), deck(copy="Alpha updated"))
        self.assertEqual(plan.slides, ["a"])
        self.assertTrue(plan.static and plan.downloads)
        self.assertFalse(plan.full_browser or plan.gallery or plan.full_tests or plan.tests)

    def test_scoped_css_keeps_validation_local(self):
        plan = make_plan(["index.html"], deck(), deck(css="#a .card { padding: 8px; }"))
        self.assertEqual(plan.slides, ["a"])
        self.assertFalse(plan.full_browser)

    def test_selector_attribute_values_are_not_positive_slide_anchors(self):
        for css in ('a[href="#a"] { padding: 8px; }',
                    '@supports selector(#a) { .card { padding: 8px; } }',
                    'section:nth-child(1 of #a) { padding: 8px; }'):
            with self.subTest(css=css):
                self.assertTrue(make_plan(["index.html"], deck(), deck(css=css)).full_browser)
        local = make_plan(["index.html"], deck(), deck(css='#a a[href="#b"] { padding: 8px; }'))
        self.assertEqual(local.slides, ["a"])
        self.assertFalse(local.full_browser)

    def test_gallery_only_asset_runs_gallery_checks(self):
        plan = make_plan(["media/gallery-only.png"], deck(), deck(), gallery_assets={"media/gallery-only.png"})
        self.assertTrue(plan.gallery and plan.static and plan.downloads)
        self.assertFalse(plan.full_browser or plan.slides or plan.full_tests)

    def test_nested_stylesheet_assets_resolve_relative_paths_and_import_cycles(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "styles").mkdir()
            (root / "main.css").write_text('@import "styles/theme.css";', encoding="utf-8")
            (root / "styles/theme.css").write_text(
                '@import url("../main.css"); .card {background:url("../media/my%20image.png")}', encoding="utf-8")
            assets = css_dependencies(root, {"main.css"})
            self.assertEqual(assets, {"main.css", "styles/theme.css", "media/my image.png"})
            plan = make_plan(["media/my image.png"], deck(), deck(), shared_assets=assets)
            self.assertTrue(plan.full_browser and plan.gallery)

    def test_native_ready_environment_in_linked_worktree_is_reused(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            linked = root / "linked"
            interpreter = linked / ".venv-reveal-qa-native/Scripts/python.exe"
            interpreter.parent.mkdir(parents=True)
            interpreter.touch()
            (root / "requirements-qa.txt").write_text("playwright==1.56.0\n", encoding="utf-8")
            with patch("validate_changes.ROOT", root), patch("validate_changes.git", return_value=f"worktree {linked}\n"), \
                    patch("validate_changes.subprocess.run", return_value=SimpleNamespace(returncode=0)) as probe, \
                    patch.dict("validate_changes.os.environ", {"IE_QA_PYTHON": ""}):
                chosen, _ = qa_python()
            self.assertEqual(chosen, str(interpreter))
            self.assertIn("1.56.0", probe.call_args.args[0][2])

    def test_optional_template_standards_follow_their_shared_dependencies(self):
        available = {"test_template_standards"}
        for path in ("scripts/check_browser_qa.py", "scripts/check_deck.py", "ie-scitech-reveal.css",
                     "ie-reveal-fit.js", "slide-aliases.js", "ie-components.js", "slide_patterns.html"):
            with self.subTest(path=path):
                plan = make_plan([path], deck(), deck(), available_tests=available)
                self.assertIn("test_template_standards", plan.tests)
        shared = make_plan(["index.html"], deck(), deck(script="startNew()"), available_tests=available)
        self.assertIn("test_template_standards", shared.tests)

    def test_optional_template_standards_do_not_slow_routine_copy_edits(self):
        plan = make_plan(["index.html"], deck(), deck(copy="Updated"),
                         available_tests={"test_template_standards"})
        self.assertFalse(plan.tests or plan.full_tests)

    def test_absent_optional_template_standards_are_not_selected(self):
        plan = make_plan(["ie-components.js"], deck(), deck(), available_tests=set())
        self.assertNotIn("test_template_standards", plan.tests)

    def test_shared_css_and_runtime_force_full_scan(self):
        for new in (deck(css=".card { padding: 8px; }"), deck(script="startNew()")):
            with self.subTest(new=new):
                self.assertTrue(make_plan(["index.html"], deck(), new).full_browser)

    def test_css_cascade_reordering_is_not_a_noop(self):
        old = deck(css=".card { color: red; } .card { color: blue; }")
        new = deck(css=".card { color: blue; } .card { color: red; }")
        self.assertTrue(make_plan(["index.html"], old, new).full_browser)

    def test_css_import_changes_require_full_rendering(self):
        old = deck(css="@import url('old.css');")
        new = deck(css="@import url('new.css');")
        self.assertTrue(make_plan(["index.html"], old, new).full_browser)

    def test_mixed_selector_cannot_hide_a_global_change(self):
        for css in ("#a .card, .card { padding: 8px; }",
                    ":is(#a, .card) { padding: 8px; }",
                    "section:not(#a) { padding: 8px; }",
                    "#a + section { padding: 8px; }"):
            with self.subTest(css=css):
                self.assertTrue(make_plan(["index.html"], deck(), deck(css=css)).full_browser)

    def test_positive_id_group_includes_each_consumer(self):
        plan = make_plan(["index.html"], deck(), deck(css=":is(#a, #b) .card { padding: 8px; }"))
        self.assertEqual(plan.slides, ["a", "b"])
        self.assertFalse(plan.full_browser)

    def test_new_slide_checks_its_boundaries_without_scanning_every_slide(self):
        new = deck().replace("<section id='b'>", "<section id='new'>New</section><section id='b'>")
        plan = make_plan(["index.html"], deck(), new)
        self.assertEqual(plan.slides, ["a", "b", "new"])
        self.assertFalse(plan.full_browser)

    def test_removed_slide_is_not_sent_to_the_browser(self):
        sections, _ = deck_parts(deck())
        plan = make_plan(["index.html"], deck(), deck().replace(sections["b"], ""))
        self.assertEqual(plan.slides, ["a", "c"])
        self.assertTrue(plan.static)

    def test_reorder_checks_changed_boundaries(self):
        sections, _ = deck_parts(deck())
        new = deck().replace(sections["a"] + sections["b"], sections["b"] + sections["a"])
        plan = make_plan(["index.html"], deck(), new)
        self.assertEqual(plan.slides, ["a", "b", "c"])

    def test_asset_and_download_changes_follow_their_consumers(self):
        for path in ("media/a.png", "media/prompt.md"):
            with self.subTest(path=path):
                plan = make_plan([path], deck(), deck())
                self.assertEqual(plan.slides, ["a"])
                self.assertTrue(plan.static and plan.downloads)
                self.assertFalse(plan.full_browser or plan.full_tests)

    def test_shared_asset_runs_both_decks(self):
        for path in ("logos/brand.svg", "backgrounds/light.jpg", "ie-scitech-reveal.css", "slide-aliases.js"):
            with self.subTest(path=path):
                plan = make_plan([path], deck(), deck())
                self.assertTrue(plan.full_browser and plan.gallery)

    def test_download_paths_with_percent_encoded_spaces_are_detected(self):
        html = deck().replace("media/a.png", "media/my%20image.png")
        self.assertEqual(make_plan(["media/my image.png"], html, html).slides, ["a"])

    def test_responsive_image_consumers_are_detected(self):
        html = deck().replace("src='media/a.png'", "srcset='media/a.png 1x, media/a-large.png 2x'")
        self.assertEqual(make_plan(["media/a-large.png"], html, html).slides, ["a"])

    def test_asset_referenced_by_shared_styles_widens_the_scope(self):
        plan = make_plan(["media/shared.png"], deck(), deck(), shared_assets={"media/shared.png"})
        self.assertTrue(plan.full_browser and plan.gallery)

    def test_asset_referenced_by_inline_code_widens_the_scope(self):
        html = deck(script="hero.src = 'media/hero.png'")
        plan = make_plan(["media/hero.png"], html, html)
        self.assertTrue(plan.full_browser)

    def test_documentation_only_needs_no_render_or_tooling_suite(self):
        plan = make_plan(["instructions/browser_qa.md", "AGENTS.md"], deck(), deck())
        self.assertFalse(plan.slides or plan.full_browser or plan.gallery or plan.full_tests or plan.tests)

    def test_tool_changes_select_their_tests(self):
        plan = make_plan(["scripts/check_commit_scope.py"], deck(), deck())
        self.assertEqual(plan.tests, ["test_commit_scope", "test_validate_changes"])
        self.assertFalse(plan.full_tests)

    def test_unmapped_tool_changes_run_the_full_suite(self):
        self.assertTrue(make_plan(["scripts/new_tool.py"], deck(), deck()).full_tests)

    def test_roster_changes_check_the_roster(self):
        self.assertTrue(make_plan(["groups.csv"], deck(), deck()).roster)

    def test_full_regression_is_explicit_and_complete(self):
        plan = make_plan([], deck(), deck(), full=True)
        self.assertTrue(plan.full_browser and plan.gallery and plan.full_tests and plan.roster and plan.downloads)

    def test_line_endings_do_not_widen_the_scope(self):
        plan = make_plan(["index.html"], deck(), deck().replace("><", ">\n<").replace("\n", "\r\n"))
        # Whitespace inside a section can affect preformatted text, so it stays a real edit
        self.assertFalse(plan.full_browser)

    def test_preformatted_whitespace_is_a_real_slide_change(self):
        old = deck(copy="<pre>A\nB</pre>")
        new = deck(copy="<pre>A B</pre>")
        self.assertEqual(make_plan(["index.html"], old, new).slides, ["a"])

    def test_malformed_section_structure_cannot_get_a_small_scope(self):
        for new in (deck().replace("id='b'", "id='a'"), deck().replace("</section>", "", 1)):
            with self.subTest(new=new):
                self.assertTrue(make_plan(["index.html"], deck(), new).full_browser)


if __name__ == "__main__":
    unittest.main()
