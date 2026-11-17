import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from code_figure import code_figure  # noqa: E402

CSS = (ROOT / "ie-scitech-reveal.css").read_text(encoding="utf-8")
GALLERY = (ROOT / "slide_patterns.html").read_text(encoding="utf-8")


class CodeFigureTests(unittest.TestCase):
    def test_python_is_escaped_and_highlighted(self):
        html = code_figure('if x < 1:\n    raise ValueError("bad")  # why', lang="py", caption="src/a.py", tag="After", state="after")
        self.assertIn('class="ie-code is-after"', html)
        self.assertIn("&lt;", html)
        self.assertIn('<span class="k">raise</span>', html)
        self.assertIn('<span class="s">&quot;bad&quot;</span>', html)
        self.assertIn('<span class="c">  # why</span>', html)

    def test_terminal_marks_prompt_comment_and_output(self):
        html = code_figure("# note\n$ pytest\n4 passed", lang="term", caption="terminal", tag="Run it", state="run", grow=True)
        self.assertIn('class="ie-code is-run is-grow"', html)
        self.assertIn('<span class="p">$</span> <span class="cmd">pytest</span>', html)
        self.assertIn('<span class="o">4 passed</span>', html)

    def test_unknown_language_is_rejected(self):
        with self.assertRaises(ValueError):
            code_figure("x", lang="cobol")

    def test_shared_styles_and_gallery_ship_the_demo_pattern(self):
        for selector in (".ie-code ", ".ie-code-lines", ".ie-code.is-before", ".ie-code.is-after",
                         ".ie-demo-grid", ".ie-demo-grid--wide-left", ".ie-demo-lead", ".ie-demo-col"):
            self.assertIn(selector, CSS)
        self.assertIn('id="pattern-33-live-demo"', GALLERY)


if __name__ == "__main__":
    unittest.main()
