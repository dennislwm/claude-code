# Self Skill

Audit the current session for memory gaps, get user approval, update memory,
and optionally propagate durable rules to CLAUDE.md.

Trigger: `/self` or user requests to sync/update memory from this session.

## Procedure

### Step 1 — Load current memory

Read `MEMORY.md` from the project memory directory
(`~/.claude/projects/<slug>/memory/MEMORY.md`). If it does not exist, treat
all memory as empty.

Also read each linked memory file to understand what is already recorded.

### Step 2 — Identify session gaps

Review the current conversation for instructions, constraints, preferences,
or feedback the user gave that are **not already captured** in memory. Focus on:

- Corrections or redirections ("don't do X", "stop Y", "use Z instead")
- Confirmed non-obvious approaches the user accepted without pushback
- User role, domain knowledge, or collaboration style signals
- Project decisions, deadlines, motivations, or external pointers
- Any "from now on" or "always/never" rules

Also scan for **failure learnings** and **workflow optimizations**:

- Tool calls or commands that failed and what the fix or workaround was
- Approaches that were tried, abandoned, and replaced by a better method
- Multi-step sequences that were shortened or reordered to avoid errors
- Parallel vs. sequential tool use patterns that proved more effective
- Environment or config quirks discovered only through a failed attempt

Label each such entry with its source: `[failure]` or `[optimization]` so the
user can judge whether it generalizes beyond this session.

Skip entries covered by the Rules section (ephemeral state, code-derivable
facts, CLAUDE.md content). Also skip failures whose fix is already obvious
from the code or docs — only record when the lesson is non-obvious.

For each gap, draft a candidate memory entry with:
- Proposed filename (e.g. `feedback_no_summaries.md`)
- Type: `user`, `feedback`, `project`, or `reference`
- Source tag: `[failure]`, `[optimization]`, or `[preference]`
- One-line description (for MEMORY.md index)
- Body content (rule/fact + **Why:** + **How to apply:** for feedback/project types)

### Step 3 — Present gaps to user

If there are no gaps, report "Memory is up to date — nothing new to record."
and stop.

If there are gaps, use **`AskUserQuestion`** (never plain text) to present them.
Group related entries into a single question where possible. Show:

```
Gap [N]: [filename] ([type]) [source tag]
Description: [one-line summary]
Body preview:
  [first 3-4 lines of proposed body]
```

Options per batch: **Save** / **Skip** / **Edit first**

If the user selects "Edit first", ask targeted clarification questions before saving.
For **all** types:
- What specifically should the rule cover?
- Are there exceptions?
- Is this project-specific or global?

For **`[failure]`** entries, also ask:
- Is this failure pattern likely to recur in other projects or just this one?
- Was the root cause a config issue, a tool quirk, or a wrong assumption?

For **`[optimization]`** entries, also ask:
- Does the optimized workflow depend on a specific tool version or environment?
- Should this replace or supplement an existing workflow in memory?

Revise the draft based on the answers, then re-present for approval.

### Step 4 — Write approved entries

For each approved entry:

1. Write the memory file to the project memory directory with correct frontmatter:
   ```markdown
   ---
   name: <slug>
   description: <one-line summary>
   metadata:
     type: <user|feedback|project|reference>
   ---

   <body content here>
   ```

2. Add or update the pointer in `MEMORY.md`:
   `- [Title](filename.md) — one-line hook`

   Create `MEMORY.md` if it does not exist (no frontmatter, index only).

### Step 5 — Ask about CLAUDE.md

After all entries are saved, ask the user:

> "Should any of these rules also go into the project CLAUDE.md so they apply
> to all contributors and future agents (not just your personal memory)?"

Use `AskUserQuestion` with options: **Yes, add to CLAUDE.md** / **No, memory only**

If yes, ask which entries and where in CLAUDE.md they should appear, then use
Read + Edit to apply. Do not duplicate content already present.

## Rules

- **NEVER write, update, or delete memory without explicit user approval.**
  Always use `AskUserQuestion` — never silently persist anything.
- Never save ephemeral task state, in-progress work, or session context.
- Never save code patterns, conventions, or architecture — read the code instead.
- Never save git history, recent changes, or activity summaries.
- Never duplicate content that already exists in memory or CLAUDE.md.
- If the memory directory does not exist, create it before writing
  (`~/.claude/projects/<slug>/memory/`). The slug is the working directory
  path with `/` replaced by `-`.
- Keep MEMORY.md index lines under ~150 characters each.
- Lines after 200 in MEMORY.md will be truncated — keep the index concise.
- Prefer updating an existing memory file over creating a duplicate.
