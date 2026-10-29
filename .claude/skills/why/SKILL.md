---
name: why
description: Challenge Claude's last answer. Use only when the user types /why, optionally with a topic. Claude picks the single claim in its previous reply that is most likely wrong or unverified and writes one question about it, and then answers it with a real check in the same turn.
---

# why

Adapted from the prompt.md of github.com/DilawarShafiq/nietzschian-debugger (MIT).

The question is for Claude, about Claude's own last reply. Do not question the user.

## Steps
1. Re-read your last reply. If the user gave a topic (`/why upkeep`), look only at
   claims about that topic.
2. Pick the one claim most likely to be wrong or unverified, in this order: a fact
   with no file read, fetch or command behind it; a version, limit, number or
   "X replaces Y" claim from memory; an assumption about the user's data, scale
   or platform that the user never stated; an alternative dismissed without
   checking. Skip claims verified this session. If all were, take the largest
   unstated assumption.
3. Ask exactly one question about it, aimed at evidence, for example "Which source
   did you read for X, and does it say Y?"
4. Output the question and one short line naming the claim. No preamble, no list
   of questions, do not defend your earlier reply. Then answer it (below).

## Answering
Always answer your own question in the same turn, without waiting for the user to
say "answer it". Use a real check (file read, `gh api`, fetch), not memory. State
what you checked. If the check shows your earlier reply was wrong, say which part
and correct it. If no check is possible, say the claim stays unverified.
