"""Official download-control policy and rendered browser checks.

Static checks use only the standard library. Browser checks load Pillow lazily.
"""
from __future__ import annotations
import base64
from collections import Counter
from io import BytesIO
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse

BUTTON = "ie-download-btn"
ICON = "ie-download-icon"
HEADING = "ie-title-with-download"
ICON_SOURCE = "media/icons/tabler/download.svg"


def load_exceptions(root: Path) -> list[dict]:
    path = root / "download-exceptions.json"
    return json.loads(path.read_text(encoding="utf-8"))["exceptions"] if path.exists() else []


def slide_id(node) -> str:
    return next((n.attrs.get("id", "") for n in node.ancestors() if n.tag == "section"), "")


def validate_download_nodes(nodes, root: Path, deck: str) -> list[str]:
    """Reject ad hoc controls and exceptions that lack an exact registry entry."""
    errors, seen = [], Counter()
    registry = load_exceptions(root)
    for node in nodes:
        a = node.attrs
        if not ("download" in a or "data-download-source" in a or BUTTON in node.classes
                or a.get("href", "").startswith(("data:text/", "data:application/"))):
            continue
        label = f"{deck}:{node.line}: download"
        if node.tag != "a":
            errors.append(f"{label} must be an anchor")
        filename = a.get("download", "")
        if not filename or Path(filename).name != filename or "\\" in filename:
            errors.append(f"{label} needs an exact download filename")
        if a.get("target", "").lower() not in ("", "_self"):
            errors.append(f"{label} must not open another tab or window")
        if a.get("onclick"):
            errors.append(f"{label} must not override the native download action")
        try:
            header, payload = a.get("href", "").split(",", 1)
            if not header.startswith("data:") or ";base64" not in header:
                raise ValueError
            base64.b64decode(payload, validate=True)
        except (ValueError, TypeError):
            errors.append(f"{label} needs a generated base64 data URI")
        if not a.get("data-download-source"):
            errors.append(f"{label} needs data-download-source")
        if not a.get("aria-label", "").strip():
            errors.append(f"{label} needs an accessible label")
        exception = a.get("data-download-exception", "")
        if exception:
            key = (deck, slide_id(node), a.get("data-download-source", ""), exception)
            matches = [r for r in registry if (r["deck"], r["slide"], r["source"], r["kind"]) == key]
            if len(matches) != 1 or not matches[0].get("reason", "").strip():
                errors.append(f"{label} has an unregistered exception")
            seen[key] += 1
            continue
        if BUTTON not in node.classes:
            errors.append(f"{label} must use the official {BUTTON} title icon")
            continue
        heading = next((n for n in node.ancestors() if n.tag in ("h1", "h2", "h3")), None)
        if heading is None or HEADING not in heading.classes:
            errors.append(f"{label} must sit beside a title with {HEADING}")
        images = [n for n in node.iter() if n.tag == "img"]
        if len(images) != 1 or images[0].attrs.get("src") != ICON_SOURCE or ICON not in images[0].classes:
            errors.append(f"{label} must use the official local download icon")
        if not a.get("title", "").strip():
            errors.append(f"{label} needs a filename or file-type tooltip")
    for r in registry:
        if r["deck"] != deck:
            continue
        key = (deck, r["slide"], r["source"], r["kind"])
        if seen[key] != r["count"]:
            errors.append(f"{deck}: exception {r['slide']} / {r['kind']} expected {r['count']} controls, found {seen[key]}")
    return errors


def luminance(rgb):
    channels = [v / 255 for v in rgb[:3]]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
    return sum(v * w for v, w in zip(linear, (.2126, .7152, .0722)))


def contrast_ratio(first, second):
    a, b = sorted((luminance(first), luminance(second)))
    return (b + .05) / (a + .05)


def foreground_contrast(normal_png: bytes, background_png: bytes,
                        mask_png: bytes, mask_background_png: bytes) -> float:
    """Measure the weakest glyph-core contrast on the actual rendered surface.

    A separate marker background reveals the complete glyph mask, including
    strokes invisible on the real background. Near-opaque mask pixels avoid
    antialiased edges without discarding a low-contrast part of the glyph.
    """
    from PIL import Image
    images = [Image.open(BytesIO(data)).convert("RGB") for data in
              (normal_png, background_png, mask_png, mask_background_png)]
    if len({im.size for im in images}) != 1:
        raise ValueError("Download control moved while measuring contrast")
    pixels = [list(getattr(im, "get_flattened_data", im.getdata)()) for im in images]
    normal, background, mask, mask_background = pixels
    strength = [max(abs(a-b) for a,b in zip(first, second))
                for first,second in zip(mask, mask_background)]
    peak = max(strength, default=0)
    if peak < 6:
        return 1.0
    core = [i for i,value in enumerate(strength) if value >= peak * .98]
    if len(core) < 3:
        return 1.0
    return min(contrast_ratio(normal[i], background[i]) for i in core)


