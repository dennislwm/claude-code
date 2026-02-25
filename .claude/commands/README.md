# Skills Registry

Skills are slash commands invoked in Claude Code as `/skill-name [arguments]`.
They are defined as markdown files in this directory and discovered automatically.

Run `make help` from the project root to list all available skills and agents.

## Common Flag

All `gh run` skills inherit the `--repo` flag:

```
-R, --repo [HOST/]OWNER/REPO   Select another repository
```

## gh run Skills

| Skill | Description |
|---|---|
| `/gh-run-view` | View a summary or logs of a workflow run |

Additional `gh run` skills (`cancel`, `delete`, `download`, `list`, `rerun`, `watch`) are planned.

## ledger Skills

| Skill | Description |
|---|---|
| `/ledger` | Run ledger CLI reports for balance, register, and spending analysis |
