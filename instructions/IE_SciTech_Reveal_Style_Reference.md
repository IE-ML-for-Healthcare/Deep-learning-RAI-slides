# IE School of Science and Technology - Reveal.js Style Reference v4

Source deck: `SciTech-2026_-_Master.pptx`

Original brand style-pack reference. It is subordinate to `instructions/slide_rules.md`, which wins on any conflict. Use it for brand intent, palette meaning, and logo lockups.

---

## Core instruction

Generate Reveal.js slides aligned with the IE School of Science and Technology visual identity: restrained, precise, modern, scientific. Navy and white contrast, charcoal or dark-green backgrounds, lime and mint accents, Montserrat typography, generous whitespace, and official logo lockups.

---

## File structure

All files must live in the **same folder** as your HTML deck.

```
your-deck.html
ie-scitech-reveal.css
ie-reveal-fit.js
logos/
  ie-scitech-horizontal-light-accent.svg   ← light, white, or clear logo regions
  ie-scitech-horizontal-dark-accent.svg    ← dark logo regions
  ie-scitech-horizontal-light-noaccent.svg
  ie-scitech-vertical-light-accent.svg
  ie-scitech-vertical-light-noaccent.svg
  ie-scitech-vertical-dark-noaccent.svg
backgrounds/
  bg-light-circles.png        ← abstract circles right (light)
  bg-light-circles-alt.png    ← circles top-right variant (light)
  bg-light-students.png       ← students in lab, circle mask (light)
  bg-dark-science.png         ← petri dish science right (dark)
  bg-dark-abstract.jpg        ← dark abstract texture (dark)
```

---

## Changelog from v3

| Issue | Fix |
|---|---|
| CSS specificity - `.ie-dark`/`.ie-light` could lose to base rule | Selectors promoted to `.reveal .slides section.ie-slide.ie-dark` (0,4,1 > 0,3,1). No `!important` needed |
| `ie-light` shorthand `background` reset `background-image` on bg classes | bg class rules use full `background` shorthand with image + fallback color. No shorthand clash |
| Logo overlapped dense content | `padding-bottom` raised to 130px (logo top is ~90px from bottom; 40px clearance) |
| Split layout bottom not logo-safe | `.ie-split .ie-content` gets `padding-bottom: 130px` |
| Card grid used fixed large padding | Cards use `padding: 72px 96px 130px` to match logo safety area |
| Auto-fit minimum 0.72 - overflow still possible | Floor lowered to 0.50 |
| Font not guaranteed | `@import` Montserrat added at top of CSS |
| Misleading `data-bg` attribute comment | Removed - bg classes are applied directly as CSS classes |

---

## Reveal.js setup

```js
Reveal.initialize({
  hash: true,
  width:  1600,
  height:  900,
  margin: 0,
  transition: "fade",
  disableLayout: false
});
```

HTML head load order (must be exact):

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/theme/white.css">
<link rel="stylesheet" href="ie-scitech-reveal.css">
```

---

## Logo usage

```html
<!-- Logo over a light, white, or clear region -->
<div class="ie-logo">
  <img src="logos/ie-scitech-horizontal-light-accent.svg"
       alt="IE University School of Science and Technology">
</div>

<!-- Logo over a dark region -->
<div class="ie-logo">
  <img src="logos/ie-scitech-horizontal-dark-accent.svg"
       alt="IE University School of Science and Technology">
</div>
```

Rules:
- Bottom-left, 48px from each edge (CSS handles this)
- Light, white, or clear region → `horizontal-light-accent.svg`
- Dark region → `horizontal-dark-accent.svg`
- On mixed-background layouts, choose the variant from the actual region beneath the logo
- Narrow-space fallback: add `ie-logo-vertical` class (112px wide)
- **Never** add text with the school name - the SVG already contains it
- **Never** rebuild the logo in HTML or CSS

---

## Colour tokens

```
--ie-navy-950:       #000024   primary text, dark slides
--ie-navy-900:       #000066   secondary navy
--ie-white:          #ffffff   text on dark, card fill
--ie-off-white:      #f7f7f5   light slide background
--ie-dark:           #242424   dark slide base
--ie-dark-green:     #15260f   dark slide gradient start
--ie-scitech-lime:   #c9ff8a   accent, card fill
--ie-scitech-green:  #9be15d   secondary accent
--ie-scitech-mint:   #b7e4c7   glow, highlight
--ie-soft-grey:      #e8e8e8   dividers, subtle backgrounds
```

---

## Typography

```
font-family: "Montserrat", "Aptos", "Helvetica Neue", Arial, sans-serif

