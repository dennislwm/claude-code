---
description: View a summary or logs of a GitHub Actions workflow run
allowed-tools: Bash
---

View a GitHub Actions workflow run using `gh run view`.

Run the following command with the provided arguments:

```
gh run view $ARGUMENTS
```

If `$ARGUMENTS` is empty, run `gh run view` without arguments to interactively select a run.

## Supported flags

| Flag | Purpose |
|---|---|
| `<run-id>` | View a specific run by ID |
| `--verbose` | Show individual job steps |
| `--log` | View full log output |
| `--log-failed` | View only failed step logs |
| `--job <job-id>` | Scope output to a specific job |
| `--attempt <n>` | View a specific retry attempt |
| `--web` | Open the run in the browser |
| `--exit-status` | Exit non-zero if the run failed (for scripting) |
| `-R <OWNER/REPO>` | Target a different repository |

## After viewing

Based on the run status, offer the user relevant follow-up actions:

- **Failed**: suggest `gh run rerun --failed <run-id>`
- **In progress**: suggest `gh run watch <run-id>` to tail live progress
- **Succeeded**: suggest `gh run download <run-id>` if artifacts are present
