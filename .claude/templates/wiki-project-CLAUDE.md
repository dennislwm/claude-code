# CLAUDE.md

Project-level rules for all agents working in this wiki.

---

## Project context

<!-- Substitute per project (see 20playradar.wiki's /wiki scaffold command):
     - one-paragraph description of the pipeline/tool this wiki tracks
     - background link: https://github.com/<owner>/playradar/wiki/<ArticleFilename>
     - sibling repo this wiki depends on: ../<prefix><name> (the pipeline code) -->

Sibling repo this wiki depends on: [<name>](https://github.com/<owner>/<name>) (the pipeline code).

---

## Wiki structure

| File / Folder | Purpose |
|---|---|
| `Requirements.md` | Tracked requirements with ID, status, and notes |
| `Decisions.md` | Index of Architectural Decision Records (ADRs) |
| `decisions/` | Full ADR documents in format `adr-NN-short-title.md` |
| `Conventions.md` | Code-level and implementation decisions; flat reference table |
| `Tests.md` | Test cases with REQ traceability and status |
| `Deferred.md` | Detailed specs for deferred requirements; "Add when:" triggers |
| `Implementation.md` | Stage contracts, CLI reference, data formats between stages |
| `Home.md` | Project overview and navigation |

---

## Conventions

### Requirement IDs (REQ-NNN)

Requirements are tracked in `Requirements.md` as a table with columns `ID | Description | Status | Notes`. Status is open; common values are `Open`, `In Progress`, `Done`, and `Deferred`. No fixed lifecycle is enforced.

When a requirement is `Deferred`, a corresponding `## REQ-NNN` section must exist in `Deferred.md` with a detailed spec and an "Add when:" trigger condition.

### Test IDs (TST-NNN)

Tests are tracked in `Tests.md` as a table with columns `ID | Test | File | REQ | Status`. Each test must link to at least one REQ. Default status for a new test is `Pending`.

---

## ADR format

ADRs follow the full format defined in [playradar wiki ADR](https://github.com/<owner>/playradar/wiki/ADR):

- Frontmatter: `status`, `date`, `deciders`
- Sections: Context and Problem Statement, Decision Drivers, Considered Options (minimum two), Decision Outcome, Consequences
- Status values: `Proposed`, `Rejected`, `Accepted`, `Deprecated`, `Superseded`. `Rejected` = proposed but declined, never adopted (kept as a record of the decision)
- Files: `decisions/adr-NN-short-title.md`; register in `Decisions.md` index after creating

ADR titles are framed from the user's perspective ("User wants X") not the implementation ("Use Y instead of Z").

Before writing any ADR title, ask: "what problem was the user trying to solve?" The answer is the title. Implementation details (chosen approach, rejected alternative) belong in Considered Options, Decision Outcome, and Consequences -- not the title or Problem Statement.

Any claim about an external tool's or library's API, input/output contract, or capability must be verified against its actual documentation or source before it is written into an ADR's Decision Drivers, Considered Options, or Consequences -- never asserted from the tool's name, a summary, or prior familiarity alone. If a claim can't be verified, say so in the ADR rather than stating it as fact.

---

## Design consultations

When presenting design options, apply the ponytail ladder first (YAGNI, reuse what's already in the codebase, stdlib, native, fewest files, shortest diff) and label the winner before asking the user to choose. Never list options as neutral alternatives -- pick one and present the others only for context. If the user disagrees, they will redirect.

"Reuse what's already in the codebase" outranks reaching for a new file, even a clean single-purpose native config file (e.g. a project-local `pytest.ini` or `conftest.py`). Check whether an existing file the project already treats as its entry point (a `Makefile`, a config already in use) can take a one-line edit before adding a new file for the same purpose.

A frequently run command (test suite, a pipeline stage, a status check) gets a target in the project's existing canonical task runner (`Makefile`, `package.json` scripts, `tox`, `invoke` -- whatever the project already uses), not a raw command repeated in a README or memorized. That entry point is the one door in; new scripts don't bypass it.

---

## Wiki artifact placement

Before writing anything to the wiki, place it at the first rung that fits:

1. Derivable from a single file by reading it? Don't write it anywhere. Derivable but only by cross-referencing several files, and something already reaches for that aggregation? `Implementation.md`. This applies inside an otherwise-legitimate entry too -- naming a mechanism is fine; enumerating a data file's current values in the same breath isn't, it'll drift the moment the file changes.
2. A capability the pipeline now has or lost? `Requirements.md` note on the relevant REQ.
3. An implementation choice with a reason someone could re-litigate? `Conventions.md` row.
4. A multi-option decision with a real rejected alternative that could recur? A new ADR.
5. Correct but not ready to build? `Deferred.md` entry with an "Add when" trigger.

- A consequence/limitation of an already-written ADR stays in that ADR's
  Consequences section. Only split it into a Conventions.md row if the
  workaround grows independent implementation detail someone would look up
  without reading the ADR.

---

## Agent workflows

### Session start

When `/wiki` is invoked without a recognized command, respond with:

> This is the **<name>** wiki -- requirements, decisions, and test triage for <one-line project description>.
>
> Commands: `triage` | `add req` | `add test` | `create scaffold` | `check scaffold` | `check loop`

Then stop. Do not run triage automatically.

### `triage`

Read-only scan of all wiki files. Report without editing:

| Artifact | What to surface |
|---|---|
| `Requirements.md` | Open or In Progress reqs; Deferred reqs whose "Add when:" trigger in `Deferred.md` may now be met |
| `Decisions.md` / `decisions/` | ADRs in `Proposed` status; Accepted ADRs linked to a REQ that has since moved to Deferred |
| `Tests.md` | REQs with no TST coverage; tests with `Fail` status |
| `Conventions.md` | No triage -- static reference |
| `Deferred.md` | Sections for REQs no longer `Deferred` status -- should be removed, with any non-duplicate rationale migrated to `Conventions.md` first |
| `Implementation.md` | No triage -- static reference |

Output: a short grouped report. No file edits.

### `add req`

1. Prompt for: description, initial status, notes (optional).
2. Append a new row to `Requirements.md` using the next available REQ-NNN.
3. If status is `Deferred`: also create a `## REQ-NNN` stub in `Deferred.md` with placeholder spec and "Add when:" line.

### `add test`

1. Prompt for: test description, linked REQ-NNN, file path.
2. Append a new row to `Tests.md` using the next available TST-NNN with status `Pending`.

### `create scaffold`

Scaffolds the sibling implementation folder (`../<prefix><name>`, code not wiki).

1. Verify no existing implementation: check `../<prefix><name>` doesn't
   already exist. If it does, stop and report.
2. Resolve GitHub owner from this wiki repo's own `git remote -v`.
3. Create the minimum layout: `app/`, `tests/`, `Pipfile`, `.gitignore`,
   `README.md`. Skip domain dirs (`input/`, `output/`, `templates/`,
   `mappings/`) -- not implied by this project.
4. Invoke the `make-framework` agent to generate `Makefile` + `make.sh`.
5. Present the full folder tree + file contents for confirmation.
6. On confirmation: write files. No `git init`, no remote, no stage code.

### `check scaffold`

Read-only scaffold audit of `../<prefix><name>`. Report without editing:

| Check | What to surface |
|---|---|
| Layout | `create scaffold`'s minimum layout (`app/`, `tests/`, `Pipfile`, `.gitignore`, `README.md`, `Makefile`, `make.sh`) still present; any domain dir (`input/`, `output/`, `templates/`, `mappings/`) not implied by a current REQ |
| Root Python files | Any `.py` or Python config file (e.g. `conftest.py`, `pytest.ini`) at repo root -- per this file's Design consultations note, these belong behind an existing entry point (`Makefile`), not as new root files |
| Untracked artifacts | Root-level files matching build/output patterns (e.g. model weights, logs, `.DS_Store`) not covered by `.gitignore` |
| Makefile targets | Any CLI entry point (`__main__` block) in `app/` without a corresponding `Makefile` target |

Output: a short report. No file edits in `../<prefix><name>`.

### check loop

> **Config loads at session start.** `settings*.json` and subagent definitions are
> read when a session begins, so a running loop executes the copy it loaded and no
> later edit reaches it. Fixing a misbehaving loop therefore means *stop it and
> relaunch* -- patching config while it runs changes nothing, and the same
> misbehaviour recurring after a fix is an echo from stale config, not a failure of
> the fix. Check this first: if the loop's session predates the config, every other
> finding below is unreliable.

Read-only audit of an autonomous-loop setup for this project. Given
`[repo folder]` (sibling code) and `[wiki folder]` (this wiki), report without
editing whether the loop is completely and safely configured.

| Check | What to surface |
|---|---|
| Loop spec | `<wiki>/.claude/loop.md` exists and states: a goal, a bound on the success path (either an iteration cap with a self-stop, or a human gate that fires every iteration), a work step, an audit step that spawns the verifier, an escalation contract (what STOPS vs. what retries), and branch/secret/network boundaries |
| Verifier subagent | A `<wiki>/.claude/agents/*.md` exists with `model`, `effort`, `tools`, and a rubric plus an output contract; and it is referenced by name in loop.md (no dangling reference) |
| State | loop.md names a loop-state location (e.g. `.claude/loop-state.json`) kept separate from human-facing files |
| Permissions | The allow-list covers EVERY mutation class the loop performs -- file edits and writes as well as git verbs -- or a documented decision to run interactive-only. A partial allow-list is indistinguishable from none: each uncovered call still prompts |
| Tooling rules | loop.md's tooling rules match the tools actually available in the session (a rule mandating an unavailable tool stalls every iteration and forces a fallback), and forbid chained Bash -- `cd X && ...` and any `&&`, `\|\|`, `;`, or subshell join. Chaining is what defeats auto-allow: the same programs run unchained do not prompt |
| Boundaries | loop.md forbids irreversible or external actions a working branch cannot undo (push/merge to main, production API writes, secret reads, external network calls) |
| ADR integration (if the loop produces ADRs) | Each loop-produced ADR uses the template's standard status lifecycle and is registered in `Decisions.md`; the loop does not re-propose a gap already carrying an ADR |
| Config placement | `loop.md`, the verifier subagent, and any loop settings live on the default branch, not only on a work branch -- deleting a work branch must not destroy the loop. Work branches carry state and work product only |
| Terminal states | Every way the loop discards or declines work leaves a durable record where the exclusion check looks. An item discarded with no record -- or recorded only in a wipeable state file -- is rediscovered and redone |
| Everything the loop records is gated | Whatever artifact the loop writes -- a decision, a defect, a requirement -- passes a gate before it is recorded. A path that writes on the producing agent's say-so will file fabrications: applying a gate retroactively to four such entries discarded one whose every assertion the code contradicted, and reframed a second |
| Gates match the artifact | A **decision** needs verifying AND deciding: an automated gate plus a human one. A **defect** needs only verifying -- a bug is a bug, so a human gate adds nothing. Gate asymmetry is correct; identical gating for both is either too slow or too loose |
| Fixes prove themselves | Any change the loop makes ships a check that FAILS before it and passes after. A suite that was already green proves nothing about the path it never exercised -- that is how the defect being fixed survived the tests in the first place |
| Allow-list matches the spec | The allow-list patterns actually match the command FORMS loop.md prescribes. Patterns are prefix matches: `Bash(git checkout *)` does not match `git -C /path checkout ...`. Paths outside the project root (a sibling repo, a virtualenv holding dependency source) need explicit `Read()` entries whatever the command |

Output: a short report. No file edits.

#### After a run: audit the prompts

A static audit only catches causes you already thought of. In practice every
prompt worth fixing was unanticipated -- a pattern that did not match the command
form actually used, a path outside the project root, a chained command, a tool
reached for despite a better one being granted. Without this step the detection
mechanism is the human approving prompts one at a time.

So after a run, extract the commands from the session transcript and, for each
that prompted, classify it:

- **Well-formed and still prompted -> CONFIG GAP.** Add the pattern to the
  allow-list.
- **Malformed -- chained, using a banned tool, or an unbounded search ->
  AGENT ERROR.** Fix the agent's prompt.

**Never allow-list around an agent error.** Allow-listing a malformed command
entrenches the misbehaviour and silences the only signal that it is happening.
Reuse `/fewer-permission-prompts` for the extraction and the allow-list diff, but
apply this classification to its suggestions rather than accepting them wholesale
-- it will happily propose allow-listing the very patterns you want eliminated.

### create loop  [DRAFT -- NOT VALIDATED, DO NOT RUN AS READY]

> DRAFT / UNVERIFIED. This command has never been run, and it generates a loop
> shape that has never completed a cycle. Do NOT invoke it as a ready command --
> it is a design record persisted so the design survives session loss. Promote it
> to a live command only after a loop built by hand from this shape (first
> instantiation: `13coda-cli.wiki`) completes one real work cycle end to end,
> reconciling the draft against what actually worked.

Scaffolds an autonomous-loop setup. Signature:
`/wiki create loop [repo folder] [wiki folder] [docs/user instructions]`

Generates, all under the wiki's `.claude/`:

1. `loop.md` from this general skeleton:
   - **Setup** -- idempotent working-branch bootstrap in the repo(s): the one
     action allowed to start from main; all later work stays on the branch.
   - **Each iteration** -- bound the success path (an iteration cap with a
     self-stop, or a human gate that fires every iteration) ->
     do the next unit of work (scope defined by `[docs/user instructions]`) ->
     spawn the verifier on each durable artifact -> escalation contract
     (CONFIRMED stops the loop, PLAUSIBLE auto-retries once) -> record the
     outcome.
   - **State** -- `.claude/loop-state.json`: iteration count + progress; persist
     each gate outcome and any stop/escalation reason (the only events not
     already on disk) for out-of-band inspection.
   - **Boundaries** -- work only on the branch; escalate anything a branch cannot
     undo (push/merge to main, production writes, secret reads, external network).
2. `agents/<verifier>.md` -- a cold verifier subagent: `model`, `effort`,
   `tools`, `skills: ponytail`; rubric = ponytail + the wiki placement ladder +
   i-have-adhd + objective passes (`triage`, `check scaffold`, tests); worst-first
   output contract (plain text until ReportFindings is confirmed grantable to a
   subagent).
3. Permissions posture -- either a scoped `.claude/settings*.json` allow-list, or
   a documented decision to run interactive-only.

The **work step is project-specific**: `[docs/user instructions]` defines what a
unit of work is and its gates. The first instantiation (`13coda-cli.wiki`)
specializes it into a code-vs-design gap -> ADR flow with an added human
accept/reject/edit gate and extra statuses (`Approved`). That specialization is
NOT part of this generator until validated -- see that wiki as the worked example.

**A loop with only one output type jams on everything else it finds.** If the
loop can only emit decisions, the defects it turns up while investigating have
nowhere to go: it records them and moves on, generating work it never does. Give
each artifact its own path and its own gates -- and put one test between them:
**if a second plausible approach can be named, it is a decision, not a defect.**
One obvious change (a missing call, an unchecked return) is a defect; anything
with alternatives needs the human gate a defect path deliberately lacks. Naming
the second approach IS the evidence, which keeps the test falsifiable rather than
a matter of taste.

**Choosing the demand source is the hard part, and getting it wrong wastes every
run.** A discovery loop is only as good as where it looks for demand, and the
source must be the tool's OWN users rather than its platform's. The first
instantiation spent five runs researching the pain of the platform it wraps and
produced nothing usable -- every candidate was a platform limit its CLI could
make no decision about -- while one report from an actual calling repo and two
investigations of its own failure paths produced three real requirements. Decide
where demand comes from before tuning anything else; gates were straightforward
by comparison.