h1:    300 weight  72px                       uppercase  letter-spacing 0.08em
h2:    300 weight  54px                       uppercase  letter-spacing 0.08em
h3:    700 weight  30px                       uppercase  letter-spacing 0.02em
p/li:  400 weight  22px                       sentence case
.subtitle: 400 weight  26px                      sentence case
```

Body text always uses regular weight, including paragraphs, bullets, questions, quotes, captions, takeaways, callouts, and table cells. Reserve bold weight for titles, headings, subheadings, and non-prose structural markers. Do not use `<strong>` for emphasis inside body copy. Use color, spacing, grouping, or concise subheadings instead.

Key takeaway strips are the one fixed exception to free styling: white at 40 % opacity with an 8 px lime edge on light slides, white at 10 % opacity with a 10 px lime edge on dark slides, 24 px regular weight text (allowed 22 to 26 px), clear of the IE logo and other elements. See `instructions/slide_rules.md`.

---

## Background image classes

Add one class to the `section`. Do not combine with `ie-light` or `ie-dark`.

| Class | Tone | When to use |
|---|---|---|
| `ie-bg-light-circles` | Light | Title, transition, section open |
| `ie-bg-light-circles-alt` | Light | Alternate title variant |
| `ie-bg-light-students` | Light | Collaborative / hands-on context |
| `ie-bg-dark-science` | Dark | Module breaks, emphasis |
| `ie-bg-dark-abstract` | Dark | Pure contrast, no imagery needed |

Dark-bg classes auto-apply white text and a left-side overlay. No extra classes needed.

Keep text left-aligned - all background images are right-weighted.

Use sparingly: max 1 in every 3–4 slides.

```html
<!-- Light bg -->
<section class="ie-slide ie-bg-light-circles ie-title" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg"
         alt="IE University School of Science and Technology">
  </div>
  <div class="ie-title-block ie-auto-fit">
    <h1>Title here</h1>
    <p class="subtitle">Subtitle</p>
  </div>
</section>

<!-- Dark bg -->
<section class="ie-slide ie-bg-dark-science" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg"
         alt="IE University School of Science and Technology">
  </div>
  <div class="ie-content ie-auto-fit">
    <h2>Section title</h2>
    <p>Body text - white is applied automatically.</p>
  </div>
</section>
```

---

## Layout patterns

### 1. Light title

```html
<section class="ie-slide ie-light ie-title" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg"
         alt="IE University School of Science and Technology">
  </div>
  <div class="ie-title-block ie-auto-fit">
    <h1>Title</h1>
    <p class="subtitle">Subtitle</p>
  </div>
</section>
```

### 2. Dark hero

```html
<section class="ie-slide ie-dark ie-hero" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg"
         alt="IE University School of Science and Technology">
  </div>
  <div class="ie-content ie-auto-fit">
    <h2>Concept</h2>
    <p>Short message</p>
  </div>
</section>
```

### 3. Four-card grid

```html
<section class="ie-slide ie-cards ie-dark" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg"
         alt="IE University School of Science and Technology">
  </div>
  <div class="ie-card-grid">
    <article class="ie-card ie-card-lime">
      <div class="ie-card-content ie-auto-fit"><h3>Title</h3><p>Text</p></div>
    </article>
    <article class="ie-card ie-card-white">
      <div class="ie-card-content ie-auto-fit"><h3>Title</h3><p>Text</p></div>
    </article>
    <article class="ie-card ie-card-offwhite">
      <div class="ie-card-content ie-auto-fit"><h3>Title</h3><p>Text</p></div>
    </article>
    <article class="ie-card ie-card-dark">
      <div class="ie-card-content ie-auto-fit"><h3>Title</h3><p>Text</p></div>
    </article>
  </div>
