from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_commit_scope as scope  # noqa: E402


def deck(a: str = "Alpha", b: str = "Beta", css: str = "") -> str:
    return (
        "<html><head><style>\n"
        ".reveal .slides section:is(#slide-a, #slide-b) .card { color: navy; }\n"
        f"{css}</style></head><body><div class=\"slides\">\n"
        f"<section id=\"slide-a\" class=\"ie-slide\"><h2>{a}</h2>\n"
        "  <section><p>nested</p></section></section>\n"
        f"<section id=\"slide-b\" class=\"ie-slide\"><h2>{b}</h2></section>\n"
        "<section id=\"slide-b-2\" class=\"ie-slide\"><h2>Other</h2></section>\n"
        "</div><script>var s = '<section id=\"fake\">';</script></body></html>\n"
    )


class ChangedSlideTests(unittest.TestCase):
    def test_identical_decks_change_nothing(self) -> None:
        self.assertEqual(scope.changed_slides(deck(), deck()), [])

    def test_text_change_names_only_that_slide(self) -> None:
        self.assertEqual(scope.changed_slides(deck(), deck(a="Alpha 2")), ["slide-a"])

    def test_whitespace_and_line_endings_are_ignored(self) -> None:
        crlf = deck().replace("\n", "\r\n").replace("<section id", "\r\n    <section id")
        self.assertEqual(scope.changed_slides(deck(), crlf), [])

    def test_script_text_does_not_create_a_slide(self) -> None:
        self.assertNotIn("fake", scope.split_sections(deck()))

    def test_added_and_removed_slides_count(self) -> None:
        extra = deck().replace("</div><script>", "<section id=\"slide-c\"><h2>C</h2></section></div><script>")
        self.assertEqual(scope.changed_slides(deck(), extra), ["slide-c"])
        self.assertEqual(scope.changed_slides(extra, deck()), ["slide-c"])

    def test_slide_scoped_css_change_is_detected(self) -> None:
        old = deck(css="#slide-b .x { color: red; }\n")
        new = deck(css="#slide-b .x { color: blue; }\n")
        self.assertEqual(scope.changed_slides(old, new), ["slide-b"])

    def test_leaving_a_shared_rule_does_not_touch_the_neighbour(self) -> None:
        old = deck()
        new = deck().replace(":is(#slide-a, #slide-b)", "#slide-b")
        self.assertEqual(scope.changed_slides(old, new), ["slide-a"])

    def test_changing_a_shared_rule_body_touches_both(self) -> None:
        new = deck().replace("color: navy", "color: teal")
        self.assertEqual(scope.changed_slides(deck(), new), ["slide-a", "slide-b"])

    def test_projection_ignores_unrelated_deck_ids(self) -> None:
        selector = ":is(#slide-a, #slide-b, #slide-b-2) .card"
        ids = {"slide-a", "slide-b", "slide-b-2"} | {f"unrelated-{i}" for i in range(1000)}
        self.assertEqual(scope.project(selector, "slide-a", ids), "#slide-a .card")


class WorkflowPolicyTests(unittest.TestCase):
    def test_message_policy_is_pr_only_and_cannot_skip_product_qa(self) -> None:
        workflow = (ROOT / ".github/workflows/qa.yml").read_text(encoding="utf-8")
        jobs = dict(re.findall(r"^  (\w+):\n(.*?)(?=^  \w+:|\Z)", workflow, re.M | re.S))
        policy = jobs["commit_scope"]
        self.assertIn("    if: github.event_name == 'pull_request'\n", policy)
        self.assertIn("github.event.pull_request.base.sha", policy)
        self.assertIn("github.event.pull_request.head.sha", policy)
        self.assertNotIn("github.event.before", policy)
        self.assertIn("scripts/check_commit_scope.py --range", policy)
        product = jobs["qa"]
        self.assertNotRegex(product, r"^    (?:if|needs):", "product QA must run independently")
        self.assertNotIn("scripts/check_commit_scope.py", product)
        for script in ("check_deck.py", "sync_downloads.py --check", "unittest discover",
                       "check_browser_qa.py --deck index.html", "check_browser_qa.py --deck slide_patterns.html"):
            self.assertIn(script, product)
        self.assertIn("    branches: [main]", workflow)


