# Changelog

## Unreleased, 4 November 2026: standard GitHub link button

- Added the official GitHub mark and `ie-github-btn`, with light and dark treatments, lime hover and keyboard focus
- Shared the download button geometry without changing download behaviour; added `ie-title-with-link` for title-side links
- Added gallery pattern-34 and the usage rule in `instructions/slide_rules.md`
- Migration: use the GitHub icon for GitHub links when no visible text name is requested; keep requested text labels

## Unreleased, 1 November 2026: live demo slide

- Added the shared `ie-code` figure and the `ie-demo-*` live demo slide layout, gallery pattern-33: Before and After code beside a Run it terminal with real output
- Added `scripts/code_figure.py` to build highlighted, escaped code figures, with unit tests
- Made the live demo slide the default for code, configuration and terminal output in `AGENTS.md`, `instructions/slide_rules.md`, `instructions/layout_playbook.md`, `instructions/ie_slide_examples.md` and `instructions/review_checklist.md`

## Unreleased, 19 October 2026: official download button

- Standardized the title-side download icon, with light and dark surface treatments
- Added static enforcement and an exact registry for existing layout exceptions
- Added rendered contrast and direct-save checks over file and HTTP routes, including popup and navigation rejection
- Migration: use the shared `ie-download-btn` and `ie-title-with-download` classes; preserve only registered existing exceptions

## Unreleased, 14 October 2026

Requested by the professor after repeated rule misses in the MLOps course deck

### Changed

- `deck.config.json` defaults `speakerNotes` to `forbidden`; the static QA already fails any `class="notes"` when forbidden
- `AGENTS.md` adds a Rule Compliance section: every rule applies to every task, profile values and patterns are stated before editing, conflicts are asked, and each correction becomes a scripted check
- `instructions/browser_qa.md` documents stylesheet-import, gallery, and selector scope handling in the validation runner
- `.githooks/pre-commit` points to `instructions/git_multi_agent.md`

### Added

- Static QA guard: hover or focus pop-ups must use the shared `ie-tooltip`; `role="tooltip"`, custom tooltip or popover classes, bare `data-tooltip`, and an `ie-tooltip` without `tabindex`, `data-tooltip`, and `aria-label` fail
- Unit tests for the pop-up guard and the speaker-notes default

## Unreleased, 13 October 2026

Ported TI-022, approved by the professor's explicit request: consistent commit-message policy for direct main commits and agent pull requests

### Changed

- Direct commits on `main`, including ordinary VS Code and Copilot-generated messages, are exempt from commit-message policy both locally and in GitHub Actions
- Agent branches retain the local scope hook; pull requests run the same scope check in a separate job so policy failures cannot skip product QA
- Agents must complete the required change-aware validation before committing and compare their actual diff with the approved scope
- Scope checking projects only slide identifiers present in each CSS selector, avoiding redundant pattern compilation on large decks
- Regression tests preserve stale-copy detection and verify the main exemption, pull-request enforcement, and independent product checks

### Migration notes for existing course repositories

1. Adopt the workflow, hook, scope checker, tests, and owner instructions together; static, download, unit, and browser checks remain required on pushes to `main`
2. The existing `qa` job keeps its name; `commit_scope` is a new pull-request job. Any decision to require it through branch protection remains with the professor
3. Manual `check_commit_scope.py --range` commands remain strict on every branch

## Unreleased, 12 October 2026

Ported TI-021, approved by the professor's explicit request: proportional validation and ready-environment reuse. No course content, identifiers, URLs, or media were ported

### Added

- `scripts/validate_changes.py`: choose checks from the actual diff, include aliases, affected slide boundaries, gallery media and imported CSS dependencies, reuse a pinned browser environment, run independent checks concurrently, and report coverage and elapsed time
- Tests for validation selection, alias expansion, unknown slide ids, and scoped functional checks
- VS Code tasks for changed-slide validation and full regression

### Changed

- `--slides` now validates only selected slides and their aliases, including functional checks; the full deck remains the default when no selection is given
- Browser measurement waits for resources and completed animations instead of fixed sleeps per slide, retaining the template's generic design assertions and component checks
- Agents read relevant material once per working session, execute explicit maintenance requests directly, and rerun only affected checks during iteration

