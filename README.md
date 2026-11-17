# IE SciTech Reveal.js Template

Reusable Reveal.js foundation for IE School of Science and Technology course decks: one continuous 1600 x 900 deck per course, a shared design system with 31 tested layout patterns, automated QA, a cumulative release pipeline, and one set of instructions that works with any AI agent.

## Start A New Course

1. Create the course repository from this template (GitHub "Use this template", or copy the folder without `.git`)
2. Fill in the Course Profile table in `AGENTS.md` and the values in `deck.config.json`
3. Replace `syllabus_roadmap.md` with the course roadmap and get it approved
4. Set up the planner AI project with `instructions/planner_project_instructions.md`
5. Enable the Git hooks once: `git config core.hooksPath .githooks` (`pre-commit` keeps agents off `main`, `commit-msg` makes every commit name the slides it changes; see `instructions/git_multi_agent.md`, Gates by lane)
6. Reuse a ready browser environment; install only when needed with `bash scripts/setup_browser_qa.sh`
7. Replace the starter slides in `index.html` with Session 1, keeping the sentinels and session markers
8. Leave `slide_patterns.html` and `media/placeholders/` in place as references; `examples/` holds a historical finished deck that predates some current rules, so copy patterns from `slide_patterns.html` instead. Delete `examples/downloads/` once the course has its own downloads

## Daily Workflow

For a clear correction or specified maintenance change, the professor's direct request can go straight to execution. Agents follow the proportional validation rules in `instructions/browser_qa.md`

1. Plan the next package with an online AI, starting from `instructions/new_ai_session_kickoff.md`
2. Approve the content, then get an execution brief in the format of `instructions/task_prompt_patterns.md`
3. Hand the brief to a local coding agent, which follows `AGENTS.md`
4. Review the executor report, the screenshots, and the audit verdict
5. Approve, land on `main`, and publish through the release workflow when ready

`instructions/collaboration_workflow.md` explains roles, approval gates, and status labels.

## Works With Any AI Agent

| Tool | Reads | Notes |
| --- | --- | --- |
| Codex, Copilot coding agent, Cursor, Windsurf, Jules, Aider, and other `AGENTS.md` tools | `AGENTS.md` | Native support |
| Claude Code | `CLAUDE.md`, which imports `AGENTS.md` | Also reads `AGENTS.md` alone when no `CLAUDE.md` exists |
| Gemini CLI | `GEMINI.md`, which imports `AGENTS.md` | Or set `context.fileName` to `AGENTS.md` |
| ChatGPT, Claude.ai, Gemini, Grok, or any chat AI | `instructions/planner_project_instructions.md` and `instructions/new_ai_session_kickoff.md` | Connect the repository or upload the files |

All rules live in `AGENTS.md` and `instructions/`, one owner file per topic. Never add rules to a vendor-specific file.

## Preview

Open `index.html` directly in a browser, or serve the folder:

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Open `slide_patterns.html` to browse every reusable layout. Press S for the presenter view.

## Quality Checks

```bash
python scripts/validate_changes.py                             # select checks from the actual diff
python scripts/validate_changes.py --base main                 # also include committed branch changes
python scripts/validate_changes.py --plan                      # inspect the selection
python scripts/validate_changes.py --full                      # full local regression
```

VS Code provides **Validate changed slides** and **Full deck regression** tasks. GitHub Actions keeps full regression checks on every pull request through `.github/workflows/qa.yml`. Details: `instructions/browser_qa.md` and `instructions/review_checklist.md`.

## Export To PDF

Open the deck with `?print-pdf`, for example `http://127.0.0.1:8000/?print-pdf`, then print from Chrome or Edge to PDF, landscape, no margins, background graphics on. For validated PDFs with collapsed fragments, use the release workflow or `scripts/release_pdf.py`.

## Publish

Publishing is manual and cumulative by slide number through the `release-slides` GitHub Actions workflow, after professor approval. The full procedure, including first-time GitHub Pages setup, is in `instructions/release_pipeline.md`.

## Repository Map

| Path | What it is |
| --- | --- |
| `index.html` | The active course deck |
| `slide_patterns.html` | Rendered gallery of every reusable pattern |
| `ie-scitech-reveal.css` | Design system: tokens, variants, and patterns |
| `ie-reveal-fit.js`, `slide-aliases.js`, `ie-components.js` | Shrink-to-fit, repeated slides, and gallery and roadmap components |
| `syllabus_roadmap.md` | Approved course content authority |
| `deck.config.json` | Machine-readable course settings for the tooling |
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | Agent instructions, one source |
| `instructions/` | Rules, guides, and prompts |
| `scripts/`, `tests/`, `.github/workflows/` | QA, release tooling, and continuous integration |
| `logos/`, `backgrounds/`, `media/` | Brand assets, 1600 x 900 backgrounds, icons, device frames, placeholders |
| `template_improvements.md` | Reusable candidates found during course work |
| `CHANGELOG.md` | Template versions and migration notes for course repositories |