class CoverageTests(unittest.TestCase):
    def test_named_slide_is_covered(self) -> None:
        self.assertEqual(scope.uncovered(["slide-a"], "fix(slide-a): reword"), [])

    def test_unnamed_slide_is_reported(self) -> None:
        self.assertEqual(scope.uncovered(["slide-a", "slide-b"], "fix(slide-a): reword"), ["slide-b"])

    def test_id_must_match_as_a_whole_token(self) -> None:
        self.assertEqual(scope.uncovered(["slide-b"], "fix(slide-b-2): reword"), ["slide-b"])
        self.assertEqual(scope.uncovered(["slide-b-2"], "fix(slide-b): reword"), ["slide-b-2"])

    def test_all_trailer_needs_a_reason(self) -> None:
        self.assertEqual(scope.uncovered(["slide-a"], "x\n\nSlides: all (shared stylesheet reflow)"), [])
        self.assertEqual(scope.uncovered(["slide-a"], "x\n\nSlides: all (ok)"), ["slide-a"])
        self.assertEqual(scope.uncovered(["slide-a"], "x\n\nSlides: all"), ["slide-a"])

    def test_comment_lines_do_not_count(self) -> None:
        self.assertEqual(scope.uncovered(["slide-a"], "x\n# slide-a was edited"), ["slide-a"])


class GitFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")
        hooks = self.dir / ".githooks"
        hooks.mkdir()
        shutil.copy(ROOT / ".githooks" / "commit-msg", hooks / "commit-msg")
        (hooks / "commit-msg").chmod(0o755)
        (self.dir / "scripts").mkdir()
        shutil.copy(ROOT / "scripts" / "check_commit_scope.py", self.dir / "scripts")
        self.git("config", "core.hooksPath", ".githooks")
        self.write(deck())
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore: baseline add guard", "--no-verify")
        self.base = self.git("rev-parse", "HEAD").strip()
        # The hook covers agent branches; the professor's own main checkout is exempt
        self.git("checkout", "-q", "-b", "agent/topic")

    def git(self, *args: str, check: bool = True) -> str:
        result = subprocess.run(["git", *args], cwd=self.dir, capture_output=True, text=True)
        if check and result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        return result.stdout if check else result.stdout + result.stderr + f"\nexit={result.returncode}"

    def write(self, html: str) -> None:
        (self.dir / "index.html").write_text(html, encoding="utf-8", newline="\n")

    def commit(self, message: str) -> subprocess.CompletedProcess:
        self.git("add", "index.html")
        return subprocess.run(["git", "commit", "-q", "-m", message], cwd=self.dir,
                              capture_output=True, text=True)

    def test_hook_accepts_named_slide(self) -> None:
        self.write(deck(a="Alpha 2"))
        result = self.commit("fix(slide-a): reword")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_hook_rejects_unnamed_slide(self) -> None:
        self.write(deck(a="Alpha 2", b="Beta 2"))
        result = self.commit("fix(slide-a): reword")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("slide-b", result.stderr)

    def test_hook_rejects_stale_whole_file_copy(self) -> None:
        self.write(deck(b="Beta 2"))
        self.assertEqual(self.commit("feat(slide-b): redesign").returncode, 0)
        self.write(deck(a="Alpha 2"))  # stale copy: slide-b reverted, slide-a edited
        result = self.commit("fix(slide-a): reword")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("slide-b", result.stderr)

    def test_hook_allows_the_professors_main_checkout(self) -> None:
        self.git("checkout", "-q", "main")
        self.write(deck(a="Alpha 2", b="Beta 2"))
        result = self.commit("fix: professor edit")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_hook_ignores_commits_without_deck_changes(self) -> None:
        (self.dir / "notes.md").write_text("hello\n", encoding="utf-8")
        self.git("add", "notes.md")
        result = subprocess.run(["git", "commit", "-q", "-m", "docs: notes"], cwd=self.dir,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_range_mode_flags_only_commits_after_the_guard(self) -> None:
        self.write(deck(a="Alpha 2", b="Beta 2"))
        self.git("add", "index.html")
        self.git("commit", "-q", "-m", "fix: unnamed", "--no-verify")
        script = [sys.executable, "scripts/check_commit_scope.py", "--range", f"{self.base}..HEAD"]
        result = subprocess.run(script, cwd=self.dir, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("slide-a", result.stderr)

    def test_range_mode_passes_named_commits_and_unknown_base(self) -> None:
        self.write(deck(a="Alpha 2"))
        self.git("add", "index.html")
        self.git("commit", "-q", "-m", "fix(slide-a): reword", "--no-verify")
        script = [sys.executable, "scripts/check_commit_scope.py", "--range", f"{self.base}..HEAD"]
        self.assertEqual(subprocess.run(script, cwd=self.dir).returncode, 0)
        zeros = [sys.executable, "scripts/check_commit_scope.py", "--range", f"{'0' * 40}..HEAD"]
        self.assertEqual(subprocess.run(zeros, cwd=self.dir).returncode, 0)


if __name__ == "__main__":
    unittest.main()