def _control_snapshot(control, hide_foreground=False, marker_background=False) -> bytes:
    """Temporarily isolate foreground or its mask, then restore every style."""
    originals = control.evaluate("""(e, options) => {
        const nodes = [e,...e.querySelectorAll('*')];
        const originals = nodes.map(n=>n.getAttribute('style'));
        const borders = nodes.map(n=>getComputedStyle(n).borderColor);
        nodes.forEach((n,i)=>{
            if(options.marker) {
                n.style.setProperty('background', i===0 ? 'rgb(255,0,255)' : 'transparent','important');
                n.style.setProperty('border-color','transparent','important');
                n.style.setProperty('outline','none','important');
                n.style.setProperty('box-shadow','none','important');
            }
            if(options.hide) {
                if(n.matches('img,svg')) n.style.setProperty('visibility','hidden','important');
                else {
                    if(!options.marker) n.style.setProperty('border-color',borders[i],'important');
                    n.style.setProperty('color','transparent','important');
                    n.style.setProperty('text-shadow','none','important');
                }
            }
        });
        return originals;
    }""", {"hide":hide_foreground, "marker":marker_background})
    try:
        return control.screenshot(animations="disabled")
    finally:
        control.evaluate("""(e, originals) => [e,...e.querySelectorAll('*')].forEach((n,i)=>{
            if(originals[i]===null) n.removeAttribute('style'); else n.setAttribute('style',originals[i]);
        })""", originals)




def check_control_contrast(page, control, label: str, errors: list[str]) -> list[float]:
    results = []
    for state in ("normal", "hover", "keyboard focus"):
        page.mouse.move(0, 0)
        control.evaluate("e => e.blur()")
        if state == "hover":
            control.hover()
        elif state == "keyboard focus":
            page.keyboard.press("Tab")
            control.focus()
        if BUTTON in (control.get_attribute("class") or "").split():
            geometry = control.evaluate("""e => {
                const c = getComputedStyle(e), i = getComputedStyle(e.querySelector('img'));
                return [parseFloat(c.width), parseFloat(c.height), parseFloat(c.borderRadius),
                        parseFloat(i.width), parseFloat(i.height),
                        parseFloat(c.outlineWidth), c.outlineStyle, e.matches(':focus-visible'),
                        parseFloat(getComputedStyle(e.closest('h1,h2,h3')).columnGap)];
            }""")
            if any(abs(a-b) > .1 for a,b in zip(geometry[:5], (42,42,8,24,24))):
                errors.append(f"{label}: official button geometry changed in {state}: {geometry[:5]}")
            if state == "keyboard focus" and (not geometry[7] or geometry[5] < 2 or geometry[6] == "none"):
                errors.append(f"{label}: keyboard focus indicator is missing")
            if abs(geometry[8] - 16) > .1:
                errors.append(f"{label}: title gap must be 16 px, found {geometry[8]}")
        normal = _control_snapshot(control)
        background = _control_snapshot(control, hide_foreground=True)
        mask = _control_snapshot(control, marker_background=True)
        mask_background = _control_snapshot(control, hide_foreground=True, marker_background=True)
        ratio = foreground_contrast(normal, background, mask, mask_background)
        results.append(ratio)
        if ratio < 3:
            errors.append(f"{label}: {state} foreground/background contrast {ratio:.2f}:1 is below 3:1")
    page.mouse.move(0, 0)
    control.evaluate("e => e.blur()")
    return results


def click_download(page, control, expected: bytes, filename: str, errors: list[str], label: str) -> bool:
    """Observe the action, including unexpected tabs and same-tab navigation."""
    context = page.context
    pages_before = list(context.pages)
    url_before = page.url
    origin_before = page.evaluate("performance.timeOrigin")
    popups, navigations = [], []
    def on_page(new_page):
        popups.append(new_page)
    def on_navigation(frame):
        if frame == page.main_frame:
            navigations.append(frame.url)
    context.on("page", on_page)
    page.on("framenavigated", on_navigation)
    valid = True
    try:
        with page.expect_download(timeout=5000) as pending:
            control.click(timeout=3000)
        download = pending.value
        if download.suggested_filename != filename:
            errors.append(f"{label}: filename mismatch, received {download.suggested_filename!r}")
            valid = False
        path = download.path()
        if path is None or Path(path).read_bytes() != expected:
            errors.append(f"{label}: downloaded bytes differ from the source")
            valid = False
        page.wait_for_timeout(100)
    except Exception as exc:
        errors.append(f"{label}: did not save the file ({type(exc).__name__})")
        valid = False
    finally:
        context.remove_listener("page", on_page)
        page.remove_listener("framenavigated", on_navigation)
        if popups or any(p not in pages_before for p in context.pages):
            errors.append(f"{label}: download opened another tab or window")
            valid = False
        # Reveal can emit a queued hash event for the already-current URL
        # A different URL or document is actual navigation, including reloads
        changed_document = page.evaluate("performance.timeOrigin") != origin_before
        if any(url != url_before for url in navigations) or page.url != url_before or changed_document:
            errors.append(f"{label}: download navigated the page (events={navigations}, before={url_before}, after={page.url})")
            valid = False
        for popup in popups:
            if not popup.is_closed():
                popup.close()
    return valid