### Migration notes for existing course repositories

1. Adopt `scripts/validate_changes.py`, its tests, and the owner workflow instructions together; run `--full` for release or shared rendering changes
2. Commands that previously used `--slides` only for screenshots must add `--full` when a full browser scan is intended
3. Allow `.vscode/tasks.json` in `.gitignore`; keep editor-specific local settings ignored
4. Reuse a ready interpreter with the pinned Playwright version, optionally through `IE_QA_PYTHON`; always run the current checkout's scripts

## 2.1.0, 11 October 2026

Port of every reusable improvement from the Rapid Prototyping with AI course repository since 2.0.0 (course commits `c612582` to `16baa40`, backlog entries TI-012 to TI-019), plus the course-local features that had not been logged. Course content, slide ids, media, and wording were not ported.

### Added

- Key takeaway strip standard (TI-012): two looks only, one 24 px size, one shared registry in the stylesheet, `check_deck.py`, and `check_browser_qa.py`, with a logo and element clash test; `ie-takeaway` is the opt-in class for any course-specific strip
- Safe frame modifiers `safe-frame--open`, `--dense`, `--full-bleed`, one quote size with `ie-quote-emphasis`, type scale tokens, `ie-logo-tr` and `ie-logo-br`, and static guards for scoped insets, quote sizes, and agenda cards (TI-013)
- Margin to margin fit in `ie-reveal-fit.js`, `ie-table-key-row`, `ie-card-light`, and the extended `ie-compare` template for two-sided activities (TI-014)
- Canonical gridlines in `instructions/slide_rules.md`, section Grid, enforced by the browser QA with a `data-grid-exception` opt-out (TI-015)
- Key-takeaway image modal as a shared component (TI-016): `ie-image-modal-*` classes, the "CLICK FOR IMAGE" pill that tells the presenter a takeaway opens an image, an optional eye icon, an optional source link, print hiding, and generic wiring in `ie-components.js`; gallery pattern 30
- Full-bleed media cards with equal overlays and a default light overlay look (TI-017); gallery pattern 29
- Commit scope guard (TI-018): `scripts/check_commit_scope.py`, the `commit-msg` hook, CI over every push and pull request, and tests
- Design Quality Bar, Design excellence, and Design QA (TI-019)
- Table with brand marks: `ie-table-brand-*` classes for official marks linked to the vendor page, with a name and optional note; gallery pattern 31
- Gates by lane table in `instructions/git_multi_agent.md`: what the VS Code main lane, other agents, and the professor may waive, and what is never waived
- Workspace Boundary section in `AGENTS.md` for repositories that sit inside a parent course workspace
- `tests/test_template_standards.py`: strip registries match and hold no course classes, no slide-id selectors in the shared stylesheet, modal and brand-table contracts
- Tabler icons used by the new standards, including `thin/eye.svg` and `markdown.svg`

### Changed

- `agent_handoff/` became `agent-handoff/`, tracked with its contents git-ignored; `.claude/commands/add-slide.md` removed, `AGENTS.md` stays the single source
- The browser QA checks logo positions by edge (bottom-left bottom 852 px, top-right right 1504 px and top 52 px, bottom-right right 1552 px), so it no longer depends on the lockup height
- `ie-lr` logo sits on the 52 px top-right gridline; the `ie-lr` shared takeaway spans the content margins and is left aligned
- Gallery pattern 17 carries a documented grid exception; the gallery passes browser QA with zero failures and zero warnings
- Two invalid escape sequences in `check_browser_qa.py` fixed (SyntaxWarning on Python 3.12 or later)

### Migration notes for existing course repositories

1. Add `ie-takeaway` to every course-specific takeaway class, then remove those classes from the shared registries
2. Replace slide-local image modal scripts and `s2-image-modal-*` classes with `ie-image-modal-*` plus `aria-controls`; `ie-components.js` must be loaded
3. Replace slide-scoped brand-table rules with `ie-table-brand-*`
4. Move slide-id selectors out of `ie-scitech-reveal.css` into `index.html`
5. If the deck still applies the Reveal.js image margin to the logo, apply 2.0.0 migration note 4 before running the new logo grid check

## 2.0.0, 26 September 2026

Port of every reusable improvement from the Rapid Prototyping with AI course repository, commit `83b2a14`, refactored on the way in. No course content, media, or wording was ported.

