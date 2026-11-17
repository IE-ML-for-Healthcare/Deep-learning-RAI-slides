# Multi-Agent Git Runbook

Step-by-step commands behind the Multi-Agent Coordination rules in `AGENTS.md`. Read this before your first commit in a session where another agent might also be active.

## Why this exists

Agents from different vendors (Codex, Claude Code, GitHub Copilot, and others) can work on this repository at the same time, often without seeing each other's sessions. There is no lock server and no automatic review between commits. Plain Git worktrees, branches, and careful merges are the coordination layer. Skipping them is how work gets silently overwritten.

Known failure modes seen in course repositories that use this setup:

- A conflict-free merge silently kept an old revert over a newer content fix
- A "cosmetic" commit reintroduced old wording over another agent's fix
- Stale 0-byte `.lock` files blocked commits and looked like a live agent
- The open working file drifted from the committed version because of uncommitted edits in the `main` checkout

## 1. Start in your own worktree

Follow `AGENTS.md`, section Temporary files and cleanup. Create a worktree only when isolation is needed. Configure a tool's built-in feature to use the main checkout's `tmp/worktrees/`, or use Git directly; never accept a default path outside `tmp/`

Run this discovery once at the start of a working session. During consecutive small fixes in the same checkout, refresh status and the affected diff; repeat worktree and history discovery only when checkout, branch, ownership or concurrency changes. Existing isolation and preservation rules still apply

From the main checkout root:

```bash
git --no-optional-locks worktree list              # see who else is working
git --no-optional-locks status --short             # uncommitted work in main belongs to someone else
git --no-optional-locks log --all --oneline -15    # recent commits on every agent branch
git worktree add tmp/worktrees/<topic> -b <agent>/<topic> main
```

Use an isolated worktree for concurrent implementation. Read-only checks and cleanup do not require another worktree

The VS Code main lane works directly on `main`. Direct maintenance may also use `main` when the professor requests it or no other writer is active. Confirm the VS Code lane rather than assume it:

```bash
echo "$TERM_PROGRAM $VSCODE_PID"      # bash: expect "vscode" or a process id
```

```powershell
"$env:TERM_PROGRAM $env:VSCODE_PID"   # PowerShell
```

If neither is set, do not assume the VS Code lane; apply the direct-maintenance and concurrent-isolation rules above

- Branch names follow `<agent>/<topic>`, for example `claude/session-03-compare` or `codex/fit-fix`
- Reuse the same branch across a multi-turn task; do not create a new branch per turn
- Never reuse another agent's branch or worktree directory

Working directly in the professor's `main` checkout is allowed only when the professor asks for it or no other agent is active. Say so in your report, because the working tree may then contain uncommitted edits.

## One-time setup: the hooks

The repository ships a `pre-commit` hook in `.githooks/` that blocks direct commits on `main`. Enable it once per clone; linked worktrees share the setting:

```bash
git config core.hooksPath .githooks
```

The hook allows commits on `main` from the VS Code main lane, detected by `TERM_PROGRAM=vscode` or `VSCODE_PID`. Agents never bypass it with `--no-verify`. The professor can override it anywhere with `ALLOW_MAIN_COMMIT=1 git commit ...` (PowerShell: `$env:ALLOW_MAIN_COMMIT=1; git commit ...`). Fast-forward merges do not run the hook.

The same folder ships a `commit-msg` hook, the commit scope guard (section 9). It needs Python on the path and runs on every commit on an agent branch in every worktree. It is waived on `main`, where the professor and the VS Code main lane commit directly. The GitHub workflow applies the same waiver: commit scope runs only on pull requests, in a separate job that cannot stop product QA from running. Ordinary VS Code or Copilot-generated messages on `main` need no slide identifiers, Conventional Commits format, or agent trailers

Gates by lane:

| Gate | VS Code main lane (`main` checkout) | Any other agent (own worktree and `<agent>/<topic>` branch) | Professor by hand |
| --- | --- | --- | --- |
| `pre-commit`, no direct commits on `main` | Allowed, detected by `TERM_PROGRAM=vscode` or `VSCODE_PID` | Enforced; commit on your branch | Override with `ALLOW_MAIN_COMMIT=1` |
| `commit-msg`, commit scope guard | Waived on `main` | Enforced; name every changed slide `id` | Waived on `main` |
| `qa` workflow in CI (static QA, downloads, unit tests, browser QA) | Runs on push to `main` | Runs on pull request | Runs on push to `main` |
| Separate `commit_scope` job in CI | Waived for pushes to `main` | Enforced on pull requests | Waived for pushes to `main` |
| Browser QA and screenshot review (`instructions/browser_qa.md`) | Required before reporting | Required before reporting; state it if the environment cannot run Chromium | Recommended |
| `--no-verify` | Never | Never | Professor decision only |

The `main` waiver covers commit-message policy locally and in CI. It never waives product QA. Agents still validate and report their work before handing it back

## 2. Work loop

```bash
git status                            # confirm you are in your own worktree and branch
git diff                              # read back exactly what changed
python scripts/validate_changes.py    # required checks must pass before an agent commit
git add <specific files>              # never git add -A or git add .
git commit -m "feat(session-06): <what changed and why>" -m "Co-Authored-By: <agent name> <email>"
```

