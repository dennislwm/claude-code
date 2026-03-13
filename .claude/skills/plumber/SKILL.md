# Plumber Skill

Plumber keeps the spec, tests, and code in sync using Claude's native
reasoning — no plumb CLI required. All state lives in `.plumb/` using a
standalone schema compatible with the global `plumber` script.

The global helper script lives at `~/.local/bin/plumber` (stdlib only,
no pip install needed). Run it from any directory — it auto-discovers the
project root by walking up from CWD to find `.plumb/`.

> **Goal:** Plumber is designed to fully replace the plumb CLI. If you see
> instructions referencing `plumb` commands, translate them to the equivalent
> `plumber` subcommand listed in the Command Reference below.

## Before Starting Work

Run the session pre-flight to catch common failures in one pass:

```bash
# 1. Verify config paths
cat .plumb/config.json

# 2. Check requirement count (guard against wipe)
COUNT=$(python3 -c "import json; print(len(json.load(open('.plumb/requirements.json'))))" 2>/dev/null || echo 0)
echo "$COUNT requirements"
# If 0, re-parse (but verify result is non-zero before overwriting):
# plumber parse-spec

# 3. Generate gaps
plumber gaps

# 4. Report status
plumber status
```

Report a brief summary of requirement count, gap count, and pending decisions
before proceeding.

## Before Committing

Run `plumber diff` to preview pending decisions (existing + any that would be
created from staged changes). Report the count so the user is not surprised
during review.

## When git commit is Intercepted

If the pre-commit hook is installed (`plumber install-hook`), it fires
automatically on every `git commit`. When the hook exits non-zero:

> **Hook fix:** If the generated hook calls `python3 plumber.py` (common when
> `pipenv` is active), replace `.git/hooks/pre-commit` with the correct form
> that uses the global binary:
> ```sh
> #!/bin/sh
> # Plumber pre-commit hook
> cd "$(git rev-parse --show-toplevel)" || exit 1
> output=$(plumber hook 2>&1)
> exit_code=$?
> echo "$output"
> exit $exit_code
> ```

1. Parse the JSON from stdout — it has this shape:
   ```json
   {
     "pending_decisions": 2,
     "decisions": [
       {
         "id": "dec-abc123",
         "question": "...",
         "decision": "...",
         "made_by": "plumber",
         "confidence": 0.6
       }
     ]
   }
   ```

2. **Review all decisions and suggest an answer for each before asking the user.**
   For each decision, compare the `question` and `decision` text against the
   staged diff and the requirement it references:
   - **Approve** — the change directly implements, fixes, or improves this requirement
   - **Ignore** — the change is a refactor/cleanup that does not alter the requirement's
     observable behaviour, or the decision is out of scope for this project
   - **Reject** — the change contradicts or regresses the requirement

   Group decisions with the same suggested action into batches. Present each batch
   in a single `AskUserQuestion` call showing the count, IDs, and your reasoning.
   Never present decisions one-by-one when batching is possible.

3. **Use `AskUserQuestion` (never plain text)** to present each batch:
   ```
   Batch [label] ([N] decisions) — [suggested action]:
   [reasoning summary]
   IDs: [comma-separated list]
   ```
   Options: **Apply as suggested** / **Skip for now**

4. Execute the user's selection:
   - Approve: `plumber approve <id>`
   - Approve all: `plumber approve --all`
   - Approve with edits: `plumber edit <id> "<new text>"`
   - Ignore: `plumber ignore <id>`
   - Reject: `plumber reject <id> --reason "..."`
     Then use Read/Edit to revert the rejected change in the staged files.

5. Run the **Sync Procedure** to update spec files and generate tests.
   Stage all modified files with `plumber stage`.

6. Re-run `git commit` with a message listing approved decision IDs and
   summaries. The hook fires again — if no pending decisions remain it exits 0.

> **Do not commit if any decisions have `status: rejected`.** The rejected
> change must be reverted first (use Read/Edit to undo the change, then
> re-stage).

