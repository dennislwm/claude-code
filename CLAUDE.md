# Project Instructions

<!-- plumb:start -->
## Spec/Test/Code Sync (Plumber)

This project uses **Plumber** to keep the spec, tests, and code in sync.
Plumber replaces the plumb CLI — use `plumber.py` subcommands and `make`
targets instead of `plumb` commands. The plumb skill is being phased out.

- **Spec:** doc/spec.md
- **Tests:** app/tests/
- **State:** `.plumb/` (decisions.jsonl, gaps.json, config.json)

### When working in this project:

- Run `cd app && make status` before beginning work to understand current alignment.
- Run `cd app && make diff` before committing to preview pending decisions.
- When `git commit` is intercepted by the pre-commit hook, **use `AskUserQuestion`**
  to present each pending decision via the native multiple-choice UI. Options:
  Approve, Approve with edits, Ignore, Reject.
  **NEVER approve, reject, or edit decisions on the user's behalf.** This is
  non-negotiable.
- After all decisions are resolved, run `cd app && make sync` to update the spec
  and generate tests. Stage the sync output (`cd app && make stage`), then
  re-run `git commit`. Draft the commit message **after** decision review.
- Use `cd app && make coverage` (or `make coverage-semantic`) to identify what
  needs to be implemented or tested next.
- Never edit `.plumb/decisions.jsonl` directly — use `plumber.py` subcommands.
- Treat the spec markdown files as the source of truth for intended behavior.
- Install the pre-commit hook once per repo: `cd app && make install-hook`
<!-- plumb:end -->