def check_page_downloads(page, root: Path, controls, errors: list[str], notes: list[str], route: str) -> None:
    tested, contrasts, exceptions = 0, [], 0
    page.add_style_tag(content="a[download],a[download] * { transition:none!important; animation:none!important; }")
    for index in range(controls.count()):
        control = controls.nth(index)
        filename = control.get_attribute("download") or ""
        label = f"{route} download {filename!r}"
        source_ref = control.get_attribute("data-download-source") or ""
        source = (root / source_ref).resolve()
        if not filename or root not in source.parents or not source.is_file():
            errors.append(f"{label}: missing filename or local source")
            continue
        href = control.get_attribute("href") or ""
        try:
            header, encoded = href.split(",", 1)
            if not header.startswith("data:") or ";base64" not in header:
                raise ValueError
            payload = base64.b64decode(encoded, validate=True)
        except (ValueError, TypeError):
            errors.append(f"{label}: href is navigable or not a generated payload")
            continue
        if payload != source.read_bytes():
            errors.append(f"{label}: payload is stale")
            continue
        if control.get_attribute("target") not in (None, "", "_self"):
            errors.append(f"{label}: target must not open another window")
        info = control.evaluate("""e => {
            const s = e.closest('.reveal .slides section');
            if (!s || !window.Reveal) return null;
            const i = Reveal.getIndices(s); Reveal.slide(i.h,i.v,-1);
            s.querySelectorAll('.fragment').forEach(f=>f.classList.add('visible'));
            return s.id;
        }""")
        if info:
            page.wait_for_function("(id) => Reveal.getCurrentSlide().id === id", arg=info)
            page.wait_for_function("(id) => location.hash === '#/' + id", arg=info)
            label = f"{route} #{info} download {filename!r}"
            page.evaluate("""async id => {
                const slide=document.getElementById(id);
                for(const animation of slide.getAnimations({subtree:true})) {
                    if(animation.effect.getComputedTiming().iterations===Infinity) animation.pause();
                    else animation.finish();
                }
                await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
            }""", info)
        page.evaluate("document.fonts.ready")
        # Images and filter changes must be ready before measuring the glyph
        control.evaluate("async e => Promise.all([...e.querySelectorAll('img')].map(i=>i.decode()))")
        if control.get_attribute("data-download-exception"):
            exceptions += 1
        contrasts.extend(check_control_contrast(page, control, label, errors))
        if click_download(page, control, payload, filename, errors, label):
            tested += 1
    minimum = f"{min(contrasts):.2f}:1" if contrasts else "n/a"
    notes.append(f"Downloads ({route}): {controls.count()} controls, {tested} saved with exact filename/bytes, no navigation or new windows; {exceptions} registered layout exceptions; minimum rendered contrast {minimum} in normal/hover/focus states")


def check_downloads_both_routes(page, root: Path, errors: list[str], notes: list[str], selected_ids=None) -> None:
    from qa_common import local_server, WAIT_FOR_REVEAL
    def controls_for(target):
        if selected_ids is None:
            return target.locator("a[download]")
        scope = ",".join(f"section[id={json.dumps(sid)}] a[download]" for sid in selected_ids)
        return target.locator(scope) if scope else target.locator("a.__no_downloads_selected")
    controls = controls_for(page)
    if not controls.count():
        notes.append("Downloads: no controls in the selected scope")
        return
    check_page_downloads(page, root, controls, errors, notes, "file")
    deck = Path(unquote(urlparse(page.url).path.lstrip("/"))).resolve()
    # Windows file URIs start with /C:/; POSIX absolute paths must retain /
    if not re.match(r"^[A-Za-z]:", str(deck)):
        deck = Path(unquote(urlparse(page.url).path)).resolve()
    relative = deck.relative_to(root).as_posix()
    with local_server(root) as port:
        http_page = page.context.new_page()
        try:
            http_page.goto(f"http://127.0.0.1:{port}/{relative}")
            http_page.wait_for_function(WAIT_FOR_REVEAL, timeout=15000)
            http_page.evaluate("Reveal.configure({transition:'none',backgroundTransition:'none'})")
            check_page_downloads(http_page, root, controls_for(http_page), errors, notes, "HTTP")
        finally:
            http_page.close()
