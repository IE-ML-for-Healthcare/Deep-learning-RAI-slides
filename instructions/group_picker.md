# Group and Student Picker

Owner file for the in-slide random group and student picker (`.s-picker`). Read this before adding, moving, or changing the picker on any slide, and before regenerating its roster.

## What it is

A small pill button, top right corner by default, that on click spins for about two seconds and then shows a random group number and a random student's name, drawn from the same pick, so the two are always consistent. The result stays on screen until the professor clicks it again, or leaves the slide; it never resets on its own.

## Trigger phrases

Any of these mean the same task: "insert a randomiser", "insert a randomizer", "add a group picker", "add the student picker". Treat "on slide 42" or "slide #42" as the slide's position in the deck, counted from 1 including every top-level `<section>`; confirm the exact `id` before editing, for example by counting sections or asking the professor.

## Roster: source of truth and how to regenerate it

The roster lives in `groups.csv` at the repository root, the raw group-members export downloaded from the university system, kept exactly as exported. Do not hand-edit its format or reformat it into Markdown or another shape. Expected columns: `Group Code`, `First Name`, `Last Name` (other columns are ignored). A row with no first or last name is a blank seat and is skipped.

To load a new roster, for a new group set or a new course, replace `groups.csv` with the new export, keeping the same column headers, then run:

```bash
python scripts/sync_group_roster.py
```

This regenerates the JSON embedded in the deck between the `GROUP ROSTER DATA START` and `GROUP ROSTER DATA END` markers, near the end of `<head>`. The deck never fetches `groups.csv` at runtime, so the picker keeps working over `file://` with no server. Verify with:

```bash
python scripts/sync_group_roster.py --check
```

This fails if the embedded roster is stale relative to `groups.csv`. Run it as part of the Quality Gates whenever `groups.csv` changes.

## Adding the picker to a slide

Add this markup as a direct child of the `<section>`, alongside `.ie-logo`, not inside `.safe-frame`:

```html
<button type="button" class="s-picker" aria-label="Pick a random group or student">
  <span class="s-picker-die" aria-hidden="true">&#127922;</span>
  <span class="s-picker-label">Pick a group</span>
</button>
```

No other markup or script registration is needed. The shared init function scans the page for every `.s-picker` element and wires it automatically. Add `class="s-picker s-picker-bottom-right"` instead, to use the bottom right corner on a slide whose top right is already busy with other content.

## Where the code lives

- CSS: the `.s-picker` block at the end of `ie-scitech-reveal.css`, a self-contained, reusable component using only palette tokens
- Roster loading, spin animation, and slide-change reset: the group picker functions inside `ie-components.js`, wired automatically by `IEComponents.init()`, the same call every deck already makes; no extra script tag or registration step is needed in a deck built from this template
- Roster generation: `scripts/sync_group_roster.py`, following the same pattern as `scripts/sync_downloads.py`
- Roster data and example: `groups.csv` at the repository root holds placeholder names only, and `slide_patterns.html` (`#pattern-28-group-picker`) demonstrates the picker; `scripts/sync_group_roster.py` defaults to updating `slide_patterns.html`

## Starting a new course from this template

1. Replace `groups.csv` with that course's real group-members export
2. Add the `.s-picker` button markup to whichever slides in `index.html` need it
3. Run `python scripts/sync_group_roster.py --deck index.html` (repeat `--deck` for every deck that should carry the picker)
4. Once the course deck is the one that matters day to day, update `scripts/sync_group_roster.py`'s `DEFAULT_DECKS` to point at it, so a plain `python scripts/sync_group_roster.py` with no `--deck` flag targets it directly

## Rules

- Never hand-edit the JSON between the `GROUP ROSTER DATA` markers; it is generated, and a manual edit is overwritten on the next sync
- Never point the picker at a live roster containing more than first name and surname initial; the display format is fixed at "First L." and is not configurable per slide
- The picker's placement (top right or bottom right) is the only per-slide choice; its size, colour, and animation come from the shared CSS and must not be overridden per slide
- Treat `groups.csv` like any other course data file: real student rosters stay in the course repository, never in the template
