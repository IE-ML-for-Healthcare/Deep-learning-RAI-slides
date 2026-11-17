# IE Slide Examples

Copy-paste HTML snippets for the core slide types and interactive techniques. Rules live in `instructions/slide_rules.md`, pattern choice in `instructions/layout_playbook.md`, and the rendered versions of every layout in `slide_patterns.html`. Replace example ids with `session-NN-topic` ids.

## Title Slide

```html
<section class="ie-slide ie-bg-light-circles ie-title" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="ie-title-block ie-auto-fit">
    <h1>Presentation title</h1>
    <p class="subtitle">Short practical session subtitle</p>
  </div>
</section>
```

## Standard Content Slide

```html
<section class="ie-slide ie-light" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="safe-frame">
    <div class="ie-auto-fit">
      <h2>Core idea</h2>
      <p>Explain one important concept clearly</p>
    </div>
  </div>
</section>
```

## Two-Column Slide

Uses `ie-two-col` for two content columns inside a normal slide frame. Works on light or dark variants.

```html
<section class="ie-slide ie-light" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="safe-frame">
    <div class="ie-auto-fit">
      <h2>Two perspectives</h2>
      <div class="ie-two-col">
        <div>
          <h3>First lens</h3>
          <p>Use concise evidence or framing</p>
        </div>
        <div>
          <h3>Second lens</h3>
          <p>Use concise contrast or action</p>
        </div>
      </div>
    </div>
  </div>
</section>
```

## LHS / RHS Slide

Use `ie-lr` for a true 50/50 slide. The structural rules are in `instructions/slide_rules.md`, section Layout; `ie-bg-green-dark-left ie-lr` is the standard composition.

Every takeaway example below renders as a standard strip at 24 px; do not restyle it in slide CSS (see `instructions/slide_rules.md`, section Key Takeaway Strips).

Shared takeaway example:

```html
<section class="ie-slide ie-bg-green-dark-left ie-lr" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <header class="ie-lr-title-left">
    <h2>Compare two approaches</h2>
  </header>
  <div class="ie-lr-grid">
    <div class="ie-lr-left">
      <div class="ie-lr-panel">
        <div class="ie-auto-fit">
          <h3>Left-hand side</h3>
          <p>Place the first perspective in the first structural half</p>
        </div>
      </div>
    </div>
    <div class="ie-lr-right">
      <div class="ie-lr-panel">
        <div class="ie-auto-fit">
          <h3>Right-hand side</h3>
          <p>Place the second perspective in the second structural half</p>
        </div>
      </div>
    </div>
  </div>
  <footer class="ie-lr-footer">
    <p class="ie-lr-takeaway-shared">State one shared takeaway across both halves</p>
  </footer>
</section>
```

Per-side takeaway example:

```html
<section class="ie-slide ie-bg-green-dark-left ie-lr" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <header class="ie-lr-title-left">
    <h2>Compare two choices</h2>
  </header>
  <div class="ie-lr-grid">
    <div class="ie-lr-left">
      <div class="ie-lr-panel">
        <div class="ie-auto-fit">
          <h3>First choice</h3>
          <p>Explain the first option inside its content-safe panel</p>
        </div>
      </div>
    </div>
    <div class="ie-lr-right">
      <div class="ie-lr-panel">
        <div class="ie-auto-fit">
          <h3>Second choice</h3>
          <p>Explain the second option inside its content-safe panel</p>
        </div>
      </div>
    </div>
  </div>
  <footer class="ie-lr-footer">
    <p class="ie-lr-takeaway-left">Act on the first takeaway</p>
    <p class="ie-lr-takeaway-right">Act on the second takeaway</p>
  </footer>
</section>
```

## Comparison, left versus right

Use `ie-compare ie-compare-dark`. Copy pattern 24 from `slide_patterns.html` for the full five-row version; the skeleton is:

