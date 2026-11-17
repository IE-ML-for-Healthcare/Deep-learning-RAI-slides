# Browser QA

Owner file for browser validation: setup, the checks the runner performs, and how to recover when a browser tool is unavailable.

## Temporary output

Follow `AGENTS.md`, section Temporary files and cleanup, before running any command. Keep task screenshots, logs, downloads, previews, temporary browser profiles, and command-output files under `tmp/`. Disable Python bytecode for agent commands and configure child-process temporary directories when needed. Reuse the existing validation environment and dependency mirror as installed infrastructure; do not create disposable copies outside `tmp/`. Inspect required evidence before cleaning up your task output

## Setup, once per machine or environment

First use a ready environment in this clone or one of its linked worktrees, including `.venv-reveal-qa-native` on Windows. `scripts/validate_changes.py` finds and checks it automatically, and reuses a local CDN mirror when available. `IE_QA_PYTHON` can name another existing interpreter. Reuse the interpreter only, always run the current checkout's scripts against its current files

Install only when no ready environment exists:

```bash
bash scripts/setup_browser_qa.sh
```

It creates `.venv-reveal-qa`, installs `requirements-qa.txt` (Playwright, pypdf, Pillow), installs Chromium, and confirms a headless launch. Conda users can run `conda env create -f environment.yml`, activate `reveal-qa`, then `playwright install chromium`.

Interpreter paths: `.venv-reveal-qa/bin/python` on macOS, Linux, and WSL; `.venv-reveal-qa/Scripts/python.exe` on native Windows.

## Run

For normal work, use the change-aware runner from the repository root:

```bash
python scripts/validate_changes.py
python scripts/validate_changes.py --base main
python scripts/validate_changes.py --slides session-01-core-idea
python scripts/validate_changes.py --plan
python scripts/validate_changes.py --full
```

The default compares `HEAD` with staged, unstaged, and untracked files. `--base` includes committed branch changes. Capture the task's baseline commit before editing when other changes already exist. `--slides` adds checks and cannot narrow a required full scan

| Change | Required validation |
| --- | --- |
| Slide copy, local layout, or multiple scoped slides | Whole-deck fast static and download checks, strict browser checks on affected slides and aliases, screenshots, visual and Logic QA |
| Insert, remove, or move slides | The same checks, plus affected sequence boundaries |
| Referenced media or download source | Its consuming slides and aliases, including relevant download clicks |
| Shared CSS, runtime, logos, backgrounds, browser checker, or dependency versions | Full affected-deck browser checks; the pattern gallery for shared dependencies |
| Tool or test code | Relevant test modules; the full unit suite if the dependency mapping is unknown |
| Documentation only | Diff and source review; no unrelated render or unit suite |
| Release or PDF work | Full regression plus `instructions/release_pipeline.md` |

The runner runs independent checks concurrently, records each duration, and saves logs and `validation_report.json` in `tmp/validation/`. Inspect that report and the applicable screenshots before claiming success. Local stylesheet imports are followed with relative asset paths and cycle protection. Gallery-only assets select the gallery. Selector attribute values and feature-query conditions cannot establish slide scope. No selection is inferred from slide numbers or task size; unknown shared scope widens the checks. Gallery-only assets trigger gallery checks, imported CSS assets follow their dependencies, and selector text such as a link fragment never proves slide-local scope. Removed slides are checked structurally and are not sent as nonexistent browser ids

