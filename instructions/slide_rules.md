# IE Reveal.js Slide Rules

Canonical design rules for IE School of Science and Technology Reveal.js decks. `instructions/layout_playbook.md` explains which pattern to choose; this file states the fixed rules. If they conflict, this file wins and the conflict is reported.

## Canvas And Runtime

- Every deck uses a 1600 x 900 px, 16:9 canvas: Reveal.js `width: 1600`, `height: 900`, `margin: 0`
- Set `pdfMaxPagesPerSlide: 1` so print export never splits a slide across pages; the release tooling adds `pdfSeparateFragments: false` for PDFs
- Pin exact CDN versions, for example `reveal.js@5.2.1`; never a floating major such as `reveal.js@5`
- Load `ie-scitech-reveal.css` after the Reveal.js base and theme stylesheets
- Load `reveal.js`, then `ie-reveal-fit.js`, `slide-aliases.js`, and `ie-components.js`
- Call `IESlideAliases.resolve()` and `IEComponents.prepare()` before `Reveal.initialize`
- Call `IEComponents.init()` and `IERevealFit.fitAll()` only inside `Reveal.initialize(...).then(...)`
- Typography is sized in px on the fixed canvas; never use `vw` or `vh` units, which follow the browser window instead of the slide
- Content slide titles use `var(--ie-title-size)` (54 px), or `var(--ie-title-size-compact)` (44 px) when the layout is dense; leads use `var(--ie-lead-size)` (28 px) or `var(--ie-lead-size-compact)` (22 px); display and quote slides may exceed these only with a CSS comment stating why
- Logo placement uses the shared classes: default bottom-left, `ie-logo-tr` for top-right, `ie-logo-br` for bottom-right; do not write per-slide logo rules unless a documented clash requires it
- `ie-auto-fit` only shrinks content, never enlarges it, and floors at 0.50; a fit scale below 0.75 means the slide should be split or simplified
- Inside a `safe-frame`, `ie-reveal-fit.js` widens and heightens the scaled box by `1 / scale`, so scaled content always spans the frame margin to margin; never size a box with `var(--fit-scale)` in slide CSS, `scripts/check_deck.py` fails it
- Do not run custom scaling logic, and keep all deck JavaScript scoped to the slide it serves

## Slide Structure

Every slide is a top-level section with a stable id:

```html
<section id="session-03-market-sizing" class="ie-slide [variant] [pattern]" data-transition="fade">
```

- The id is kebab-case, starts with its session prefix, and never changes once referenced
- Every normal slide has one `.ie-logo` block, one main layout block, and one clear student-facing message
- Sessions sit between the course sentinels, each inside one paired `SESSION NN START` and `SESSION NN END` comment, with `NN` matching the roadmap session number
- Every session opens with a title slide, a purpose, and an adaptable agenda slide using `ie-agenda-stack`
- Quote slides using `ie-quote-slide` show the quotation and attribution only: no takeaway, takeaway card, or visible source line

## Slide Aliases

- Repeat an identical slide with `<section id="new-id" data-slide-ref="canonical-id"></section>`, never with copied HTML
- An alias points directly at a canonical slide, never at another alias, and keeps its own unique id
- Edit the canonical slide only; the resolver copies attributes and namespaces descendant ids per alias

## Variants

Solid variants: `ie-light`, `ie-dark`

Image background variants, each a 1600 x 900 file in `backgrounds/`:

- `ie-bg-light-circles`, `ie-bg-light-circles-alt`, `ie-bg-light-students`
- `ie-bg-dark-science`, `ie-bg-dark-abstract`
- `ie-bg-green-dark-left`, the standard composition for true 50/50 `ie-lr` slides
- `ie-bg-green-cards-right`, `ie-bg-green-cards-left`, with four card panels baked into the image

Rules:

- Never combine `ie-light` or `ie-dark` with an `ie-bg-*` class
- Dark image variants add a legibility overlay automatically; their direct children sit above it at zero specificity, so a component's own positioning always wins
- On green-card backgrounds, add text overlays only, aligned to the baked cards: navy text on white and lime cards, white text on the dark card, logo opposite the card area
- Photo-background slides keep text in the non-photo area, with a clear gap between text and image

