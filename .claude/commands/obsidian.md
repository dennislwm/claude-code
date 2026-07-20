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

**Write/destructive commands** (require confirmation): `create`, `daily` (new note only), `daily:append`, `daily:prepend`, `append`, `move`, `properties:set`, `properties:remove`, `delete`, `plugin:enable`, `plugin:disable`, `plugin:reload`, `eval`, any command with `--overwrite`, and any mid-file change (see **Write operations** below -- apply it via `create overwrite`, not the Edit tool).

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

## Write operations

Writes hit irreplaceable user data. Confirm before every write, and stop at the first rung.

0. **Target first.** Address every note by its full relative path *and* `vault=<name>` — never a bare filename. Bare names collide across the vault's JD systems (`file="00.00 Index.md"` can resolve to the wrong section). Resolve the exact path with `obsidian files | grep` before any write.
1. **Read-only** (`read`, `files`, `folders`, `search`, `tags`, `backlinks`, `links`, `orphans`, `unresolved`) — run directly, no confirmation.
2. **Append / prepend** — `append` / `prepend`. Confirm.
3. **New note** — `create path="<dir>/<Name>.md" content="..."`. Put the filename in `path=`, never `name=` (`name=` truncates dotted names: `34.04 coda-cli` → `34.md`). Confirm.
4. **Mid-file change / insert** — do NOT edit the vault file in place (many projects forbid the Edit/Write tools on vault files):
   a. `obsidian read` the note into a local temp file.
   b. Edit the temp (sed/awk or the Edit tool on the *temp*), diff it, confirm exactly the intended lines changed.
   c. `obsidian create overwrite path="<full path>" content="$(cat <temp>)"`.
   Read+Edit in place is acceptable only where a project explicitly permits editing vault files.
5. **Rename / move** — `move`. Confirm.

**Verify after every write:** `obsidian read` the target back and confirm it matches intent (right path, right content). Mandatory — the operator is error-prone.

**Guardrails:**
- Never probe a write command with `--help` — `create --help` *creates* a note. Read a command's flags from the top-level `obsidian --help` instead.
- Scope every operation to the vault section named in the request; never touch other sections.

## After running

- `search` with zero results: suggest broadening the query or trying `tags`.
- `orphans` or `unresolved` with results: offer to open the first file.
- `daily`: suggest `daily:open yesterday` or `daily:open tomorrow`.