## Sync Procedure (Claude-Native)

This replaces `plumb sync`. Claude performs the sync using Read, Grep, and
Edit/Write tools directly — no external LLM pipeline. Alternatively, run
`plumber sync` for an automated version.

### Step 1 — Load approved decisions

```bash
plumber decisions
# Filter for approved status in the JSON output — or read .plumb/decisions.jsonl directly
```

### Step 2 — Find the affected requirement

Use `Grep` to search `.plumb/requirements.json` for the `requirement_id` from each approved decision, then use `Read` to open the full record.

### Step 3 — Update spec bullet points

For each approved decision that changes requirement wording:
- Use `Read` to open the spec file (`source_file` field on the requirement).
- Find the bullet matching `requirement.text`.
- Use `Edit` to replace the bullet with the updated wording from `decision`.
- Do NOT reformat surrounding bullets or add new sections.

### Step 4 — Generate or update tests

For each approved decision that adds a new behaviour:
- Use `Grep` to find the test file closest to the affected source.
- Read the test file to understand existing style and fixtures.
- Write a new test function with a docstring matching the requirement text.
- Use `Edit` to append the test, or `Write` to create the file if missing.

### Step 5 — Re-run gaps and report closed count

```bash
plumber gaps
```

Report how many gaps were closed to the user.

### Step 6 — Stage all modified files

```bash
plumber stage
```

## Decision Generation

When you see staged changes (via `git diff --staged`) that affect files in
`app/` or `doc/`, compare the diff against `.plumb/requirements.json`.
For each change that aligns with, extends, or contradicts a requirement,
create a decision record:

```bash
plumber create-decision \
  --req-id <req-id> \
  --question "<question text>" \
  --decision "<your assessment>" \
  --confidence 0.85
```

Present these to the user via `AskUserQuestion` before committing.

The keyword-based `plumber hook` provides an automated first pass;
Claude's own reasoning is the authoritative source and should supplement it.

## After Committing

Run `plumber coverage` and briefly report the three coverage dimensions:
spec-to-test, spec-to-code, and decision resolution rate. Flag any gaps that
should be addressed before the next commit.

For deeper coverage analysis (no plumb CLI required):
```bash
plumber coverage-semantic
```
This reads `.plumb/code_coverage_map.json` (if plumb was run) or falls back to
`.plumb/semantic_coverage.json` (agent-native analysis).

## Rules

- **NEVER approve, reject, or edit decisions without explicit user instruction.**
  Always use `AskUserQuestion` — never present decisions as plain text.
- Never edit `.plumb/decisions.jsonl` directly — use `plumber` subcommands.
- You MAY edit `.plumb/config.json` directly to correct `spec_paths` or
  `test_paths` when they point to the wrong locations.
- This skill is installed globally (`~/.claude/skills/plumber/`) and applies to any project using the Plumber workflow.
- Spec files are source of truth. Let the Sync Procedure update them — do not
  edit spec files manually to resolve decisions.
- Before running `parse-spec`, note the current requirement count. If the
  result is 0, retry once. If still 0, report the failure and stop.
- `plumber` uses stdlib only. Never add third-party imports to it.
- Do not commit if any decisions have `status: rejected`. Revert the change
  first using Read/Edit, then re-stage.

## Command Reference

All standard `plumb` subcommands (`approve`, `reject`, `ignore`, `edit`,
`parse-spec`, `gaps`, `status`, `decisions`, `sync`, `coverage`) are supported
by `plumber` with identical arguments — just replace `plumb` with `plumber`.

New commands with no `plumb` equivalent:

| Command | When to use |
|---|---|
| `plumber coverage-semantic` | Semantic coverage (LLM or agent-native) |
| `plumber install-hook` | Install git pre-commit hook |
| `plumber stage` | Stage `.plumb/`, spec, test files |
| `plumber migrate --all-branches` | Migrate from plumb decisions format |
| `plumber create-decision --req-id <id> --question "..." --decision "..."` | Create pending decision |
