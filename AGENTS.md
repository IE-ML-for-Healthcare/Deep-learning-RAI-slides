# Agent Instructions

Single instruction file for every AI coding agent working in this repository: Codex, Claude Code, Gemini CLI, GitHub Copilot, Cursor, Windsurf, Jules, Aider, and any tool that follows the open `AGENTS.md` convention. `CLAUDE.md` and `GEMINI.md` only import this file. Put shared rules here, never in a vendor-specific file.

This repository is either the reusable IE SciTech Reveal.js template or a course repository created from it. The rules are identical in both; only the Course Profile changes.

## Course Profile

Fill this in when a course repository is created. Tools read the machine-readable values from `deck.config.json`.

| Setting | Value |
| --- | --- |
| Course | Course title, programme, year, semester |
| Deck owner and sole approver | The professor |
| Content authority | `syllabus_roadmap.md` |
| Active deck | Root `index.html` |
| Speaker notes | `forbidden` by default, mirrored in `deck.config.json`; set `allowed` only on the deck owner's explicit instruction |
| Public URL | Empty until the first approved release |
| Golden reference project | Optional, name it here when the course uses one |

## Workspace Boundary

- This repository may sit inside a parent course workspace; when a parent `../AGENTS.md` exists, read it for course strategy, approval gates, work package scope, and project-wide constraints
- Follow Temporary files and cleanup below for every generated artifact; requested handoff files go in `tmp/agent-handoff/`, and routine reports stay in chat
- Use this repository `AGENTS.md` for local implementation, protected-file rules, validation, and reporting
- Treat parent material and archive folders as read-only unless an approved brief explicitly permits changes; archives are historical and non-authoritative
- Make implementation changes only inside this repository or the task worktree unless an approved brief explicitly permits another path
- Run Git commands from the repository root
- When parent and repository instructions conflict, stop and report the conflict before editing

## Authority Order

1. The professor's latest explicit instruction
2. `syllabus_roadmap.md`, the approved content authority
3. The approved execution brief for the current task
4. This file and `instructions/`
5. Current primary external sources

Repository instructions control how to implement, never what the course teaches. When sources conflict, stop and report the conflict before editing. Never silently change objectives, session order, assessment weights, or scope. No AI approves its own work, and agreement between AIs is not approval.

## Read Before Any Task

