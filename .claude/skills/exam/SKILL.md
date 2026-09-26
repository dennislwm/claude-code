---
name: exam
description: Write or restructure a technical explainer as an exam study guide -- numbered sections, Concept/Code split with inline verified-source citations or explicit unconfirmed tags, comparison tables, tiered code examples, and a Sources footer that closes every unconfirmed tag used in the body. Use when the user asks for a "study guide", "exam guide", "cram sheet", "reference doc" for a technical topic, or says to format existing notes/docs like one. Modeled on this project's own doc/agentcore-guide.md. Combines i-have-adhd's action-first, no-fluff structure with simple-english's short-sentence, active-voice, one-term-per-concept discipline for all prose; code blocks, tables, and quoted facts are untouched.
---

# exam

Produce a technical study guide the reader can scan under time pressure and act on without re-reading. Two disciplines apply to every sentence of prose: ADHD-shaped structure (i-have-adhd) and Simplified Technical English (simple-english). Code, commands, and cited facts are never rewritten for style -- only the surrounding prose is.

## Output contract (from doc/agentcore-guide.md)

1. **Title** -- `# <Topic> — Exam Study Guide`
2. **Numbered top-level sections** (`## N. <question or claim the section answers>`). Each section answers one question a reader would face, not a grab-bag of related trivia.
3. Inside a section, split by role, in this order when present:
   - **Concept** -- one short paragraph or bullet list stating the fact/rule, labeled `**Concept:**` or `**Concept — <subtopic>:**`. STE rules apply (below). A failure-mode Concept quotes the exact error text verbatim, then states cause, then fix.
   - **Code** -- verbatim, runnable, untouched by prose rules. Never place a code block without a preceding Concept line -- a bare block with no stated why/what is not allowed.
   - **Comparison table** -- any time 2+ items share comparable axes (not just two things explicitly being "contrasted"), a table beats prose or a bulleted list. One row per axis, not per detail.
4. **Verified vs unconfirmed, both directions, no bare unverified claim:**
   - A claim confirmed against a real source gets an inline parenthetical naming exactly where: `(verified from SDK source, path/to/file.py)`, `(confirmed against provider docs)`. Do not state a specific, checkable claim (a method signature, a field name, a limit) without this citation.
   - A claim that could not be confirmed gets flagged inline (`unconfirmed`) or grouped in a closing caveat -- never stated as bare fact, per this project's global rule on not guessing APIs/versions.
5. **Sources** section at the end, listing exactly what was checked (doc names, repo paths, provider docs) -- not a generic "official documentation" -- and explicitly restating which flagged claims remain unconfirmed and why. It closes the loop on every unconfirmed tag used in the body, not just a bibliography.
6. **Takeaway lines get a bold label**, not a buried clause mid-paragraph: `Key nuance:`, `Caution:`, `Tradeoff:`, `Rule that emerges:`, `Fix:`. One label, one sentence, at the point the synthesis becomes clear -- not saved for a closing summary.
7. **Tier code examples explicitly when complexity jumps.** If the minimal working version and the realistic version differ meaningfully, name both as `Example 1 (<what it does>)`, `Example 2 (<what it adds>)` rather than one example that jumps straight to full complexity.

## Prose rules inside Concept blocks (simple-english, pragmatic mode)

- Procedural sentences (do X): imperative, 20-word cap, condition before command.
- Descriptive sentences (X is Y): simple present, 25-word cap, one new fact per sentence.
- Active voice. Banned modals: should/would/may/might/could -- use must/can, or restate as fact.
- One term per concept for the whole guide (pick "runtime" or "service", not both) -- if the source material mixes terms, normalize before writing.
- Delete slop: "leverage", "seamlessly", "robust", "it's worth noting", "simply". See simple-english's substitution table for the full list.
- Never touch code, identifiers, flags, paths, or quoted error text.

## Structure rules from i-have-adhd

- No preamble ("Let's look at...") before a section; the heading IS the lead-in.
- Multi-step procedures inside a Concept block are a numbered list, not a run-on sentence.
- No closing recap or "hope this helps" after the guide -- it ends at Sources.

## Workflow

1. Identify the source material, then classify each fact as settled or `unconfirmed`, and group facts into numbered sections by the question they answer (not by source-file order).
2. Draft each section per the Output contract above.
3. Self-check every Concept block against the Prose rules and Structure rules above (sentence length, banned modals, term consistency, no preamble/closer), then write Sources.
