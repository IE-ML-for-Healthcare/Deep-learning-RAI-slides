# Layout Playbook

Design-thinking guide for choosing and extending reusable Reveal.js slide layouts.

This file sits alongside `instructions/slide_rules.md`. `slide_rules.md` states the fixed
rules (canvas size, variants, logos, text limits). This file states the judgment: which
layout pattern to reach for, given what the slide needs to communicate, and how to design
a new one when none of the existing patterns fit.

`instructions/slide_rules.md` remains the canonical design source of truth for rules.
This playbook is the canonical source for layout selection reasoning. If the two ever
conflict, `slide_rules.md` wins, and the conflict should be reported.

## When to use this file

Read this file before designing a new slide layout, and before proposing an alternative
layout for an existing slide. Use it together with `slide_patterns.html`, which is the
browser-previewable code gallery. This file explains the thinking behind each entry
there; `slide_patterns.html` is the working code. Every pattern below has a matching
numbered entry in that file and a commented block in `ie-scitech-reveal.css`.

## Design preservation and visual quality

This section owns visual change scope and preservation. Factual accuracy, logical flow, technical compliance, and visual quality are separate requirements. Success in one does not compensate for failure in another

### Establish the visual contract

- Classify the task before editing: review only, content correction, targeted layout repair, or new design/redesign
- A review-only request authorizes inspection and findings, not edits to the deck, assets, layout, or content
- A content correction authorizes the specified wording, facts, links, or process changes within the existing composition; it does not authorize redesign, slide splitting, reordering, asset removal, or a new visual style
- Use the professor's latest accepted deck or named reference as the visual baseline, regardless of which person or AI created it; do not substitute an agent's preferred minimalist style
- Record the actual baseline revision or working-tree snapshot and affected stable slide ids; read the current files and preserve other agents' work

### Maintain an elegant, visually rich deck

- Preserve the composition, focal hierarchy, imagery, diagrams, visual density, typography relationships, colour balance, and rhythm of established slides during content maintenance
- Keep visual richness purposeful and restrained: use meaningful imagery, diagrams, comparisons, process flows, and varied compositions without ornamental clutter or excessive decoration
- Edit copy and links in place first, and make only the smallest adjustment needed within the authorized visual scope
- Do not replace designed compositions with generic numbered lists, plain tables, repeated text cards, or widely spaced lines because they are easier to implement or validate
- Do not replace an interactive roadmap with a static table, remove media, flatten a comparison, or normalize several slides to one convenient pattern unless the professor requests that structural change
- For new slides or an authorized redesign, inspect relevant professor-accepted slides and the pattern gallery, select a pattern that expresses the content, and maintain the surrounding deck's quality and visual rhythm
- Preserve intentional negative space and readable content density; do not enlarge gaps or text, strip away meaning, or crowd the canvas merely to satisfy a word-count or frame-occupancy heuristic
- Correct a verified design-rule breach narrowly within the authorized scope; it is not permission to restyle the slide or deck, weaken checks, or invent exceptions
- If a required correction cannot fit without a substantial composition change, report the exact slide and conflict and propose a targeted alternative; continue independent authorized work without imposing new approval rounds on routine copy fixes

### Verify preservation, not only rendering

- Compare full-size baseline and revised screenshots of every visually edited slide at the same viewport and comparable interaction state. Reuse an existing baseline when it matches the current pre-edit slide, relevant styles/assets and interaction state; record its path and revision or working-tree state. Capture a fresh baseline only when matching evidence is unavailable. A download-payload-only change with unchanged appearance may reuse its prior visual evidence; validate the changed download behaviour through the required runner checks
- Check that the requested correction is visible while hierarchy, balance, useful visuals, readability, alignment, and neighbouring-slide rhythm are preserved or improved within scope
- Assess content accuracy and Logic QA separately from Design QA; distinguish an inherited issue from a regression introduced by the edit
- Automated checks establish their measured technical conditions, not aesthetic quality; never report Design QA as passed solely because scripts passed
- A content-maintenance improvement pass can confirm that the accepted composition should stay unchanged; it must not manufacture a visual redesign to satisfy a reporting checkbox
- Report content changes and visual changes separately, identify the baseline and screenshot evidence, and explain every deliberate visual departure

## Design priorities, in order

1. One clear message per slide. The layout exists to carry that message, not to
   decorate the slide
2. Structural clarity over density. If a layout needs a legend to explain itself, it is
   too complex for a live teaching session
3. Reuse before invention. Check the patterns below, and the `ie-` prefixed components
   in `ie-scitech-reveal.css`, before creating a new layout
4. Numbers, tags, dashed borders, and colour are teaching devices, not decoration. Use
   them only when they carry meaning, for example a dashed border to say "this is
   deliberately separate", a numbered chip to say "this is an ordered sequence", or lime
   to mark the two or three words that carry the argument
5. Highlight sparingly. If half the line is lime, nothing is emphasised
6. Every new reusable pattern must survive `IERevealFit.fitAll()` at 1600 x 900 with no
   spill before being promoted to `ie-scitech-reveal.css`
