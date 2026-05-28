# Lens Skill

Write design/specification-lens documentation from a source file or description.

Trigger: `/lens <file_path|description> [output_path]`

## The Lens

Every element of the document must serve a reader trying to understand
**intent and behaviour** — not implement it.

**Include:** intent, behaviour contracts, decisions and rationale, trade-offs,
operational model, user journey, limitations, risks, comparisons with related
tools.

**Exclude:** code snippets, command syntax, flag values, awk/sed logic,
chmod values, temp file naming patterns, bash-version workarounds,
implementation mechanics.

**Test per element:** "Does the reader need this to understand the system's
intent and behaviour, or to build it?" — if the latter, exclude or reframe at
the spec level (e.g. `chmod 600 + rm -f` → "temp files use restricted
permissions and are removed before the function returns").

## Procedure

### Step 1 — Parse input

Examine the args:

- A **file path** is recognizable by file extension (`.sh`, `.py`, `.md`, etc.)
  or existence on disk. Read it as source material.
- Remaining text is the **writing brief** — intent, focus, or scope.
- Both may be present: file = source material, brief = writing focus.
  If only a brief is given, use it as the sole basis for the draft.

### Step 2 — Determine output path

Resolve the output path before drafting:

- If the user included an output path in args, note it and confirm before
  writing (Step 5).
- If the source is a file, suggest a logical `.md` output path — e.g.
  `src/lpassrc.sh` → `wiki/tools/lpass.md`. State the suggestion clearly
  before drafting so the user can redirect early.
- If no output path can be inferred (description-only input), ask the user
  for the target path before drafting.

### Step 3 — Draft

Write the document applying the lens rules to every element.

While drafting, track each **significant exclusion or reframe** — source
content that was a natural candidate but was excluded or rewritten because it
failed the lens test. You will annotate these on the first draft only.

### Step 4 — Present draft

Output the full document.

**First draft only:** after the document body, append a brief lens notes
section:

```
---
**Lens notes**
- Excluded: [item] — [why it failed the test]
- Reframed: "[original]" → "[spec-level equivalent]"
```

Then ask one open conversational question — invite the user to push back,
expand a section, cut something, or redirect. Do not list options or use
structured prompts.

### Step 5 — Revision loop

Read the user's response and determine intent:

- **Approved** — user signals the draft is ready (e.g. "looks good", "ship
  it", "write it", "that's it"). Confirm the output path if not already
  confirmed, write the file, report `Written to <path>.`, and stop.
- **Discarded** — user cancels (e.g. "discard", "cancel", "start over",
  "never mind"). Stop without writing anything.
- **Revision** — apply the feedback. Keep the lens rules intact — do not let
  revision feedback reintroduce coding-lens content unless the user explicitly
  overrides the lens for a specific element. Output the full redrafted document
  (no lens notes). Ask one open question and loop.

### Step 6 — Write

Write the confirmed draft to the output path as a `.md` file.
Report: `Written to <path>.`

## Rules

- Never write the file before the user approves.
- Apply the lens test to every element on every round — revisions can
  reintroduce coding-lens content; catch it.
- Full redraft every round — never partial updates or diffs.
- Lens notes appear on the first draft only.
- Output must always be a `.md` file.
- Do not open with a preamble — go straight to the suggested output path
  (or path question), then the draft.
- If the user explicitly overrides the lens for a specific element ("keep the
  chmod example"), honour it without argument and note the override in the
  document with a brief inline comment.
