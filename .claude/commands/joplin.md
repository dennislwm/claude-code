---
description: Translate natural language requests into Joplin CLI commands and run them
allowed-tools: Bash
---

Use joplin-butler to answer `$ARGUMENTS`.

## Step 1: Verify prerequisites

Run `joplin-butler --help`. If that fails, give the user these instructions:

1. Install joplin-butler: `go install github.com/Garoth/joplin-butler@latest`
2. Ensure Joplin Desktop is running with Web Clipper enabled: Settings > Web Clipper > Enable Web Clipper Service.
3. Ensure `JOPLIN_TOKEN` is set: copy the token from Settings > Web Clipper Options and run `export JOPLIN_TOKEN=<token>`.
4. Ensure `JOPLIN_PORT` is set (default 41184): `export JOPLIN_PORT=41184`.

Check Web Clipper is reachable:
```
curl -s "http://localhost:${JOPLIN_PORT:-41184}/ping"
```
If it does not return `JoplinClipperServer`, ensure Joplin Desktop is running with Web Clipper enabled.

## Step 2: Interpret, classify, and execute

All joplin-butler commands require the token passed via env or flag. Use:
```
JOPLIN_TOKEN="${JOPLIN_TOKEN}" JOPLIN_PORT="${JOPLIN_PORT:-41184}" joplin-butler <command>
```

**If `$ARGUMENTS` starts with a known command** (`notes`, `note`, `get folders`, `create note`, `create resource`, `delete`):
- Write/destructive: state the exact command and ask for confirmation before running.
- Read-only: run it directly.

**If `$ARGUMENTS` is a natural language request**, translate to the best-fit command, apply the same classification, and run it with a one-line explanation.

**If `$ARGUMENTS` is empty**, run `joplin-butler notes` to list recent notes.

## Command Reference

| Syntax | Purpose |
|---|---|
| `notes` | List recent notes |
| `note <id>` | Read a note by ID |
| `get folders` | List all notebooks |
| `create note --title <title> --body <body> --parent <folder-id>` | Create a new note |
| `create resource <file-path>` | Upload a file as a resource |
| `delete note/<id>` | Delete a note by ID |

## After running

- `notes` with no results: suggest checking that Joplin Desktop is open and synced.
- `get folders` result: suggest using a folder ID with `create note --parent`.