Read the governing rules once per working session and retain the applicable requirements. For consecutive small fixes, follow [Short continuous fixes](instructions/collaboration_workflow.md#short-continuous-fixes). Re-read instructions only when they change, new scope makes additional sections relevant, context is lost, or the professor explicitly requests a fresh read. A new wording or spacing request alone does not restart the instruction-reading sequence. Always read the affected source from disk and check the current diff before editing

1. This file
2. `instructions/collaboration_workflow.md`, roles, gates, and status labels
3. The relevant sections of `syllabus_roadmap.md` and the approved brief or professor's explicit request for the task
4. The affected sections, scoped styles, and dependencies in `index.html`, the record of what is already implemented
5. `instructions/slide_rules.md`, the canonical design rules
6. `instructions/layout_playbook.md` (above all its Design excellence section) and `slide_patterns.html`, before designing or changing any layout
7. `instructions/review_checklist.md`, before reporting
8. Task-specific guides only when relevant: `instructions/ie_slide_examples.md` (code snippets, live demo slides), `instructions/asset_sourcing.md` (icons, photos, logos), `instructions/browser_qa.md`, `instructions/release_pipeline.md` (publishing and PDFs), `instructions/git_multi_agent.md` (branches and worktrees), `instructions/task_prompt_patterns.md` (briefs and reports), `instructions/group_picker.md` (the in-slide random group and student picker, read this whenever asked to insert a randomiser or randomizer)

Each topic has exactly one owner file. If you find the same rule in two places, the owner above wins; report the duplicate.

## Rule Compliance

- Every rule, guide, pattern, and check in this repository applies to every task, however small. "I did not apply it" is never an acceptable explanation; a missed rule is a failed task
- Before the first edit, state the Course Profile values the task touches (for example speaker notes) and the shared pattern or rule section each change will follow
- When no shared pattern fits, or a profile value, rule, or request conflict, ask the professor before editing; never improvise a local variant
- Turn every correction into a check: when the professor corrects a mistake that a script could detect, add the check to `scripts/check_deck.py` or `scripts/check_browser_qa.py` with a unit test in the same task, and record it in `template_improvements.md` when it is reusable
- A required gate that cannot run is reported as not run, with the reason; never replace it with a weaker check without saying so

## Role

- Online planner AIs (ChatGPT, Claude.ai, Gemini, Grok, or others) plan, review, and write execution briefs
- Local coding agents execute approved briefs only, validate, and report
- Implement only the approved scope; never add unapproved or future-session content
- Label anything you infer or propose as `Proposed`; never present it as approved

## Repository Map

| Path | Purpose | Edit when |
| --- | --- | --- |
| `index.html` | Active deck, sessions in roadmap order | Every slide task |
| `ie-scitech-reveal.css` | Shared design system: tokens, variants, patterns | Only for an approved reusable pattern |
| `ie-reveal-fit.js` | Shrink-to-fit helper for `.ie-auto-fit` | Only to fix the helper itself |
| `slide-aliases.js` | `data-slide-ref` single-source repeated slides | Only to fix the resolver |
| `ie-components.js` | Gallery and roadmap initialisers | Only to fix or add a generic component |
| `slide_patterns.html` | Rendered gallery of every reusable pattern | When a pattern is added or changed |
| `instructions/` | Rules and guides, one owner per topic | When a rule changes |
| `scripts/` | QA, download sync, release, SVG checks | When tooling changes |
| `tests/` | Unit tests for the tooling | With every tooling change |
| `logos/`, `backgrounds/` | Official brand assets | Never, unless replacing official assets |
| `media/` | Deck media, icons, device frames, placeholders | When a slide needs an asset |
| `template_improvements.md` | Reusable candidates found during course work | When a reusable improvement is found |
| `groups.csv` | Group-members export, source of truth for the group picker; placeholder names here, replace for a real course | Starting a new course, never hand-edited otherwise |
| `scripts/sync_group_roster.py` | Regenerates the picker's embedded roster from `groups.csv` | After `groups.csv` changes |

## Editing Rules

Apply [Design preservation and visual quality](instructions/layout_playbook.md#design-preservation-and-visual-quality) and [Design excellence](instructions/layout_playbook.md#design-excellence) before designing a new slide or deciding whether a task permits any visual change

- Keep Reveal.js at width `1600`, height `900`, margin `0`, `pdfMaxPagesPerSlide: 1`, with exact pinned CDN versions
- Load `reveal.js`, then `ie-reveal-fit.js`, `slide-aliases.js`, and `ie-components.js`; call `IESlideAliases.resolve()` and `IEComponents.prepare()` before `Reveal.initialize`, and `IEComponents.init()` plus `IERevealFit.fitAll()` inside `.then(...)`
- Give every top-level `<section>` a stable kebab-case `id` prefixed by its session, for example `session-03-market-sizing`, and refer to slides by `id`, never by number
- Keep every session inside `<!-- COURSE SESSION CONTENT START -->` and `<!-- COURSE SESSION CONTENT END -->`, with one paired `<!-- SESSION NN START -->` and `<!-- SESSION NN END -->` block per session from its first draft, and make `NN` match the roadmap session number
- Reuse and vary patterns from `slide_patterns.html` before inventing one; choreograph expressive visual structures across consecutive slides, match item counts and copy length to pattern geometry, and never fall back to bare lists or repetitive plain cards; one-off CSS goes in `index.html`, scoped by slide `id`
- Code, configuration files and terminal output use the shared `ie-code` figure, and every live demo or code walkthrough uses the live demo slide (gallery pattern-33): Before and After code beside a Run it terminal with real output, one takeaway strip, one demo after each topic's explanation slides; build figures with `scripts/code_figure.py` and follow `instructions/slide_rules.md`, section Code And Live Demo Slides
- Hover or focus pop-ups use the shared `ie-tooltip` pattern only, with its standard semi-transparent background; `scripts/check_deck.py` fails `role="tooltip"`, custom tooltip or popover classes, and `data-tooltip` without `ie-tooltip`
- Full-bleed media cards use the shared `ie-card--media-bleed`, `ie-card-media--full-bleed`, and `ie-card-overlay--full-width` classes; images and overlays must run from the card's inner left border to its inner right border
- In repeated media-card rows, use `ie-card-grid--equal-overlays` with `--ie-card-overlay-height` so peer quote panels share one height and bottom edge
- Card media geometry belongs to HTML and CSS; do not add JavaScript or fit-helper logic for full-size images or side-to-side overlays
- Never restyle shared tokens, tables, source lines, or comparison slides in slide-scoped CSS
- Use only palette tokens from `ie-scitech-reveal.css`; no new hex values
- Repeated slides use `data-slide-ref`, never copied HTML
- Downloads use the official title-side icon defined in `instructions/slide_rules.md`, section Downloads; follow that section for contrast, direct-save behaviour, and the registered legacy exceptions
- Key-takeaway image modals use the shared `ie-image-modal-*` classes wired by `ie-components.js` (see `instructions/slide_rules.md` and `slide_patterns.html` pattern-30): bind only to the exact takeaway strip, keep the "CLICK FOR IMAGE" pill, keep the modal inside the same section, and validate keyboard and close behaviour
- Tables that name tools, products, or brands use the shared `ie-table-brand-*` classes with local marks in `media/brands/` linked to the official page (pattern-31)
- Follow the speaker-note setting in the Course Profile
- Add Reveal fragments only when the brief explicitly asks for a reveal sequence
- Write in plain English, active voice, sentence case; no em dash characters; bullet lines never end with a full stop; define uncommon acronyms at first use; use International System of Units
- In any `ie-table` cell with more than one independent statement or block item, use a compact literal `- ` prefix for every statement at the existing cell text edge; avoid `<ul>` or `<ol>` default indentation, and keep labels and single statements unbulleted
- Apply Temporary files and cleanup to every command and generated artifact
- Never regenerate the whole folder, delete assets, or edit protected files without an explicit instruction

## Temporary files and cleanup

This section is the single owner of the file-hygiene policy for every AI agent and tool working on this repository

- Put every task-created temporary artifact under this repository's gitignored `tmp/` directory: scratch scripts, draft briefs, handoffs, execution reports, review files, screenshots, previews, logs, command-output files, backups, downloads used only for inspection, and disposable caches
- Use `tmp/<task>/` for task evidence and `tmp/agent-handoff/` for explicitly requested handoff files; routine reports belong in chat, with no separate report file unless the professor requests one
- Temporary worktrees belong only under the main checkout's `tmp/worktrees/<topic>/`; never create sibling working folders, user-level agent worktrees, or tool-specific worktree folders outside `tmp/`
- Before each command that can write files, resolve its output paths and configure its temporary directory and cache options to stay under `tmp/`; disable Python bytecode with `PYTHONDONTWRITEBYTECODE=1` or `python -B`, and set `TMPDIR`, `TMP`, and `TEMP` for the child process when needed
- If a tool cannot keep task-created temporary output under `tmp/`, use a compatible command or report the limitation before running it; a tool default or ignore rule is not permission to write elsewhere
- Approved source edits, explicitly requested final deliverables at their agreed paths, Git's required metadata, and reusable installed validation dependencies are not temporary artifacts; reuse the existing validation environment and offline dependency mirror rather than creating disposable copies outside `tmp/`
- Before finishing, remove your disposable task files after inspecting the required evidence; retain only evidence or handoffs still needed for an active review, identify their `tmp/` paths in chat, and remove them when that review closes
- After your work is merged into `main` and no session uses it, remove your clean worktree and merged branch with Git's checked commands; preserve unique commits, uncommitted work, and files owned by another active session
- Verify the resolved absolute path before recursive deletion, keep it inside the intended task directory, and report permission failures or remaining leftovers accurately
- On Windows, use native PowerShell `Remove-Item -LiteralPath` with `-ErrorAction Stop` for routine cleanup; add `-Recurse` only for a verified task-owned directory, and omit `-Force`. Forced deletion can trigger an agent command-policy block even when ordinary deletion is permitted. Leave read-only or locked files in place and report them rather than forcing deletion or changing permissions
- Clean only disposable task-owned paths, never empty `tmp/` wholesale. Preserve active review evidence, worktrees, shared validation infrastructure, and files owned by another session
- If cleanup is rejected by policy or denied by the filesystem, report the exact remaining task paths once and continue with the requested work; retry only after a relevant permission or environment change, and never bypass the rejection
- Use command-line tools or Codex in VS Code for repository maintenance and cleanup; do not use desktop or browser interface automation

## Quality Gates

Use the change-aware runner before committing and before reporting. Reuse successful evidence when the final diff and environment are unchanged. Never commit an agent implementation with failed or incomplete required checks. `instructions/browser_qa.md` owns validation selection, environment reuse, and commands. Design and Logic QA remain mandatory for every changed slide. A failed or incomplete required check is never a pass

```bash
python scripts/validate_changes.py                        # actual working-tree changes
python scripts/validate_changes.py --base main            # include committed branch changes
python scripts/validate_changes.py --full                 # full regression for release or shared changes
```

- Prefer the existing ready browser environment in this clone or its worktrees; do not reinstall it for each task. Run `bash scripts/setup_browser_qa.sh` only if no ready environment is available, and before claiming Playwright or Chromium is unavailable
- For slide content, local layout, media, or interaction changes, validate affected slides and their dependencies at full check strength; a small slide edit does not require unrelated tooling tests or a full-deck browser scan
- Shared rendering or runtime changes require full affected-deck browser checks; tooling changes require relevant tooling tests; releases require the full suite and release-specific checks
- Run one complete final validation for the current diff. During iteration, rerun only checks affected by a new edit or unresolved failure; do not repeat successful unchanged checks without a reason
- In a sandbox without CDN access, run `bash scripts/setup_offline_cdn.sh` or set `IE_QA_CDN_MIRROR`; a blocked CDN is not a reason to skip browser QA
- A connected or in-app browser refusing `file://` is a tool limit, not a QA failure; use the Playwright runner
- Key takeaway strips follow the two approved looks in `instructions/slide_rules.md` and nothing else, at one text size of 24 px (allowed 22 to 26 px); a takeaway with its own class name also carries `ie-takeaway`; the browser QA fails any other background and any clash with the IE logo or another element, so run it before reporting
- Browser QA enforces the full-bleed media-card edge and equal-overlay contracts described in `instructions/slide_rules.md`
- Every element sits on the canonical gridlines in `instructions/slide_rules.md`, section Grid; the browser QA fails a breach on `index.html`, and a deliberate break needs `data-grid-exception="<reason>"` on its section
- Inspect the screenshots of every changed slide yourself; passing scripts do not prove a slide is logically or visually right
- Passing the gates is the floor, not the goal: meet the Design Quality Bar in `instructions/slide_rules.md` and complete one improvement or preservation assessment using `instructions/review_checklist.md`; make another edit and render only when that assessment finds an issue within the approved scope
- Complete the Logic QA in `instructions/review_checklist.md` for every changed slide

## Multi-Agent Git

Plain Git is the coordination layer when several agents work at once. Commands live in `instructions/git_multi_agent.md`.

- Start the working session with `git --no-optional-locks status --short`, `worktree list`, and `log --all --oneline -15`; during consecutive fixes, refresh status and the affected diff, repeating worktree/history discovery only when the checkout, branch, ownership or concurrency changes
- Use the current `main` checkout for direct maintenance when the professor requests it or no other writer is active; isolate concurrent implementation in your own `<agent>/<topic>` branch and worktree under the main checkout's `tmp/worktrees/`
- Treat uncommitted changes you did not make as someone else's work: never edit, stage, stash, reset, or discard them
- Stage specific files only; never `git add -A` or `git add .`
- On agent branches, commit small, in Conventional Commits style, with a `Co-Authored-By: <agent> <email>` trailer; the professor's direct `main` commits, including VS Code or Copilot-generated messages, need no special format or trailers
- Use `git --no-optional-locks` for read-only commands; a 0-byte `.lock` file with no running Git process is stale, remove it and report it
- Never force-push, hard reset, bypass hooks with `--no-verify`, or silently revert another agent's work
- Merge `main` into your branch and grep for your content before handing back; land on `main` only after approval, by fast-forward
- On agent branches, name every slide `id` a commit changes in its message, or add `Slides: all (<reason>)`; the `commit-msg` hook and the separate pull-request commit-scope job enforce it
- Direct `main` commits are exempt from commit-message policy locally and in CI; static, download, unit, and browser QA still run on every push to `main`
- Before an agent commit, compare the actual diff with the approved scope and run `python scripts/check_commit_scope.py --range main..HEAD --list` after committing; a valid message is an audit aid, not proof that another agent's work was preserved
- Never copy files between worktrees or from an old checkout; integrate only with Git (`merge`, `rebase`, `cherry-pick`)
- Follow Temporary files and cleanup for worktree placement, task evidence, handoffs, and end-of-task removal; never create agent-named output folders outside `tmp/`

## Publishing

Read `instructions/release_pipeline.md` first. Publish only through the manual `release-slides` workflow after professor approval. Never deploy, push, tag, unpublish, or change repository settings without explicit authorisation. Query strings and CSS hiding are not access control.

## Template Improvement Tracking

- Record a genuinely reusable improvement in `template_improvements.md` when you find it, with the candidate template
- Never classify course titles, content, activities, media, datasets, or assessment rules as reusable
- Porting to the template is a separate, approved task that follows `instructions/port_back_template_improvements.md`

## Report Format

Report results in chat by default, using the relevant fields in `instructions/task_prompt_patterns.md`. Create a report file only when the professor requests one, under `tmp/agent-handoff/`, and include any temporary evidence retained for active review. For each changed element, identify the shared pattern id or rule section it follows