```html
<section id="session-03-option-compare" class="ie-slide ie-compare ie-compare-dark" data-transition="fade"
  aria-label="Option A compared with option B">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <header class="ie-compare-title"><h2>Compare two options</h2></header>
  <div class="ie-compare-grid">
    <div class="ie-compare-col is-a">
      <div class="ie-compare-head"><h3>Option A</h3><span class="ie-compare-tag">Current state</span></div>
      <ul class="ie-compare-list">
        <li class="ie-compare-row"><span class="ie-compare-num">1</span>
          <div class="ie-compare-txt">
            <h4 class="ie-compare-label">First dimension</h4>
            <p class="ie-compare-desc">How option A behaves on it</p>
          </div>
        </li>
        <!-- rows 2 to 5 -->
      </ul>
    </div>
    <div class="ie-compare-col is-b">
      <div class="ie-compare-head"><h3>Option B</h3><span class="ie-compare-tag">Preferred</span></div>
      <ul class="ie-compare-list">
        <!-- the same five rows, in the same order -->
      </ul>
    </div>
  </div>
  <footer class="ie-compare-takeaway">
    <p>One shared takeaway with <span class="ie-compare-accent">the decisive words</span></p>
  </footer>
  <p class="ie-source-line">Sources: <a href="https://example.org/" target="_blank" rel="noopener noreferrer">Author (year)</a></p>
</section>
```

## Card Grid Slide

Uses `ie-cards` on the section and `ie-card-grid` / `ie-card` / `ie-card-content` for the 2x2 grid. Valid card fills: `ie-card-lime`, `ie-card-white`, `ie-card-offwhite`, `ie-card-dark`.

```html
<section class="ie-slide ie-dark ie-cards" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="ie-card-grid">
    <article class="ie-card ie-card-lime">
      <div class="ie-card-content ie-auto-fit">
        <h3>Step one</h3>
        <p>One point per card</p>
      </div>
    </article>
    <article class="ie-card ie-card-white">
      <div class="ie-card-content ie-auto-fit">
        <h3>Step two</h3>
        <p>White cards contrast well on dark backgrounds</p>
      </div>
    </article>
    <article class="ie-card ie-card-offwhite">
      <div class="ie-card-content ie-auto-fit">
        <h3>Step three</h3>
        <p>Off-white adds variety without breaking the palette</p>
      </div>
    </article>
    <article class="ie-card ie-card-dark">
      <div class="ie-card-content ie-auto-fit">
        <h3>Step four</h3>
        <p>Use dark cards sparingly to anchor the composition</p>
      </div>
    </article>
  </div>
</section>
```

## Full-Bleed Media Card Slide

Use the shared media-card classes when an image must fill a card and a quote or short
text panel must run side to side across the card. Add
`ie-card-grid--equal-overlays` and set `--ie-card-overlay-height` when repeated
overlays need one height. The geometry belongs to HTML and CSS, not JavaScript.

```html
<section class="ie-slide ie-light ie-cards" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="ie-card-grid ie-card-grid--equal-overlays" style="--ie-card-overlay-height: 152px">
    <article class="ie-card ie-card-light ie-card--media-bleed">
      <div class="ie-card-media--full-bleed">
        <img src="media/example.jpg" alt="Concise description of the image">
      </div>
      <blockquote class="ie-card-overlay--full-width">“Short sourced quote or takeaway”</blockquote>
    </article>
  </div>
</section>
```

The image must use the full inner card width and height with no inherited max-size or
horizontal margin constraint. The overlay must share the same inner left and right
edges. Use a measured height that fits the longest copy when the row contains several
quote cards.

## Four-Card Background Slide

These examples rely on shared CSS in `ie-scitech-reveal.css`. Do not add CSS in the deck for this component unless the layout is truly deck-specific.

Image right variant:

```html
<section class="ie-slide ie-bg-green-cards-right" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="four-card-layer">
    <article class="four-card">
      <h3 class="four-card-title">Define</h3>
      <p class="four-card-subtitle">Name the concept</p>
      <p class="four-card-body">State what the idea means in practical terms</p>
    </article>
    <article class="four-card">
      <h3 class="four-card-title">Compare</h3>
      <p class="four-card-subtitle">Show the contrast</p>
      <p class="four-card-body">Connect the idea to a choice or tradeoff</p>
    </article>
    <article class="four-card">
      <h3 class="four-card-title">Practice</h3>
      <p class="four-card-subtitle">Try one move</p>
      <p class="four-card-body">Use a short task to make the concept visible</p>
    </article>
    <article class="four-card four-card-dark">
      <h3 class="four-card-title">Reflect</h3>
      <p class="four-card-subtitle">Extract the lesson</p>
      <p class="four-card-body">Capture what changed and what comes next</p>
    </article>
  </div>
</section>
```