## Layout

- Normal content slides use `safe-frame` with one `ie-auto-fit` inside it
- Choose the safe frame inset with one modifier class on the `safe-frame` element, never with a slide-scoped rule: default (no modifier, 86 px top, 96 px sides, 130 px bottom), `safe-frame--open` (88 / 96 / 96 / 96 px), `safe-frame--dense` (74 / 84 / 70 / 84 px) for tables, checklists, and rubrics, or `safe-frame--full-bleed` (0 px) for quote and full-canvas slides
- A slide whose content cannot fit legibly in any variant keeps a scoped inset rule with a `Safe frame exception` comment stating why; never shrink text to fit a variant
- Every quote slide uses one size: `source-quote` or `ie-quote-text` at 50 px light italic, `ie-quote-emphasis` for the lime bold phrases, and a 30 px attribution that starts with `- `; only a quote over 40 words adds `source-quote--long` (30 px); any other size needs a `Display exception` comment on its scoped rule
- Cards on light slides use `ie-card-light` (white, hairline border, lime top bar, navy text), or `ie-card-light--side` for a wide callout; never fill cards with solid navy on a light slide
- Full-bleed media cards use `ie-card--media-bleed` on the card, `ie-card-media--full-bleed` on the media wrapper, and `ie-card-overlay--full-width` on the quote or text overlay
- Full-bleed card images set width and height to 100 %, remove inherited max-width, max-height, and horizontal margins, and run from the card's inner left border to its inner right border
- Full-width overlays use the same inner left and right edges; never rely on the browser's default blockquote width, margin, or max-width
- Repeated media-card rows use `ie-card-grid--equal-overlays` with `--ie-card-overlay-height` sized for the longest copy so all peer overlays share one height and bottom edge
- `scripts/check_browser_qa.py` enforces the full-bleed media-card edge and equal-overlay contracts
- A side by side comparison or two-sided activity uses the `ie-compare ie-compare-dark` template, never a one-off two column layout
- Agenda cards use `ie-agenda-stack`; do not restyle `agenda-card` text sizes per slide
- `ie-two-col` is two content columns inside the normal frame
- `ie-split` is an asymmetric media and text split
- `ie-lr` is a true 50/50 structural slide: padding-free halves, content inside `ie-lr-panel`, side-specific title with the logo in the opposite top corner, aligned panel starts, a reserved `ie-lr-footer` band, and either one shared takeaway or one takeaway per half
- Every left versus right comparison uses `ie-compare ie-compare-dark`, unless the professor approves another treatment for that slide; five rows per side is the tuned maximum
- Keep visible content inside the 96 px side margins and never let it spill outside the canvas
- Titles and subtitles are left-aligned
- Use image-only slides only when intentionally designed

## Links and click targets


### Standard icon buttons

