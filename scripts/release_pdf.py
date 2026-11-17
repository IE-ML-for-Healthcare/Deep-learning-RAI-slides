#!/usr/bin/env python3
"""Validate a generated Reveal.js deck and optionally create a checked PDF"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import ConsoleMessage, Page, Response, sync_playwright
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_common import install_cdn_mirror, local_server  # noqa: E402


def validate_page(
    page: Page,
    url: str,
    expected_slides: int | None = None,
    expect_pdf_pages: bool = False,
) -> tuple[int, list[str], list[str]]:
    console_errors: list[str] = []
    missing_assets: list[str] = []
    page_errors: list[str] = []
    local_origin = urlparse(url).netloc

    def record_console(message: ConsoleMessage) -> None:
        if message.type == "error":
            source_url = message.location.get("url", "")
            suffix = f" [{source_url}]" if source_url else ""
            console_errors.append(f"{message.text}{suffix}")

    def record_response(response: Response) -> None:
        parsed = urlparse(response.url)
        if parsed.netloc == local_origin and response.status >= 400:
            missing_assets.append(f"{response.status} {response.url}")

    page.on("console", record_console)
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.on("response", record_response)
    page.goto(url, wait_until="networkidle")
    page.wait_for_function("window.Reveal && Reveal.isReady()")
    if expect_pdf_pages:
        page.wait_for_function(
            "document.querySelectorAll('.pdf-page').length === Reveal.getTotalSlides()"
        )
    page.evaluate("document.fonts.ready")
    broken_images = page.evaluate(
        """async () => {
          await Promise.all(Array.from(document.images).map((image) => {
            if (image.complete) return Promise.resolve();
            return new Promise((resolve) => {
              image.addEventListener('load', resolve, { once: true });
              image.addEventListener('error', resolve, { once: true });
            });
          }));
          return Array.from(document.images)
            .filter((image) => !image.complete || image.naturalWidth === 0)
            .map((image) => image.currentSrc || image.src);
        }"""
    )
    if broken_images:
        missing_assets.extend(f"broken image {item}" for item in broken_images)

    fit_result = page.evaluate(
        """async () => {
          if (!window.IERevealFit || typeof window.IERevealFit.fitAll !== 'function') {
            return { available: false, pending: -1 };
          }
          window.IERevealFit.fitAll();
          await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
          const visible = Array.from(document.querySelectorAll('.ie-auto-fit')).filter((element) => {
            const style = getComputedStyle(element.closest('section'));
            return style.display !== 'none' && style.visibility !== 'hidden';
          });
          const pending = visible.filter((element) => !element.style.getPropertyValue('--fit-scale')).length;
          return { available: true, pending };
        }"""
    )
    if not fit_result["available"]:
        raise RuntimeError("window.IERevealFit is unavailable")
    if fit_result["pending"]:
        raise RuntimeError(f"IERevealFit did not finish for {fit_result['pending']} visible element(s)")

    slide_count = page.evaluate("Reveal.getTotalSlides()")
    if not isinstance(slide_count, int) or slide_count <= 0:
        raise RuntimeError(f"Reveal.getTotalSlides() returned {slide_count!r}")
    if expected_slides is not None and slide_count != expected_slides:
        raise RuntimeError(
            f"Reveal.getTotalSlides() returned {slide_count}, expected {expected_slides}"
        )
    console_errors.extend(page_errors)
    return slide_count, console_errors, missing_assets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--expected-slides",
        type=int,
        help="Require the runtime Reveal slide count to equal this value",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.validate_only == (args.pdf is not None):
        print("release_pdf error: require either --validate-only or --pdf", file=sys.stderr)
        return 2
    if args.expected_slides is not None and args.expected_slides <= 0:
        print("release_pdf error: --expected-slides must be positive", file=sys.stderr)
        return 2

    html_path = args.html.resolve()
    if not html_path.is_file():
        print(f"release_pdf error: generated HTML does not exist: {html_path}", file=sys.stderr)
        return 2

    pdf_path = args.pdf.resolve() if args.pdf is not None else None
    if pdf_path is not None:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with local_server(html_path.parent) as port:
            suffix = "?print-pdf" if pdf_path is not None else ""
            url = f"http://127.0.0.1:{port}/{html_path.name}{suffix}"
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    context = browser.new_context()
                    install_cdn_mirror(context)
                    page = context.new_page()
                    slide_count, console_errors, missing_assets = validate_page(
                        page,
                        url,
                        expected_slides=args.expected_slides,
                        expect_pdf_pages=pdf_path is not None,
                    )
                    if console_errors:
                        raise RuntimeError("Browser console errors: " + " | ".join(console_errors))
                    if missing_assets:
                        raise RuntimeError("Missing local runtime assets: " + " | ".join(missing_assets))
                    if pdf_path is not None:
                        page.pdf(
                            path=str(pdf_path),
                            print_background=True,
                            prefer_css_page_size=True,
                            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                        )
                finally:
                    browser.close()

        print(f"Reveal slides: {slide_count}")
        print("Browser console errors: 0")
        print("Missing local runtime assets: 0")
        if pdf_path is None:
            print(f"Validated HTML: {html_path}")
            return 0

        if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
            raise RuntimeError(f"PDF was not created or is empty: {pdf_path}")
        pdf_reader = PdfReader(str(pdf_path))
        pdf_pages = len(pdf_reader.pages)
        if pdf_pages <= 0:
            raise RuntimeError("PDF has no pages")
        if pdf_pages != slide_count:
            raise RuntimeError(f"PDF page count {pdf_pages} does not equal Reveal slide count {slide_count}")
        print(f"PDF pages: {pdf_pages}")
        print(f"PDF: {pdf_path}")
        print(f"Bytes: {pdf_path.stat().st_size}")
        return 0
    except Exception as error:
        print(f"release_pdf error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
