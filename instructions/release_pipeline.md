# Slide Release Pipeline

## Purpose and safety

Owner file for publishing the cumulative student deck and producing optional Portable Document Format (PDF) handovers

Private `main` contains the complete working deck. The manual `release-slides` workflow checks out one exact commit, validates the source, builds only the requested slide cutoff, validates the generated artifacts, and deploys only the validated `dist/` artifact

The stable student URL is recorded in `deck.config.json` as `publicUrl` and in the Course Profile of `AGENTS.md`. It never changes once students have it

Query strings, URL parameters, Cascading Style Sheets hiding, and client-side JavaScript hiding are not access controls

## Publication contract

The public deck is cumulative from slide 1 through the requested cutoff `N`. The number is the Reveal.js slide number for the whole source deck, not a session number, session-slide shorthand, identifier, filename, or `<!-- Slide N -->` comment

The input accepts either form:

```text
88
88/117
```

The numerator must be an integer from 1 through the actual source slide total `T`. If a denominator is supplied, it must equal `T` exactly. The workflow fails before deployment for malformed input, whitespace, zero, negative values, decimals, multiple slashes, a numerator above `T`, or a denominator mismatch

The deck must stay flat. The slicer identifies direct top-level `<section>` elements inside `.reveal .slides` in document order. If it finds nested `<section>` elements that would create vertical Reveal.js slides, it fails closed with an actionable error. Vertical-stack numbering is not supported

Session markers are authoring structure for navigation and source validation:

```html
<!-- COURSE SESSION CONTENT START -->
<!-- SESSION NN START -->
<!-- SESSION NN END -->
<!-- COURSE SESSION CONTENT END -->
```

They must remain paired, unique, ordered, and ascending in the source deck. They do not define public or PDF boundaries, and a public cumulative cutoff may end in the middle of a session

## PDF contract

The optional `pdf_through_slide` input accepts these exact forms:

```text
M
M/T
A - B/T
```

Blank means that no PDF HTML is built, no PDF is rendered or validated, and no PDF artifact is uploaded. Blank is the only skip state. The range form requires one ASCII space on each side of the hyphen

`M` and `M/T` select the cumulative range from slide 1 through `M`. `A - B/T` selects source slides `A` through `B`, inclusive, in original source order. The denominator must equal the actual source slide total `T`, and `B` cannot exceed the public cutoff `N`

PDF artifacts use three-digit start and end numbers:

```text
<pdfPrefix>_001-088
<pdfPrefix>_001-088.pdf
<pdfPrefix>_055-072.pdf
```

`pdfPrefix` comes from `deck.config.json`, letters, digits, `_`, or `-` only, for example `MLOps_Slides`

If the deck exceeds 999 slides, numbering expands rather than silently truncating

## Workflow inputs and evidence

The only public workflow is the manual `release-slides` workflow

```text
publish_through_slide: 88/118
pdf_through_slide: 88/118
```

Before the deployment job becomes eligible, the build job writes validated evidence to the workflow summary:

- Checked-out commit
- Actual source slide total
- Static source slide count and runtime Reveal.js source count
- Requested public cutoff
- Published range `1..N`
- Last included slide number and its source identity
- First excluded slide number and its source identity, or `none`
- Requested PDF input, or `skipped`
- Normalized PDF source range and selected slide count, or `skipped`
- Validation result

The identity comes from the checked-out source, using the slide `id` or the best available heading. It is not hard-coded workflow text

The operator sequence is:

1. Run the manual `release-slides` workflow from the approved commit
2. Inspect the build summary and confirm the cutoff, identities, source total, validation result, and PDF state
3. Approve the gated `deploy` job only when the evidence is correct
4. Reject the deployment when the evidence is wrong or incomplete
5. Verify the stable student URL after an authorised deployment

## Native deployment protection

The deploy job must retain the native GitHub Actions environment reference:

```yaml
environment:
  name: github-pages
```

The professor must configure a required-reviewer protection rule under `Settings > Environments > github-pages`. Enable `Prevent self-review` when available if governance requires a second person rather than the workflow initiator

