"""Shared helpers for the browser QA and release scripts.

Offline or sandboxed agents often cannot reach cdn.jsdelivr.net or Google
Fonts. Set IE_QA_CDN_MIRROR to a folder containing node_modules with
reveal.js, katex, and @fontsource/montserrat (see scripts/setup_offline_cdn.sh)
and every CDN request is answered from that folder instead. Without the
variable, requests go to the network as usual.
"""

from __future__ import annotations

import contextlib
import functools
import http.server
import json
import mimetypes
import os
import re
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CDN_PATTERN = re.compile(r"^https://cdn\.jsdelivr\.net/npm/((?:@[^/@]+/)?[^/@]+)(?:@[^/]+)?/(.+)$")
FONT_HOST = "https://ie-qa-mirror.invalid/fonts/"


def load_config() -> dict:
    """Read deck.config.json, returning an empty dict when absent."""
    path = ROOT / "deck.config.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def mirror_dir() -> Path | None:
    value = os.environ.get("IE_QA_CDN_MIRROR", "").strip()
    if not value:
        default = ROOT / ".cache" / "cdn-mirror"
        return default if (default / "node_modules").is_dir() else None
    path = Path(value).expanduser().resolve()
    return path if path.is_dir() else None


def _font_css(modules: Path, query: str) -> str:
    weights = re.findall(r"wght@([\d;]+)", query)
    wanted = weights[0].split(";") if weights else ["300", "400", "700"]
    rules = []
    for weight in wanted:
        rules.append(
            "@font-face{font-family:'Montserrat';font-style:normal;font-weight:%s;"
            "font-display:swap;src:url('%smontserrat-latin-%s-normal.woff2') format('woff2');}"
            % (weight, FONT_HOST, weight)
        )
    return "\n".join(rules)


def install_cdn_mirror(context) -> Path | None:
    """Route CDN and font requests to a local node_modules mirror when available."""
    mirror = mirror_dir()
    if mirror is None:
        return None
    modules = mirror / "node_modules"

    def handle(route, request):
        url = request.url
        match = CDN_PATTERN.match(url.split("?", 1)[0])
        if match:
            package, rest = match.groups()
            target = modules / package / rest
            if target.is_file():
                content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
                route.fulfill(status=200, body=target.read_bytes(), content_type=content_type,
                              headers={"Access-Control-Allow-Origin": "*"})
                return
            route.fulfill(status=404, body=f"not mirrored: {url}")
            return
        if url.startswith("https://fonts.googleapis.com/"):
            route.fulfill(status=200, body=_font_css(modules, url), content_type="text/css",
                          headers={"Access-Control-Allow-Origin": "*"})
            return
        if url.startswith(FONT_HOST):
            target = modules / "@fontsource" / "montserrat" / "files" / url[len(FONT_HOST):]
            if target.is_file():
                route.fulfill(status=200, body=target.read_bytes(), content_type="font/woff2",
                              headers={"Access-Control-Allow-Origin": "*"})
                return
            route.fulfill(status=404, body="font not mirrored")
            return
        route.continue_()

    for pattern in ("https://cdn.jsdelivr.net/**", "https://fonts.googleapis.com/**", FONT_HOST + "**"):
        context.route(pattern, handle)
    return mirror


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return


@contextlib.contextmanager
def local_server(directory: Path):
    """Serve a directory on a random loopback port for the duration of the block."""
    handler = functools.partial(QuietHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


WAIT_FOR_REVEAL = "() => window.Reveal && typeof Reveal.isReady === 'function' && Reveal.isReady()"
