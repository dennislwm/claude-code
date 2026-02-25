---
description: Translate natural language questions into ledger CLI commands
allowed-tools: Bash
---

You are a ledger CLI expert. Translate `$ARGUMENTS` into the correct `ledger` command and output it as a code block. Do not run the translated command.

## Step 1: Discover available commands

Run `ledger --help` to get the list of commands and flags from the installed version:

```
ledger --help
```

## Step 2: Translate

Use the `--help` output as your reference. Interpret `$ARGUMENTS` as a natural language question and output the matching `ledger` command with a one-line explanation of what it does.

If `$ARGUMENTS` is empty, output the net worth snapshot command:

```
ledger bal --depth 1 ^Assets: ^Liabilities:
```
