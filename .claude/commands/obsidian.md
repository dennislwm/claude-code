---
description: Translate natural language requests into Obsidian CLI commands and run them
allowed-tools: Bash
---

Use the Obsidian CLI to answer `$ARGUMENTS`.

## Step 1: Discover available commands

Run `obsidian --help`. If that fails, try `/Applications/Obsidian.app/Contents/MacOS/Obsidian --help`.

If both fail, check:
1. Obsidian is running (CLI requires it).
2. CLI enabled: Settings > General > CLI > "Register CLI" (needs v1.12.4+ and installer v1.11.7+; re-download DMG to update installer).
3. PATH: add `export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"` to `~/.zprofile` or `~/.bash_profile`. Fish: `fish_add_path /Applications/Obsidian.app/Contents/MacOS`.
4. After quit/relaunch: toggle CLI off/on in Settings and re-register.

## Step 2: Interpret, classify, and execute

**If `$ARGUMENTS` starts with a known command** (`daily`, `search`, `tags`, `backlinks`, `links`, `orphans`, `unresolved`, `files`, `folders`, `read`):
- Write/destructive: state the exact command and ask for confirmation before running.
- Read-only: run it directly.

**If `$ARGUMENTS` is a natural language request**, translate to the best-fit command, apply the same classification, and run it with a one-line explanation.

**If `$ARGUMENTS` is empty**, run `obsidian daily`.

**Write/destructive commands** (require confirmation): `create`, `daily` (new note only), `daily:append`, `daily:prepend`, `append`, `move`, `properties:set`, `properties:remove`, `delete`, `plugin:enable`, `plugin:disable`, `plugin:reload`, `eval`, any command with `--overwrite`.

## Command Reference

| Syntax | Purpose |
|---|---|
| `daily` | Open today's daily note |
| `daily:read` | Read today's daily note |
| `daily:open yesterday\|tomorrow` | Navigate adjacent daily notes |
| `search <query>` | Full-text search across vault |
| `tags` | List all tags in vault |
| `tags --tag=<name>` | List files with a specific tag |
| `backlinks file=<name>` | Incoming links to a file |
| `links file=<name>` | Outgoing links from a file |
| `orphans` | Files with no incoming links |
| `unresolved` | Broken/unresolved links |
| `files` | List files in vault |
| `folders` | List folders in vault |
| `read file=<name>` | Read a note's content |

**Useful flags:** `vault=<name>`, `format=json|tsv|csv|md`, `total`, `open`

## After running

- `search` with zero results: suggest broadening the query or trying `tags`.
- `orphans` or `unresolved` with results: offer to open the first file.
- `daily`: suggest `daily:open yesterday` or `daily:open tomorrow`.
