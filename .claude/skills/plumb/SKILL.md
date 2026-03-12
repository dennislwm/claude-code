# Plumb Skill

Plumb keeps the spec, tests, and code in sync via a pre-commit hook that
surfaces decisions for review before each commit lands.

For initial setup, API key configuration, spec format requirements, and
troubleshooting, see [SETUP.md](SETUP.md).

## Session Pre-flight

Run before `plumb status` to catch common failures in one pass:

```bash
# 1. Source .env if present (required for all LLM-dependent commands)
[ -f .env ] && set -a && source .env && set +a

# 2. Verify API key
echo "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:+set} OPENAI_API_KEY=${OPENAI_API_KEY:+set} PLUMB_MODEL=${PLUMB_MODEL:-default}"

# 3. Check config paths are correct (spec_paths must point to declarative bullet-point requirements)
cat .plumb/config.json

# 4. Check requirements are parsed (if 0, run `plumb parse-spec`)
python3 -c "import json; r=json.load(open('.plumb/requirements.json')); print(len(r), 'requirements')"

# 5. Generate gaps file (no LLM call needed)
plumb-gaps

# 6. Run status (only meaningful if requirements > 0)
plumb status
```

## Responsibilities

**Before starting work:** Run the Session Pre-flight, then `plumb status`.
Report a brief summary of spec/test/code alignment and any pending decisions.

**Before committing:** Run `plumb diff`. Report the estimated decisions so
the user is not surprised during review.

**When git commit is intercepted** (exits non-zero with Plumb output):

1. Parse stdout JSON fields: `pending_decisions` (int), `decisions[]` with
   `id`, `question`, `decision`, `made_by`, `confidence`.

2. Use `AskUserQuestion` (never plain text) to present each decision:
   ```
   Plumb found [N] decision(s). Decision [X of N]:
   Question: [question]
   Decision: [decision]
   Made by: [made_by] (confidence: [confidence])
   ```
   Options: Approve / Approve with edits / Ignore / Reject

3. Execute the user's selection:
   - Approve: `plumb approve <id>` (or `plumb approve --all` if all approved)
   - Approve with edits: `plumb edit <id> "<new text>"`
   - Ignore: `plumb ignore <id>`
   - Reject: `plumb reject <id> --reason "..."` (code is modified automatically)

4. Run `plumb sync` to update spec files and generate tests. Stage the output.

5. Re-run `git commit` with a message listing approved decision IDs and summaries.
   Repeat review if new decisions are found.

**After committing / when guiding next work:** Run `plumb coverage`. Report
gaps across all three dimensions (code coverage, spec-to-test, spec-to-code)
and flag requirements with no tests or implementation.

## Rules

- NEVER approve, reject, or edit decisions without explicit user instruction.
- Never edit `.plumb/decisions.jsonl` directly.
- You MAY edit `.plumb/config.json` directly to correct `spec_paths` or
  `test_paths` when they point to the wrong locations.
- Never install this skill globally (`~/.claude/`). It is project-local only.
- Spec files are source of truth. Let `plumb sync` update them — do not edit
  spec files manually to resolve decisions.
- Do not commit if any decision has `status: rejected_manual`. The user must
  resolve these first.
- `plumb map-tests` requires interactive confirmation. Use
  `echo "y" | plumb map-tests` to apply mappings non-interactively.

## Command Reference

| Command | When to use |
|---|---|
| `plumb status` | After pre-flight, start of session |
| `plumb diff` | Before committing |
| `plumb approve <id>` | User approves a decision |
| `plumb approve --all` | User approves all pending decisions |
| `plumb reject <id> --reason "<text>"` | User rejects a decision |
| `plumb ignore <id>` | User marks decision as not spec-relevant |
| `plumb edit <id> "<text>"` | User amends decision text before approving |
| `plumb sync` | After approving — updates spec and generates tests |
| `plumb coverage` | Report coverage across all three dimensions |
| `plumb parse-spec` | Re-parse spec after manual edits |
| `echo "y" \| plumb map-tests` | Map tests to requirements non-interactively |
| `plumb-gaps` | Write `.plumb/gaps.json` without an LLM call |
