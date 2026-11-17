/* IE SciTech Reveal.js interactive components - v1
 *
 * Generic, data-driven initialisers for the interactive patterns in
 * slide_patterns.html. Load after reveal.js and before your inline script:
 *
 *   IESlideAliases.resolve();   // optional, slide-aliases.js
 *   IEComponents.prepare();     // BEFORE Reveal.initialize: builds markup and fragments
 *   Reveal.initialize({...}).then(function () {
 *     IEComponents.init();      // AFTER Reveal is ready: wires events
 *     IERevealFit.fitAll();
 *   });
 *
 * Components
 *   Thumbnail gallery   [data-gallery] with [data-gallery-hero], optional
 *                       [data-current-count], and .ie-gallery-thumb buttons
 *                       carrying data-src and data-alt
 *   Roadmap             section.ie-roadmap containing
 *                       <script type="application/json" class="ie-roadmap-data">
 *   Group picker         .s-picker button reading a roster embedded as
 *                        <script type="application/json" id="ie-group-roster">.
 *                        See instructions/group_picker.md and
 *                        scripts/sync_group_roster.py.
 *   Image modal          .ie-image-modal-trigger on one key takeaway strip,
 *                        aria-controls="<id>" naming an .ie-image-modal in the
 *                        same section (or the section's only .ie-image-modal).
 *                        Opens on click, Enter, Space; closes on Escape,
 *                        overlay or outside click, and slidechanged. Clicks on
 *                        .ie-image-modal-link follow the link instead.
 *
 * Every component is idempotent, scoped to its own slide, and safe when absent.
 * Do not put deck-specific content or selectors in this file.
 */
