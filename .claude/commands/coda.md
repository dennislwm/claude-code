---
description: Translate natural language requests into Coda CLI commands and run them
allowed-tools: Bash
---

Use the Coda CLI to answer `$ARGUMENTS`.

## Step 1: Verify prerequisites

Run `coda --help`. If that fails, give the user these instructions:

1. From `~/fx-git-pull/02claude-code`, run `make setup` — this installs the wrapper, adds `~/.local/bin` to PATH, and prompts for the API key.
2. Or manually: create `~/.local/bin/coda` as a shell script that `cd`s into your `13coda-cli/app` directory and runs `exec pipenv run python coda.py "$@"`, then `chmod +x ~/.local/bin/coda` and ensure `~/.local/bin` is on your PATH.
3. Set your API key: `export CODA_API_KEY=<key>` or add it to `app/config.json`.

## Step 2: Interpret, classify, and execute

**If `$ARGUMENTS` starts with a known command** (see Command Reference):
- Write/destructive (`update-row`, `upsert-row`, `import-template`, `register-template`, `remove-template`): state the exact command and ask for confirmation before running.
- Read-only: run it directly.

**If `$ARGUMENTS` is a natural language request**, translate to the best-fit command, apply the same classification, and run it with a one-line explanation.

**If `$ARGUMENTS` is empty**, run `coda list-docs` to list available documents.

## Command Reference

`--doc` accepts a template name or Coda browser URL in addition to a raw document ID.

| Syntax | Purpose |
|---|---|
| `coda verify-auth` | Verify the configured API key |
| `coda list-docs` | List all owned documents |
| `coda get-doc --doc <id\|name>` | Get document metadata |
| `coda list-sections --doc <id\|name>` | List sections in a document |
| `coda list-tables --doc <id\|name>` | List tables in a document |
| `coda list-columns --doc <id\|name> --table <id>` | List columns in a table |
| `coda list-views --doc <id\|name>` | List views in a document |
| `coda list-controls --doc <id\|name>` | List controls in a document |
| `coda list-folders --doc <id\|name>` | List folders in a document |
| `coda list-formulas --doc <id\|name>` | List formulas in a document |
| `coda get-section --doc <id\|name> --section <id>` | Get a section |
| `coda get-column --doc <id\|name> --table <id> --column <id>` | Get a column |
| `coda list-rows --doc <id\|name> --table <id>` | List rows in a table |
| `coda update-row --doc <id\|name> --table <id> --row <id> --cells col=val,...` | Update an existing row |
| `coda upsert-row --doc <id\|name> --table <id> --cells col=val,... [--key-columns col,...]` | Insert or update a row |
| `coda export-table --doc <id\|name> --table <id> [--output file.csv]` | Export table to CSV |
| `coda export-template --doc <id\|name> [--output file.yaml]` | Export document as YAML template |
| `coda list-templates` | List registered template name→doc mappings |
| `coda register-template --name <name> --doc <id> [--description <desc>]` | Register a template |
| `coda remove-template --name <name>` | Remove a registered template |
| `coda import-template --file <path> [--variables VAR=val]` | Create a new document from a YAML template |

## After running

- `list-docs` with no results: suggest running `verify-auth` to confirm the API key is valid.
- `list-rows` with no results: suggest checking the table ID with `list-tables`.
- `import-template` success: note the returned document ID for use in future `--doc` arguments.