7. Aim above the floor. Passing the rules and gates is the minimum; follow "Design
   excellence" below and push every slide to its clearest, most compelling form

## Design excellence

Template standard since 2.1.0. The deck rules are the floor, not the goal. Every new or changed slide must aim to be the clearest and most visually compelling version of its message that the rules allow. The hard rules live in `instructions/slide_rules.md`, section Design Quality Bar; this section explains how to reach them. Reference patterns: `slide_patterns.html` pattern-08, pattern-19, pattern-24, and pattern-31. A course deck may list its own best slides here as extra references

### Principles

1. Show the mechanism, not a list. Before choosing a layout, ask what shape the content has: an order, a fork, layers, owners, a spectrum, magnitudes or a file tree. Draw that shape; the reader should understand the idea before reading every word
2. Make the takeaway visible. The layout should prove the closing line: if the takeaway says "people decide the exceptions", the slide shows where people act
3. Balance the frame with meaning. Preserve intentional negative space and the established focal hierarchy; address accidental empty bands within the authorized visual scope rather than spreading a few lines across the canvas
4. One focal point. Give the eye one place to land first: one key card, row, badge or figure, never several competing ones
5. Clear hierarchy at a distance. Large title, distinct headings, comfortable body, small uppercase labels; a student at the back of the room must read every word
6. Consistent visual vocabulary. The same shape means the same thing everywhere in the deck (see Visual vocabulary below)
7. Truth before beauty. Every arrow, lane and box must be factually right; a beautiful diagram that implies a wrong flow is worse than a plain table
8. Rhythm across the block. Alternate light and dark slides in a block, and vary the pattern so consecutive slides do not look identical, unless they form a deliberate family
9. Motion only with meaning. Keep the standard fade; a reveal sequence needs a reason and the professor's request

### Choosing structure from the message

| Message shape | Draw it as | Avoid |
| --- | --- | --- |
| Ordered steps | Process icon flow or numbered ladder | Unnumbered bullet list |
| Parallel independent work that rejoins | Fork and join diagram with outcome branches | A straight rail that hides the parallelism |
| Who does what | Lanes by actor, steps placed in their owner's lane | Identical boxes with the actor in the text |
| System parts | Layers stacked in flow order, cross-cutting parts as a separate dashed pillar | A table of module names |
| Levels or a spectrum | Cards in order plus an axis that names the two ends | Three unrelated cards |
| A few decisive numbers | Stat cards with large figures, one key card | Numbers buried in a sentence or table |
| Files a process produces | A folder tree numbered to rows that say what each item is for | A table of filenames |
| Rules or safeguards | Icon cards with a short heading and one rule | Numbered cards with text at the bottom |
| Two sides | `ie-compare ie-compare-dark` | One-off two-column layouts |
| Code, a configuration change or a command | Live demo slide: Before and After code beside a Run it terminal (pattern-33) | Screenshots of code, highlight.js blocks, prose that describes output |
| Genuine reference data | `ie-table`, with one key row when one row matters most | Tables for content that has a shape |

### Aesthetic craftsmanship and session choreography

- Choreograph each session across diverse, expressive pattern families from `slide_patterns.html`: combine process icon flows (`ie-process-flow`), narrowing ladders with contrasting callout panels (`ie-ladder-layout`), baked green-card grids (`ie-bg-green-cards-right`, `ie-bg-green-cards-left`), dark editorial comparisons (`ie-compare ie-compare-dark`), log-and-callout layouts (`ie-log-layout`), brand-mark tables (`ie-table-brand-*`), device and screen mockups (`ie-device-slide`, `ie-screen-slide`), 50/50 activity panels (`ie-lr`), numbered objective grids (`ie-objectives-grid`), and interactive roadmaps or galleries (`ie-roadmap`, `ie-gallery`)
- Never repeat the same content layout pattern on more than two consecutive content slides unless they form a deliberate multi-part sequence, and alternate light, dark, and curated `ie-bg-*` image surfaces to pace the session visually
- Reject utilitarian fallbacks: never build a content slide as a bare `<ol>` or `<ul>` stack, a wall of text cards, or a plain table when a structural pattern in `slide_patterns.html` can express the relationship visually
- Match content cardinality and copy length to pattern geometry so containers look purposefully tailored rather than underfilled or clipped:
  - In `.ie-compare-list`, populate all 5 rows on both sides (or match the shared grid template) so no empty track sits at the bottom of the frame
  - In `.ie-process-flow`, keep `.ie-process-label` headings concise enough to stay on one line so every step description starts on the same horizontal baseline
  - In `.ie-roadmap`, keep the slide subtitle to one concise line so the stage hover highlight never touches wrapped header text
  - Keep `.ie-auto-fit` scale factors healthy (`0.85` or higher where possible, never below `0.75` without a documented reason) by tightening prose and shaping cards rather than relying on heavy shrink-to-fit scaling
