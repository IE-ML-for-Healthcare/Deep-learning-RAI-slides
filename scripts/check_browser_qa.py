#!/usr/bin/env python3
"""Browser QA for IE SciTech Reveal.js decks, using Playwright Chromium.

Opens the deck over file:// at 1600 x 900 and checks, slide by slide:

  - Reveal.js starts with zero console errors, page errors, or missing local assets
  - Static top-level slide count equals the runtime Reveal.getTotalSlides()
  - No duplicate element ids after slide aliases resolve
  - Every .ie-auto-fit block fits; reports its fit scale and flags scales below --fit-warn
  - No text sits outside the 1600 x 900 canvas, and no text is clipped by a container
  - Every key takeaway strip uses the approved background: white at 40 % opacity with an
    8 px lime edge on light slides, white at 10 % opacity with a 10 px lime edge on dark slides
  - No text, image, or takeaway strip clashes with the IE logo, and no takeaway strip
    overlaps any other element (3 px tolerance)
  - Full-bleed card media and overlays span the card's inner left and right edges,
    and repeated card overlays share one height
  - Every slide sits on the canonical gridlines: safe-frame margins and top line, title
    anchored at the frame top, takeaway strips on a gridline, logo and quote positions;
    a section opts out only with data-grid-exception="<reason>"
  - Every download control saves the exact file over file:// and matches its source
  - Galleries, roadmaps, tooltips, and click-and-Escape targets behave as documented

    .venv-reveal-qa/bin/python scripts/check_browser_qa.py
    .venv-reveal-qa/bin/python scripts/check_browser_qa.py --deck slide_patterns.html
    .venv-reveal-qa/bin/python scripts/check_browser_qa.py --slides session-01-title,session-01-agenda
    .venv-reveal-qa/bin/python scripts/check_browser_qa.py --screenshots all

Screenshots and a JSON report go to tmp/qa/ (gitignored). Exit code 1 on any failure.
--slides limits both slide and functional checks and includes canonical-slide aliases.
No selection, or --full, checks every slide. --screenshots none always suppresses images.
Set IE_QA_CDN_MIRROR for offline or sandboxed runs, see scripts/qa_common.py.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_common import ROOT, WAIT_FOR_REVEAL, install_cdn_mirror  # noqa: E402

SLIDE_SCAN_JS = """
(args) => {
  const [h, v, fitWarn] = args;
  const slide = Reveal.getSlide(h, v);
  const canvas = slide.getBoundingClientRect();
  const scale = canvas.width / 1600;
  const tol = 2 * scale;
  const report = { id: slide.id || null, h, v, fits: [], spills: [], outside: [], clipped: [] };
  const label = (el) => {
    const text = (el.textContent || '').trim().replace(/\\s+/g, ' ');
    const cls = typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\\s+/).join('.') : '';
    return el.tagName.toLowerCase() + cls + ' "' + text.slice(0, 60) + '"';
  };
  const visible = (el) => {
    const style = getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) return false;
    const box = el.getBoundingClientRect();
    return box.width > 0 && box.height > 0;
  };
  slide.querySelectorAll('.ie-auto-fit').forEach((el) => {
    if (!visible(el)) return;
    const fit = parseFloat(el.style.getPropertyValue('--fit-scale') || '1');
    const parent = el.parentElement;
    const spillX = el.scrollWidth * fit - parent.clientWidth;
    const spillY = el.scrollHeight * fit - parent.clientHeight;
    report.fits.push(Math.round(fit * 1000) / 1000);
    if (spillX > 2 || spillY > 2) report.spills.push(label(el) + ' spills ' + Math.round(Math.max(spillX, spillY)) + 'px at scale ' + fit);
  });
  const textTags = 'h1,h2,h3,h4,h5,p,li,td,th,figcaption,blockquote,span,a,button,label';
  slide.querySelectorAll(textTags).forEach((el) => {
    if (!visible(el)) return;
    const own = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    if (el.closest('.ie-rm-steps, [aria-hidden="true"]')) return;
    const box = el.getBoundingClientRect();
    if (box.left < canvas.left - tol || box.top < canvas.top - tol || box.right > canvas.right + tol || box.bottom > canvas.bottom + tol) {
      report.outside.push(label(el));
      return;
    }
    let node = el.parentElement;
    while (node && node !== slide) {
      const style = getComputedStyle(node);
      if (style.overflowX !== 'visible' || style.overflowY !== 'visible') {
        const clip = node.getBoundingClientRect();
        if (box.bottom > clip.bottom + tol || box.right > clip.right + tol || box.top < clip.top - tol || box.left < clip.left - tol) {
          report.clipped.push(label(el));
        }
        break;
      }
      node = node.parentElement;
    }
  });
  const STRIP = '.ie-band, .ie-takeaway, .deck-takeaway-card, .ie-compare-takeaway, .ie-lr-takeaway-left, .ie-lr-takeaway-right, .ie-lr-takeaway-shared, .ie-process-takeaway, .ie-step-takeaway';
  const isDark = slide.matches('.ie-dark, .ie-bg-dark-abstract, .ie-bg-dark-science, .ie-bg-green-dark-left, .ie-compare-dark');
  const want = isDark ? { a: 0.1, w: 10 } : { a: 0.4, w: 8 };
  report.strips = [];
  report.clashes = [];
  const strips = Array.from(slide.querySelectorAll(STRIP)).filter(visible);
  strips.forEach((el) => {
    const s = getComputedStyle(el);
    const m = s.backgroundColor.match(/[0-9.]+/g) || [];
    const a = m.length > 3 ? Number(m[3]) : 1;
    const ok = Number(m[0]) === 255 && Number(m[1]) === 255 && Number(m[2]) === 255 && Math.abs(a - want.a) < 0.006
      && s.backgroundImage === 'none' && parseFloat(s.borderLeftWidth) === want.w
      && s.borderLeftColor === 'rgb(201, 255, 138)' && parseFloat(s.borderTopWidth) === 0 && parseFloat(s.borderBottomWidth) === 0;
    const fsz = parseFloat(s.fontSize);
    if (fsz < 22 || fsz > 26) {
      report.strips.push(label(el) + ' has font size ' + s.fontSize + '; key takeaway text must be 22 to 26 px (standard 24 px)');
    }
    if (!ok) {
      report.strips.push(label(el) + ' uses ' + s.backgroundColor + ' with a ' + s.borderLeftWidth + ' ' + s.borderLeftColor
        + ' edge; expected white at ' + want.a + ' opacity with a ' + want.w + ' px lime edge');
    }
  });
  const boxOf = (el) => { const r = el.getBoundingClientRect(); return { l: r.left, t: r.top, r: r.right, b: r.bottom }; };
  const textBox = (el) => {
    let box = null;
    Array.from(el.childNodes).forEach((n) => {
      if (n.nodeType !== 3 || !n.textContent.trim()) return;
      const range = document.createRange();
      range.selectNodeContents(n);
      Array.from(range.getClientRects()).forEach((r) => {
        if (r.width <= 0 || r.height <= 0) return;
        box = box ? { l: Math.min(box.l, r.left), t: Math.min(box.t, r.top), r: Math.max(box.r, r.right), b: Math.max(box.b, r.bottom) }
          : { l: r.left, t: r.top, r: r.right, b: r.bottom };
      });
    });
    return box;
  };
  const hit = (p, q) => Math.min(p.r, q.r) - Math.max(p.l, q.l) > 3 * scale && Math.min(p.b, q.b) - Math.max(p.t, q.t) > 3 * scale;
  const items = [];
  slide.querySelectorAll(textTags + ',dt,dd,code,pre,img,svg,canvas').forEach((el) => {
    if (!visible(el) || el.closest('.ie-logo, [aria-hidden="true"]')) return;
    const media = ['IMG', 'svg', 'CANVAS'].includes(el.tagName);
    const box = media ? boxOf(el) : textBox(el);
    if (!box) return;
    if (media && (box.r - box.l) * (box.b - box.t) > 0.5 * canvas.width * canvas.height) return;
    items.push({ el, box });
  });
  const logo = slide.querySelector('.ie-logo');
  if (logo && visible(logo)) {
    const lb = boxOf(logo);
    items.forEach((it) => { if (hit(it.box, lb)) report.clashes.push(label(it.el) + ' clashes with the IE logo'); });
    strips.forEach((el) => { if (hit(boxOf(el), lb)) report.clashes.push(label(el) + ' clashes with the IE logo'); });
  }
  strips.forEach((strip) => {
    const sb = boxOf(strip);
    items.forEach((it) => {
      if (strip.contains(it.el) || it.el.contains(strip)) return;
      if (hit(it.box, sb)) report.clashes.push(label(it.el) + ' clashes with the takeaway strip ' + label(strip));
    });
  });
  // Deck standards: tables, quotes and cards must follow the shared system
  report.standards = [];
  const note = (message) => report.standards.push(message);
  slide.querySelectorAll('table.ie-table').forEach((table) => {
    if (!visible(table)) return;
    const frame = table.closest('.safe-frame');
    if (!frame) return;
    const t = table.getBoundingClientRect();
    const f = frame.getBoundingClientRect();
    const slack = 6 * scale;
    if (t.left - f.left > slack || f.right - t.right > slack) note('table stops short of its frame, tables span margin to margin: ' + label(table));
    if (t.right - f.right > slack) note('table runs past its frame: ' + label(table));
  });
  slide.querySelectorAll('.source-quote, .ie-quote-text').forEach((quote) => {
    if (!visible(quote)) return;
    const long = quote.classList.contains('source-quote--long');
    const words = (quote.textContent || '').trim().split(/\\s+/).length;
    const want = long ? 30 : 50;
    const px = parseFloat(getComputedStyle(quote).fontSize);
    if (Math.abs(px - want) > 0.5) note('quote is ' + px + ' px, the standard is ' + want + ' px: ' + label(quote));
    if (long && words <= 40) note('source-quote--long is only for quotes over 40 words, this one has ' + words + ': ' + label(quote));
    quote.querySelectorAll('.ie-quote-emphasis').forEach((em) => {
      const cs = getComputedStyle(em);
      if (parseInt(cs.fontWeight, 10) < 700) note('quote emphasis must be bold: ' + label(em));
      if (cs.color !== 'rgb(201, 255, 138)') note('quote emphasis must be lime: ' + label(em));
    });
  });
  slide.querySelectorAll('.source-attribution, .ie-quote-attribution').forEach((attr) => {
    if (!visible(attr)) return;
    const px = parseFloat(getComputedStyle(attr).fontSize);
    if (Math.abs(px - 30) > 0.5) note('quote attribution is ' + px + ' px, the standard is 30 px: ' + label(attr));
    if (!(attr.textContent || '').trim().startsWith('- ')) note('quote attribution must start with "- ": ' + label(attr));
  });
  slide.querySelectorAll('tr.ie-table-key-row th[scope="row"]').forEach((th) => {
    if (!visible(th)) return;
    if (parseFloat(getComputedStyle(th).paddingLeft) < 20) note('key row heading is too close to its lime bar: ' + label(th));
  });
  if (slide.classList.contains('ie-light')) {
    slide.querySelectorAll('[class*="card"]').forEach((card) => {
      if (!visible(card) || card.closest('.ie-tooltip, [aria-hidden="true"]') || card.classList.contains('ie-card-dark')) return;
      const m = getComputedStyle(card).backgroundColor.match(/rgba?\\(([^)]+)\\)/);
      if (!m) return;
      const [r, g, b, a = 1] = m[1].split(',').map(Number);
      if (a >= 0.5 && (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255 < 0.25) note('dark card on a light slide, use ie-card-light: ' + label(card));
    });
  }
  slide.querySelectorAll('.ie-card.ie-card--media-bleed').forEach((card) => {
    if (!visible(card)) return;
    const cardBox = boxOf(card);
    const cardStyle = getComputedStyle(card);
    const innerLeft = cardBox.l + parseFloat(cardStyle.borderLeftWidth) * scale;
    const innerRight = cardBox.r - parseFloat(cardStyle.borderRightWidth) * scale;
    const edgeTolerance = 3 * scale;
    const spansEdges = (el) => {
      if (!el || !visible(el)) return false;
      const box = boxOf(el);
      return Math.abs(box.l - innerLeft) <= edgeTolerance && Math.abs(box.r - innerRight) <= edgeTolerance;
    };
    const media = card.querySelector('.ie-card-media--full-bleed');
    const image = media && media.querySelector('img, video');
    const overlay = card.querySelector('.ie-card-overlay--full-width');
    if (!media || !spansEdges(media)) note('full-bleed card media must span the card interior from left to right: ' + label(card));
    if (!image || !spansEdges(image)) note('full-bleed card image must span the card interior from left to right: ' + label(card));
    if (image) {
      const imageStyle = getComputedStyle(image);
      if (imageStyle.maxWidth !== 'none' || imageStyle.maxHeight !== 'none' || parseFloat(imageStyle.marginLeft) !== 0 || parseFloat(imageStyle.marginRight) !== 0) {
        note('full-bleed card image must remove max-size and horizontal margin constraints: ' + label(image));
      }
    }
    if (!overlay || !spansEdges(overlay)) note('full-width card overlay must span the card interior from left to right: ' + label(card));
  });
  slide.querySelectorAll('.ie-card-grid.ie-card-grid--equal-overlays').forEach((grid) => {
    const overlays = Array.from(grid.querySelectorAll('.ie-card-overlay--full-width')).filter(visible);
    if (overlays.length < 2) return;
    const heights = overlays.map((overlay) => overlay.getBoundingClientRect().height);
    if (Math.max(...heights) - Math.min(...heights) > 1 * scale) note('equal-overlay card grid has different overlay heights: ' + label(grid));
  });
  // Grid: canonical gridlines, owned by instructions/slide_rules.md, section Grid.
  // A slide opts out with data-grid-exception="<reason>" on its section; the reason is reported.
  report.grid = [];
  report.gridException = slide.getAttribute('data-grid-exception');
  if (!report.gridException) {
    const G = (el) => { const r = el.getBoundingClientRect(); return { l: (r.left - canvas.left) / scale, t: (r.top - canvas.top) / scale, r: (r.right - canvas.left) / scale, b: (r.bottom - canvas.top) / scale }; };
    const near = (v, list, tolerance) => list.some((x) => Math.abs(v - x) <= tolerance);
    const px = (v) => Math.round(v) + ' px';
    const frame = slide.querySelector(':scope > .safe-frame');
    const fullBleed = frame && frame.classList.contains('safe-frame--full-bleed');
    if (frame && visible(frame) && !fullBleed) {
      const f = G(frame);
      if (!near(f.l, [96, 84], 2) || !near(1600 - f.r, [96, 84], 2)) report.grid.push('safe frame sides sit at ' + px(f.l) + ' and ' + px(1600 - f.r) + '; use the 96 px or 84 px margin lines');
      if (!near(f.t, [86, 88, 74], 2)) report.grid.push('safe frame top sits at ' + px(f.t) + '; use the 86, 88 or 74 px top line');
      const title = Array.from(frame.querySelectorAll('h1, h2')).find(visible);
      if (title) {
        const t = G(title);
        if (Math.abs(t.l - f.l) > 4) report.grid.push('title starts at ' + px(t.l) + ', not on the frame margin ' + px(f.l));
        if (t.t - f.t > 32) report.grid.push('title top sits ' + px(t.t - f.t) + ' below the frame top line; anchor the title at the top, 28 px lower only under an eyebrow');
      }
    }
    const lines = [0, 1600, 800, 360, 84, 96, 1504, 1516, 772, 776, 780, 786, 814, 820, 824, 828];
    if (frame && visible(frame)) { const f = G(frame); lines.push(f.l, f.r); }
    const blocks = Array.from(slide.querySelectorAll('*')).filter((el) => visible(el) && !el.closest('.ie-logo, .ie-source-line, [aria-hidden="true"]'));
    strips.forEach((strip) => {
      const sb = G(strip);
      const edges = lines.slice();
      blocks.forEach((el) => {
        if (el === strip || strip.contains(el) || el.contains(strip)) return;
        const b = G(el);
        if (b.r - b.l >= 120) edges.push(b.l, b.r);
      });
      if (strip.parentElement) { const pb = G(strip.parentElement); edges.push(pb.l, pb.r); }
      if (!near(sb.l, edges, 4) || !near(sb.r, edges, 4)) report.grid.push('takeaway strip ' + px(sb.l) + ' to ' + px(sb.r) + ' does not sit on a gridline; span the content column or align both edges to a column above it: ' + label(strip));
    });
    if (logo && visible(logo)) {
      const b = G(logo);
      // Edge anchors, independent of the lockup height: bottom-left (left 48, bottom 852),
      // ie-logo-tr (right 1504, top 52), ie-logo-br (right 1552, bottom 852)
      const n = (a, v) => Math.abs(a - v) <= 3;
      const onSpot = (n(b.l, 48) && n(b.b, 852)) || (n(b.r, 1504) && n(b.t, 52)) || (n(b.r, 1552) && n(b.b, 852));
      if (!onSpot) report.grid.push('logo sits at ' + px(b.l) + ', ' + px(b.t) + ' to ' + px(b.r) + ', ' + px(b.b) + '; use the bottom-left, ie-logo-tr or ie-logo-br position');
    }
    slide.querySelectorAll('.source-quote, .ie-quote-text').forEach((quote) => {
      if (!visible(quote)) return;
      const q = G(quote);
      const top = quote.classList.contains('source-quote--long') ? 86 : 154;
      if (Math.abs(q.l - 96) > 4 || Math.abs(q.t - top) > 4) report.grid.push('quote starts at ' + px(q.l) + ', ' + px(q.t) + '; quote copy starts at 96 px, ' + top + ' px');
    });
  }
  report.minFit = report.fits.length ? Math.min(...report.fits) : null;
  report.lowFit = report.minFit !== null && report.minFit < fitWarn;
  return report;
}
"""


def decode_download_payload(href: str) -> bytes:
    header, _, payload = href.partition(",")
    if not header.startswith("data:") or ";base64" not in header:
        raise RuntimeError("Download href must be a base64 data: URI")
    return base64.b64decode(payload, validate=True)


def goto_section(page, locator) -> bool:
    return bool(locator.evaluate(
        """target => {
            const section = target.closest('.reveal .slides section');
            if (!section || !window.Reveal) return false;
            const i = Reveal.getIndices(section);
            Reveal.slide(i.h, i.v);
            return true;
        }"""
    ))


def select_slides(slides: list[dict], wanted: set[str], full: bool = False) -> list[dict]:
    """Validate requested ids and include aliases of selected canonical slides."""
    known = {slide["id"] for slide in slides}
    missing = wanted - known
    if missing:
        raise ValueError("Unknown slide ids: " + ", ".join(sorted(missing)))
    if full or not wanted:
        return slides
    selected = set(wanted)
    while True:
        expanded = selected | {s["id"] for s in slides if s.get("ref") in selected}
        if expanded == selected:
            return [s for s in slides if s["id"] in selected]
        selected = expanded


def scoped_locator(page, selector: str, selected_ids: list[str] | None = None):
    """Limit functional checks to the same sections as the geometry scan."""
    if selected_ids is None:
        return page.locator(selector)
    scope = ", ".join(
        part for sid in selected_ids
        for part in (f"section[id={json.dumps(sid)}]", f"section[id={json.dumps(sid)}] *")
    )
    return page.locator(f":is({selector}):is({scope})")


def prepare_slide(page, h: int, v: int) -> None:
    """Wait for actual slide resources and layout, without a per-slide sleep."""
    page.evaluate("([h, v]) => Reveal.slide(h, v, -1)", [h, v])
    page.wait_for_function(
        """([h, v]) => {
            const s = Reveal.getSlide(h, v);
            return s === Reveal.getCurrentSlide() && Array.from(s.querySelectorAll('img')).every(img => {
                const cs = getComputedStyle(img);
                if (cs.display === 'none' || cs.visibility === 'hidden' || !img.getClientRects().length) return true;
                return img.complete;
            });
        }""", arg=[h, v], timeout=10000,
    )
    page.evaluate("""async ([h, v]) => {
        const slide = Reveal.getSlide(h, v);
        slide.querySelectorAll('.fragment').forEach(f => f.classList.add('visible'));
        await document.fonts.ready;
        // Measure the completed visual state, including delayed CSS entrances
        for (const animation of slide.getAnimations({subtree: true})) {
            if (animation.effect.getComputedTiming().iterations === Infinity) animation.pause();
            else animation.finish();
        }
        if (window.IERevealFit) IERevealFit.fitAll();
        await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    }""", [h, v])


def check_downloads(page, errors: list[str], notes: list[str], selected_ids=None) -> None:
    from download_controls import check_downloads_both_routes
    check_downloads_both_routes(page, ROOT, errors, notes, selected_ids)


def check_galleries(page, errors: list[str], notes: list[str], selected_ids=None) -> None:
    galleries = scoped_locator(page, "[data-gallery]", selected_ids)
    for index in range(galleries.count()):
        gallery = galleries.nth(index)
        goto_section(page, gallery)
        page.wait_for_timeout(300)
        thumbs = gallery.locator(".ie-gallery-thumb")
        if thumbs.count() < 2:
            continue
        thumbs.nth(1).click()
        page.wait_for_timeout(300)
        hero = gallery.locator("[data-gallery-hero]").get_attribute("src")
        if hero != thumbs.nth(1).get_attribute("data-src"):
            errors.append(f"Gallery {index + 1}: clicking a thumbnail did not change the hero image")
        thumbs.nth(0).click()
    if galleries.count():
        notes.append(f"Galleries: {galleries.count()} checked")


def check_roadmaps(page, errors: list[str], notes: list[str], out: Path, shots: bool, selected_ids=None) -> None:
    roadmaps = scoped_locator(page, "section.ie-roadmap", selected_ids)
    for index in range(roadmaps.count()):
        roadmap = roadmaps.nth(index)
        rid = roadmap.get_attribute("id") or f"roadmap-{index + 1}"
        goto_section(page, roadmap)
        page.wait_for_timeout(500)
        stages = roadmap.locator(".ie-rm-stage")
        fragments = roadmap.locator(".ie-rm-steps .fragment")
        if stages.count() == 0:
            errors.append(f"Roadmap #{rid} rendered no stages; check its JSON block and the console")
            continue
        if fragments.count() != stages.count() + 1:
            errors.append(f"Roadmap #{rid}: expected {stages.count() + 1} fragments, found {fragments.count()}")
        stages.nth(0).hover()
        page.wait_for_timeout(300)
        if roadmap.locator(".ie-rm-steps .fragment.visible").count() != 0:
            errors.append(f"Roadmap #{rid}: hover preview changed the committed fragment state")
        target = min(1, stages.count() - 1)
        stages.nth(target).click()
        page.wait_for_timeout(400)
        if stages.nth(target).get_attribute("aria-current") != "step":
            errors.append(f"Roadmap #{rid}: clicking a stage did not commit it")
        if roadmap.locator(".ie-rm-steps .fragment.visible").count() != target + 1:
            errors.append(f"Roadmap #{rid}: fragment state not synchronised after click")
        if shots:
            page.screenshot(path=str(out / f"roadmap_{rid}_focus.png"))
        page.evaluate("document.documentElement.classList.add('print-pdf')")
        page.wait_for_timeout(200)
        if not roadmap.locator(".ie-rm-print-summary").is_visible():
            errors.append(f"Roadmap #{rid}: print summary is not visible in print mode")
        page.evaluate("document.documentElement.classList.remove('print-pdf')")
        roadmap.evaluate("section => { const i = Reveal.getIndices(section); Reveal.slide(i.h, i.v, -1); }")
    if roadmaps.count():
        notes.append(f"Roadmaps: {roadmaps.count()} checked for hover, click, fragments, and print")


def check_tooltips(page, errors: list[str], selected_ids=None) -> None:
    missing = scoped_locator(page, ".ie-tooltip", selected_ids).evaluate_all(
        """els => els.filter(el => !el.hasAttribute('tabindex') || !el.getAttribute('data-tooltip')
                              || !el.getAttribute('aria-label')).map(el => el.textContent.trim().slice(0, 40))"""
    )
    for item in missing:
        errors.append(f"Tooltip {item!r} needs tabindex, data-tooltip, and aria-label")


def check_click_escape(page, notes: list[str], selected_ids=None) -> None:
    for selector in ("[data-lightbox]", "[data-zoom]", ".zoomable", ".lightbox-trigger", "details summary"):
        locator = scoped_locator(page, selector, selected_ids).first
        if locator.count() == 0:
            continue
        goto_section(page, locator)
        page.wait_for_timeout(400)
        try:
            locator.click(timeout=1500)
            page.keyboard.press("Escape")
            notes.append(f"Click and Escape passed on {selector}")
            return
        except Exception:  # noqa: BLE001
            continue
    notes.append("No click-and-Escape target found, check skipped")


def main() -> int:
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--deck", default="index.html", help="deck HTML relative to the repository root")
    parser.add_argument("--slides", default="", help="comma-separated slide ids to validate, including their aliases")
    parser.add_argument("--full", action="store_true", help="validate the full deck; --slides then selects screenshots only")
    parser.add_argument("--screenshots", choices=("none", "listed", "all"), default="listed")
    parser.add_argument("--fit-warn", type=float, default=0.75, help="flag fit scales below this value")
    parser.add_argument("--out", default="tmp/qa", help="output folder for screenshots and the JSON report")
    parser.add_argument("--strict", action="store_true", help="treat clipped text and low fit scales as failures")
    parser.add_argument("--grid", choices=("auto", "error", "warn"), default="auto",
                        help="grid breaches fail the run (error) or only warn; auto fails on index.html and warns on other decks")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001
        print(f"Playwright import failed: {exc}\nRun: bash scripts/setup_browser_qa.sh")
        return 1

    deck = (ROOT / args.deck).resolve()
    if not deck.is_file():
        print(f"Deck not found: {args.deck}")
        return 1
    out = (ROOT / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    wanted = {s.strip() for s in args.slides.split(",") if s.strip()}
    grid_strict = args.grid == "error" or (args.grid == "auto" and Path(args.deck).name == "index.html")

    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    slides_report: list[dict] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 900}, accept_downloads=True)
        mirror = install_cdn_mirror(context)
        if mirror:
            notes.append(f"CDN requests served from local mirror {mirror}")
        page = context.new_page()
        console: list[str] = []
        page.on("pageerror", lambda error: console.append(f"page error: {error}"))
        page.on("console", lambda msg: console.append(f"console: {msg.text}") if msg.type == "error" else None)
        page.on("requestfailed", lambda req: console.append(f"missing asset: {req.url}")
                if req.url.startswith("file:") else None)

        page.goto(deck.as_uri(), wait_until="load")
        try:
            page.wait_for_function(WAIT_FOR_REVEAL, timeout=15000)
        except Exception:  # noqa: BLE001
            print("Browser QA FAILED: Reveal.js did not become ready within 15 s")
            for item in console:
                print(f"  FAIL  {item}")
            browser.close()
            return 1
        notes.append("Browser launch passed")
        page.evaluate("Reveal.configure({ transition: 'none', backgroundTransition: 'none' })")
        notes.append("QA measures completed animations with transitions disabled; fonts, images and layout are awaited")

        nested = page.evaluate("document.querySelectorAll('.reveal .slides > section > section').length")
        static_count = page.evaluate("document.querySelectorAll('.reveal .slides > section').length")
        runtime = page.evaluate("Reveal.getTotalSlides()")
        if not nested and static_count != runtime:
            errors.append(f"Static slide count {static_count} differs from runtime count {runtime}")
        duplicates = page.evaluate(
            """() => { const seen = {}, dup = new Set();
                 document.querySelectorAll('[id]').forEach(el => { if (seen[el.id]) dup.add(el.id); seen[el.id] = 1; });
                 return Array.from(dup); }"""
        )
        for dup in duplicates:
            errors.append(f"Duplicate id after alias resolution: #{dup}")

        all_slides = page.evaluate(
            """Reveal.getSlides().map(s => { const i = Reveal.getIndices(s);
                return { id: s.id, ref: s.getAttribute('data-slide-ref'), h: i.h, v: i.v || 0 }; })"""
        )
        try:
            selected = select_slides(all_slides, wanted, args.full)
        except ValueError as exc:
            print(f"Browser QA FAILED: {exc}")
            browser.close()
            return 1
        scope = "targeted" if wanted and not args.full else "full"
        selected_ids = [s["id"] for s in selected] if scope == "targeted" else None
        print(f"Browser QA: {scope}, {len(selected)}/{len(all_slides)} slides", flush=True)
        for slide in selected:
            h, v = slide["h"], slide["v"]
            prepare_slide(page, h, v)
            report = page.evaluate(SLIDE_SCAN_JS, [h, v, args.fit_warn])
            name = report["id"] or f"slide-{h + 1}"
            report["number"] = h + 1
            for item in report["spills"]:
                errors.append(f"#{name}: {item}")
            for item in report["outside"]:
                errors.append(f"#{name}: text outside the 1600 x 900 canvas: {item}")
            for item in report["strips"]:
                errors.append(f"#{name}: key takeaway strip breaks the standard: {item}")
            for item in report["clashes"]:
                errors.append(f"#{name}: layout clash: {item}")
            for item in report["standards"]:
                errors.append(f"#{name}: deck standard: {item}")
            for item in report["grid"]:
                (errors if grid_strict else warnings).append(f"#{name}: grid: {item}")
            if report["gridException"]:
                notes.append(f"#{name}: grid exception: {report['gridException']}")
            for item in report["clipped"]:
                (errors if args.strict else warnings).append(f"#{name}: text clipped by its container: {item}")
            if report["lowFit"]:
                (errors if args.strict else warnings).append(
                    f"#{name}: fit scale {report['minFit']} is below {args.fit_warn}; consider splitting the slide")
            if not report["id"]:
                warnings.append(f"Slide {h + 1} has no id; give every top-level section a stable id")
            if args.screenshots == "all" or (args.screenshots == "listed" and (report["id"] in wanted or scope == "targeted")):
                page.screenshot(path=str(out / f"{h + 1:03d}_{name}.png"))
            slides_report.append(report)
        notes.append(f"Scanned {len(selected)}/{len(all_slides)} slides for fit, spill, canvas, clipping, takeaway strip standard, logo or element clashes, and the table, quote and card standards")

        page.evaluate("Reveal.slide(0, 0)")
        page.wait_for_timeout(200)
        check_downloads(page, errors, notes, selected_ids)
        check_galleries(page, errors, notes, selected_ids)
        check_roadmaps(page, errors, notes, out, args.screenshots != "none", selected_ids)
        check_tooltips(page, errors, selected_ids)
        check_click_escape(page, notes, selected_ids)

        errors.extend(console)
        browser.close()

    (out / "qa_report.json").write_text(json.dumps(
        {"deck": args.deck, "scope": scope, "requested_ids": sorted(wanted),
         "total_slides": len(all_slides), "scanned_slides": len(selected),
         "elapsed_seconds": round(time.perf_counter() - started, 3),
         "errors": errors, "warnings": warnings, "notes": notes, "slides": slides_report},
        indent=2), encoding="utf-8")

    print(f"Deck: {args.deck}")
    for note in notes:
        print(f"  info  {note}")
    for warning in warnings:
        print(f"  WARN  {warning}")
    for error in errors:
        print(f"  FAIL  {error}")
    fits = [f"{r['id'] or r['number']}={r['minFit']}" for r in slides_report if r["minFit"] is not None]
    print(f"Fit scales: {', '.join(fits) if fits else 'no ie-auto-fit blocks'}")
    print(f"Report: {out / 'qa_report.json'}")
    print("Browser QA " + ("FAILED" if errors else "PASSED") + f" ({len(errors)} failures, {len(warnings)} warnings)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
