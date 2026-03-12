---
description: Extract and review spec decisions on session end (Stop event)
event: Stop
---

Fires automatically when Claude ends a session. Runs only if `.plumb/` exists in the project root.

Extracts implementation decisions from the diff and agent traces, then presents them for approval before the session closes. Approved decisions are written back into the spec.

## Prerequisites

- Install plumb: `make plumb-install`
- Initialize in your project: `plumb init`
- See the [Plumb Skill SETUP.md](.claude/skills/plumb/SETUP.md) for API key configuration and spec format requirements.

## Behavior

- Skipped silently if `.plumb/` is not present
- Blocks session close if unreviewed decisions remain
