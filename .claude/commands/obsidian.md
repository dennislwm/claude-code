---
description: Translate natural language requests into Obsidian CLI commands and run them
allowed-tools: Bash, Read, Edit
---

Use the Obsidian CLI to answer `$ARGUMENTS`.

## Step 1: Discover available commands (conditional)

**Skip this step if `$ARGUMENTS` maps to a command in the Command Reference table below.**

Only run `obsidian --help` when `$ARGUMENTS` contains an unknown command not in the reference table, or when a CLI call returns an error. If `obsidian --help` fails, try `/Applications/Obsidian.app/Contents/MacOS/Obsidian --help`.

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

**Write/destructive commands** (require confirmation): `create`, `daily` (new note only), `daily:append`, `daily:prepend`, `append`, `move`, `properties:set`, `properties:remove`, `delete`, `plugin:enable`, `plugin:disable`, `plugin:reload`, `eval`, any command with `--overwrite`, and any **replace/update** operation using `Read` + `Edit`.

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

## Replace/update content in a note

Use this path when `$ARGUMENTS` requires replacing or modifying an existing line (not just appending). Treat as a write operation — state the exact change and confirm before executing.

1. **Resolve vault path:** parse `~/Library/Application Support/obsidian/obsidian.json` with Python to extract the vault path:
   ```bash
   python3 -c "
   import json, sys
   d = json.load(open(sys.argv[1]))
   for v in d.get('vaults', {}).values():
       print(v.get('path', ''))
   " ~/Library/Application\ Support/obsidian/obsidian.json
   ```
   If multiple vaults are returned, match on the `vault=<name>` argument or ask the user to clarify.

2. **Construct note path:** use `obsidian files` or `obsidian daily:read` to identify the relative note path, then join with the vault path. Always quote paths (they may contain spaces).

3. **Edit:** use the `Read` tool to load current content, then the `Edit` tool to replace the target line. Confirm the exact change with the user before executing.

## After running

- `search` with zero results: suggest broadening the query or trying `tags`.
- `orphans` or `unresolved` with results: offer to open the first file.
- `daily`: suggest `daily:open yesterday` or `daily:open tomorrow`.
