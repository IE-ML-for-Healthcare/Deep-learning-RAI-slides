"""Build an ie-code figure (pattern-33) from a code snippet.

Writes the escaped, highlighted HTML for the shared code figure used on live demo
slides and annotated file slides. Paste the output into index.html.

Examples
    python scripts/code_figure.py src/validate.py --lang py --tag After --state after
    python scripts/code_figure.py run.txt --lang term --tag "Run it" --state run --caption terminal
    git diff | python scripts/code_figure.py - --lang plain --caption "git diff"

Terminal snippets: lines starting with "$ " are commands, "#" comments, "!" emphasised
output (the "!" is dropped), everything else is plain output. Paste REAL output only.
"""

from __future__ import annotations

import argparse
import html
import re
import sys

PY_KEYWORDS = r"\b(def|return|raise|if|elif|else|not|in|for|while|import|from|try|except|finally|with|as|is|None|True|False|class|lambda|yield|assert|and|or)\b"
STATES = {"before": "is-before", "after": "is-after", "run": "is-run", "": ""}


def _split_comment(line: str) -> tuple[str, str]:
    match = re.search(r"(\s+#.*$|^\s*#.*$)", line)
    if match and line[: match.start()].count('"') % 2 == 0 and line[: match.start()].count("'") % 2 == 0:
        return line[: match.start()], line[match.start():]
    return line, ""


def highlight_python(code: str) -> str:
    out = []
    for raw in code.split("\n"):
        line, comment = _split_comment(raw)
        parts = re.split(r'("[^"]*"|\'[^\']*\')', line)
        buf = []
        for part in parts:
            if len(part) >= 2 and part[0] == part[-1] and part[0] in "\"'":
                buf.append(f'<span class="s">{html.escape(part)}</span>')
            else:
                buf.append(re.sub(PY_KEYWORDS, r'<span class="k">\1</span>', html.escape(part)))
        if comment:
            buf.append(f'<span class="c">{html.escape(comment)}</span>')
        out.append("".join(buf))
    return "\n".join(out)


def highlight_yaml(code: str) -> str:
    out = []
    for raw in code.split("\n"):
        line, comment = _split_comment(raw)
        match = re.match(r"^(\s*-?\s*)([A-Za-z_][\w.\-]*)(:|=)(.*)$", line)
        if match:
            indent, key, sep, rest = match.groups()
            text = f'{html.escape(indent)}<span class="k">{html.escape(key)}</span>{sep}<span class="s">{html.escape(rest)}</span>'
        elif line.strip():
            text = f'<span class="s">{html.escape(line)}</span>'
        else:
            text = html.escape(line)
        if comment:
            text += f'<span class="c">{html.escape(comment)}</span>'
        out.append(text)
    return "\n".join(out)


def highlight_terminal(code: str) -> str:
    out = []
    for line in code.split("\n"):
        if line.startswith("$ ") or line == "$":
            out.append(f'<span class="p">$</span> <span class="cmd">{html.escape(line[2:])}</span>'.rstrip())
        elif line.startswith("#"):
            out.append(f'<span class="c">{html.escape(line)}</span>')
        elif line.startswith("!"):
            out.append(f'<span class="e">{html.escape(line[1:])}</span>')
        else:
            out.append(f'<span class="o">{html.escape(line)}</span>')
    return "\n".join(out)


HIGHLIGHTERS = {
    "py": highlight_python,
    "yaml": highlight_yaml,
    "ini": highlight_yaml,
    "env": highlight_yaml,
    "term": highlight_terminal,
    "plain": html.escape,
}


def code_figure(code: str, *, lang: str = "py", caption: str = "", tag: str = "", state: str = "", grow: bool = False) -> str:
    """Return the ie-code figure HTML for one snippet."""
    if lang not in HIGHLIGHTERS:
        raise ValueError(f"Unknown language {lang!r}; use one of {sorted(HIGHLIGHTERS)}")
    if state not in STATES:
        raise ValueError(f"Unknown state {state!r}; use before, after or run")
    classes = " ".join(c for c in ("ie-code", STATES[state], "is-grow" if grow else "") if c)
    label = html.escape(f"{tag}: {caption}" if tag else caption, quote=True)
    tag_html = f'<span class="ie-code-tag">{html.escape(tag)}</span>' if tag else ""
    body = HIGHLIGHTERS[lang](code.strip("\n"))
    return (f'<figure class="{classes}" aria-label="{label}"><figcaption>{tag_html}'
            f'<span class="ie-code-file">{html.escape(caption)}</span></figcaption>'
            f'<pre class="ie-code-lines">{body}</pre></figure>')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", help="file to read, or - for stdin")
    parser.add_argument("--lang", default="py", choices=sorted(HIGHLIGHTERS))
    parser.add_argument("--caption", help="file name shown in the figure bar; defaults to the source path")
    parser.add_argument("--tag", default="", help='Before, After or "Run it"')
    parser.add_argument("--state", default="", choices=["before", "after", "run", ""])
    parser.add_argument("--grow", action="store_true", help="let the figure fill its demo column")
    args = parser.parse_args(argv)
    code = sys.stdin.read() if args.source == "-" else open(args.source, encoding="utf-8").read()
    caption = args.caption or ("terminal" if args.source == "-" else args.source)
    print(code_figure(code, lang=args.lang, caption=caption, tag=args.tag, state=args.state, grow=args.grow))
    return 0


if __name__ == "__main__":
    sys.exit(main())