Do not add extra card backgrounds on top of these baked panels. Keep text overlays aligned to the visible card areas.
For `ie-bg-green-cards-right`, the baked card panels are on the left and the logo sits on the lower-right side.

Image left variant:

```html
<section class="ie-slide ie-bg-green-cards-left" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="four-card-layer">
    <article class="four-card">
      <h3 class="four-card-title">Map</h3>
      <p class="four-card-subtitle">List the choices</p>
      <p class="four-card-body">Use this card for the first part of a reusable framework</p>
    </article>
    <article class="four-card">
      <h3 class="four-card-title">Compare</h3>
      <p class="four-card-subtitle">Show the tradeoff</p>
      <p class="four-card-body">Keep navy text on white and lime baked card areas</p>
    </article>
    <article class="four-card">
      <h3 class="four-card-title">Apply</h3>
      <p class="four-card-subtitle">Make it concrete</p>
      <p class="four-card-body">Connect the category to a practical student action</p>
    </article>
    <article class="four-card four-card-dark">
      <h3 class="four-card-title">Reflect</h3>
      <p class="four-card-subtitle">Name the insight</p>
      <p class="four-card-body">Use the dark card for the strongest takeaway</p>
    </article>
  </div>
</section>
```

For `ie-bg-green-cards-left`, the baked card panels are on the right and the logo sits on the lower-left side.

## Table Slide

```html
<section class="ie-slide ie-light" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="safe-frame">
    <div class="ie-auto-fit">
      <h2>Compare options</h2>
      <table class="ie-table">
        <colgroup>
          <col style="width: 22%">
          <col style="width: 39%">
          <col style="width: 39%">
        </colgroup>
        <thead>
          <tr><th scope="col">Option</th><th scope="col">Use when</th><th scope="col">Watch for</th></tr>
        </thead>
        <tbody>
          <tr><td>A</td><td>Need speed</td><td>Lower precision</td></tr>
          <tr><td>B</td><td>Need confidence</td><td>More setup</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>
```

## Activity Instruction Slide

```html
<section class="ie-slide ie-bg-light-students" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="ie-content ie-auto-fit">
    <h2>Activity brief</h2>
    <p>Work in pairs for 8 minutes and produce one clear output</p>
  </div>
</section>
```

## Image-Only Slide

```html
<section class="ie-slide ie-bg-dark-abstract" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="ie-content ie-auto-fit">
    <h2>Visual prompt</h2>
  </div>
</section>
```

## Final Takeaway Slide

```html
<section class="ie-slide ie-bg-dark-science" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="closing-frame">
    <div class="ie-auto-fit">
      <div class="takeaway-block">
        <h2>Key takeaway</h2>
        <p>State the one idea students should remember</p>
      </div>
    </div>
  </div>
</section>
```

For photo-background takeaway slides, constrain text width so it stays in the non-photo area. A safe starting point is `left: 96px`, `top: 150px`, `width: 760px`, and `bottom: 130px`.

## Resource Slide

```html
<section class="ie-slide ie-light" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="safe-frame">
    <div class="ie-auto-fit">
      <h2>Resources</h2>
      <ul>
        <li>Primary reading</li>
        <li>Practice file</li>
        <li>Next step</li>
      </ul>
    </div>
  </div>
</section>
```

## Speaker Notes

Only when the Course Profile allows them (`"speakerNotes": "allowed"` in `deck.config.json`). Press S to open the presenter view. Never put required citations or facilitation records only in notes.

```html
<section id="session-01-core-idea" class="ie-slide ie-light" data-transition="fade">
  <!-- logo and content blocks -->
  <aside class="notes">Timing, talking points, and transitions for the presenter</aside>
</section>
```

## Live Demo Slide