- Use the standard download button for file downloads, following [Downloads](#downloads), pattern-27
- Use the standard GitHub icon button for GitHub destinations when no visible text name is requested, following pattern-34; preserve an explicitly requested text label
- Use `ie-github-btn` with a local `media/brands/github-official.svg` carrying `ie-github-icon`; this is the official GitHub brand mark used in the professor's reference
- Keep the shared 42 x 42 px button, 24 x 24 px mark, 8 px corner radius, 16 px heading gap, lime hover and visible 2 px keyboard-focus outline
- Place title-side links in `ie-title-with-link`; the existing `ie-title-with-download` heading class remains supported and can contain either control
- Choose `ie-github-btn--dark` on an actual dark surface; use the default treatment on a light surface, and check normal, hover and keyboard-focus contrast
- Use an anchor with a GitHub `href`, a destination-specific `aria-label`, a `title` tooltip, `target="_blank"` and `rel="noopener noreferrer"`; keep the mark's `alt=""` because the anchor names the action
- GitHub buttons navigate to their destination; reserve `download` and `data-download-source` for file downloads

```html
<h2 class="ie-title-with-link">Project resources
  <a class="ie-github-btn" href="https://github.com/OWNER/REPOSITORY"
     target="_blank" rel="noopener noreferrer"
     aria-label="Open the project repository on GitHub" title="Open repository on GitHub">
    <img class="ie-github-icon" src="media/brands/github-official.svg" alt="">
  </a>
</h2>
```

## Grid

Template standard since 2.1.0: every element sits on a gridline. The canonical lines below are shared by the patterns in `slide_patterns.html`. `scripts/check_browser_qa.py` enforces them on `index.html` and fails the run on a breach; other decks, including the gallery, only warn.

Vertical lines (x):

| Line | Value | Use |
| --- | --- | --- |
| Canvas edges | 0 and 1600 px | Full-bleed images, panels and bands |
| Source line | 44 px | `.ie-source-line` only |
| Logo edge | 48 px | Bottom-left logo and footer elements |
| Content margins | 96 and 1504 px | Titles, content, strips on default and open frames; the top-right logo ends on 1504 |
| Dense margins | 84 and 1516 px | Titles, content and strips on `safe-frame--dense` |
| Logo-clear line | 360 px | Left edge of a strip that shares the bottom band with a bottom-left logo |
| Centre axis | 800 px | `ie-lr` halves and centred compositions; a two-column gutter sits symmetrically on it |
| Split text line | 736 px | Text column beside a 640 px `ie-split` image panel |
| Hero indent | 192 px | Session or section title slides only |

Horizontal lines (y):

| Line | Value | Use |
| --- | --- | --- |
| Top-right logo | 52 px | `ie-logo-tr` top, level with compare titles |
| Frame top | 86, 88 or 74 px | Default, open or dense frame; the title box sits on it |
| Eyebrow offset | frame top + 28 px | Title top when a kicker or eyebrow sits above it |
| Quote copy | 154 px | Top of every quote, at x 96 px; a `source-quote--long` quote starts on 86 px |
| Frame bottom | 770, 804 or 830 px | Default, open or dense frame |
| Bottom-left logo | 852 px | Logo bottom edge, 48 px above the canvas edge (top-right logo: right edge 1504 px, top 52 px; `ie-logo-br`: right edge 1552 px, bottom 852 px); nothing full width may cross the logo at x below 258 px |

Rules:

- Pick a safe-frame variant, never an ad hoc inset; a `Safe frame exception` may change the bottom inset only, the top and sides stay on the lines above
- The title starts on the frame margin and its top sits on the frame top line, or 28 px lower under an eyebrow; never centre a whole slide stack vertically so the title floats
- A takeaway strip spans its content column, frame margin to frame margin or the column it closes; it never floats centred at a width that matches no other element. Beside a bottom-left logo it starts on the 360 px logo-clear line
- Card grids use a 28 px gutter (20 px for dense rows); keep one gutter per grid
- Repeated families (agenda, checkpoint, rubric, checklist, core tool, applied example) share identical lines from slide to slide, so nothing jumps on a page turn
- Quote copy starts at x 96 px, y 154 px, 800 px wide at most
- A new layout may add a gridline when the design needs it: align every element on the slide to it, reuse it across the family, and record it in this table when a second slide uses it
- A slide that cannot follow the grid carries `data-grid-exception="<reason>"` on its section; the browser QA reports the reason instead of failing. Keep exceptions rare and specific

## Sources And Citations

- Every footnote-style source uses `.ie-source-line`, bottom left, outside the 96 px content margin; use `.is-wrap` for a second line
- Place the logo top right on any slide with a source line
- The source colour follows the section background class; a slide whose scoped CSS changes the bottom-left background sets the colour explicitly and is contrast-checked
- Record source details for photos, quotations, and screenshots in visible citations or an approved source record, never only in speaker notes
- `.ie-source-line` is the one reserved place at the bottom of a slide for both Sources and Notes; a Source cites where a claim or figure comes from, a Note spells out an abbreviation or a term used inline. Never render either as a separate block, and never place one above the title, context bar, table, or main content
- Mark the term that needs a note with a small superscript number at the point it appears, using `<sup class="ie-note-marker">1</sup>`; repeat the same number in the Notes text at the bottom that explains it, wrapped in the same `ie-note-marker` class so both ends match in size
- Number notes in the order their markers first appear on the slide, starting at 1; reuse the same number for a repeated marker
- Order inside `.ie-source-line`: `Sources: ...` first, then `Notes: ...` after it. Show only `Notes: ...` when the slide has notes but no sources, and only `Sources: ...` when it has sources but no notes; never show an empty `Sources:` or `Notes:` label

## Tables

- Every data or reference table uses `ie-table`, which owns the navy header, 25 px body and 22 px header text, borders, alignment, and alternating lime rows
- Set every column width with a `<colgroup>`
- Use `ie-table-numeric` for centred, non-wrapping numeric columns and `ie-table-value` only for genuinely critical figures
- Use `ie-table-compact` only for six or more rows; it keeps the shared visual style
- Never restyle table colours, sizes, borders, or striping in slide-scoped CSS; split a long table instead of shrinking it
- Every table spans its frame margin to margin; the browser QA fails a table that stops short of, or runs past, its safe frame
- Highlight one decisive row with `ie-table-key-row` on the `tr` (lime bar plus 26 px clearance so text never touches the bar), and add `ie-table-key-row--bold` only for one short statement; never use a scoped inset shadow, a heavy border or a filled row, and never more than one key row per table
- Keep every cell of a column the same size, for example one source column style, never mixed sizes
- When a cell contains more than one independent statement or block item, prefix every statement with the literal `- ` at the existing cell text edge
- Do not use `<ul>` or `<ol>` for these compact table bullets because browser-default indentation wastes cell width; preserve category labels and single statements without bullets
- Short-text tables keep the shared 25 px and default padding; only long-text `ie-table-compact` rubrics may use a documented 20 px Table exception
- A table that names tools, products, or brands shows each mark in its first column with the shared brand-mark classes: `ie-table-brand-cell` on the `td`, `ie-table-brand` around the mark and name, `ie-table-brand-link` linking the mark to the official page (`target="_blank" rel="noopener noreferrer"` and an `aria-label` naming the destination), `ie-table-brand-name`, and optional `ie-table-brand-note`; see `slide_patterns.html` pattern-31
- Store brand marks locally under `media/brands/`, record the official source and retrieval date in an HTML comment beside the rows, give the mark an empty `alt` because the visible name carries the meaning, and use a Tabler icon without a link for a generic or default row

## Colour

- Use only the palette tokens in `ie-scitech-reveal.css`: navy, white, off-white, dark, dark green, lime, scitech green, mint, soft grey, and the documented semantic tokens
- For translucency use the channel tokens, for example `rgb(var(--ie-navy-950-rgb) / 0.2)`; never a new hex value
- When an accent fails contrast on its background, most often lime or scitech green on a light slide, derive a darker variant of the same hue and confirm WCAG AA, 4.5 to 1 for body text, before using it
- Charts and diagrams use the same palette, with axis labels and legends at 18 px or larger

## Key Takeaway Strips

Template standard since 2.1.0. These rules are strict, and `ie-scitech-reveal.css`, `scripts/check_deck.py`, and `scripts/check_browser_qa.py` all enforce them.

- Every key takeaway message at the bottom of a slide that sits in a strip uses exactly one of two looks
- Light or image-light slide: clear white at 40 % opacity, 8 px lime left edge, navy text, reference `slide_patterns.html` pattern-08
- Dark slide: white at 10 % opacity, 10 px lime left edge, white text, reference `slide_patterns.html` pattern-24
- Nothing else: no solid navy, no grey, no opaque white, no lime or green tint, no gradient, no top or bottom border, no second variant
- Every bottom takeaway is a strip: a text-only closing line with no background is no longer allowed; a takeaway is any closing message, key message, rule, or question that sits below the content of a slide
- One size for every strip in the deck: 24 px, weight 400, line height 1.25, padding 12 px 24 px, left aligned; the allowed range is 22 to 26 px and the browser QA fails anything outside it
- Never use bold, lime text, or a larger size to make a takeaway louder; hierarchy comes from position and the strip, not from type size
- The shared strip classes are `ie-band`, `ie-takeaway`, `deck-takeaway-card`, `ie-compare-takeaway`, `ie-lr-takeaway-left`, `ie-lr-takeaway-right`, `ie-lr-takeaway-shared`, `ie-process-takeaway`, and `ie-step-takeaway`
- A course-specific takeaway class must also carry `ie-takeaway` (for example `class="ie-takeaway s5-loop-takeaway"`); never add course class names to the shared registries
- A new shared takeaway pattern must be added to the standard blocks in `ie-scitech-reveal.css` and to `STRIP_CLASSES` in `scripts/check_deck.py` and the `STRIP` selector in `scripts/check_browser_qa.py` before use; the browser QA scans fragments in their revealed state, so a hidden takeaway is tested too
- Slide-scoped CSS in `index.html` loads after the shared file, so it can override the standard; keep slide-scoped rules to margins and positions and never set colour, background, border, or font size on a strip
- Never set a background or border on a strip in slide-scoped CSS or inline; the shared block uses `!important` and the static check fails inline styles
- The `is-solid` variant is retired and fails the static check

## Clash-Free Layout

Hard rule, tested on every slide by `scripts/check_browser_qa.py`, which fails the run on any breach.

- No text, image, or takeaway strip may overlap the IE logo
- No takeaway strip may overlap any other text, image, table, or figure
- The tolerance is 3 px; anything larger is a failure, not a warning
- Fix a clash by simplifying or moving content, or with a slide-scoped margin; never hide the collision by shrinking the logo or clipping content
- Inspect the screenshot of every changed slide as well, because the test measures boxes and a person judges whether the result looks right

## Design Quality Bar

Apply the visual-scope contract in [Design preservation and visual quality](layout_playbook.md#design-preservation-and-visual-quality) before using these quality criteria to change an existing slide

Template standard since 2.1.0. These rules sit on top of every rule above; `instructions/layout_playbook.md`, section Design excellence, explains how to meet them.

- Passing the gates is the floor, not the goal: every new or changed slide must be the clearest, most visually compelling version of its message that these rules allow
- Draw the shape of the content: order, branching, layers, ownership, spectrum, magnitude or a file tree becomes a diagram, lanes, stack, axis, stat cards or tree; plain tables and rows of identical cards are for genuine reference data only
- Vary layout patterns and surface treatments across a session: do not repeat the same content pattern on more than two consecutive content slides outside a deliberate sequence, and never fall back to bare `<ol>` or `<ul>` lists or repetitive plain text cards when a pattern in `slide_patterns.html` fits
- Tailor copy and item counts to the chosen pattern's geometry: populate all 5 rows of `.ie-compare-list` without slide-scoped `.ie-compare` overrides, keep `.ie-process-label` headings on one line so peer descriptions share one baseline, keep `.ie-roadmap` subtitles on a single line clear of stage highlights, and aim for `.ie-auto-fit` scales of `0.85` or higher
- Balance the safe frame: preserve intentional negative space and focal hierarchy; investigate unexplained empty bands, but do not inflate spacing, enlarge text, or redistribute an accepted composition solely to meet a frame-occupancy heuristic
- Use the available vertical span on new slides and approved layout repairs: distribute the main visual or content between the heading and the reserved footer area. A body and takeaway compressed beneath the title with a large unexplained lower blank band fails Design QA, even when fit checks pass. Keep the title, logo, source line and safe-frame anchors on their canonical gridlines; follow [Vertical composition](layout_playbook.md#vertical-composition)
- Body text is 19 px or larger; uppercase tracked labels of 14 to 17 px are for phases, kickers and axis ends only
- One focal point per slide: at most one key card, key row, badge or lime-tinted element
- A takeaway strip holds one message; move a second line to the lead, and keep inline `<code>` out of strips because the strip layout drops the spaces around it
- Visual states keep one meaning across the deck: dashed border for separate, cross-cutting or blocked; faded dashed for disposable or generated; lime border or tint for the key item or a passing outcome
- Every arrow, lane and box is factually true; a diagram implying a wrong flow, owner or output fails the Logic QA
- Motion stays the standard fade; a reveal sequence still needs the professor's request
- Render and inspect the full-size screenshot before reporting; for existing slides apply the baseline comparison and improvement/preservation pass defined in `instructions/layout_playbook.md`, section Design preservation and visual quality

## Text

- Titles 3 to 7 words where possible, never 12 or more
- Body text 45 words or fewer per slide, sentence case, active voice
- Body text is regular weight; bold is reserved for titles, headings, subheadings, and structural markers
- Emphasis inside prose uses colour, for example lime or the pattern's `*-emphasis` class, never `<strong>`
- No em dash characters, and bullet lines never end with a full stop
- Final takeaways stay under 20 words, active, with no final full stop

## Interaction

- Reveal.js fragments only when the professor or the approved brief explicitly asks for a reveal sequence
- Speaker notes follow the Course Profile in `AGENTS.md` and `deck.config.json`; when forbidden, no `<aside class="notes">`, `class="notes"`, or hidden presenter comments
- `ie-tooltip` for optional one-sentence definitions of 12 words or fewer, with `tabindex="0"`, `data-tooltip`, and an `aria-label` holding the term and definition; never hide required meaning in a tooltip
- D3 is the chart library, loaded at a pinned version only in decks that use it; Mermaid diagrams render on Reveal `ready` and `slidechanged`
- One chart or diagram per slide, with one clear message
- See `instructions/ie_slide_examples.md` for working code, math, chart, diagram, download, alias, and roadmap snippets

### Key-takeaway image modal

- Use this pattern only when an optional, source-specific image adds context or evidence to the slide
- Bind the interaction to the exact key takeaway strip, never to the whole slide, its parent layout, or an unrelated card
- Use the shared hooks `ie-image-modal-trigger`, `ie-image-modal`, `ie-image-modal-content`, `ie-image-modal-img`, and optionally `ie-image-modal-link` and `ie-image-modal-trigger-icon`; `ie-components.js` wires the behaviour, so never write a slide-local initialiser
- The trigger always shows the shared "CLICK FOR IMAGE" pill on its right edge, so the presenter knows the takeaway opens an image; add the Tabler thin `eye.svg` as `ie-image-modal-trigger-icon` before the text for a stronger cue. Never hide, restyle, or relabel the pill per slide
- Point the trigger at its dialog with `aria-controls="<modal id>"`
- Give the takeaway `role="button"`, `tabindex="0"`, and an action-focused `aria-label`; give the modal `role="dialog"`, `aria-modal="true"`, `aria-hidden="true"`, and an informative label
- Give an informative image a concise `alt`; use an empty `alt` only when adjacent visible text already conveys the image meaning
- Open on click, Enter, and Space; close on Escape, overlay or outside click, and `slidechanged`
- Keep the modal absolutely positioned inside the same section so it does not alter slide layout or fit measurement
- Use a local image asset with no runtime network dependency, and hide the modal in print mode
- Validate the closed and open states at 1600 x 900, including keyboard, outside-click, Escape, slide-change, overflow, and console checks

## Code And Live Demo Slides

Template standard since November 2026. Gallery pattern-33 is the reference; `instructions/ie_slide_examples.md`, section Live Demo Slide, holds the markup.

- Code, configuration files and terminal output always use the shared `ie-code` figure: a dark terminal-style panel with a file-name bar, 18 px monospace text and the shared highlight spans; never a screenshot of code and never a new highlight.js block
- A live demo or a code walkthrough uses the live demo slide: `ie-slide ie-dark ie-logo-tr`, `safe-frame safe-frame--dense`, a title starting with `Demo` (or `Demo N:`) of 3 to 7 words, one `ie-demo-lead` line, one `ie-demo-grid`, and one `ie-band ie-demo-band` takeaway
- The grid holds two columns: the change on the left as an `is-before` figure (dashed, faded, the code being replaced) above an `is-after` figure (lime top bar, the target), and the proof on the right as one `is-run` terminal figure with the real commands and their output; use `ie-demo-grid--wide-left` when the code lines are longer than the terminal lines, `ie-demo-grid--wide-right` when the After code is the widest
- A demo that only runs commands may replace the code column with an `ie-demo-legend` that explains the output; a demo whose output lines are wider than a column puts the terminal full width under the grid with `ie-demo-terminal`
- Every output line on a demo slide comes from actually running the code shown; shorten with `...`, never invent a result. Keep the runnable demo in the course's class exercises folder with a step-by-step demo script
- Place one demo slide after the explanation slides of each topic, so every topic closes with its proof; all demo slides in a block share the same layout, so nothing jumps between them
- Lines must fit their column without clipping: about 80 characters in the wide column, 52 in the narrow one, 78 in a full-width terminal at 17 px; shorten or split code instead of shrinking it, and keep `ie-auto-fit` at 0.85 or higher
- An annotated file on a light or dark slide (for example `config.yaml` or `.env`) uses the same `ie-code` figure, with `ie-tooltip` hot spots on the keys
- Build figures with `python scripts/code_figure.py` instead of hand-escaping code; slide-scoped CSS may only add margins or a font size between 17 and 19 px, never restyle the figure

## Downloads

- The official download control is the compact title-side icon in pattern-27: `ie-title-with-download`, `ie-download-btn`, and the local `media/icons/tabler/download.svg` with `ie-download-icon`
- Place it beside the relevant heading; keep the 42 x 42 px button, 24 x 24 px glyph, 8 px corner radius, and 16 px title gap; resource cards and text links are not the default download button
- Choose the light treatment for an actual light surface and `ie-download-btn--dark` for an actual dark surface; inspect the rendered surface, including cards, gradients, and photos, rather than inferring contrast from the slide class
- Check the icon against its rendered background in normal, hover, and keyboard-focus states: minimum 3:1 contrast; keep a visible keyboard-focus outline of at least 2 px
- Contrast basis: [Web Content Accessibility Guidelines 2.2, non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html); the browser check measures rendered contrast and is not a full accessibility certification
- Existing professor-approved layout exceptions are listed narrowly by deck, slide, source, kind, count, and reason in `download-exceptions.json` and marked with `data-download-exception`; do not create or expand an exception without the professor's instruction
- Every control, including an exception, uses an anchor with an exact `download` filename, `data-download-source`, an accessible label, and a generated base64 `data:` URI; standard buttons also have a filename or file-type tooltip
- Generate and refresh payloads with `python scripts/sync_downloads.py`; never use a relative or external navigable URL, a new-window target, or an `onclick` handler for a download
- Prove the action with `scripts/check_browser_qa.py`: over both `file://` and HTTP, save the exact filename and source bytes with no popup, new tab, or same-tab navigation; an exception changes only presentation, never this behaviour
- See `instructions/ie_slide_examples.md` for the implementation and `instructions/browser_qa.md` for validation commands

## Assets

- Follow `instructions/asset_sourcing.md` for every icon, photo, logo, screenshot, or diagram
- Keep every icon in one rail, flow, or repeated family on the same Tabler variant and stroke width; the standard is `media/icons/tabler/thin/` at `stroke-width="1.25"`
- Store assets locally in optimised files; no runtime hotlinks and no embedded base64 images
- Reusable backgrounds are exactly 1600 x 900 px, resized with centre-crop in their original format; keep originals in Git history before replacing

## Logos

- `logos/ie-scitech-horizontal-light-accent.svg` over light, white, or clear regions
- `logos/ie-scitech-horizontal-dark-accent.svg` over dark regions
- On mixed backgrounds, choose from the actual region beneath the logo
- Never add the school name as text next to the logo; the lockup contains it

## Protected Files

Do not modify `ie-reveal-fit.js`, `slide-aliases.js`, `ie-components.js`, `logos/`, or `backgrounds/` unless the task is explicitly about them.
