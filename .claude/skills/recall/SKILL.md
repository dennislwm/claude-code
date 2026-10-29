---
name: recall
description: Keyword search over the files in the current folder, and optional sibling folders, using bm25s. Use when the user asks what their local notes or documents say about something, or types /recall. Indexes .md and .txt by default; no PDF or DOCX yet.
---

# recall

Run: `bash ~/.claude/skills/recall/recall.sh [-s sibling]... [-r] [--ext rst,py] "query"`

- The current folder is always searched. `-s NAME` adds a sibling folder; repeat it for more.
- `-r` reuses the folders and extensions from the last `-s` call in this folder.
- With no query it prints help. Show it to the user verbatim in your reply.
- First use on a device installs bm25s (about 200 MB) and takes about a minute.
- The index rebuilds itself when files are added, changed or deleted.

After running:
1. Tell the user which folders were searched (the script prints them).
2. Answer from the returned paths and snippets. Read the files for detail if needed.
3. If it prints "no matches", say so and try one reworded query.
4. Matching is by words, so a question phrased differently from the notes can miss. Say so if results look unrelated.

Index data lives under `~/.recall/`, outside every repo. Never copy it into a repository.