(function (window, document) {
  "use strict";

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function icon(base, name, className) {
    var img = el("img", className || "");
    img.src = (base || "") + name;
    img.alt = "";
    return img;
  }

  function reportError(message, section) {
    console.error("[IE Components] " + message + (section && section.id ? " (#" + section.id + ")" : ""));
  }

  /* ─── Thumbnail gallery ──────────────────────────────────────────── */

  function initGallery(gallery, reveal) {
    if (gallery.dataset.galleryReady === "true") return;
    var hero = gallery.querySelector("[data-gallery-hero]");
    var thumbs = Array.prototype.slice.call(gallery.querySelectorAll(".ie-gallery-thumb"));
    var count = gallery.querySelector("[data-current-count]");
    if (!hero || !thumbs.length) {
      reportError("Gallery needs [data-gallery-hero] and at least one .ie-gallery-thumb", gallery.closest("section"));
      return;
    }
    var activeIndex = Math.max(0, thumbs.findIndex(function (thumb) {
      return thumb.getAttribute("aria-pressed") === "true";
    }));

    function select(index) {
      activeIndex = (index + thumbs.length) % thumbs.length;
      var selected = thumbs[activeIndex];
      hero.style.opacity = "0";
      window.setTimeout(function () {
        hero.src = selected.dataset.src;
        hero.alt = selected.dataset.alt || "";
        hero.style.opacity = "1";
      }, 120);
      thumbs.forEach(function (thumb, thumbIndex) {
        thumb.setAttribute("aria-pressed", String(thumbIndex === activeIndex));
      });
      if (count) count.textContent = String(activeIndex + 1).padStart(2, "0");
    }

    thumbs.forEach(function (thumb, index) {
      thumb.addEventListener("click", function () { select(index); });
    });

    document.addEventListener("keydown", function (event) {
      if (!reveal || typeof reveal.getCurrentSlide !== "function") return;
      var current = reveal.getCurrentSlide();
      if (!current || !current.contains(gallery)) return;
      if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
      event.preventDefault();
      event.stopImmediatePropagation();
      select(activeIndex + (event.key === "ArrowRight" ? 1 : -1));
    }, true);

    gallery.dataset.galleryReady = "true";
  }

  /* ─── Roadmap ────────────────────────────────────────────────────── */

  var TONES = { green: true, navy: true, grey: true };

  function readRoadmapConfig(section) {
    var script = section.querySelector("script.ie-roadmap-data");
    if (!script) {
      reportError("Roadmap slide has no script.ie-roadmap-data block", section);
      return null;
    }
    var config;
    try {
      config = JSON.parse(script.textContent);
    } catch (error) {
      reportError("Roadmap JSON is invalid: " + error.message, section);
      return null;
    }
    var problems = [];
    if (!config.total || config.total < 1) problems.push("total must be a positive number");
    if (!Array.isArray(config.stages) || !config.stages.length) problems.push("stages must be a non-empty array");
    if (!Array.isArray(config.phases) || !config.phases.length) problems.push("phases must be a non-empty array");
    var phaseIds = {};
    (config.phases || []).forEach(function (phase) {
      phaseIds[phase.id] = phase;
      if (!TONES[phase.tone]) problems.push("phase " + phase.id + " tone must be green, navy, or grey");
    });
    (config.stages || []).forEach(function (stage, index) {
      if (!phaseIds[stage.phase]) problems.push("stage " + (index + 1) + " references unknown phase " + stage.phase);
      if (!(stage.from >= 1 && stage.to >= stage.from && stage.to <= config.total)) {
        problems.push("stage " + (index + 1) + " has an invalid from/to range");
      }
    });
    (config.milestones || []).forEach(function (milestone, index) {
      var stages = milestone.stages || (milestone.stage ? [milestone.stage] : []);
      if (!stages.length) problems.push("milestone " + (index + 1) + " needs stage or stages");
      milestone.stages = stages;
    });
    if (problems.length) {
      reportError("Roadmap configuration errors: " + problems.join("; "), section);
      return null;
    }
    config.unit = config.unit || "Session";
    config.iconBase = config.iconBase || "media/icons/tabler/";
    config.milestones = config.milestones || [];
    config.stages.forEach(function (stage, index) {
      stage.n = index + 1;
      stage.tone = phaseIds[stage.phase].tone;
      stage.range = stage.from === stage.to
        ? config.unit + " " + stage.from
        : config.unit + "s " + stage.from + " to " + stage.to;
    });
    config.phaseById = phaseIds;
    return config;
  }

  function sideList(config, items) {
    var list = el("ul", "ie-rm-side-list");
    items.forEach(function (item) {
      var li = el("li");
      li.appendChild(icon(config.iconBase, item.icon || "flag.svg"));
      var text = el("span");
      text.appendChild(el("span", "ie-rm-side-session", item.label));
      text.appendChild(document.createTextNode(item.text));
      li.appendChild(text);
      list.appendChild(li);
    });
    return list;
  }

  function buildRoadmap(section, config) {
    var stageCount = config.stages.length;
    section.style.setProperty("--ie-rm-count", String(stageCount));
    var frame = el("div", "ie-rm-frame");

    var header = el("header", "ie-rm-header");
    var titles = el("div");
    titles.appendChild(el("h2", "", config.title || "Roadmap"));
    if (config.subtitle) titles.appendChild(el("p", "ie-rm-subtitle", config.subtitle));
    header.appendChild(titles);
    var legend = el("div", "ie-rm-legend");
    legend.setAttribute("aria-label", "Phase legend");
    config.phases.forEach(function (phase) {
      var chip = el("span", "ie-rm-chip");
      chip.dataset.tone = phase.tone;
      chip.dataset.phase = phase.id;
      chip.appendChild(el("span", "ie-rm-dot"));
      chip.appendChild(document.createTextNode(phase.label));
      legend.appendChild(chip);
    });
    header.appendChild(legend);
    frame.appendChild(header);

    var rail = el("nav", "ie-rm-rail");
    rail.setAttribute("aria-label", stageCount + " stages");
    var line = el("div", "ie-rm-rail-line");
    line.appendChild(el("span", "ie-rm-rail-fill"));
    rail.appendChild(line);
    rail.appendChild(el("ol", "ie-rm-stages"));
    frame.appendChild(rail);

    var panel = el("div", "ie-rm-panel");
    panel.dataset.tone = "overview";
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-live", "polite");
    frame.appendChild(panel);

    var summary = el("div", "ie-rm-print-summary");
    var outcomes = el("div");
    outcomes.appendChild(el("span", "ie-rm-print-label", config.printStagesLabel || "Stage outcomes"));
    var outcomeList = el("ol", "ie-rm-print-list");
    config.stages.forEach(function (stage) {
      var li = el("li");
      li.appendChild(el("span", "", stage.n));
      li.appendChild(document.createTextNode(stage.output));
      outcomeList.appendChild(li);
    });
    outcomes.appendChild(outcomeList);
    summary.appendChild(outcomes);
    if (config.milestones.length) {
      var marks = el("div");
      marks.appendChild(el("span", "ie-rm-print-label", config.printMilestonesLabel || "Key milestones"));
      var markList = el("ol", "ie-rm-print-list");
      config.milestones.forEach(function (milestone) {
        var li = el("li");
        li.appendChild(el("span", "", milestone.short || milestone.label));
        li.appendChild(document.createTextNode(milestone.text));
        markList.appendChild(li);
      });
      marks.appendChild(markList);
      summary.appendChild(marks);
    }
    frame.appendChild(summary);

    var timeline = el("div", "ie-rm-timeline");
    timeline.setAttribute("aria-label", "Timeline with key milestones");
    var axis = el("div", "ie-rm-axis");
    var axisLabels = config.axis || [config.unit + " 1", config.unit + " " + config.total];
    axis.appendChild(el("span", "", axisLabels[0]));
    axis.appendChild(el("span", "", axisLabels[1]));
    timeline.appendChild(axis);
    timeline.appendChild(el("div", "ie-rm-bands"));
    timeline.appendChild(el("div", "ie-rm-marks"));
    frame.appendChild(timeline);
    section.appendChild(frame);

    if (config.artifacts && Array.isArray(config.artifacts.items) && config.artifacts.items.length) {
      var artifacts = el("div", "ie-rm-artifacts");
      artifacts.style.setProperty("--ie-rm-artifact-count", String(config.artifacts.items.length));
      artifacts.setAttribute("aria-label", config.artifacts.label || "Artifacts");
      artifacts.appendChild(el("span", "ie-rm-artifacts-label", config.artifacts.label || "Artifacts"));
      config.artifacts.items.forEach(function (item) {
        var chip = el("span", "ie-rm-artifact");
        chip.appendChild(icon(config.iconBase, item.icon || "file-text.svg"));
        chip.appendChild(document.createTextNode(item.text));
        artifacts.appendChild(chip);
      });
      section.appendChild(artifacts);
    }

    /* Reveal registers fragments during initialize, so they must exist now:
       one per stage plus the closing state */
    var steps = el("div", "ie-rm-steps");
    steps.setAttribute("aria-hidden", "true");
    steps.style.display = "none";
    for (var index = 0; index <= stageCount; index += 1) {
      steps.appendChild(el("span", "fragment"));
    }
    section.appendChild(steps);
    section.dataset.roadmapPrepared = "true";
  }

  function wireRoadmap(section, config, reveal) {
    if (section.dataset.roadmapReady === "true") return;
    var stages = config.stages;
    var total = config.total;
    var closingState = stages.length + 1;
    var railFill = section.querySelector(".ie-rm-rail-fill");
    var stagesEl = section.querySelector(".ie-rm-stages");
    var bandsEl = section.querySelector(".ie-rm-bands");
    var marksEl = section.querySelector(".ie-rm-marks");
    var panelEl = section.querySelector(".ie-rm-panel");
    var chips = Array.prototype.slice.call(section.querySelectorAll(".ie-rm-chip"));
    var fragments = Array.prototype.slice.call(section.querySelectorAll(".ie-rm-steps .fragment"));
    var previewState = 0;
    var state = committedState();

    function committedState() {
      return Math.min(closingState, fragments.filter(function (fragment) {
        return fragment.classList.contains("visible");
      }).length);
    }

    function pct(at) { return ((at - 0.5) / total) * 100; }

    function setPreview(n) { previewState = n; render(); }
    function clearPreview(n) { if (previewState === n) { previewState = 0; render(); } }

    function bindPreview(node, n) {
      node.addEventListener("mouseenter", function () { setPreview(n); });
      node.addEventListener("mouseleave", function () { clearPreview(n); });
      node.addEventListener("focus", function () { setPreview(n); });
      node.addEventListener("blur", function () { clearPreview(n); });
      node.addEventListener("click", function () { goTo(n); });
    }

    stages.forEach(function (stage) {
      var item = el("li");
      var button = el("button", "ie-rm-stage");
      button.type = "button";
      button.dataset.tone = stage.tone;
      button.dataset.stage = String(stage.n);
      button.setAttribute("aria-label", "Stage " + stage.n + ", " + stage.name + ", " + stage.range);
      button.appendChild(el("span", "ie-rm-stage-node", stage.n));
      button.appendChild(el("span", "ie-rm-stage-name", stage.name));
      button.appendChild(el("span", "ie-rm-stage-sessions", stage.range));
      bindPreview(button, stage.n);
      item.appendChild(button);
      stagesEl.appendChild(item);

      var band = el("span", "ie-rm-band");
      band.dataset.tone = stage.tone;
      band.dataset.stage = String(stage.n);
      band.style.left = ((stage.from - 1) / total * 100) + "%";
      band.style.width = ((stage.to - stage.from + 1) / total * 100) + "%";
      bandsEl.appendChild(band);
    });

    config.milestones.forEach(function (milestone, index) {
      var mark = el("button", "ie-rm-mark" + (milestone.gate ? " ie-rm-gate" : ""));
      var previewStage = milestone.stages[0];
      mark.type = "button";
      mark.dataset.idx = String(index);
      mark.setAttribute("aria-label", milestone.label + ", " + milestone.text + ", show Stage " + previewStage);
      mark.style.left = pct(milestone.at) + "%";
      mark.appendChild(el("span", "ie-rm-mark-dot"));
      var text = el("span", "ie-rm-mark-text");
      text.appendChild(el("span", "ie-rm-mark-session", milestone.label));
      text.appendChild(document.createTextNode(milestone.text));
      mark.appendChild(text);
      bindPreview(mark, previewStage);
      marksEl.appendChild(mark);
    });

    function clampMarks() {
      var width = marksEl.offsetWidth;
      if (!width) return;
      Array.prototype.forEach.call(marksEl.querySelectorAll(".ie-rm-mark"), function (mark) {
        var text = mark.querySelector(".ie-rm-mark-text");
        var x = parseFloat(mark.style.left) / 100 * width;
        var left = -95;
        if (x + left < 0) left = -x;
        if (x + left + 190 > width) left = width - x - 190;
        text.style.left = left + "px";
      });
    }

    function gates() {
      return config.milestones.filter(function (milestone) { return milestone.gate; });
    }

    function panelMain(eyebrow, title, iconName, outputLabel, output) {
      var main = el("div", "ie-rm-panel-main");
      main.appendChild(el("span", "ie-rm-eyebrow", eyebrow));
      var heading = el("div", "ie-rm-panel-title");
      var badge = el("span", "ie-rm-panel-icon");
      badge.appendChild(icon(config.iconBase, iconName || "target-arrow.svg"));
      heading.appendChild(badge);
      heading.appendChild(document.createTextNode(title));
      main.appendChild(heading);
      if (outputLabel) main.appendChild(el("span", "ie-rm-output-label", outputLabel));
      if (output) main.appendChild(el("p", "ie-rm-panel-output", output));
      return main;
    }

    function panelSide(label, items) {
      var side = el("div", "ie-rm-panel-side");
      side.appendChild(el("span", "ie-rm-side-label", label));
      side.appendChild(sideList(config, items));
      return side;
    }

    function renderPanel(view) {
      panelEl.textContent = "";
      if (view === closingState) {
        panelEl.dataset.tone = stages[stages.length - 1].tone;
        var closing = el("div", "ie-rm-panel-closing");
        closing.appendChild(icon(config.iconBase, (config.closing && config.closing.icon) || "target-arrow.svg"));
        closing.appendChild(el("p", "", (config.closing && config.closing.text) || ""));
        panelEl.appendChild(closing);
        return;
      }
      var inner = el("div", "ie-rm-panel-inner");
      if (view === 0) {
        var overview = config.overview || {};
        panelEl.dataset.tone = "overview";
        inner.appendChild(panelMain(overview.eyebrow || "Roadmap", overview.title || (stages.length + " stages"),
          overview.icon, null, overview.text));
        if (gates().length) inner.appendChild(panelSide(overview.sideLabel || "Phase gates", gates()));
        panelEl.appendChild(inner);
        return;
      }
      var stage = stages[view - 1];
      var phase = config.phaseById[stage.phase];
      panelEl.dataset.tone = stage.tone;
      inner.appendChild(panelMain(
        "Stage " + stage.n + " of " + stages.length + ", " + (phase.short || phase.id) + ", " + stage.range,
        stage.name, stage.icon, config.outputLabel || "Cumulative outcome", stage.output));
      var inStage = config.milestones.filter(function (milestone) {
        return milestone.stages.indexOf(stage.n) !== -1;
      });
      if (inStage.length) {
        inner.appendChild(panelSide(config.milestonesLabel || "Milestones in this stage", inStage));
      } else {
        var next = gates().filter(function (gate) { return gate.at > stage.to; })[0];
        if (next) inner.appendChild(panelSide(config.nextGateLabel || "Next phase gate", [next]));
      }
      panelEl.appendChild(inner);
    }

    function render() {
      var view = previewState || state;
      var focus = view >= 1 && view <= stages.length ? view : 0;
      section.dataset.roadmapState = String(state);
      section.dataset.roadmapView = String(view);
      section.classList.toggle("is-overview", view === 0);
      section.classList.toggle("is-closing", view === closingState);

      Array.prototype.forEach.call(stagesEl.querySelectorAll(".ie-rm-stage"), function (button) {
        var n = parseInt(button.dataset.stage, 10);
        button.classList.toggle("is-active", n === focus);
        button.classList.toggle("is-done", focus > 0 && n < focus);
        button.classList.toggle("is-preview", previewState === n && state !== n);
        button.setAttribute("aria-pressed", String(state === n));
        if (state === n) button.setAttribute("aria-current", "step");
        else button.removeAttribute("aria-current");
      });
      Array.prototype.forEach.call(bandsEl.querySelectorAll(".ie-rm-band"), function (band) {
        var n = parseInt(band.dataset.stage, 10);
        band.classList.toggle("is-active", n === focus);
        band.classList.toggle("is-done", focus > 0 && n < focus);
      });
      Array.prototype.forEach.call(marksEl.querySelectorAll(".ie-rm-mark"), function (mark) {
        var milestone = config.milestones[parseInt(mark.dataset.idx, 10)];
        mark.classList.toggle("is-active", focus > 0 && milestone.stages.indexOf(focus) !== -1);
      });
      chips.forEach(function (chip) {
        chip.classList.toggle("is-active", focus > 0 && stages[focus - 1].phase === chip.dataset.phase);
      });

      var end = focus > 0 ? stages[focus - 1].to : (view === closingState ? total : 0);
      var tone = focus > 0 ? stages[focus - 1].tone : (view === closingState ? stages[stages.length - 1].tone : stages[0].tone);
      railFill.style.width = (end / total * 100) + "%";
      railFill.style.background = "var(--ie-rm-" + tone + ")";
      renderPanel(view);
    }

    function goTo(n) {
      previewState = 0;
      state = n;
      render();
      if (!reveal || typeof reveal.getIndices !== "function") return;
      var indices = reveal.getIndices(section);
      reveal.slide(indices.h, indices.v, n - 1);
    }

    function sync() {
      previewState = 0;
      window.requestAnimationFrame(function () { state = committedState(); render(); });
    }

    if (reveal && typeof reveal.on === "function") {
      reveal.on("fragmentshown", function (event) { if (section.contains(event.fragment)) sync(); });
      reveal.on("fragmenthidden", function (event) { if (section.contains(event.fragment)) sync(); });
      reveal.on("slidechanged", function (event) {
        if (event.currentSlide !== section) return;
        previewState = 0;
        state = committedState();
        render();
        clampMarks();
      });
    }
    window.addEventListener("resize", clampMarks);
    section.dataset.roadmapReady = "true";
    clampMarks();
    render();
  }

  /* ─── Public API ─────────────────────────────────────────────────── */

  var roadmapConfigs = [];

  /* ─── Group and student picker ──────────────────────────────────── */
  /* .s-picker button, reading a roster embedded as JSON in a
   * <script type="application/json" id="ie-group-roster"> tag. See
   * instructions/group_picker.md and scripts/sync_group_roster.py for how
   * to generate that roster from a course's group-members export. */

  var GROUP_PICKER_SPIN_MS = 2000;
  var GROUP_PICKER_CYCLE_MS = 90;
  var groupPickerRoster = null;
  var groupPickerRosterRead = false;

  function readGroupPickerRoster() {
    if (groupPickerRosterRead) return groupPickerRoster;
    groupPickerRosterRead = true;
    var dataEl = document.getElementById("ie-group-roster");
    if (!dataEl) return null;
    try {
      var roster = JSON.parse(dataEl.textContent);
      if (roster && Array.isArray(roster.students) && roster.students.length > 0) {
        groupPickerRoster = roster;
      } else {
        reportError("group roster JSON has no students");
      }
    } catch (e) {
      reportError("could not parse the embedded group roster JSON: " + e.message);
    }
    return groupPickerRoster;
  }

  function resetGroupPicker(button) {
    window.clearInterval(button._pickerCycleTimer);
    window.clearTimeout(button._pickerStopTimer);
    button.classList.remove("is-spinning");
    var label = button.querySelector(".s-picker-label");
    if (label) label.textContent = "Pick a group";
    button.dataset.picked = "false";
  }

  function initGroupPicker(button, roster) {
    if (button.dataset.pickerReady === "true") return;
    button.dataset.pickerReady = "true";
    button.dataset.picked = "false";

    button.addEventListener("click", function () {
      if (button.classList.contains("is-spinning")) return;
      var label = button.querySelector(".s-picker-label");
      button.classList.add("is-spinning");
      if (label) label.textContent = "Pick a group";

      button._pickerCycleTimer = window.setInterval(function () {
        var g = 1 + Math.floor(Math.random() * roster.groupCount);
        if (label) label.innerHTML = "Group <span class=\"s-picker-group\">" + g + "</span>";
      }, GROUP_PICKER_CYCLE_MS);

      button._pickerStopTimer = window.setTimeout(function () {
        window.clearInterval(button._pickerCycleTimer);
        button.classList.remove("is-spinning");
        var student = roster.students[Math.floor(Math.random() * roster.students.length)];
        if (label) {
          label.innerHTML = "Group <span class=\"s-picker-group\">" + student.group + "</span> – " + student.name;
        }
        button.dataset.picked = "true";
      }, GROUP_PICKER_SPIN_MS);
    });
  }


  /* ── Key-takeaway image modal ─────────────────────────────────────── */
  var openImageModal = null;

  function closeImageModal(event) {
    if (!openImageModal) return;
    if (event) { event.preventDefault(); event.stopPropagation(); }
    var modal = openImageModal;
    openImageModal = null;
    modal.classList.remove("is-active");
    modal.setAttribute("aria-hidden", "true");
    document.removeEventListener("click", onImageModalOutsideClick, true);
    if (modal._ieTrigger && typeof modal._ieTrigger.focus === "function") {
      modal._ieTrigger.focus({ preventScroll: true });
    }
  }

  function onImageModalOutsideClick(event) {
    if (!openImageModal) return;
    if (event.target.closest && event.target.closest(".ie-image-modal-link")) return;
    closeImageModal(event);
  }

  function initImageModal(trigger) {
    if (trigger.dataset.imageModalReady === "true") return;
    var section = trigger.closest("section");
    var id = trigger.getAttribute("aria-controls");
    var modal = id ? document.getElementById(id) : null;
    if (!modal && section) {
      var candidates = section.querySelectorAll(".ie-image-modal");
      if (candidates.length === 1) modal = candidates[0];
    }
    if (!modal) {
      reportError("an .ie-image-modal-trigger has no matching .ie-image-modal (set aria-controls)", section);
      return;
    }
    if (section && !section.contains(modal)) {
      reportError("an .ie-image-modal must sit inside the same section as its trigger", section);
      return;
    }
    trigger.dataset.imageModalReady = "true";
    if (!trigger.hasAttribute("role")) trigger.setAttribute("role", "button");
    if (!trigger.hasAttribute("tabindex")) trigger.setAttribute("tabindex", "0");
    if (!modal.hasAttribute("role")) modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-hidden", "true");
    modal._ieTrigger = trigger;

    function open(event) {
      if (event) { event.preventDefault(); event.stopPropagation(); }
      if (openImageModal === modal) return;
      closeImageModal();
      openImageModal = modal;
      modal.classList.add("is-active");
      modal.setAttribute("aria-hidden", "false");
      window.setTimeout(function () {
        document.addEventListener("click", onImageModalOutsideClick, true);
      }, 50);
    }

    trigger.addEventListener("click", function (event) { if (openImageModal !== modal) open(event); });
    trigger.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") open(event);
    });
    modal.addEventListener("click", function (event) {
      if (event.target.closest && event.target.closest(".ie-image-modal-link")) return;
      closeImageModal(event);
    });
  }

  var imageModalGlobalsReady = false;
  function initImageModals(deck) {
    var triggers = document.querySelectorAll(".ie-image-modal-trigger");
    if (!triggers.length) return;
    Array.prototype.forEach.call(triggers, initImageModal);
    if (imageModalGlobalsReady) return;
    imageModalGlobalsReady = true;
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && openImageModal) closeImageModal(event);
    }, true);
    if (deck && typeof deck.on === "function") {
      deck.on("slidechanged", function () { closeImageModal(); });
    }
  }


  function prepare(root) {
    var scope = root || document;
    Array.prototype.forEach.call(scope.querySelectorAll("section.ie-roadmap"), function (section) {
      if (section.dataset.roadmapPrepared === "true") return;
      var config = readRoadmapConfig(section);
      if (!config) return;
      buildRoadmap(section, config);
      roadmapConfigs.push({ section: section, config: config });
    });
  }

  function init(reveal) {
    var deck = reveal || window.Reveal;
    Array.prototype.forEach.call(document.querySelectorAll("[data-gallery]"), function (gallery) {
      initGallery(gallery, deck);
    });
    roadmapConfigs.forEach(function (entry) { wireRoadmap(entry.section, entry.config, deck); });
    initImageModals(deck);

    var roster = readGroupPickerRoster();
    if (roster) {
      Array.prototype.forEach.call(document.querySelectorAll(".s-picker"), function (button) {
        initGroupPicker(button, roster);
      });
      if (deck && typeof deck.on === "function") {
        deck.on("slidechanged", function (event) {
          if (!event.previousSlide) return;
          Array.prototype.forEach.call(event.previousSlide.querySelectorAll(".s-picker"), resetGroupPicker);
        });
      }
    } else if (document.querySelector(".s-picker")) {
      reportError("a .s-picker button is on the page, but #ie-group-roster is missing or empty");
    }
  }

  window.IEComponents = { prepare: prepare, init: init };
})(window, document);
