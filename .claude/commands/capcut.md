---
description: Translate natural language requests into capcut-cli commands and run them
allowed-tools: Bash
---

Use capcut-cli to answer `$ARGUMENTS`. Trust `capcut <cmd> --help` over this file.

## Step 1: Verify prerequisites

Run `capcut doctor`. It checks Node, the binary, ffmpeg/whisper, the Anthropic
key, and the draft directory in one shot. If `capcut` is not found, give the user:

1. Install: `npm install -g capcut-cli` (needs Node >= 18)
2. Optional per-feature tools: `brew install ffmpeg` (for `render`, `detect-scenes`,
   media metadata); Whisper for `caption`; `export ANTHROPIC_API_KEY=<key>` for `translate`.
3. Re-run `capcut doctor` until the draft directory resolves. On macOS the default is
   `$HOME/Movies/CapCut/User Data/Projects/com.lveditor.draft/`; pass an explicit
   path if doctor cannot find it.

Do not attempt any edit until `doctor` passes.

## Step 2: Interpret, classify, and execute

Run `capcut describe` (full spec as JSON) or `capcut <cmd> --help` for the command
surface. `<project>` is a filesystem path to the draft folder (or its `draft_info.json`),
not the bare folder name — get it from the `path` field of `capcut projects`.

- **Read-only** (`info`, `segments`, `texts`, `timeline`, `lint`, `export-srt`,
  `diff`, `projects`): run directly.
- **Mutating** (anything that writes the draft): state the exact command, then run.
  Every mutating command writes a `.bak`; undo with `capcut restore <project> --list`
  then `--step N`. For destructive intent (`cut`, `prune`, `replace-media`, bulk
  edits), confirm with the user first.
- **Natural language**: translate to the best-fit command, classify as above,
  run with a one-line explanation.
- **Empty `$ARGUMENTS`**: run `capcut projects` to list drafts on disk.

## Flow

capcut-cli edits the draft; CapCut renders the final video. For a first-time user:

1. `capcut init <name>` — creates and registers the draft where CapCut can open it.
2. Add source media from anywhere: `capcut add-video <project> <file> <start> <duration>`.
   The file is copied into the draft's `assets/` folder, so the draft is self-contained
   and the original can be moved or deleted. Add text and edits with the other commands.
3. `capcut lint <project>` — check before finishing (exit 2 = errors).
4. Open the project in CapCut and Export. CapCut writes the final MP4 to the folder you
   choose; capcut-cli does not produce the deliverable.

## Limits

- No final render: `capcut render` is a low-res ffmpeg proxy; `capcut export` is
  experimental macOS UI-automation.
- JianYing 6.0+ encryption is unsupported (`capcut decrypt` only explains the workaround).
