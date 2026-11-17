# Task Prompt Patterns

Owner file for execution briefs, executor reports, and reusable task prompts. The prompts work with any local coding agent: Codex, Claude Code, Gemini CLI, Copilot, Cursor, or others. Deliver briefs and routine reports in chat unless a file is requested; requested files go under `tmp/agent-handoff/`

## General Rules

Use [Design preservation and visual quality](layout_playbook.md#design-preservation-and-visual-quality) and [Design excellence](layout_playbook.md#design-excellence) when defining visual scope, choosing patterns, and setting baseline evidence

- Follow `AGENTS.md`, section Temporary files and cleanup; every brief must keep temporary artifacts under `tmp/` and include cleanup in its acceptance criteria
- Name the exact files that may change, and the files that must not
- Scope one work package, or one to three slides, per brief; refer to slides by `id`
- Anchor every brief to the professor's approval, `syllabus_roadmap.md`, and the implemented `index.html`
- Reuse patterns from `slide_patterns.html`; say which pattern each slide uses, vary patterns across consecutive slides, and reject plain list or text-wall fallbacks
- Put validation and the report format in every brief
- Include this line in every brief that touches slides: Key takeaway strips: every bottom takeaway sits in one of two approved strips (white at 40 % opacity with an 8 px lime edge on light slides, white at 10 % opacity with a 10 px lime edge on dark slides), at one size of 24 px in regular weight, never bold, lime, larger, solid, tinted, or backgroundless, and clear of the IE logo and every other element. `scripts/check_browser_qa.py` fails any breach; the full rule is in `instructions/slide_rules.md`, section Key Takeaway Strips
- Never ask for a whole-folder regeneration or a separate session-planning file
- Reusable CSS moves to `ie-scitech-reveal.css` only after approval, and its inline copy is deleted in the same change

## Execution Brief Template

```markdown
# Execution brief: <short name>
Status: DRAFT FOR REVIEW | READY TO RUN
Approved by the professor on: <date, or Unresolved>

## Goal
<one or two sentences>

## Approved source
- syllabus_roadmap.md, session <NN>, section <name>
- Professor decision: <quote or summary with date>

## Visual scope and baseline
- Task class: review only | content correction | targeted layout repair | new design/redesign
- Visual reference: <professor-accepted revision, working-tree snapshot, or named reference>
- Authorized visual departures: <exact affected ids and changes, or none>

## Allowed files
- index.html
- <other files, each with a reason>

## Must not change
- <files or slides that stay untouched>

## Exact requirements
| Slide id | Pattern | Content, verbatim where approved | Label |
| --- | --- | --- | --- |
| session-NN-topic | ie-compare | ... | Confirmed |

## Exclusions
- <what is out of scope>

## Acceptance criteria
- <observable, testable statements>

## Validation
- python scripts/validate_changes.py --base <task baseline commit>
- Inspect screenshots and complete Logic QA

## Open decisions
- <none, or each Unresolved item>

## Report format
Use the short continuous fix report when applicable; otherwise use the executor report template in instructions/task_prompt_patterns.md
```

## Short continuous fix reports

For [Short continuous fixes](collaboration_workflow.md#short-continuous-fixes), report in two to five concise lines: what changed and where, the required validation result, screenshot/fit evidence when applicable, and any material deviation or unresolved issue. State commit/push status when relevant. Use the full template below for larger work or when the professor requests it; an explicit professor report format takes precedence

## Executor Report Template

```markdown
# Executor report: <brief name>
Summary: <what changed, in two lines>
Files changed: <list>
Slide ids changed: <list>
Implementation notes: <patterns used, scoped CSS added, anything non-obvious>
Visual scope and baseline: <task class and accepted reference>
Content changes: <facts, wording, links, or process corrections>
Visual changes: <none, or authorized departures and reasons>
Before-and-after evidence: <matching screenshots for edited slides, or not applicable for read-only work>
Validation:
- check_deck.py: PASS | FAIL, with warnings explained
- sync_downloads.py --check: PASS | FAIL | not applicable
- unit tests: PASS | FAIL | not run, why
- check_browser_qa.py: PASS | FAIL, fit scales below 0.75: <list or none>
- Validation scope and time: <targeted ids or full decks, test modules, elapsed seconds>
- Screenshots inspected: <paths>
- Logic QA: <result per slide>
Deviations from the brief: <none, or each with reason>
Assumptions: <list>
Failures and unresolved issues: <list>
Reusable candidates for template_improvements.md: <list or none>
Git: worktree <path>, branch <name>, commit <hash>, reached main: yes | no
```

For a routine change, keep the chat report brief: result, affected ids, validation scope and time, remaining issues, and Git state. Keep detailed evidence under `tmp/` only while needed for active review; create a separate report file only when requested. Mark unrelated tests as not applicable, never as passed. Do not add reporting rounds or rerun successful unchanged checks to fill the template

## Audit Verdicts

An auditing AI returns one verdict with reasons: `PASS` (meets the brief and every gate), `REVISE` (fixable gaps, listed), or `BLOCKED` (cannot proceed without a professor decision, stated).

## Reusable Prompts

### Add a slide

```text
Read AGENTS.md, syllabus_roadmap.md, the approved brief, instructions/slide_rules.md, instructions/layout_playbook.md, instructions/review_checklist.md, and index.html.
Edit only index.html.
Add slide <id> after slide <id> in session <NN>, using pattern <name> from slide_patterns.html.
Match item counts and copy length to the pattern's geometry (for example 5 rows in ie-compare-list, single-line ie-process-label headings, healthy ie-auto-fit scale) and keep all visible text inside the pattern's frame.
Do not change CSS or JavaScript unless the brief allows it.
Run the Quality Gates in AGENTS.md, inspect the screenshot against neighbouring slides for visual richness and rhythm, complete Logic QA, and report with the executor report template.
```

### Modify a slide

```text
Read AGENTS.md, the approved brief, instructions/slide_rules.md, instructions/review_checklist.md, and index.html.
Edit only index.html.
Update slide <id> to say <approved message> within its existing composition. Apply the visual-scope contract in instructions/layout_playbook.md; overflow is a specific issue to resolve narrowly, not permission to replace the pattern.
Title under 12 words, body 45 words or fewer.
Run the Quality Gates, inspect the screenshot, and report with the executor report template.
```

### Fix a layout

```text
Read AGENTS.md, instructions/slide_rules.md, instructions/layout_playbook.md, and index.html.
Fix <issue> on slide <id>.
Prefer an existing pattern; otherwise add CSS in index.html scoped by the slide id.
For a full-size image inside a card, use `ie-card--media-bleed` with `ie-card-media--full-bleed` and `ie-card-overlay--full-width`; the image and overlay must meet the card's inner left and right borders, with no inherited max-width, max-height, or horizontal margin constraints.
For repeated quote overlays, add `ie-card-grid--equal-overlays` and set `--ie-card-overlay-height` for the longest copy so every overlay has the same height.
Do not edit ie-scitech-reveal.css unless the fix is an approved reusable pattern, and never edit ie-reveal-fit.js.
Do not add JavaScript for card geometry; CSS and HTML own this layout contract.
Validate with scripts/check_browser_qa.py --slides <id> --strict and report selectors changed and remaining risk.
```

### Build a true 50/50 slide

```text
Use ie-lr on slide <id> with the background class chosen independently of the layout.
Keep ie-lr-grid at two 800 px halves, padding-free, with one ie-lr-panel and one ie-auto-fit per half.
Title in ie-lr-title-left, logo top right, panels starting at the same height.
Choose one ie-lr-takeaway-shared, or one takeaway per half, inside ie-lr-footer.
Do not wrap ie-lr-grid in safe-frame or add slide-specific geometry without approval.
Report measured geometry, takeaway pattern, and assumptions.
```

### Add a download

```text
Add the source file at <path>, add an anchor with download="<name>", data-download-source="<path>", and an empty data: href, then run python scripts/sync_downloads.py.
Prove it with scripts/check_browser_qa.py, which click-tests the download over file://. HTML inspection or an HTTP-only test is not proof.
```

### Insert a randomiser (group and student picker)

```text
Read instructions/group_picker.md first; it is the owner file for this feature.
Confirm the exact slide id at position <N> of the deck before editing; a slide number shifts whenever slides are added or removed.
Add the .s-picker button markup from instructions/group_picker.md as a direct child of that slide's <section>, alongside .ie-logo.
Do not add any other markup, script tag, or registration call; IEComponents.init() wires every .s-picker automatically.
If groups.csv changed, run python scripts/sync_group_roster.py --deck <deck> and verify with python scripts/sync_group_roster.py --deck <deck> --check.
Run the Quality Gates, inspect the screenshot on both a fresh view and after clicking the picker, and report with the executor report template.
```

### Add a source or a note

```text
Read the "Sources And Citations" rules in instructions/slide_rules.md first.
Sources and Notes both go in the slide's one .ie-source-line at the bottom, never as a separate block: Sources cite where a claim or figure comes from, Notes spell out an abbreviation or term used inline.
For a Note, mark the term at the point it appears with <sup class="ie-note-marker">N</sup>, then repeat the same number in the Notes text at the bottom, also wrapped in ie-note-marker.
Number notes in the order their markers first appear, starting at 1. Order at the bottom is Sources first, then Notes; omit whichever label has nothing to show.
Run the Quality Gates and check the rendered slide for contrast and overflow.
```

### Clean up

```text
Remove duplicated or unused slide-specific code related to <area> in index.html without changing content or visual behaviour.
Delete inline copies of any pattern that already exists in ie-scitech-reveal.css.
Compare before and after screenshots of every affected slide and report any pixel-level difference.
```