Follow [Short continuous fixes](collaboration_workflow.md#short-continuous-fixes) for small edits. Run `python scripts/validate_changes.py` once after the final edit and use its logged static, download, browser and relevant tooling results as the final gate evidence. Do not separately rerun component checks before or after a successful runner unless an input changed, a failure remains unresolved, or a required check is absent from the runner, such as a byte comparison with a helper copy outside the repository

A direct targeted browser run during iteration is optional when it resolves a specific fit, layout or interaction question before the edit is ready. Do not run a preliminary browser scan merely to recreate an existing valid baseline screenshot; baseline reuse is governed by `instructions/layout_playbook.md`, section Design preservation and visual quality. If a shared change requires a full scan, run it once when ready. Documentation-only changes use the diff and source review selected by the runner, without slide screenshots or unrelated render and test suites

When VS Code opens this repository folder, **Validate changed slides** and **Full deck regression** are available through its built-in Run Task command. The first uses this same runner and reuses the existing environment

Direct browser commands remain available:

```bash
.venv-reveal-qa/bin/python scripts/check_browser_qa.py                                  # index.html
.venv-reveal-qa/bin/python scripts/check_browser_qa.py --slides session-02-agenda,session-02-close
.venv-reveal-qa/bin/python scripts/check_browser_qa.py --deck slide_patterns.html --screenshots all
.venv-reveal-qa/bin/python scripts/check_browser_qa.py --strict                         # clipped text and low fit fail
.venv-reveal-qa/bin/python scripts/check_browser_qa.py --full --slides session-02-agenda # full scan, selected screenshots
```

Screenshots and `qa_report.json` go to `tmp/qa/`, which is gitignored.

`--slides` now restricts the geometry and functional checks to the named ids and aliases of selected canonical slides. Unknown ids fail. With no ids, or with `--full`, the runner checks every slide. `--screenshots none` always suppresses screenshots. Reports state targeted or full coverage and list the scanned slides, so a targeted pass is never described as a full-deck pass

Both modes retain the same design assertions. Deck readiness, total slide count, duplicate ids, and console errors remain global. The QA browser measures the completed state of finite animations, pauses repeating effects, disables transitions only during measurement, and waits for fonts, images, and layout instead of sleeping on each slide. The production deck keeps its normal motion

## What it checks

- Reveal.js becomes ready with zero console errors, page errors, and missing local assets
- Static top-level slide count equals `Reveal.getTotalSlides()`, and no id is duplicated after aliases resolve
- Every selected slide: `ie-auto-fit` fit scale and spill, text outside the 1600 x 900 canvas, and text clipped by an overflow container
- Every key takeaway strip uses the approved background: white at 40 % opacity with an 8 px lime edge on light slides, white at 10 % opacity with a 10 px lime edge on dark slides, and its text is 22 to 26 px (standard 24 px); fragments are shown before the scan so hidden takeaways are tested
- Every `ie-table` spans its safe frame margin to margin, every quote is 50 px (30 px only with `source-quote--long` and over 40 words) with bold lime `ie-quote-emphasis` and a 30 px attribution starting with `- `, every `ie-table-key-row` heading clears its lime bar, and no dark card sits on a light slide
- Full-bleed media cards use the shared card classes, with images and overlays spanning the card's inner left and right edges; repeated overlay grids use one height
- No text, image, or takeaway strip overlaps the IE logo, and no takeaway strip overlaps any other element, with a 3 px tolerance; any breach is a failure
- Grid: safe-frame margins and top line, title anchored at the frame top (28 px lower under an eyebrow), takeaway strips on a gridline, logo and quote positions, as defined in `instructions/slide_rules.md`, section Grid. Breaches fail on `index.html` and warn on other decks (`--grid error|warn` overrides); a section with `data-grid-exception="<reason>"` is skipped and its reason listed
- Every download control in the selected scope: base64 `data:` payload, byte match with `data-download-source`, and a real click over `file://` that saves the named file
- Galleries change their hero image; roadmaps preview on hover without committing, commit on click, keep fragments in sync, and show the print summary in print mode
- Tooltips carry `tabindex`, `data-tooltip`, and `aria-label`
- A generic click and Escape check for lightbox, zoom, and disclosure targets

Passing the runner is necessary, not sufficient. Open the screenshots of every changed slide and judge them yourself.

## Offline and sandboxed environments

Many agent sandboxes block `cdn.jsdelivr.net` and Google Fonts. That is not a reason to skip QA:

```bash
bash scripts/setup_offline_cdn.sh      # npm installs reveal.js, KaTeX, and Montserrat into .cache/cdn-mirror
```

The runner and `scripts/release_pdf.py` then answer every CDN request from the mirror. Point `IE_QA_CDN_MIRROR` at another folder that contains `node_modules` if needed.

## When a browser tool refuses `file://`

A connected or in-app browser may refuse local `file://` pages. That is a tool limit, not a failed deck:

1. Run the Playwright runner above, which uses `file://` directly
2. For shared visual inspection, serve the repository with `python -m http.server 8000 --bind 127.0.0.1` and open `http://127.0.0.1:8000/index.html`
3. Keep download validation on `file://` through the runner, because the offline workflow must work

Do not ask the professor to fix a browser-tool refusal, and never disable browser security or use unsafe flags. Report a blocker only when `setup_browser_qa.sh` or the Chromium launch fails, with the exact command and output.

## When setup fails

- Fixable failures, such as line endings or a missing package: fix and retry
- Environment failures, such as Chromium needing root for system libraries: stop, report the exact error, and do not loop. Install Chromium where it is allowed instead: in the environment setup script of a cloud agent (for example the Codex Cloud setup phase), or once in a normal terminal on the local machine

## Release validation

For cumulative releases and PDFs, use `scripts/release_pdf.py` as described in `instructions/release_pipeline.md`. It serves the generated deck over loopback HTTP, requires zero console errors and missing assets, and checks that the PDF page count equals the slide count with fragments collapsed.

## Download controls

The browser runner checks the official title-side geometry, rendered foreground/background contrast in normal, hover, and keyboard-focus states, and real saves over file and HTTP routes. It observes new windows and same-tab navigation and compares the saved filename and bytes with the source. Static QA rejects unregistered visual exceptions and navigable download links. The policy owner is `instructions/slide_rules.md`, section Downloads
