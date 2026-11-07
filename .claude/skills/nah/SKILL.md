---
name: nah
description: Redo Claude's last question with full context. Use only when the user types /nah, optionally with a note.
---

# nah

The last question lacked context. Redo it; do not defend the earlier message.

Follow "Design consultations" in the global CLAUDE.md. It already says what a question must contain; do not restate it here.

## Steps
1. Re-read your last reply and find the question or choice it put to the user. If there is none, say so and stop. If the user gave a note (`/nah the tests`), look only at that question.
2. Define any term you coined, in plain words, and say what each option replaces.
3. Reuse the last Jev result if it is in this conversation and its facts still hold. Otherwise run `/jev choice`, with its state built from quoted file text, not paraphrase.
4. Invoke the i-have-adhd skill and shape the reply with it: the next action first, steps numbered, one concrete next action last.
5. No edits and no new options.
