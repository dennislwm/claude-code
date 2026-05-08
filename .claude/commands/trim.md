---
name: trim
description: Run the cost-efficiency-reviewer on an artifact, then ask the user for approval on each cut before making changes.
argument-hint: "<artifact> -- e.g. 'the review', 'the changes', 'the proposal', or a file path"
---

## Step 1: Identify the artifact

Resolve `$ARGUMENTS` to a concrete artifact:

- If it names a file path, read that file.
- If it refers to something in context ("the review", "the proposal", "the changes"), identify what was most recently produced or discussed in this conversation that fits the description.
- If ambiguous, ask the user to clarify before proceeding.

## Step 2: Review (read-only)

Spawn the `cost-efficiency-reviewer` agent on the artifact. It must produce a structured report with numbered findings -- do NOT make any changes.

## Step 3: Present findings and ask for approval

For each finding with a meaningful trade-off, use `AskUserQuestion` to present it as a choice. Group minor low-risk cuts (pure redundancy, no behavioral impact) into a single "approve all minor cuts" option rather than asking one by one.

For each question:
- State what would be cut and why
- Name the risk if any
- Offer at least: approve / keep as-is

**Never approve, reject, or edit on the user's behalf.** Wait for explicit answers before proceeding.
