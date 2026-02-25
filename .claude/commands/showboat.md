---
description: Build executable demo documents that prove agent work using showboat CLI
allowed-tools: Bash
---

Use `showboat` to build a proof-of-work demo document for `$ARGUMENTS`.

## Step 1: Check availability

Run to confirm showboat is installed and get its version:

```
uvx showboat --version
```

If this fails, `uvx` is not available — run `make status` to check whether it is installed on this machine.

## Step 2: Interpret the request

**If `$ARGUMENTS` starts with a known command** (`init`, `note`, `exec`, `image`, `pop`, `verify`, `extract`), run it directly:

```
uvx showboat $ARGUMENTS
```

**If `$ARGUMENTS` is a task description**, scaffold a full demo document using the workflow below.

**If `$ARGUMENTS` is empty**, output the command reference table.

## Workflow for building a demo

### 1. Initialize the document
```
uvx showboat init demo.md "Title of your demo"
```

### 2. Document each step (repeat as needed)
```
uvx showboat note demo.md "What this step demonstrates"
uvx showboat exec demo.md bash "command to run"
```

### 3. Verify the proof
```
uvx showboat verify demo.md
```

## Command Reference

| Command | Syntax | Purpose |
|---|---|---|
| `init` | `init <file> <title>` | Create a new demo document |
| `note` | `note <file> [text]` | Append commentary text (also accepts stdin) |
| `exec` | `exec <file> <lang> [code]` | Run code and capture output |
| `image` | `image <file> <path>` | Embed an image from a path or markdown syntax |
| `pop` | `pop <file>` | Remove the most recent entry |
| `verify` | `verify <file> [--output <new>]` | Re-run all code blocks and validate outputs |
| `extract` | `extract <file> [--filename <name>]` | Emit CLI commands to recreate the document |

## Global options

| Flag | Purpose |
|---|---|
| `--workdir <dir>` | Set execution directory (default: current) |
| `--version` | Show version |

## After running

Based on the command executed, offer relevant follow-up actions:

- **After `init`**: suggest adding a `note` then `exec` to begin documenting steps
- **After `exec`**: suggest `verify` to confirm the output is reproducible
- **After `verify` (pass)**: document is ready to share as proof of work
- **After `verify` (fail)**: use `pop` to remove the stale entry, then re-run `exec` to capture fresh output
- **After `extract`**: pipe the output to a shell script to rebuild the document from scratch
