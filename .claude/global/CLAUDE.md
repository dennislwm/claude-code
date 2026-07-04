## Approach
- Read existing files before writing. Don't re-read unless changed.
- Thorough in reasoning, concise in output.
- Skip files over 100KB unless required.
- No sycophantic openers or closing fluff.
- No emojis or em-dashes.
- Do not guess APIs, versions, flags, commit SHAs, or package names. Verify by reading code or docs before asserting.
- If there are significant tensions, raise the issue to the user instead of making a decision based on assumptions.
- When deleting files tracked by git, use `git rm <file>` not `rm`. Plain `rm` leaves the deletion unstaged. If already deleted with `rm`, `git rm <path>` still stages it.
- For JSON parsing in CLI pipelines, use `jq` or tool-native `--jq` flags. Never pipe CLI output to `python3 -c` for JSON parsing -- interpreter pipelines trigger permission prompts. For base64-encoded content, pipe to `base64 -d`.
- `~/.claude/CLAUDE.md`, `~/.claude/commands/`, and `~/.claude/skills/` are symlinks into `02claude-code`. When asked to update the global CLAUDE.md or global commands/skills, always edit via the `02claude-code/` paths directly. The correct path is `02claude-code/.claude/global/CLAUDE.md` -- edits via `~/.claude/` write back through the symlink and obscure the real location.
- Before concluding a Python package (e.g. pytest) isn't installed, check for a project-local pipenv/venv (`pipenv --venv`, or look for a `Pipfile`) and try `pipenv run <command>` before declaring the tool unavailable. A system-only `pip3 list` / bare command check can miss a working project environment entirely.

## Design consultations
When presenting options or making choices, apply this ladder first and label the winner before showing alternatives: (1) does this need to exist at all? (2) already in this codebase? (3) stdlib? (4) native platform feature? (5) already-installed dependency? (6) can it be one line? (7) only then: minimum code that works. Never list options as neutral -- pick one. Never ask "A or B?" -- that forces the user to do evaluation work you should have done.

Before proposing an implementation approach, next step, design choice, or test plan, invoke the `ponytail:ponytail` skill (if installed) to get the lazy/minimal framing first, then present that to the user -- don't reason through the ladder silently and only invoke ponytail when asked. If the skill isn't available, apply the ladder above directly instead.