The default for any slide that shows code, a configuration file or terminal output (gallery pattern-33, rules in `instructions/slide_rules.md`, section Code And Live Demo Slides). Generate each figure with `python scripts/code_figure.py <file> --lang py|yaml|ini|env|term|plain --caption <name> --tag Before|After|"Run it" --state before|after|run [--grow]`, then paste it into the columns below.

```html
<section id="demo-example" class="ie-slide ie-dark ie-logo-tr" data-transition="fade">
  <div class="ie-logo"><img src="logos/ie-scitech-horizontal-dark-accent.svg" alt="IE University School of Science and Technology"></div>
  <div class="safe-frame safe-frame--dense"><div class="ie-auto-fit">
    <h2>Demo: fail fast on bad data</h2>
    <p class="ie-demo-lead">Run it, then make <code>validate</code> raise instead of fix</p>
    <div class="ie-demo-grid ie-demo-grid--wide-left">
      <div class="ie-demo-col">
        <figure class="ie-code is-before" aria-label="Before: src/validate.py"><figcaption><span class="ie-code-tag">Before</span><span class="ie-code-file">src/validate.py</span></figcaption><pre class="ie-code-lines">...</pre></figure>
        <figure class="ie-code is-after is-grow" aria-label="After: src/validate.py"><figcaption><span class="ie-code-tag">After</span><span class="ie-code-file">src/validate.py</span></figcaption><pre class="ie-code-lines">...</pre></figure>
      </div>
      <div class="ie-demo-col">
        <figure class="ie-code is-run is-grow" aria-label="Run it: terminal"><figcaption><span class="ie-code-tag">Run it</span><span class="ie-code-file">terminal</span></figcaption><pre class="ie-code-lines"><span class="p">$</span> <span class="cmd">python -m src.main</span>
<span class="o">ValueError: 1 row(s) have a negative usage_hours</span></pre></figure>
      </div>
    </div>
    <p class="ie-band ie-demo-band">One closing line that the run on the right proves</p>
  </div></div>
</section>
```

Highlight spans inside `ie-code-lines`: `.k` keyword or key, `.s` string or value, `.c` comment, `.p` prompt, `.cmd` command, `.o` output, `.e` emphasised output.

## Code Slide

Legacy only: keep existing highlight.js blocks, but build every new code slide as a Live Demo Slide or an `ie-code` figure. The Highlight plugin stays loaded for old slides.

The Highlight plugin is loaded by default. Use `data-trim` to strip indentation and `data-line-numbers` for stepped highlighting, for example `data-line-numbers="1-2|4"` to walk through lines across fragments.

```html
<section class="ie-slide ie-dark" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="safe-frame">
    <div class="ie-auto-fit">
      <h2>Code example</h2>
      <pre><code class="language-python" data-trim data-line-numbers>
        def greet(name):
            return f"Hello, {name}"
      </code></pre>
    </div>
  </div>
</section>
```

## Math Slide

The Math plugin (KaTeX) is loaded by default. Use `\(...\)` for inline math and `\[...\]` for display math.

```html
<section class="ie-slide ie-light" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="safe-frame">
    <div class="ie-auto-fit">
      <h2>The model</h2>
      <p>\[ \hat{y} = \beta_0 + \beta_1 x + \varepsilon \]</p>
    </div>
  </div>
</section>
```

## D3 Chart Slide

D3 is the default visualization library for this template. Load it from CDN only in decks that use charts, draw into a fixed-size SVG so the fit helper and Reveal scaling stay predictable, and keep colors on the IE palette.

Load D3 before `ie-reveal-fit.js`:

```html
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0"></script>
```

Slide markup:

```html
<section class="ie-slide ie-dark" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-dark-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="safe-frame">
    <div class="ie-auto-fit">
      <div class="template-header">
        <h2>Chart title</h2>
      </div>
      <svg id="chart-adoption" width="1300" height="480" role="img" aria-label="Bar chart of tool adoption by year"></svg>
    </div>
  </div>
</section>
```

Draw after Reveal initializes. Fixed SVG dimensions mean the chart renders correctly even while the slide is hidden:

```html
<script>
  function drawCharts() {
    var data = [
      { label: "2022", value: 18 },
      { label: "2023", value: 41 },
      { label: "2024", value: 67 }
    ];
    var svg = d3.select("#chart-adoption");
    if (svg.empty()) return;
    var w = +svg.attr("width"), h = +svg.attr("height"), pad = 48;
    var x = d3.scaleBand().domain(data.map(d => d.label)).range([pad, w - pad]).padding(0.25);
    var y = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).nice().range([h - pad, pad]);
    svg.selectAll("rect").data(data).join("rect")
      .attr("x", d => x(d.label)).attr("y", d => y(d.value))
      .attr("width", x.bandwidth()).attr("height", d => y(0) - y(d.value))
      .attr("fill", "#c9ff8a");
    svg.append("g").attr("transform", "translate(0," + (h - pad) + ")")
      .call(d3.axisBottom(x)).selectAll("text")
      .attr("fill", "#ffffff").style("font-size", "18px").style("font-family", "Montserrat, sans-serif");
  }

  Reveal.initialize({ /* standard options */ }).then(function () {
    if (window.IERevealFit) window.IERevealFit.fitAll();
    drawCharts();
  });
</script>
```

D3 chart rules:

- Use the IE palette: lime `#c9ff8a` for the primary series, navy `#000024` on light slides, white on dark slides
- Keep axis labels and legends at 18 px or larger in Montserrat
- One chart per slide with one clear message in the title
- Prefer bar, line, and dot charts over exotic chart types for teaching decks
- Keep the D3 code scoped to the deck, never in `ie-reveal-fit.js` or `ie-scitech-reveal.css`

## Mermaid Diagram Slide

Use Mermaid for flowcharts, sequence diagrams, and process maps. Reveal hides non-current slides, so render diagrams on `ready` and `slidechanged` rather than on page load.

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>
```

Slide markup:

```html
<section class="ie-slide ie-light" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <div class="safe-frame">
    <div class="ie-auto-fit">
      <h2>Process flow</h2>
      <pre class="mermaid">
        flowchart LR
          A[Plan] --> B[Build] --> C[Review] --> D[Publish]
      </pre>
    </div>
  </div>
</section>
```

Render hook, added after `Reveal.initialize`:

```html
<script>
  mermaid.initialize({ startOnLoad: false, theme: "neutral" });
  function renderVisibleDiagrams() {
    mermaid.run({ querySelector: "section.present .mermaid" });
  }
  Reveal.on("ready", renderVisibleDiagrams);
  Reveal.on("slidechanged", renderVisibleDiagrams);
</script>
```


## Key-Takeaway Image Modal

Use this only for optional, source-specific visual context. The takeaway strip is the
only trigger. `ie-image-modal-trigger` adds the "CLICK FOR IMAGE" pill on the strip, and
`ie-components.js` wires the behaviour, so the slide needs no script of its own.

```html
<section id="topic-slide" class="ie-slide ie-dark" data-transition="fade">
  <!-- normal slide content -->
  <p class="ie-band ie-image-modal-trigger" role="button" tabindex="0"
    aria-controls="topic-slide-image-modal" aria-label="Open the source image">
    <img class="ie-image-modal-trigger-icon" src="media/icons/tabler/thin/eye.svg" alt="" aria-hidden="true">
    State the takeaway without requiring the image
  </p>
  <div id="topic-slide-image-modal" class="ie-image-modal" role="dialog"
    aria-modal="true" aria-label="Source image" aria-hidden="true">
    <div class="ie-image-modal-content">
      <!-- optional: wrap the image in <a class="ie-image-modal-link" href="..."> -->
      <img src="media/topic/source-image.jpg" alt="Concise description of the image"
        class="ie-image-modal-img">
    </div>
  </div>
