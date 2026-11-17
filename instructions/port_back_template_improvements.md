# Port Back Template Improvements

Copy-paste prompt for porting approved reusable improvements from a course repository into this template. Run it in the template repository with any local coding agent, after the professor has approved the candidates.

```text
You are working in the IE SciTech Reveal.js template repository.
Task: port the approved reusable improvements from a course repository into this template.

First read:
1. AGENTS.md and CHANGELOG.md in this template
2. instructions/slide_rules.md, instructions/layout_playbook.md, instructions/review_checklist.md
3. The course repository template_improvements.md, and only the files its approved candidates name

Rules:
- Port only candidates with status "Approved for port-back"; list every other candidate as skipped with its status
- Port the mechanism, never the course: no titles, sessions, activities, wording, screenshots, media, datasets, URLs, or assessment content
- Generalise names, comments, and examples; replace course media with media/placeholders/
- Refactor while porting: one definition per pattern, palette tokens only, no vw units, no slide-number or date references, no workaround classes when the root cause can be fixed
- Keep index.html a generic starter deck and slide_patterns.html a gallery with one numbered example per pattern
- Update the owner instruction file for each rule, never two files
- Add or update tests for any tooling change
- Record the port in CHANGELOG.md with the candidate ids and any breaking changes for existing course repositories
- Never port automatically from unapproved candidates

Validation:
- python scripts/check_deck.py
- python scripts/sync_downloads.py --check
- python -m unittest discover -s tests
- scripts/check_browser_qa.py on index.html and on slide_patterns.html with --screenshots all, and inspect every changed pattern
- Confirm no course-specific string remains: grep for the course title, session numbers, and course media folders

Report:
1. Candidates ported, with files changed
2. Candidates skipped, with reasons
3. Breaking changes for course repositories and the migration step for each
4. Validation results
5. Then update the course repository template_improvements.md entries to "Ported", with the template commit
```
