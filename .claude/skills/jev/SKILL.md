---
name: jev
description: Ask the TypeSafe Jev API one typed question and get probabilities back. /jev choice (one of a set), /jev noul (yes/no), /jev score (degree). With no shape, propose one from the discussion. Ask only on a gap or tension.
---

# /jev

Run one Jev question and show the probabilities. Advice only: take no action on the result.

## Shapes

| Shape | Use for | Menu fields | Answer |
|---|---|---|---|
| choice | one of a defined set | `options` (2 to 255, name to description) | top option, confidence, probabilities that sum to 1 |
| noul | whether a condition holds | optional `criteria` with `true` and `false` text | probability of yes, 0 to 1; no confidence |
| score | degree along a dimension | `levels` (2 to 10 ordered descriptions) | weighted score, confidence, probabilities per level that sum to 1 |

Every menu also has `state` (what is judged) and `instructions` (the question).

## Flow

1. Shape. If the first word of the arguments is choice, noul or score, use it. If there is none, propose one from the preceding discussion with a one-line reason (a set is choice, a condition is noul, a degree is score). Any other word: list the three and stop.
2. Menu. If the next argument is an existing file, it is the menu: go to step 4. Otherwise treat the rest as a description of the data, or as empty, and draft the menu from it and the discussion.
3. Check for gaps and tensions (below). If there are none, print one line (shape, the question, option count, what the state is built from) and run. If there are any, ask one question naming it, then proceed on the answer.
4. Run. Pipe the menu on stdin; write no file:
   `~/.claude/skills/jev/jev.sh <shape> <<'EOF'` ... `EOF`
   A menu may also be a fenced block in a markdown file: `<file>.md#<name>` reads the block whose info string is `json rubric:<name>`.
   Unattended callers that cannot pipe use `jev.sh <shape> <menu.json> <state-file>`: the raw text file becomes the menu's state.
5. Report the output verbatim, with one line on how to read it. If the output is `unavailable (...)`, say so with the reason and stop; do not retry. Exit 2 is a menu bug: fix it.

## Gaps and tensions

Ask only for one of these.

- Gap: the shape is ambiguous or does not fit the question; there is nothing to build the state from; fewer than 2 options or levels.
- Tension: the state would include text the user did not point at or discuss, or text that looks like a secret; an earlier instruction forbids external calls; the task needs more than 5 calls (say how many).

## Writing a menu

- Descriptions say only what an option or level means. No evidence for or against it.
- choice: include an "other" option when nothing may fit.
- noul: near 0.5 means a split, not "medium".
- score: levels are ordered, and each describes a concrete situation that stands alone.
- Put what the model needs into `state`, as named fields. Put the question in `instructions`.

## Invariants

- The key comes only from `TYPESAFE_API_KEY` and is never printed or written.
- Nothing persists: no menu file, no saved response.
- A runtime failure prints `unavailable (reason)` and exits 0, so callers continue without advice. Exit 2 means a bad shape or menu.
- No call while a gap or tension is open. The state holds only text the user referenced or discussed.
- Only the three shapes. Other types are not supported.
