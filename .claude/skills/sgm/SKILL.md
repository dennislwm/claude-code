---
name: sgm
description: Use the sqlite-graph-memory CLI tools (sgm-index, sgm-doctor, sgm-stats) to index, check and install sgm memory for a notes folder. Use when the user types /sgm, asks to build or refresh the sgm index, asks why memory_recall returns nothing or the wrong notes, or wants to install sgm.
---

# sgm

The `memory_recall` MCP tool only searches. Indexing and health checks are CLI tools, run from the wiki root.

## Tools

| Command | Use |
|---|---|
| `BRAIN_INDEX_DIR=.sgm/index sgm-index .` | Build or refresh the index. Re-embeds only new or changed notes. `--full` forces a rebuild. |
| `sgm-doctor` | Check Python, models and index. No arguments. |
| `sgm-stats <notes_dir>` | Link-graph health numbers. `--json` for machine output. |
| `sgm-turnstate-show` | Read the optional per-turn ledger (`--session`, `--n`, `--stats`). |
| `sgm-turnstate-hook` | The ledger Stop hook command. Not installed. |
| `sgm-ask`, `sgm-mcp` | Do not run by hand. `sgm-ask` writes `_brain_answer.txt` into the current folder and has no `--help`; `sgm-mcp` starts the stdio server and never returns. |

## Rules

- Run `sgm-index .` from the repo root only, always with the inline `BRAIN_INDEX_DIR=.sgm/index` prefix. A Claude session started before the `~/.bash_profile` change keeps the old environment, and the index then lands in the old absolute path instead of under the repo. Before indexing, `echo $BRAIN_INDEX_DIR` shows what the session has.
- Ask the user to confirm before every `sgm-index` run, because it takes minutes (a first run on a new machine also downloads about 1.5 GB). Say the folder and the file count first. Run it only after a yes. `sgm-doctor` and `sgm-stats` need no confirmation.
- One index holds one notes folder. Indexing a different folder with the same `BRAIN_INDEX_DIR` replaces the first.
- The index is not refreshed automatically. Run `sgm-index .` after adding or editing notes.
- The index holds copies of note text. On the first run in a git repo (no `.sgm/index` before `sgm-index .`), if `git -c core.excludesFile=/dev/null check-ignore -q .sgm/index/_brain_e5.npy` exits 1, append `.sgm/` to the repo `.gitignore`. The global ignore does not count: it is absent on other machines and in CI. Later runs skip this.
- A folder starting with a dot is never indexed. There is no exclude option.
- If `memory_recall` errors with a missing index, there is no `.sgm/index` in the current project: run `sgm-index .`.

## Install (one-off per machine)

1. `uv tool install --python 3.12 'sqlite-graph-memory[lite]'`
2. `claude mcp add -s user sgm -e BRAIN_INDEX_DIR=.sgm/index -e SGM_MODEL_CACHE=$HOME/.sgm/models -e TURNSTATE_DB=$HOME/.sgm/turnstate.db -- sqlite-graph-memory`
3. In `~/.bash_profile`: `export BRAIN_INDEX_DIR=.sgm/index` and `export SGM_MODEL_CACHE=$HOME/.sgm/models`.
4. Add `.sgm/` to `~/.config/git/ignore`.
5. Per wiki: `cd <wiki> && sgm-index .` (the first run also adds `.sgm/` to that repo's `.gitignore`, per Rules). The first run downloads about 1.5 GB into `~/.sgm/models`.

Check: `claude mcp list` shows `sgm` connected, then `sgm-doctor`. A new Claude session is needed after registering.

## Known quirk

`sgm-doctor` warned "Models not downloaded yet" although recall works. I believe it checks the Hugging Face cache, not `SGM_MODEL_CACHE`. This is unverified.