</section>
```

Card fills: `ie-card-lime`, `ie-card-white`, `ie-card-offwhite`, `ie-card-dark`

For image-backed cards with quote overlays, use `ie-card--media-bleed`,
`ie-card-media--full-bleed`, and `ie-card-overlay--full-width`. The image and
overlay must span the card's inner left and right borders, with image max-size
and horizontal margin constraints removed. Use
`ie-card-grid--equal-overlays` with `--ie-card-overlay-height` when repeated
quote overlays must share one height

Default table cells should stay lightly transparent so the background remains visible.
Use roughly `rgba(255, 255, 255, 0.25)` for regular cells and `rgba(201, 255, 138, 0.25)` for accent cells.

### 4. Split layout (image + text)

```html
<!-- Image left, text right -->
<section class="ie-slide ie-light ie-split ie-split-left" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg"
         alt="IE University School of Science and Technology">
  </div>
  <div class="ie-split-grid">
    <figure class="ie-image-panel">
      <img src="your-image.jpg" alt="Description">
    </figure>
    <div class="ie-content ie-auto-fit">
      <h2>Heading</h2>
      <p>Body text</p>
    </div>
  </div>
</section>
```

Use `ie-split-right` to flip (text left, image right).

---

## Overflow prevention

Wrap all text containers in `ie-auto-fit`:

```html
<div class="ie-content ie-auto-fit">...</div>
<div class="ie-card-content ie-auto-fit">...</div>
<div class="ie-title-block ie-auto-fit">...</div>
```

The script scales content down to fit its parent (floor: 0.50). If content hits the floor, split it into two slides instead.

Content limits:
- h1/h2 title: max 12 words
- Standard slide body: max 45 words
- Card body: max 25 words
- Four-card slide total: max 100 words

---

## Writing rules

- One key message per slide
- 3–7 word titles, uppercase
- Active, direct wording
- International System of Units
- Define non-common acronyms on first use
- Sentence case for body and subtitles

---

## Prompt block for future sessions

Paste this into any new chat when asking an LLM to generate slides:

```
Use the IE School of Science and Technology Reveal.js style pack v4.

Files (all in the same folder as the HTML):
  ie-scitech-reveal.css, ie-reveal-fit.js, logos/, backgrounds/

Slide rules:
- Every slide: <section class="ie-slide [variant]" data-transition="fade">
- Variant classes for solid backgrounds: ie-light (off-white + navy text), ie-dark (dark green/charcoal + white text)
- Variant classes for image backgrounds: ie-bg-light-circles, ie-bg-light-circles-alt, ie-bg-light-students, ie-bg-dark-science, ie-bg-dark-abstract
  - do NOT combine ie-light/ie-dark with ie-bg-* classes
  - dark bg classes auto-apply white text and overlay

Logo rule:
- Every slide: <div class="ie-logo"><img src="logos/ie-scitech-horizontal-[light|dark]-accent.svg" alt="IE University School of Science and Technology"></div>
- Light, white, or clear logo region → light-accent logo; dark logo region → dark-accent logo
- On mixed backgrounds, choose from the actual region beneath the logo
- NEVER add any text element containing the school name alongside the logo

Typography: Montserrat, uppercase tracked headings (h1/h2 weight 300, h3 weight 700), sentence-case body at regular weight, active voice, max 12-word titles. Do not bold body text; reserve bold weight for titles, headings, and subheadings.

Overflow: wrap all text containers in ie-auto-fit.

Layouts: ie-title (ie-title-block), ie-hero (ie-content), ie-cards + ie-card-grid, ie-split + ie-split-left/right.

Card fills: ie-card-lime, ie-card-white, ie-card-offwhite, ie-card-dark.

Script: load ie-reveal-fit.js after Reveal.js; call IERevealFit.fitAll() in the then() callback.

Canvas: width 1600, height 900, margin 0, transition fade.

Writing: one message per slide, 3–7 word titles, max 45 body words, IS units.
```