Required-reviewer availability can depend on the GitHub plan and repository visibility. Do not claim this safeguard is active from the workflow file alone. Confirm it independently in GitHub settings, or report `MANUAL ACTION REQUIRED` or `UNAVAILABLE ON CURRENT PLAN`

Changing the environment rule is a manual action by the professor. Agents never change GitHub settings or trigger a release

## Exact validation sequence

The workflow must complete every applicable step before uploading a Pages artifact or starting the environment-gated deployment:

1. Check out private `main` at the workflow commit and record the commit hash
2. Parse the source HTML structurally and count direct top-level Reveal.js slides
3. Validate the public input and optional PDF input against the actual source total
4. Confirm supplied denominators equal the actual source total
5. Confirm the PDF end slide does not exceed the public cutoff
6. Build public HTML containing exactly slides `1..N`
7. Build PDF HTML containing exactly the requested slides `1..M` or `A..B` only when the PDF input is non-blank
8. Copy the runtime assets required by the retained slides
9. Validate the source deck through local Hypertext Transfer Protocol (HTTP), including runtime `Reveal.getTotalSlides()`
10. Validate the generated public HTML through local HTTP, including runtime `Reveal.getTotalSlides() == N`
11. When requested, render the PDF and require a non-zero file with exactly the selected slide count in pages
12. Confirm generated work did not modify source `index.html`
13. Write the release evidence summary
14. Upload the validated optional PDF and Pages artifacts

The static parser and runtime Reveal.js count must agree for the source deck. A disagreement fails the release. The generated artifact must contain no excluded slide sections or future work-in-progress slide HTML, must retain complete document closing markup and `Reveal.initialize`, must resolve local assets, and must produce zero browser console and page errors

## Failure behavior

The deploy job depends on the successful build and validation job. Stop on any input, structural parser, denominator, slice, runtime count, asset, browser, fitting, PDF, page-count, or source-integrity failure

Do not upload a Pages artifact after a failed validation. Correct the source or workflow on private `main`, obtain approval again when the approved source changes, and rerun the manual workflow from the intended commit

## Recovery and rollback

If a live release is wrong or exposes work in progress:

1. Unpublish the bad deployment if necessary
2. Correct the source or workflow on private `main`
3. Rerun the manual `release-slides` workflow from the approved commit
4. Inspect the new evidence summary
5. Approve the gated deployment only after the evidence is correct
6. Verify the stable URL and record the delivered commit

Unpublishing, repository settings changes, workflow execution, deployment, pushing, tagging, and other public release actions require explicit professor authorisation

## Known media exposure

The workflow deploys the full `media/` directory. Images used only by unreleased slides may be reachable through guessed URLs even though their HTML is removed. Keep sensitive or unreleased media out of `media/` until release, or approve a media-pruning step for the course

## First-time setup for a new course repository

1. Set `pdfPrefix` and, after the first release, `publicUrl` in `deck.config.json`
2. In GitHub, set Pages to deploy from GitHub Actions, not from a branch
3. Add a required-reviewer rule to the `github-pages` environment where the plan allows it
4. Keep the repository private if work in progress must stay private; Pages serves only the validated artifact
5. Run the workflow once with a small cutoff and verify the URL

## Rules for future agents

- Read this file before any public release, deployment, PDF handover, or visibility change
- Keep the stable cumulative student URL unchanged
- Keep slide aliases resolvable: the slicer stages a canonical copy when an alias's target falls outside the selection
- Keep paired session markers inside the course sentinels in ascending order
- Use the actual Reveal.js slide sequence as the only publication boundary
- Use `scripts/release_slice.py` for structural counting, input validation, and cumulative or explicit-range slicing
- Use `scripts/release_pdf.py` for local HTTP browser validation, PDF rendering, and page-count validation
- Preserve manual `workflow_dispatch` as the only workflow trigger
- Keep build and validation before Pages artifact upload
- Keep deployment in the dependent `deploy` job with the `github-pages` environment
- Do not use query-string, Cascading Style Sheets, or client-side hiding as access control
- Do not deploy, push, tag, unpublish, or change GitHub settings without explicit professor authorisation
- Do not weaken immutable action pins or workflow permissions without approval and current official verification
- Record genuinely reusable tooling improvements in `template_improvements.md`