### Added

- Layout patterns: true 50/50 `ie-lr`, comparison `ie-compare ie-compare-dark`, source line `.ie-source-line`, progressive-focus roadmap `ie-roadmap`, stacked agenda, thumbnail gallery, objectives grid, quote with cutout portrait, statement bar, data table with compact and numeric variants, device explainer, link cards, process flow, media split, activity panels, screen mockup, context tooltip, narrowing ladder, log with separate note, relay cards, and emphasis band (TI-001 to TI-005, TI-010)
- `slide_patterns.html` now holds 27 numbered, id-tagged patterns using local placeholder media only
- `slide-aliases.js` for single-source repeated slides with `data-slide-ref` (TI-009)
- `ie-components.js`: generic gallery and data-driven roadmap components, replacing per-deck copies of initialiser scripts
- Palette channel tokens for translucency and documented semantic tokens (`--ie-alert`, `--ie-screen-*`, `--ie-roadmap-*`)
- Tabler icon sets in `media/icons/tabler/` and `thin/` with licence, `media/laptop.png`, `media/placeholders/`
- Tooling: `check_deck.py` static QA, rewritten `check_browser_qa.py` (per-slide fit, spill, canvas, clipping, downloads, components), `sync_downloads.py` (TI-007), `release_slice.py` and `release_pdf.py` (TI-008, TI-011), `check_svg.py`, `qa_common.py` with an offline CDN mirror, `setup_offline_cdn.sh`, `requirements-qa.txt`, unit tests
- GitHub Actions: `qa.yml` on every pull request, manual `release-slides.yml` with the PDF name prefix from `deck.config.json`
- Multi-agent Git rules, `.githooks/pre-commit`, and `instructions/git_multi_agent.md`
- Vendor-neutral instructions: `AGENTS.md` as the single source, thin `CLAUDE.md` and `GEMINI.md` imports, `planner_project_instructions.md`, `asset_sourcing.md`, `task_prompt_patterns.md` with brief and report templates, `release_pipeline.md`
- `deck.config.json`, `syllabus_roadmap.md` skeleton, empty `template_improvements.md`

### Changed

- Reveal.js pinned to `5.2.1` everywhere instead of the floating `@5`
- Typography uses fixed px on the 1600 x 900 canvas; the old `clamp(..., vw, ...)` sizes followed the browser window, so the same slide rendered differently on different screens
- `ie-reveal-fit.js` v5 only shrinks: it no longer enlarges short content up to 127 %, so title sizes are consistent
- Dark image variants lift their children with a zero-specificity `:where()` rule, so `.safe-frame`, `.closing-frame`, and the logo keep their own positions
- Images inside slides have no inherited Reveal.js theme margin
- `ie-compare-accent` uses colour only, matching the regular-weight body rule
- `bg-green-dark-left.png` normalised to 1600 x 900
- `codex_prompt_patterns.md` became `task_prompt_patterns.md`, `git-multi-agent.md` became `git_multi_agent.md`, and `codex_handoff/` became `agent_handoff/`
- The alias fallback in `release_slice.py` also covers cumulative cutoffs whose alias targets fall later in the deck, and finds the resolver call without depending on indentation

### Removed

- `session_plan.md`, replaced by `syllabus_roadmap.md` and approved briefs
- `ie-logo-fixed`, no longer needed after the overlay fix
- Unsplash hotlinks in the gallery, replaced with local placeholders
- Unused gallery-only styles and the inline gallery script

### Migration notes for existing course repositories

Apply one at a time with before and after screenshots of every slide:

1. Replace the vw clamps: headings and body copy become their maximum px values, which is how they already render on a 1600 px wide window
2. Update `ie-reveal-fit.js`: slides whose content was being enlarged will render at designed size; recheck title slides
3. Apply the `:where()` overlay rule and remove `ie-logo-fixed` and any slide-level position fixes it made necessary
4. Add the image margin reset and recheck slides with images in flex rows
5. Move inline `ie-compare`, `.ie-source-line`, and roadmap CSS to the shared stylesheet, and replace inline gallery and roadmap scripts with `ie-components.js`
6. Pin Reveal.js to `5.2.1` and add `deck.config.json`
