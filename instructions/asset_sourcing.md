# Asset Sourcing

Decide what visual asset a slide should use, where it comes from, and whether it is technically trustworthy. Layout, wording, and slide markup are out of scope here.

## Core principle

Preserve identity, normalise generic symbolism. Keep a source's diagram, photo, screenshot, or logo. Replace a generic symbol such as an idea, phone, warning, or target with a consistent Tabler icon when its meaning stays accurate.

## Decision flow

1. Inspect the actual visual; never infer it from a filename or slide title
2. For PowerPoint sources, follow the inspection ladder below before choosing a method
3. Classify the visual as a generic semantic icon, a brand asset, or a source-specific visual
4. Acquire it through the matching branch
5. Validate it, including the SVG integrity gate
6. Report its meaning, classification, source and version, accessibility treatment, and any uncertainty

### PowerPoint inspection ladder

1. Render and inspect the slide
2. Inspect the relevant shapes and groups
3. Inspect the slide relationships in the PowerPoint Open XML package
4. Inspect the matching files in `ppt/media/`, matched through the relationship file, never by file order
5. Identify embedded media, a native shape or group, a chart, SmartArt, a composite, a screenshot or photo, or another source-specific graphic
6. Choose the extraction or replacement method only after classification

## Generic semantic icon

Common concepts with no identity of their own: idea, user, database, phone, warning, collaboration, target, growth.

- Source from Tabler Icons at a pinned release tag or commit, never an unpinned branch
- Validate the exact filename against that pinned source before copying
- Prefer outline icons; choose by meaning first, resemblance second
- Copy only the selected SVG files into `media/icons/tabler/`, or `media/icons/tabler/thin/` for rails and flows at `stroke-width="1.25"`; no runtime CDN, API, or npm dependency
- Keep `media/icons/tabler/LICENSE-tabler-icons.txt` and record source, icon name, and version in a comment or the report
- If no good match exists, stop at the first acceptable option: strong match, reasonable non-misleading match, a legible pair of Tabler icons, the original source visual, or two or three options for the professor to choose from
- Never switch to another icon library or draw a bespoke SVG without approval

## Brand asset

A real company or product mark is a brand asset, not an icon.

- When faithfully migrating a source, keep the source version unless modernisation is requested
- Flag unofficial, modified, or outdated marks instead of silently replacing them
- When modernisation is requested, use the official brand source; if none is available, report it rather than approximating a logo
- IE logos come only from `logos/`

## Source-specific visual

Photos, screenshots, proprietary diagrams, SmartArt, client graphics, and charts with real data carry information a generic icon cannot.

- Extract the original media file when it is recoverable; screenshot a rendered slide only as a last resort
- Export native shapes cleanly when possible, otherwise use a high-resolution transparent PNG or a tight high-resolution crop
- Preserve charts, SmartArt, and composites whole; rebuilding a live chart from its data is a separate build decision
- Report what was inspected when a visual cannot be classified confidently

## Reference photos

- Default source: the free Unsplash License, https://unsplash.com/license; confirm each photo page states the free licence, not the paid Unsplash+ tier
- Download to a local folder under `media/`, one folder per slide or slide group; never hotlink at runtime
- Record photographer, photo title, exact URL, and licence in a visible citation or an approved source record, never only in speaker notes
- Crop or resize only to fit the layout slot, with centre-crop and no distortion
- When no suitable free photo exists, escalate rather than switching to a library with different terms

## SVG integrity gate

Run `python scripts/check_svg.py <file.svg>` on every SVG that is extracted, exported, downloaded, or copied. It checks valid XML and SVG structure, a valid `viewBox`, no external references, no scripts, and no unexpected font dependency. An SVG that wraps raster content is a raster fallback, never vector artwork; accept it only consciously with `--allow-raster-wrapper`.

## Validate before use

- The file exists, is readable, and its type matches its contents
- Raster dimensions suit the display size, with no clipping, corruption, or unintended transparency
- Files are optimised; no embedded base64 images in HTML
- The asset renders correctly and stays legible at its target size, checked in browser QA

## Accessibility

- Informative visual: concise alternative text giving its meaning
- Functional visual: alternative text giving its action
- Redundant or decorative visual: empty `alt=""`