- Anchor tool, product, and workflow slides with authentic visual elements: use local brand marks in `media/brands/`, Tabler thin icons (`media/icons/tabler/thin/` at `stroke-width="1.25"`), device frames (`ie-device-slide`, `ie-screen-slide`), and interactive triggers (`ie-image-modal-trigger`, `ie-roadmap`, `ie-gallery`) rather than describing interfaces in prose alone

### Vertical composition

Apply the vertical-space requirement in [Design Quality Bar](slide_rules.md#design-quality-bar) when designing a new slide or repairing an approved layout. A title anchored at the top does not require the body to cluster beneath it

1. Plan three zones before placing content: the header, the main body and the closing area. Keep the header on its canonical gridline and reserve the source and logo areas; give the main body the remaining usable height. When a takeaway is present, place it near the lower edge of its content frame with a clear gap above it, rather than immediately after a short body stack
2. Build the body around a meaningful visual structure that uses its height: a layered architecture, a sequence, a comparison, a worked example or an interface view. Balance upper, middle and lower visual weight. Do not rely on normal document flow to stack every block directly below the heading
3. Use container geometry and deliberate group spacing to distribute the content. Preserve reading order, close relationships and aligned peers; do not scatter isolated labels or make every gap equal by default. Keep the whole slide stack off vertical centring, because the title must retain its grid anchor
4. For a short reference table, assess whether a different approved pattern or a supporting example would communicate better across the available body area. Keep genuine reference data as a table when appropriate. Do not add blank rows, invent entries, stretch padding or override shared table styles to fill the slide; a needed shared-pattern change follows the normal approval rules
5. For live demos, allocate a real body area to the demo grid and balance the change and proof columns within it. Let panels use that area where useful, while keeping snippets and output readable and compact. A single command may need a meaningful artifact view or clearer outcome explanation within the approved pattern; oversized empty terminals, invented output and blank code lines do not solve the layout
6. Preserve negative space when it visibly supports focus, separation or an image. An unexplained lower half left empty by a short top stack is a composition problem. Do not solve it with extra prose, decorative filler, enlarged type outside the approved scale, animations or new reveals
7. Inspect the full-size screenshot from top to bottom: where does the main body end, where does the takeaway sit, and what purpose does the remaining lower space serve? Correct an unexplained imbalance within the approved scope and render again. Record the reason when retaining a deliberately sparse composition

### Visual vocabulary

- Navy top bar or filled number chip: standard step or item
- Lime border, lime top bar or lime-tinted card: the one key item, or a passing outcome
- Dashed border: deliberately separate, cross-cutting, or blocked and waiting for a person
- Faded dashed element: disposable or generated, not the source of truth
- Uppercase tracked label: a phase, a kicker or an axis end, never body text
- Icons: Tabler thin at stroke width 1.25; on light slides inside a lime-tinted circle, on dark slides recoloured to lime, alone or inside a lime outline circle
- Monospace chips: real file, folder, module or command names only

### Self-critique loop

1. Write the one message and the takeaway first; decide the structure from the table above
2. Build, run the browser QA, and open every screenshot at full size
3. Critique it as the professor would: Where does the eye land first? Is there an empty band or an unpopulated grid track? Do peer headings and descriptions share clean horizontal baselines? Is any text below 19 px or hard to read at a distance? Does the layout prove the takeaway? Does it look as good as or better than its neighbours?
4. For new designs and authorized layout repairs, improve and render again. For content maintenance, compare with the baseline and retain its composition when it already works. Record the improvement or preservation decision in the report

### Scoped CSS conventions for new layouts

- Scope every rule by slide id and prefix new classes with a short deck-local code, for example `s12x-` for Session 12
- Colours come from palette tokens; translucency uses `rgba()` of a palette colour, never a new hex value
- Prefer CSS grid with explicit columns and rows, so elements land on the gridlines and peer cards share edges
- A layout used on a second slide becomes a `template_improvements.md` candidate

## Icon consistency

Keep every icon in one visual rail, flow, or repeated icon family on the same local
Tabler variant and stroke width. The established standard is
`media/icons/tabler/thin/` with `stroke-width="1.25"`; do not mix thin and
standard-weight icons within one family

## Gridlines

Place every element on the canonical gridlines in `instructions/slide_rules.md`, section Grid, before judging a layout finished. Start a new layout from those lines; when the design needs a new line, align every element on the slide to it and reuse it across the family. A deliberate break carries `data-grid-exception="<reason>"` on the section.

## Choosing a layout, by communication need

Match the need on the left to the pattern on the right.

**Structure and sequence**

- Ordered sequence where each step narrows scope, plus one supporting rule beside it:
  narrowing ladder (`ie-ladder-layout`)
- Linear process of 4 to 6 steps, each with an icon: process icon flow (`ie-process-flow`)
- Short ordered checklist to be filled in live during class: numbered relay cards
  (`ie-relay-grid`)
- Ordered steps beside a supporting image: media split with steps (`ie-media-split`)
- Session agenda of 3 to 6 blocks, repeated between sections with one block active:
  stacked agenda (`ie-agenda-stack`)

**Sets and comparison**

- 4 to 6 learning objectives or outcomes as equal numbered cards: numbered objectives
  grid (`ie-objectives-grid`)
- One contained list that must not be confused with a second, related item: log with
  separate note (`ie-log-layout`)
- Simple two-column comparison with no strong sequence: two-column (`ie-two-col`)
- Four-part framework or taxonomy: four-card grid (`ie-card-grid`), or the baked
  background variants (`ie-bg-green-cards-right`, `ie-bg-green-cards-left`)
- Set of external resources or tools as clickable cards: link card grid (`ie-link-grid`)

**Evidence, reference, and artefacts**

- Reference table such as an assessment breakdown: data table (`ie-table`)
- Long attributed quotation with a portrait: quote with cutout portrait
  (`ie-quote-slide`)
- One short sourced claim beside a supporting chart or image: statement bar with image
  (`ie-statement-split`)
- One tool or product introduced with a screenshot: device explainer (`ie-device-slide`)
- A long artefact such as a prompt or config file shown verbatim: screen mockup
  (`ie-screen-slide`)
- Several images that each deserve full attention, one at a time: thumbnail gallery
  (`ie-gallery`)

**Activities and closings**

- Two-sided in-class activity over an image background: activity panels on a true 50/50
  slide (`ie-lr` with `ie-activity-panel`)
- One-line closing statement below any layout: emphasis band (`ie-band`), at most one
  per slide

**Comparison and orientation**

- Two options, states, or dimensions side by side: comparison (`ie-compare ie-compare-dark`)
- A course or programme on one page, with stages, gates, and milestones: roadmap
  (`ie-roadmap`)

**Interactive support**

- Brief optional definition or guiding question: context tooltip (`ie-tooltip`)
- Optional source-specific image revealed from one key takeaway: key-takeaway image modal (`ie-image-modal-trigger`, `ie-image-modal`)
- Tools, products, or brands compared side by side: table with brand marks (`ie-table-brand`)
- A file students must save: official title-side icon (`ie-title-with-download` and `ie-download-btn`), pattern-27; follow `instructions/slide_rules.md`, section Downloads
- The same slide shown twice in a session: slide alias (`data-slide-ref`)

## Type scale and logo variants

- Classes: tokens `--ie-title-size` (54 px), `--ie-title-size-compact` (44 px), `--ie-lead-size` (28 px), `--ie-lead-size-compact` (22 px); logo classes `ie-logo-tr` and `ie-logo-br` on the slide section
- Structure: a title rule reads a token instead of a literal size; the logo class moves the shared `.ie-logo`, so no slide-scoped logo rule is needed
- Use when: any content slide needs a title, lead, or a logo away from the default bottom-left corner
- Avoid when: the slide is a display, quote, or full-bleed pattern, which may keep a documented larger size

## Safe frame inset variants

`ie-scitech-reveal.css` defines the insets once, chosen with a modifier class on the `safe-frame` element:

| Variant | Class | Insets (top / right / bottom / left) | Use for |
| --- | --- | --- | --- |
| Default | none | 86 / 96 / 130 / 96 px | Normal content slides that keep the footer logo zone clear |
| Open | `safe-frame--open` | 88 / 96 / 96 / 96 px | Content slides with no footer logo zone that need the extra height |
| Dense | `safe-frame--dense` | 74 / 84 / 70 / 84 px | Tables, checklists, rubrics, agendas, and card grids that need the largest area |
| Full bleed | `safe-frame--full-bleed` | 0 px | Quote and full-canvas slides that position their own content |

A scoped inset rule is allowed only with a `Safe frame exception` comment. `scripts/check_deck.py` fails any other slide-scoped inset rule and any unknown `safe-frame--` class.

## Quotes and cards

- Quotes: one size on every quote slide. `source-quote` and `ie-quote-text` are 50 px light italic, `source-attribution` and `ie-quote-attribution` are 30 px and always start with `- `, and every emphasised phrase is a `<span class="ie-quote-emphasis">` (lime, bold 800). Only a quote over 40 words adds `source-quote--long` (30 px). Any other size needs a scoped rule with a `Display exception` comment. The portrait may grow, the quote text may not
- Cards on light slides: `ie-card-light` (white surface, hairline border, 7 px lime top bar, soft shadow, navy text) or `ie-card-light--side` for a wide callout with a lime left bar; solid navy cards belong on dark slides only
- Full-bleed media cards: use the shared media and overlay classes so the image and quote panel meet the card's inner left and right borders; repeated overlays share one explicit height
- Key table row: `ie-table-key-row` on one `tr` per table, plus `ie-table-key-row--bold` for a single short statement
- Agenda cards: use `ie-agenda-stack` on the `agenda-grid`; a slide-scoped `agenda-card` font size fails the static check

## Reusable patterns

Each pattern lives in `ie-scitech-reveal.css` under a matching comment header, with a
working example in `slide_patterns.html`. All are safe inside `safe-frame` and
`ie-auto-fit` unless noted.

### Full-bleed media cards

Classes: `ie-card--media-bleed`, `ie-card-media--full-bleed`,
`ie-card-overlay--full-width`, and `ie-card-grid--equal-overlays`

Structure: put `ie-card--media-bleed` on the card, wrap the image in
`ie-card-media--full-bleed`, and put the quote or short text panel in
`ie-card-overlay--full-width`. The shared CSS removes Reveal's inherited image and
blockquote constraints, so both layers span the card's inner left and right borders.
For a repeated row, add `ie-card-grid--equal-overlays` and set
`--ie-card-overlay-height` to the height needed by the longest overlay.

Use this when each card is a visual panel with a quote or short takeaway over the
image. Use `object-position` only when the source composition requires it. Do not
add JavaScript or fit-helper rules for this geometry, and do not let each overlay
choose its own automatic height in a repeated row.

### Stacked agenda

Classes: `ie-agenda-stack` (with `agenda-grid`), `agenda-card`, `agenda-number`, states
`is-active`, `is-complete`, `is-upcoming`

Structure: turns the default 5-column `agenda-grid` into full-width rows, each a number
chip beside a single heading. The active row fills lime, the others drop to 48 % opacity.

Use this for a session agenda of 3 to 6 blocks, repeated between sections so students
always know where they are. Do not use it for a list of content points, it is a
navigation device and loses meaning if reused for anything else.

### Thumbnail gallery

Classes: `ie-gallery`, `ie-gallery-frame`, `ie-gallery-layout`, `ie-gallery-stage`,
`ie-gallery-hero`, `ie-gallery-sidebar`, `ie-gallery-header`, `ie-gallery-title`,
`ie-gallery-meta`, `ie-gallery-count`, `ie-gallery-rail`, `ie-gallery-thumb`,
`ie-gallery-thumb-copy`, `ie-gallery-index`, `ie-gallery-thumb-title`

Structure: a fixed 410 px sidebar holding the title, a counter, and a vertical thumbnail
rail, beside a stage that shows one image at full height. Selecting a thumbnail swaps
the hero image; left and right arrow keys do the same.

Requires `ie-components.js`, which initialises every gallery automatically, so no
per-deck script is needed. Keep the markup hooks: `data-gallery` on the layout,
`data-gallery-hero` on the hero image, `data-current-count` on the counter, and
`data-src` plus `data-alt` on every thumb button. Several galleries can share a deck.

Use this when several images each deserve full attention and shrinking them into a grid
would make them unreadable. Do not use it for images that are only decorative, and do
not exceed about six thumbnails before the rail rows get too short to read.

### Numbered objectives grid

Classes: `ie-objectives-frame` (with `safe-frame`), `ie-objectives-lead`,
`ie-objectives-grid`, `ie-objective-card`, `ie-objective-number`, `ie-objective-key`

Structure: a three-column grid of equal numbered cards over a dark background, with an
optional lead line above. Cards use a fixed minimum row height so rows stay even.

Use this for learning objectives, outcomes, or any set of 4 to 6 parallel commitments.
Keep the cards grammatically parallel, and mark only the decisive phrase in each card
with `ie-objective-key`.

### Quote with cutout portrait

Classes: `ie-quote-slide`, `ie-quote-stage`, `ie-quote-copy`, `ie-quote-wrap-shape`,
`ie-quote-text`, `ie-quote-emphasis`, `ie-quote-attribution`, `ie-quote-portrait`

Structure: a full-bleed cutout portrait anchored to a corner, with the quotation flowing
around its silhouette via `shape-outside`, and the attribution in lime beneath.

Per slide you must set the portrait width and the matching `shape-outside` image on
`ie-quote-wrap-shape` with an inline style, because both depend on the specific cutout.
Without that, the text wraps around a plain rectangle instead of the silhouette.

Use this for a long, exact quotation that carries weight on its own. Keep the quotation
verbatim, mark only the load-bearing phrases with `ie-quote-emphasis` (lime, bold), start
the attribution with `- `, and show the attribution only. Keep the 50 px quote size, make
the portrait larger instead when the slide needs more presence. Never add a key takeaway, takeaway card, or visible source line to a
quote slide. Record the source reference in the approved source or audit record rather
than in speaker notes.

### Statement bar with image

Classes: `ie-statement-split` (with `ie-split` and `ie-split-left`), `ie-statement-bar`,
`ie-statement-source`, `ie-statement-image`

Structure: a solid navy bar filling the left third with one claim, and a full-height
image or chart filling the right two thirds, edge to edge with no inner margin.

Use this when a single visual is the evidence for a single sentence, for example a
research finding beside its chart. Keep the bar to one sentence, and put the citation in
`ie-statement-source` beneath it in small type.

### Data table

Classes: `ie-table`, `ie-table-compact`, `ie-table-numeric`, `ie-table-conditions`,
`ie-table-condition`, `ie-table-value`

Structure: a fixed-layout table with a navy header row and alternating lime body rows,
optionally followed by a centred row of highlighted conditions.

Always set column widths with a `<colgroup>` so the table does not reflow
unpredictably, and put `ie-table-numeric` on numeric columns to centre them. Use
`ie-table-value` only for genuinely critical figures, it renders red.

Every data or reference table uses `ie-table` so headers, typography, borders, and
alternating rows remain consistent. Use `ie-table-compact` only for tables with six or
more rows that need less vertical padding; it does not change the shared visual style.
Do not reproduce the table system in slide-scoped CSS.

When a table cell contains more than one independent statement or block item, prefix
each statement with a compact literal `- ` at the existing cell text edge. Avoid
browser-default list indentation, and keep category labels and single statements
unbulleted.

Use this for reference content students will read rather than scan, such as an
assessment breakdown. Do not shrink the type to fit more rows, split the table instead.

### Device explainer

Classes: `ie-device-slide`, `ie-device-layout`, `ie-device-copy`, `ie-device-label`,
`ie-device-laptop`, `ie-device-screen-link`, `ie-device-screen-image`, `ie-device-frame`

Structure: labelled copy on the left, and a screenshot seated inside `media/laptop.png`
on the right. The screen aperture is positioned in percentages measured against that
frame, so the screenshot stays aligned at any width.

Do not change the aperture percentages when swapping the screenshot. Wrap the screenshot
in an anchor when the tool has a public URL, and record the capture date and source URL
in the approved source or audit record, not in speaker notes.

Use this to introduce one tool at a time. Two labelled lines, what it is and why we use
it, are usually enough.

### Link card grid

Classes: `ie-link-slide`, `ie-link-note`, `ie-link-grid`, `ie-link-card`

Structure: a three-column grid of bordered cards over a dark background, each a link
with a lime heading and one line of purpose, above an optional eyebrow line stating the
selection rule.

Every card must be an `<a>` with `target="_blank"`, `rel="noopener noreferrer"`, and an
`aria-label` naming the destination. Verify every URL before use, and record the sources
in the approved source or audit record, not in speaker notes.

Use this for optional or conditional resources. State the rule for when to reach for
them in `ie-link-note`, so the grid does not read as a list of requirements.

### Process icon flow

Classes: `ie-process-slide`, `ie-process-flow`, `ie-process-number`, `ie-process-icon`,
`ie-process-label`, `ie-process-takeaway`, `ie-process-emphasis`

Structure: a row of numbered icons joined by lime arrows, with a closing line beneath a
rule. Arrows are generated automatically between items, and suppressed after the last.

Icons are local Tabler SVGs in `media/icons/tabler/thin/`, recoloured to lime by a CSS
filter so the source files stay untouched. See `instructions/slide_rules.md` and the
`slide-asset-sourcing` guidance before adding a new icon.

Use this for a genuinely linear process of 4 to 6 steps. Keep labels to one word where
possible. Do not use it for a cycle, the arrows imply a start and an end.

### Media split with steps

Classes: `ie-media-split` (with `ie-split` and `ie-split-left` or `ie-split-right`),
`ie-media-panel`, `ie-media-content`, `ie-step-stack`, `ie-step-line`, `ie-step-emphasis`,
`ie-step-takeaway`

Structure: a full-height image in a navy panel on one side, and a stack of short
lime-edged step lines on the other, closing with a centred takeaway. The logo moves to
the text side automatically.

Use this when an image sets the tone and a short sequence carries the content. Keep each
step to one line, and mark only the verb or the decisive noun with `ie-step-emphasis`.

### Activity panels on a true 50/50 slide

Classes: `ie-activity-lr` (with `ie-lr`), `ie-activity-panel` with `is-steps` or
`is-prompts`, `ie-activity-step`, `ie-activity-step-number`, `ie-activity-context`,
`ie-activity-pattern`, plus the existing `ie-lr-grid`, `ie-lr-panel`, `ie-lr-title-left`,
`ie-lr-footer`, `ie-lr-takeaway-shared`

Structure: the `ie-lr` grid owns the full canvas and the halves meet at x = 800 px. Each
half holds a translucent navy panel so text stays legible over an image background:
`is-steps` for numbered instructions with optional prompt boxes, `is-prompts` for a
heading, a pattern line, and a bulleted challenge list. A shared takeaway sits centred in
`ie-lr-footer`. The title stays in the left top band and the logo balances it at
top-right.

Use this for a two-sided in-class activity: what to do on the left, what to ask on the
right. Keep the structural halves padding-free and place auto-fit content inside
`ie-lr-panel`.

### Comparison, left versus right

Classes: `ie-compare` with `ie-compare-dark`, `ie-compare-title`, `ie-compare-grid`,
`ie-compare-col` with `is-a` or `is-b`, `ie-compare-head`, `ie-compare-tag`,
`ie-compare-list`, `ie-compare-row`, `ie-compare-num`, `ie-compare-txt`,
`ie-compare-label`, `ie-compare-desc`, `ie-compare-takeaway`, `ie-compare-accent`, plus
`ie-source-line`

Structure: a title band with the logo top right, two columns on a fixed five-row grid,
one takeaway spanning both halves, and a source line bottom left. `is-a` is the weaker,
cautionary, or current-state side with a muted rail; `is-b` is the preferred or
evidence-backed side with a lime rail.

Use this for any slide that compares two dimensions, categories, options, states, or a
two-sided activity (what to do on the left, what to ask on the right).
Five rows per side is the tuned default and four work unchanged; six or more need a
redesign. Set `style="--cmp-rows: 3"` on a list that has three rows. Use
`ie-compare-label--sentence` when a row holds a full phrase or a question, and an
optional `ie-compare-lead` line under the column head for one short pattern or rule. Do not wrap rows in `ie-activity-panel`, do not reuse `ie-lr`, do not add
fragments, animation, or column borders.

### Source line

Class: `ie-source-line`, with `is-wrap` for two lines

Structure: small attribution text bottom left, 44 px from the sides and 18 px from the
bottom, outside the 96 px content margin, with underlined links. Colour follows the
section background.

Use this for every footnote-style citation. Move the logo top right on the same slide.
Never use it on a quote slide.

### Progressive-focus roadmap

Classes: `ie-roadmap` on the section, generated children prefixed `ie-rm-`; data in a
`<script type="application/json" class="ie-roadmap-data">` block

Structure: a header with a phase legend, a numbered stage rail, one focus panel that
changes with the selected stage, a timeline with phase bands and milestone diamonds,
optional artifact chips, and a static print summary for PDF export. `ie-components.js`
builds all markup from the JSON and adds one Reveal fragment per stage plus a closing
state. Hover and keyboard focus preview a stage without committing; click and presenter
arrows commit through the fragments.

JSON keys: `title`, `subtitle`, `unit`, `total`, `iconBase`, `phases` (`id`, `short`,
`label`, `tone` of `green`, `navy`, or `grey`), `stages` (`name`, `from`, `to`, `phase`,
`output`, `icon`), `milestones` (`at`, `stage` or `stages`, `label`, `short`, `text`,
`icon`, `gate`), `overview`, `closing`, and `artifacts`. See pattern 25 in
`slide_patterns.html`.

Use this once near the start of a course to show the whole journey and its gates. Keep
stage names to two or three words and outputs to one line. Do not use it for a single
session agenda; use the stacked agenda instead.

### Screen mockup

Classes: `ie-screen-slide`, `ie-screen-copy`, `ie-screen-lead`, `ie-screen-figure`,
`ie-screen-image`, `ie-screen-opening`, `ie-screen-text`, `ie-screen-heading`

Structure: a narrow title block on the left and a monitor frame, `media/screen.png`,
filling the right, with the artefact rendered as monospace text inside the aperture.

Set the `ie-screen-text` font size per slide so the whole artefact fits without
scrolling. Mark section headings with `ie-screen-heading` for the lime accent. When
students need the raw text, wrap the frame in a download or copy anchor.

Use this to show a long artefact verbatim, such as a prompt or a configuration file. If
it cannot stay legible on one slide, split it across two rather than shrinking the type
below readability.

### Narrowing ladder with side panel

Classes: `ie-ladder-layout`, `ie-ladder`, `ie-ladder-step`, `ie-ladder-number`,
`ie-ladder-text`, `ie-ladder-tag`, `ie-ladder-panel`, `ie-ladder-panel-rule`

Structure: a two-column grid, roughly 1.66 to 1. The left column is an ordered list of
steps, each a numbered circle, a text block, and an optional tag, with progressive lime
tint reinforcing the narrowing. The right column is a navy panel for a safety gate, a
rule, or a short summary.

Use this when a slide teaches a sequence of decisions that get progressively narrower or
shorter in horizon, and one supporting rule needs weight without becoming another list
item. Do not use it for an unordered list of options.

### Log with separate note

Classes: `ie-log-layout`, `ie-log-container`, `ie-log-head`, `ie-log-list`,
`ie-log-index`, `ie-log-note`, `ie-log-note-chip`, `ie-log-note-warn`

Structure: one bordered container with a header strip holding a numbered list, beside a
dashed-border panel that reads as deliberately separate.

Use this to prevent one common error: treating a related document as part of the main
list. The dashed border does the teaching. Do not give the note a solid border or the
same background as the list, that removes the distinction the pattern exists to make.

### Numbered relay cards

Classes: `ie-relay-grid`, `ie-relay-card`, `ie-relay-number`, `ie-relay-question`,
`ie-relay-answer`

Structure: a four-column grid of cards, each with a numbered chip breaking the top
border, a kicker label, a question, and a dashed fill-in box. Chevron connectors sit
between cards and are hidden after the last one.

Use this for a short, ordered, fill-in-now checklist. Keep the dashed box empty on the
slide, it is a live prompt, not a place for sample text. Limit it to three or four cards.

### Emphasis band

Classes: `ie-band` (also `ie-takeaway`, `deck-takeaway-card`, and the pattern takeaway classes listed in
`instructions/slide_rules.md`, section Key Takeaway Strips)

Structure: a single-line block with a lime left edge and one of exactly two backgrounds. On a
light slide it is clear white at 40 % opacity with an 8 px edge. On a dark slide it is white at
10 % opacity with a 10 px edge. There is no solid variant, no tint, and no other colour.

Text is 24 px regular weight in every strip, never bold or larger (allowed 22 to 26 px). Use at most one per slide, after the main layout, to state the takeaway in one sentence.
Keep it clear of the IE logo and every other element, the browser test fails on any overlap.

### Key-takeaway image modal

Classes: `ie-image-modal-trigger`, `ie-image-modal`, `ie-image-modal-content`,
`ie-image-modal-img`, optional `ie-image-modal-link` and `ie-image-modal-trigger-icon`

Structure: one standard `ie-band` or `deck-takeaway-card` remains the only trigger. The
trigger shows the shared "CLICK FOR IMAGE" pill and opens an absolutely positioned dialog
inside the same slide with a dark blurred overlay and one centred local image. The dialog
stays outside the slide's layout flow. `ie-components.js` wires it; there is no
slide-local script. Example: `slide_patterns.html` pattern-30.

Use this when the image is optional context or evidence that students may inspect on
demand. Keep the visible takeaway meaningful without opening the image. Support click,
Enter, and Space on the trigger, then close on Escape, overlay or outside click, and
Reveal `slidechanged`. Do not make the whole slide clickable, use hover as the only
activation path, or hide required instructions inside the image.

### Table with brand marks

Classes: `ie-table-brand-cell`, `ie-table-brand`, `ie-table-brand-link`,
`ie-table-brand-name`, `ie-table-brand-note`, optional `--ie-table-brand-size`

Structure: a normal `ie-table` whose first column shows each tool's official mark above
its short name. The mark links to the official page; the name stays plain text. A generic
or default row, usually the `ie-table-key-row`, uses a Tabler icon with no link.

Use this when students must recognise tools, products, or vendors at a glance and may
want to open them. Keep marks local in `media/brands/` with the source and retrieval date
in an HTML comment, check every row against the vendor's own page, and add a source line.
Do not hotlink logos, do not restyle the marks per slide, and do not use the pattern for
fewer than three rows. Example: `slide_patterns.html` pattern-31.

### Context tooltip

Class and attributes: `ie-tooltip`, `tabindex="0"`, `data-tooltip`, and an `aria-label`
that combines the visible term with its definition

Structure: a semi-transparent white pop-up with 14 px rounded corners, subtle blur and
shadow, and a 180 ms entrance above the trigger. It opens on hover, tap, or keyboard
focus without JavaScript

Use this for a brief optional definition or a simple question that helps students
interpret a term in context. Keep the pop-up to one short sentence, preferably 12 words
or fewer. Do not hide instructions, evidence, or meaning required to understand the slide

### Live demo slide

Classes: `ie-code`, `ie-code-tag`, `ie-code-file`, `ie-code-lines`, states `is-before`, `is-after`, `is-run`, `is-grow`; layout `ie-demo-lead`, `ie-demo-grid` (`--wide-left`, `--wide-right`), `ie-demo-col`, `ie-demo-terminal`, `ie-demo-legend`, `ie-demo-band`

Structure: a dark dense slide; on the left the Before code (dashed, faded) above the After code (lime top bar); on the right the Run it terminal with the real commands and output; one takeaway strip. Gallery pattern-33.

Use this as the default whenever a slide shows code, a configuration change or a command: it proves the idea by running it. Put one after the explanation slides of each topic, keep the family identical across a block, and keep the runnable demo and its script in the course exercises folder. The rules live in `instructions/slide_rules.md`, section Code And Live Demo Slides.

## Logo behaviour over image backgrounds

The dark image variants lift their direct children above the legibility overlay with a
zero-specificity rule, so the logo and absolutely positioned frames keep their own
placement. No extra utility class is needed.

## Extending this playbook

When a task produces a genuinely new, reusable layout pattern:

1. Build and validate it first as CSS scoped to the slide id, following
   `instructions/slide_rules.md`
2. Confirm it passes `scripts/check_browser_qa.py` at 1600 x 900 with no spill or
   clipped text
3. Record it in `template_improvements.md` as a candidate
4. Only after the professor approves the pattern for reuse, promote the CSS into
   `ie-scitech-reveal.css` under the `ie-` prefix with a comment block stating its
   purpose, and delete the slide-scoped copy in the same change
5. Add one numbered example to `slide_patterns.html` with generic placeholder wording and
   local placeholder media, never course content
6. Add one entry to this file with the same three parts: classes, structure, and when to
   use or avoid it

A pattern must exist in exactly one place in CSS. Never keep an inline duplicate of a
shared pattern.