</section>
```

Behaviour: opens on click, Enter, and Space; closes on Escape, overlay or outside click,
and `slidechanged`; a click on `ie-image-modal-link` follows the link. The trigger icon is
optional, the pill is not. Do not attach listeners to the section, the safe frame, or the
whole slide. The modal is hidden in print; validate both closed and open screenshots at
1600 x 900.

## Table With Brand Marks

Use when a table compares named tools, products, or brands. The mark links to the
official page; the name stays plain text below it.

```html
<table class="ie-table" aria-label="Comparison of tools">
  <thead><tr><th>Tool</th><th>What it is</th><th>Licence or cost</th><th>Best fit</th></tr></thead>
  <tbody>
    <!-- Official marks retrieved <date> from <source pages> -->
    <tr>
      <td class="ie-table-brand-cell"><span class="ie-table-brand">
        <a class="ie-table-brand-link" href="https://example.org/" target="_blank"
          rel="noopener noreferrer" aria-label="Open the Example homepage"><img src="media/brands/example.png" alt=""></a>
        <span class="ie-table-brand-name">Example</span>
      </span></td>
      <td>What it is</td><td>Licence</td><td>Best fit</td>
    </tr>
    <tr class="ie-table-key-row">
      <td class="ie-table-brand-cell"><span class="ie-table-brand">
        <img src="media/icons/tabler/markdown.svg" alt="">
        <span class="ie-table-brand-name">Course default</span>
        <span class="ie-table-brand-note">+ any agent</span>
      </span></td>
      <td>...</td><td>...</td><td>...</td>
    </tr>
  </tbody>
</table>
```

## Download Control

Use the official title-side icon from pattern-27. Choose `ie-download-btn--dark` only for the actual dark surface behind it; omit that modifier on a light surface. The shared stylesheet owns its geometry and interaction states

```html
<h2 class="ie-title-with-download">Your heading
  <a class="ie-download-btn ie-download-btn--dark" download="prompt-topic.md"
     data-download-source="media/prompts/prompt-topic.md"
     href="data:text/markdown;charset=utf-8;base64,"
     aria-label="Download prompt-topic.md" title="Download prompt-topic.md">
    <img class="ie-download-icon" src="media/icons/tabler/download.svg" alt="">
  </a>
</h2>
```

The empty `href` above is a scaffold. Generate its payload with `python scripts/sync_downloads.py`, then run the required checks. The canonical visual and functional requirements, including approved legacy exceptions, are in `instructions/slide_rules.md`, section Downloads

## Slide Alias

```html
<!-- canonical slide, edited once -->
<section id="session-02-agenda" class="ie-slide ie-dark" data-transition="fade">...</section>
<!-- later in the deck: an independent slide with the same content -->
<section id="session-02-agenda-return" data-slide-ref="session-02-agenda"></section>
```

## Roadmap Slide

Copy pattern 25 from `slide_patterns.html` and edit only the JSON. `ie-components.js` builds the markup, fragments, and print summary.

```html
<section id="session-01-course-roadmap" class="ie-slide ie-light ie-roadmap" data-transition="fade">
  <div class="ie-logo">
    <img src="logos/ie-scitech-horizontal-light-accent.svg" alt="IE University School of Science and Technology">
  </div>
  <script type="application/json" class="ie-roadmap-data">
  { "title": "The course on one page", "unit": "Session", "total": 20,
    "phases": [{ "id": "p1", "short": "Phase 1", "label": "Phase 1, Sessions 1 to 10", "tone": "green" }],
    "stages": [{ "name": "Discover", "from": 1, "to": 10, "phase": "p1", "output": "Framed problem", "icon": "search.svg" }] }
  </script>
</section>
```

## Future Pattern Candidates

Not yet built in this template. Recorded here so the design intent and a known bug are not lost before someone builds them.

### Reusable accordion and lightbox components

A course repository built a checklist accordion (`<details>`/`<summary>`) and an image zoom lightbox with inline JavaScript tied to deck-specific class names. Generalize both into data-attribute-driven components, for example `data-ie-component="accordion"` and `data-ie-component="lightbox"`, so future decks do not hardcode deck-specific selectors in inline scripts.

When building the accordion, design around this bug from the start: a real or simulated mouse click fires `mouseenter` before `click`. If a hover listener opens the panel and a click listener toggles it based on the panel's current open state, the click handler reads a state the hover listener already changed, and immediately closes what the click just opened. Fix: give the click handler its own independent flag for open and closed intent, separate from whatever hover or focus previewing sets, for example a `dataset.openedByClick` value written only by the click handler.
