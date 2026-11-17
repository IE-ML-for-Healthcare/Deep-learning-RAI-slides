# Review Checklist

Run before reporting any change. Automated gates cover what they can; the rest needs a human or agent eye on the screenshots. For [Short continuous fixes](collaboration_workflow.md#short-continuous-fixes), use the change-aware runner's logged results to satisfy the applicable automated criteria below; this checklist does not require separate reruns of its component commands.

## Automated Gates

- `python scripts/validate_changes.py` passes the required checks selected from the actual diff; `instructions/browser_qa.md` owns the selection rules
- Every warning is either fixed or explained, and tests outside the affected scope are marked not applicable
- Browser checks retain full strength in the selected scope: zero console errors, zero missing assets, no spill, no text outside the canvas, approved takeaway strips, no clashes, and applicable download clicks over `file://`
- Every changed slide has a screenshot that you inspected, and its fit scale is 0.75 or higher, or the low value is explained
- The report states targeted slide ids or full-deck coverage, relevant test modules, elapsed time, and any incomplete or failed required check

## Visual QA

- Titles fit and are left-aligned
- Every element sits on the canonical gridlines in `instructions/slide_rules.md`, section Grid, or on a line shared by the slide or its family; any `data-grid-exception` states a specific reason
- One logo per slide, with the accent variant matching the region beneath it
- No clipped, overlapping, or illegible text; tables readable without shrinking
- Multi-statement table cells use compact `- ` prefixes at the existing cell text edge, with no browser-default list indentation; labels and single statements remain unbulleted
- Background classes valid and never combined with `ie-light` or `ie-dark`
- Green-card overlays align with the baked cards, with the logo opposite the card area
- Full-bleed media-card images and overlays run from the card's inner left border to its inner right border; repeated overlays share one height
- Photo-background text stays in the non-photo area
- Comparison slides use `ie-compare` with no `ie-activity-panel` around numbered rows, no decorative bullet beside a row number, and one takeaway spanning both halves
- Every source line uses `.ie-source-line` bottom left, with the logo moved top right
- Quote slides show only the quotation and attribution
- Icons in one rail or flow share one Tabler variant and stroke width
- Only palette tokens; no new hex values; accents pass contrast on their background
- Print view renders: open `?print-pdf` or use `scripts/release_pdf.py`
- Every key takeaway strip matches the standard in `instructions/slide_rules.md`: clear white at 40 % opacity with an 8 px lime edge on light slides, white at 10 % opacity with a 10 px lime edge on dark slides, nothing else
- Every takeaway is a strip at the single deck size of 24 px; no bold, lime, oversized, or backgroundless takeaway text
- Key-takeaway image modals bind only to the exact takeaway strip, support click, Enter, Space, Escape, outside-click, and slide-change behaviour, and use an informative image alternative
- Nothing clashes with the IE logo, and no takeaway strip overlaps any other element; the browser test fails on any overlap above 3 px, and you confirm it on the screenshot

## Design QA

Apply [Design preservation and visual quality](layout_playbook.md#design-preservation-and-visual-quality) independently of factual accuracy, Logic QA, and automated results

- Was the authorized visual scope recorded and respected?
- For visually edited slides, was a matching baseline reused or captured under `instructions/layout_playbook.md` and compared with the final full-size screenshot at the same viewport and interaction state?
- Are the established composition, useful visuals, density, balance, and deck rhythm preserved, with every deliberate departure explained?

Ask these of every changed slide, against its screenshot, before reporting. A "no" requires a scoped correction and only the checks affected by it. A successful preservation assessment completes this review without an additional edit or render.

- Does the layout show the shape of the content (flow, fork, lanes, layers, axis, figures, tree), or is it a list or table that could be drawn?
- Does the session choreograph varied patterns from `slide_patterns.html` (avoiding bare lists, repetitive card stacks, or repeating one content pattern on more than two consecutive slides) and anchor tool or workflow slides with authentic icons, brand marks, mockups, or interactive components?
- Does the copy fit the pattern geometry cleanly: all 5 rows populated in `.ie-compare-list`, single-line `.ie-process-label` headings sharing one baseline, single-line `.ie-roadmap` subtitles clear of stage hover highlights, and `.ie-auto-fit` scales at or above `0.85` where possible?
- Does the layout prove the takeaway without narration?
- Is there one clear focal point, and does the eye land on it first?
- Does the content balance the safe frame, preserving intentional negative space without accidental gaps or artificially spread-out text?
- Apply [Vertical composition](layout_playbook.md#vertical-composition): does the main body use the available height below the fixed header, with balanced visual weight and a takeaway near the lower content edge when present? Return `REVISE` for a short top stack over a large unexplained lower blank band; fit scale and absence of overflow do not establish good vertical composition
- Is every word readable from the back of a room: body 19 px or larger, clear heading hierarchy?
- Do dashed, faded, lime and navy elements keep their deck-wide meanings?
- Does each takeaway strip hold one message, with no inline code?
- Does the slide look as good as or better than its neighbours, and does the block alternate light and dark sensibly?
- Did the improvement or preservation pass follow the authorized visual scope, with its decision and evidence recorded?

## Structure QA

- Every top-level slide has a stable kebab-case `session-NN-topic` id
- Sessions are inside the course sentinels, in roadmap order, each with one paired marker block whose number matches the roadmap
- Only approved sessions exist; no future-session placeholders
- Repeated slides use `data-slide-ref`, not copied HTML
- One-off CSS is scoped by slide id in `index.html`; no shared pattern is duplicated or restyled inline
- Speaker notes follow the Course Profile

## Writing QA

- No em dash characters and no bullet line ending with a full stop
- Titles under 12 words; body text 45 words or fewer; one message per slide
- Body text at regular weight; emphasis by colour, never `<strong>`
- Uncommon acronyms defined at first use; International System of Units
- Content matches the approved brief and stays student-facing

## Traceability QA

Review each change against, in order: the professor's instruction, `syllabus_roadmap.md`, the approved brief, repository rules, and the implemented `index.html`.

- Content stays inside the approved scope for the session and is traceable to its roadmap entry
- No approved objective, activity, output, risk, fallback, or dependency is silently dropped
- No requirement, assessment rule, integration, or architecture is invented
- Proposed or unresolved content is not presented as approved
- Any deliberate deviation is documented and approved before implementation

## Logic QA

Check that each slide is true, not only plausible:

- Every process or flow follows real-world order: step N genuinely precedes step N+1
- Every consequence follows from its paired cause, evidence, or card
- The takeaway follows from what the slide shows
- An applied example maps one to one to the framework it illustrates, with the same categories and headers
- Names, numbers, thresholds, and evidence labels match their sources and stay consistent across slides
- No hypothesis, vendor claim, or AI inference is labelled as observed or confirmed evidence
- Every live demo slide shows code that exists in the runnable demo and output captured from actually running it, with the Before, After and Run it figures telling one consistent story

## Multi-Agent And Git QA

- Concurrent implementation used an isolated worktree under the main checkout's `tmp/worktrees/`, or direct `main` work met the conditions in `AGENTS.md`
- `git --no-optional-locks status --short` shows only intended files; all task-created temporary artifacts stayed under `tmp/`, including ignored files
- Disposable task output was removed after inspection; any retained evidence is still needed for active review and its `tmp/` path is reported
- Completed merged worktrees and branches were removed when no session used them, or a remaining blocker is reported
- After merging `main`, your content and other agents' recent changes to the same slides are both present
- Commits follow Conventional Commits with a `Co-Authored-By` agent trailer
- No `--no-verify`, force-push, hard reset, discarded work, or stale `.lock` file left behind

## Release QA

Only for publishing or PDF work; see `instructions/release_pipeline.md`.

- Static and runtime slide counts agree, and denominators match the source total
- Published output contains exactly slides 1 to N; the first excluded slide is absent
- A requested PDF has exactly the selected pages with fragments collapsed; a blank PDF input produces no PDF
- Aliases whose canonical slide falls outside the selection still render
- Deployment runs only after every validation passes, through the `github-pages` environment
- The workflow summary records commit, totals, cutoffs, slide identities, and result

## Report Artifacts

Routine reports stay in chat, using relevant fields from `instructions/task_prompt_patterns.md`. A separate report file requires a professor request and belongs under `tmp/agent-handoff/`; report any temporary evidence retained for active review and any cleanup blocker

## Download review

- Official title-side icon or exact registered legacy exception, checked by static QA
- Actual background and all interaction states inspected in screenshots; browser contrast checks pass
- File and HTTP saves have the exact filename and bytes, with no new window or navigation
- Follow `instructions/slide_rules.md`, section Downloads; do not approve an exception yourself