- If a commit reverts or overrides an earlier commit, name that commit hash and the reason in the message
- On agent branches, commit messages must let another agent understand the intent from `git log` alone
- On agent branches, use Conventional Commits subjects (`feat`, `fix`, `docs`, `chore`) with the session or slide `id` as scope
- Refer to slides by `section` `id`, never by slide number

## 3. Hand back or land work

The professor is the sole approver. Landing on `main` happens only after approval.

```bash
git log --oneline -1 main             # main moves between turns, check it now
git merge main                        # bring main into your branch, in your own worktree
grep -n "<distinctive fragment you changed>" index.html
```

A merge with no conflicts is not proof nothing was lost. When your branch and `main` touched the same lines, grep for your content after every merge.

To land, the preferred standard path is a fast-forward merge in the `main` checkout, when its working tree is clean:

```bash
git -C <main-checkout> status --short    # must be empty
git -C <main-checkout> merge --ff-only <agent>/<topic>
```

If the `main` checkout has uncommitted work from someone else, do not touch it. Either hand the branch name to the professor, or move the `main` ref with a compare-and-swap that fails if `main` moved:

```bash
OLD=$(git rev-parse main)
NEW=$(git rev-parse <agent>/<topic>)
git merge-base --is-ancestor "$OLD" "$NEW" && git update-ref -m "<reason>" refs/heads/main "$NEW" "$OLD"
```

This moves only the branch pointer. The files open in the `main` checkout do not change until that checkout is refreshed, so never tell the professor "you should see it now" without checking:

```bash
git -C <main-checkout> status --short
git -C <main-checkout> diff --stat -- index.html
```

## 4. Line endings

`.gitattributes` normalises text files to LF in the repository. Windows checkouts may show CRLF on disk.

```bash
git diff --ignore-all-space --stat    # separates real edits from line-ending noise
git ls-files --eol index.html         # shows repository and working-tree endings
```

When writing a file directly, keep its existing line-ending convention. Do not introduce mixed endings.

## 5. Stale locks

On OneDrive-synced folders, Git can leave 0-byte `.lock` files behind with no process running.

```bash
find .git -name "*.lock" -size 0 -ls
```

Prevent them by running read-only commands with `git --no-optional-locks`, which never writes the index.

If the file is 0 bytes, old, and no Git process is running, remove it and retry. If removal fails with "Operation not permitted", request delete permission; do not bypass with `--no-verify`.

## 6. Housekeeping

After the task reaches `main` and no session uses its worktree, verify it has no uncommitted files or unique commits. Inspect ignored files too, remove your disposable artifacts, then use `git worktree remove <absolute-task-worktree>` and `git branch -d <merged-task-branch>`. This is standing cleanup authorization for your completed merged work, not permission to discard another session's files or unfinished work. Follow `AGENTS.md`, section Temporary files and cleanup, and report any remaining files or permission failure

```bash
git worktree prune --dry-run          # lists worktree records whose folders no longer exist
```

Prune only after the professor confirms those worktrees are finished, and run it from Windows Git: a Linux sandbox cannot see `C:/` worktree paths and will judge them missing.

## 7. If another agent reverted your work

1. Ask the professor whether the revert was intentional before re-applying anything
2. If not, merge `main` into your branch first to keep the other agent's genuine improvements
3. Re-apply only your specific content with targeted edits, never a whole-file overwrite
4. Report the reverting commit and what you did
5. If it happens a third time, stop and flag it as a coordination problem

## 8. Report

Every executor report adds: agent, worktree path, branch, commit hash, whether the change reached `main`, and any lock, revert, or dirty-worktree issue that needs professor attention.

## 9. Commit scope guard

A whole-file copy of `index.html` from a stale worktree can revert other agents' slides without a merge conflict. The guard flags changed slides omitted from an agent's message. It helps catch accidental scope drift, but cannot prove intent or detect an overwrite when the message names every affected slide

- Rule for agent branches: a commit that changes a slide in `index.html` must name that slide `id` in its message; direct `main` commits are exempt
- A slide counts as changed when its top-level `<section>` differs, or when a CSS rule scoped to its `id` differs; whitespace, comments, and line endings are ignored
- Name slides in the subject (`fix(topic-three-layers): ...`) or in a trailer: `Slides: id-one, id-two`
- Deliberate deck-wide change: `Slides: all (<reason of at least 8 characters>)`
- Enforced twice for agent branches: the `commit-msg` hook blocks the commit locally, and the separate `commit_scope` job runs `python scripts/check_commit_scope.py --range <base>..<head>` on pull requests
- Only commits made after the guard landed are judged; older history is never flagged
- When it fails and you did not mean to change the listed slides, your `index.html` is stale: merge the latest `main` into your branch, redo only your own change, and commit again; never copy the file from another worktree
- Check a range by hand with `python scripts/check_commit_scope.py --range main..HEAD --list`

Before committing, inspect `git diff` against the approved scope. After committing on an agent branch, run `python scripts/check_commit_scope.py --range main..HEAD --list` and correct any unintended changes before handoff. Do not widen the message just to silence the guard

Limits: JavaScript and class-only CSS changes are not slide-scoped, so the guard does not see them; `--no-verify` skips the local hook, but pull-request CI still reports the commit. Running `--range` manually is always strict, even when the current branch is `main`. Requiring the `qa` and `commit_scope` checks before merging is a GitHub branch protection setting, which only the professor can change
