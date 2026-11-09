---
name: gpt
description: Ask Codex to do a task in any repo, including a sibling repo. Use only when the user types /gpt.
---

Route by the first word of the user's args.

## Help

If the args are empty or the first word is `help`, print help in the reply. Do not run `gpt.sh`.

Write the help from this file. Show three forms: `/gpt [--read] [--fresh] [--wait] REPO "prompt"`, `/gpt help`, and `/gpt setup`.

Explain the flags as described in the Run a task bullets. Include the session-cap rule from below.

## Setup

If the first word is `setup`, use this skill-based flow.

First, glob `~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs`. No match means a new device. Any match means an existing device. State the verdict (new or existing) as `Verdict: new device.` or `Verdict: existing device.` in one line; the user may override it.

All missing installs, including `git`, `jq`, Node, and the Codex CLI, are report-only; print the fix command for the user to run, but do not run install commands. The one exception is the Ponytail plugin install in the existing-device flow.

### New device

Return this ordered, report-only checklist:

1. Install the Codex plugin. Point to the plugin's own installation instructions. Do not invent an install command.
2. Check for `git`. Report if missing.
3. Check for `jq`. Report if missing.

Tell the user to rerun `/gpt setup` after completing the checklist.

### Existing device

Offer every fix one at a time with its exact command and ask in plain text: `Apply fix N? yes / no`. Claude runs an approved command, never a Codex task, because its sandbox cannot write under `~/.codex`.

Follow these steps in order:

1. Load and follow the `codex:setup` skill for Codex CLI installation and login. Do not re-check those yourself.
2. Check for `git` and `jq`. Report if missing.
3. Check skill reachability. Run `readlink ~/.claude/skills` and report its target. If the path is a real directory instead of a symlink, flag it as a copy. Confirm that it resolves, `~/.claude/skills/gpt/SKILL.md` and `gpt.sh` exist, and `gpt.sh` is executable. Offer fixes only for a broken or missing `~/.claude/skills` symlink and a missing executable bit. The symlink fix is an intentional exception to the repo `CLAUDE.md` rule never to modify `~/.claude`, because the user approves each fix.
4. Check Codex skills. Required skills are `jev` and `why`; every other direct folder under `~/.claude/skills`, except `synced`, is optional. For each required skill, resolve `~/.claude/skills/<name>`. Require a `SKILL.md` whose frontmatter has `name` and `description`. If anything exists at `~/.codex/skills/<name>`, including a broken symlink, report it and never replace it. Otherwise offer `ln -s <resolved target> ~/.codex/skills/<name>`. For each optional skill, only report whether it is linked into `~/.codex/skills`; never offer a link.
5. Check Codex global instructions. Codex reads them only from `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md`. If either exists, report it and never replace it; an override takes precedence. Otherwise, if `~/.claude/CLAUDE.md` resolves to an existing file, offer `ln -s <resolved target> ~/.codex/AGENTS.md`. Require that nothing exists at the destination, neither file nor symlink. The global file has Claude-specific parts that Codex cannot run.
6. Check Ponytail in Codex with `codex plugin list` (read-only). If the command fails, report that its state is unverified and offer nothing. If Ponytail is installed, report it only. If it is missing, offer two fixes in order: first `codex plugin marketplace add DietrichGebert/ponytail`; then, after it succeeds, run `codex plugin list`, read the plugin and marketplace names shown for Ponytail, and offer `codex plugin add <plugin>@<marketplace>`. The install may fetch a newer version than the Claude copy. Tell the user to review and trust Ponytail's lifecycle hooks in Codex's `/hooks` screen and start a new thread, because setup cannot do that.
7. Read and report on `~/.codex/config.toml`. If the config looks wrong or Codex calls fail, suggest the user run `codex doctor`; do not run it yourself.
8. List repos that already have Codex sessions. Read the first line of each `~/.codex/sessions/**/*.jsonl` file. Include the unique `cwd` values whose `originator` is `Claude Code`.

## Run a task

For any other first word, treat the args as a task invocation. A repo named `setup` or `help` must be written as `./setup` or `./help`.

Run `bash ~/.claude/skills/gpt/gpt.sh [--read] [--fresh] [--wait] REPO "prompt"`. The script runs Codex in the background by default and returns at once with a job ID and commands to check it; `--wait` runs it in the foreground.

Turn the user's words into the flags. Say which flags you chose and whether the run is background or wait before you run it.

- Codex can change files unless you pass `--read`. Pass `--read` only if the user asks for read-only.
- Pass `--fresh` only if the user asks for a new thread.
- Pass `--wait` to `gpt.sh` only if the user asks to wait for the result.
- If the repo is unclear, ask. Do not guess.
- If the request is vague, has several parts or asks for edits, load `codex:gpt-5-4-prompting` and tighten the prompt first. Skip it for a short, clear request.

A new thread is allowed only in a repo with no sessions, or once, from a read thread to a write thread. After a write thread exists, no new thread is allowed.

- A `--read` call resumes the write thread if one is the latest. Read-only is then a request in the prompt, not a block.
- If the script prints `STOP` (exit 4), show it to the user and stop. Do not retry, do not change flags to get around it, and do not run `codex archive` or `codex delete` yourself. Give the user the commands the script prints.
- The script never deletes a session.

After the run:

- Show the user the `before` and `after` lists the script prints. A background run cannot print `after`; when the job finishes, run `git -C REPO status --short` and show that list.
- Show Codex's reply as `codex:codex-result-handling` describes. If Codex fails, report the error and stop. Do not do the task yourself.
- `/codex:status` in a Claude session does not list these jobs. Use the `jobs:` line the script prints.
- You cannot change Codex's sandbox. `~/.codex/config.toml` is for the user to edit.
