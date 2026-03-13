# Plumber Skill

Plumber keeps the spec, tests, and code in sync using Claude's native
reasoning — no plumb CLI required. All state lives in `.plumb/` using a
standalone schema compatible with plumber.py's agent workflow.

The helper script is `app/plumber.py` (stdlib only, no pip install needed).

> **Goal:** Plumber is designed to fully replace the plumb CLI. If you see
> instructions referencing `plumb` commands, translate them to the equivalent
> `make <target>` or `plumber.py` subcommand listed in the Command Reference
> below.

## Before Starting Work

Run the session pre-flight to catch common failures in one pass:

```bash
# 1. Verify config paths
cat .plumb/config.json

# 2. Check requirement count (guard against wipe)
COUNT=$(python3 -c "import json; print(len(json.load(open('.plumb/requirements.json'))))" 2>/dev/null || echo 0)
echo "$COUNT requirements"
# If 0, re-parse (but verify result is non-zero before overwriting):
# cd app && make parse-spec

# 3. Generate gaps
cd app && make gaps

# 4. Report status
cd app && make status
```

Report a brief summary of requirement count, gap count, and pending decisions
before proceeding.

## Before Committing

Run `cd app && make diff` to preview pending decisions (existing + any that
would be created from staged changes). Report the count so the user is not
surprised during review.

## When git commit is Intercepted

If the pre-commit hook is installed (`cd app && make install-hook`), it fires
automatically on every `git commit`. When the hook exits non-zero:

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

2. **Use `AskUserQuestion` (never plain text)** to present each decision:
   ```
   Plumber found [N] decision(s). Decision [X of N]:
   Question: [question]
   Decision: [decision]
   Made by: [made_by] (confidence: [confidence])
   ```
   Options: **Approve** / **Approve with edits** / **Ignore** / **Reject**

3. Execute the user's selection:
   - Approve: `cd app && pipenv run python3 plumber.py approve <id>`
   - Approve all: `cd app && pipenv run python3 plumber.py approve --all`
   - Approve with edits: `cd app && pipenv run python3 plumber.py edit <id> "<new text>"`
   - Ignore: `cd app && pipenv run python3 plumber.py ignore <id>`
   - Reject: `cd app && pipenv run python3 plumber.py reject <id> --reason "..."`
     Then use Read/Edit to revert the rejected change in the staged files.

4. Run the **Sync Procedure** to update spec files and generate tests.
   Stage all modified files with `cd app && make stage`.

5. Re-run `git commit` with a message listing approved decision IDs and
   summaries. The hook fires again — if no pending decisions remain it exits 0.

> **Do not commit if any decisions have `status: rejected`.** The rejected
> change must be reverted first (use Read/Edit to undo the change, then
> re-stage).

## Sync Procedure (Claude-Native)

This replaces `plumb sync`. Claude performs the sync using Read, Grep, and
Edit/Write tools directly — no external LLM pipeline. Alternatively, run
`cd app && make sync` for an automated version.

### Step 1 — Load approved decisions

```bash
cd app && pipenv run python3 plumber.py decisions
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
cd app && make gaps
```

Report how many gaps were closed to the user.

### Step 6 — Stage all modified files

```bash
cd app && make stage
```

## Decision Generation

When you see staged changes (via `git diff --staged`) that affect files in
`app/` or `doc/`, compare the diff against `.plumb/requirements.json`.
For each change that aligns with, extends, or contradicts a requirement,
create a decision record:

```bash
cd app && pipenv run python3 plumber.py create-decision \
  --req-id <req-id> \
  --question "<question text>" \
  --decision "<your assessment>" \
  --confidence 0.85
```

Present these to the user via `AskUserQuestion` before committing.

The keyword-based `make check` / `make hook` provides an automated first pass;
Claude's own reasoning is the authoritative source and should supplement it.

## After Committing

Run `cd app && make coverage` and briefly report the three coverage dimensions:
spec-to-test, spec-to-code, and decision resolution rate. Flag any gaps that
should be addressed before the next commit.

For deeper coverage analysis (no plumb CLI required):
```bash
cd app && make coverage-semantic
```
This reads `.plumb/code_coverage_map.json` (if plumb was run) or falls back to
`.plumb/semantic_coverage.json` (agent-native analysis).

## Rules

- **NEVER approve, reject, or edit decisions without explicit user instruction.**
  Always use `AskUserQuestion` — never present decisions as plain text.
- Never edit `.plumb/decisions.jsonl` directly — use `plumber.py` subcommands.
- You MAY edit `.plumb/config.json` directly to correct `spec_paths` or
  `test_paths` when they point to the wrong locations.
- Never install this skill globally (`~/.claude/`). It is project-local only.
- Spec files are source of truth. Let the Sync Procedure update them — do not
  edit spec files manually to resolve decisions.
- Before running `parse-spec`, note the current requirement count. If the
  result is 0, retry once. If still 0, report the failure and stop.
- `app/plumber.py` uses stdlib only. Never add third-party imports to it.
- Do not commit if any decisions have `status: rejected`. Revert the change
  first using Read/Edit, then re-stage.

## Command Reference

| Plumb CLI command | Plumber equivalent | When to use |
|---|---|---|
| `plumb status` | `cd app && make status` | Start of session |
| `plumb diff` | `cd app && make diff` | Before committing — preview decisions |
| `plumb hook` | `cd app && make hook` | Pre-commit hook (auto-installed) |
| `plumb parse-spec` | `cd app && make parse-spec` | Re-parse spec after manual edits |
| `plumb gaps` | `cd app && make gaps` | Write `.plumb/gaps.json` |
| `plumb approve <id>` | `cd app && pipenv run python3 plumber.py approve <id>` | User approves |
| `plumb approve --all` | `cd app && pipenv run python3 plumber.py approve --all` | Approve all pending |
| `plumb reject <id>` | `cd app && pipenv run python3 plumber.py reject <id> --reason "..."` | User rejects |
| `plumb ignore <id>` | `cd app && pipenv run python3 plumber.py ignore <id>` | Mark not spec-relevant |
| `plumb edit <id>` | `cd app && pipenv run python3 plumber.py edit <id> "<text>"` | Amend decision text |
| `plumb sync` | `cd app && make sync` | After approving — update spec + tests |
| `plumb coverage` | `cd app && make coverage` | Keyword-based coverage report |
| *(no equivalent)* | `cd app && make coverage-semantic` | Semantic coverage (LLM or agent-native) |
| *(no equivalent)* | `cd app && make install-hook` | Install git pre-commit hook |
| *(no equivalent)* | `cd app && make test` | Run all tests |
| *(no equivalent)* | `cd app && make stage` | Stage `.plumb/`, spec, test files |
| *(create decision)* | `cd app && pipenv run python3 plumber.py create-decision --req-id <id> --question "..." --decision "..."` | Create pending decision |
