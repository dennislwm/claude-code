# Plumber Skill

Plumber keeps the spec, tests, and code in sync using Claude's native
reasoning — no plumb CLI required. All state lives in `.plumb/` using the
same JSON schemas as plumb for compatibility.

The helper script is `app/plumber.py` (stdlib only, no pip install needed).

## Session Pre-flight

Run before reporting status to catch common failures in one pass:

```bash
# 1. Check config paths are correct
cat .plumb/config.json

# 2. Check requirements are parsed
COUNT=$(python3 -c "import json; print(len(json.load(open('.plumb/requirements.json'))))" 2>/dev/null || echo 0)
echo "$COUNT requirements"
# If 0, run parse-spec — but guard against it wiping requirements.json:
# cd app && make parse-spec
# NEW=$(python3 -c "import json; print(len(json.load(open('../.plumb/requirements.json'))))" 2>/dev/null || echo 0)
# [ "$NEW" -eq 0 ] && echo "WARNING: parse-spec returned 0 (was $COUNT)" && exit 1

# 3. Generate gaps (no LLM call needed)
cd app && make gaps

# 4. Report status
cd app && make status
```

## Responsibilities

**Before starting work:** Run the Session Pre-flight, then report a brief
summary of spec/test/code alignment and any pending decisions.

**Before committing:** Run `cd app && make decisions` to surface pending
decisions. Report the count so the user is not surprised.

**When pending decisions exist:**

1. Read `cd app && make decisions` output — a JSON array with fields:
   `id`, `question`, `decision`, `made_by`, `confidence`.

2. Use `AskUserQuestion` (never plain text) to present each decision:
   ```
   Plumber found [N] decision(s). Decision [X of N]:
   Question: [question]
   Decision: [decision]
   Made by: [made_by] (confidence: [confidence])
   ```
   Options: Approve / Approve with edits / Ignore / Reject

3. Execute the user's selection:
   - Approve: `cd app && pipenv run python3 plumber.py approve <id>`
   - Approve all: `cd app && pipenv run python3 plumber.py approve --all`
   - Approve with edits: `cd app && pipenv run python3 plumber.py edit <id> "<new text>"`
   - Ignore: `cd app && pipenv run python3 plumber.py ignore <id>`
   - Reject: `cd app && pipenv run python3 plumber.py reject <id> --reason "..."`

4. Run the **Sync Procedure** below to update spec files and generate tests.
   Stage all modified files.

5. Re-run `git commit` with a message listing approved decision IDs and summaries.
   Repeat review if new decisions are found.

**After committing / when guiding next work:** Run `cd app && make coverage`.
Report gaps across all three dimensions and flag requirements with no tests
or implementation.

## Sync Procedure (Claude-Native)

This replaces `plumb sync`. Claude performs the sync using Read, Grep, and
Edit/Write tools directly — no external LLM pipeline.

### Step 1 — Load approved decisions

```bash
python3 -c "
import json
lines = open('.plumb/decisions.jsonl').readlines()
approved = [json.loads(l) for l in lines if json.loads(l).get('status') == 'approved']
print(json.dumps(approved, indent=2))
"
```

### Step 2 — Find the affected requirement

```bash
python3 -c "
import json
reqs = {r['id']: r for r in json.load(open('.plumb/requirements.json'))}
print(json.dumps(reqs.get('<requirement_id>'), indent=2))
"
```

### Step 3 — Update spec bullet points

For each approved decision that changes the requirement wording:
- Use `Read` to open the spec file (`source_file` field on the requirement).
- Find the bullet matching `requirement.text`.
- Use `Edit` to replace the bullet with the updated wording from `decision`.
- Do NOT reformat surrounding bullets or add new sections.

### Step 4 — Generate or update tests

For each approved decision that adds a new behaviour:
- Use `Grep` to find the test file closest to the affected source (e.g.,
  `app/tests/test_plumber.py` for `app/plumber.py`).
- Read the test file to understand existing style, fixtures, and import pattern.
- Write a new test function that:
  - Has a docstring matching the requirement text.
  - Tests the specific behaviour described in `decision`.
  - Follows the existing assert/fixture patterns.
- Use `Edit` to append the new test, or `Write` to create the file if missing.

### Step 5 — Re-run gaps and report closed count

```bash
cd app && make gaps
```

The output reports how many gaps were closed, e.g. `3 gap(s) — 2 closed`.
Report this count to the user.

### Step 6 — Stage all modified files

```bash
cd app && make stage
```

This stages `.plumb/`, all `spec_paths`, and all `test_paths` from config in one step.

## Decision Generation

When you see staged changes (via `git diff --staged`) that affect files in
`app/` or `doc/`, compare the diff against `.plumb/requirements.json`.
For each change that aligns with, extends, or contradicts a requirement,
create a decision record via the helper script:

```bash
cd app && pipenv run python3 plumber.py create-decision \
  --req-id <req-id> \
  --question "<question text>" \
  --decision "<your assessment>" \
  --confidence 0.85
```

Present these to the user via `AskUserQuestion` before committing.

## Rules

- NEVER approve, reject, or edit decisions without explicit user instruction.
- Never edit `.plumb/decisions.jsonl` directly — use `plumber.py` subcommands.
- You MAY edit `.plumb/config.json` directly to correct `spec_paths` or
  `test_paths` when they point to the wrong locations.
- Never install this skill globally (`~/.claude/`). It is project-local only.
- Spec files are source of truth. Let the Sync Procedure update them — do not
  edit spec files manually to resolve decisions.
- Before running `parse-spec`, note the current requirement count. If the
  result is 0, retry once. If still 0, report the failure and stop.
- `app/plumber.py` uses stdlib only. Never add third-party imports to it.

## Command Reference

| Command | When to use |
|---|---|
| `cd app && make parse-spec` | Re-parse spec after manual edits |
| `cd app && make gaps` | Write `.plumb/gaps.json` |
| `cd app && make status` | After pre-flight, start of session |
| `cd app && make decisions` | Before committing — list pending |
| `cd app && make coverage` | Report coverage across all three dimensions |
| `cd app && make stage` | Stage `.plumb/`, spec, and test files after sync |
| `cd app && pipenv run python3 plumber.py create-decision --req-id <id> --question "..." --decision "..."` | Create a pending decision record |
| `cd app && make test` | Run all tests |
| `cd app && pipenv run python3 plumber.py approve <id>` | User approves a decision |
| `cd app && pipenv run python3 plumber.py approve --all` | User approves all pending |
| `cd app && pipenv run python3 plumber.py reject <id> --reason "<text>"` | User rejects |
| `cd app && pipenv run python3 plumber.py ignore <id>` | User ignores a decision |
| `cd app && pipenv run python3 plumber.py edit <id> "<text>"` | User amends decision text |
| Sync Procedure | After approving — updates spec and generates tests |
