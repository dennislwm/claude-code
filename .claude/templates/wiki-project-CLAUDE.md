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

When a loop-driven REQ closes (`Done`/`Accepted`), compress its Notes cell to the final outcome plus a pointer to the implementing commit(s) (e.g. `see <branch>@<sha>`) instead of keeping the full verdict-by-verdict GATE history inline. This is never erasure -- the full history stays in those commits' messages, which is already the authoritative record for it. Only compress on closure: a still-open REQ keeps its full history inline, since nothing else surfaces it during dispatch or audit while it's active.

### Test IDs (TST-NNN)

Tests are tracked in `Tests.md` as a table with columns `ID | Test | File | REQ | Status`. Each test must link to at least one REQ. Default status for a new test is `Pending`.

---

## ADR format

ADRs follow the full format defined in [playradar wiki ADR](https://github.com/<owner>/playradar/wiki/ADR):

- Frontmatter: `status`, `date`, `deciders`
- Sections: Context and Problem Statement, Decision Drivers, Considered Options (minimum two genuine mechanisms), Decision Outcome, Consequences. Status quo/no-op never counts toward this minimum and must not appear as a numbered option -- its deficiency is already the reason the ADR exists, stated in Context and Problem Statement, so re-listing it as "Option N: Status quo -- Rejected" is boilerplate, not a decision. If only one genuine mechanism exists, that means discovery/proposal isn't done yet, not that status quo may stand in as the second option.
- Status values: `Proposed`, `Approved`, `Rejected`, `Accepted`, `Deprecated`, `Superseded`. `Rejected` = proposed but declined, never adopted (kept as a record of the decision). `Approved` = GATE B accepted it, not yet implemented. `Accepted` = GATE C passed after implementation -- these are two distinct states in the loop's own flow (`Proposed` -> GATE B accept -> `Approved` -> implement -> GATE C pass -> `Accepted`), not interchangeable words for the same thing. A `Proposed` record can also carry a `Held: <reason>` line (see `create loop`'s GATE B) -- this is a modifier on `Proposed`, not a sixth status value.
- Files: `decisions/adr-NN-short-title.md`; register in `Decisions.md` index after creating

ADR titles are framed from the user's perspective ("User wants X") not the implementation ("Use Y instead of Z").

Before writing any ADR title, ask: "what problem was the user trying to solve?" The answer is the title. Implementation details (chosen approach, rejected alternative) belong in Considered Options, Decision Outcome, and Consequences -- not the title or Problem Statement.

Any claim about cited code's API, input/output contract, capability, or shape (line/statement count, method structure) must be verified against its actual documentation or source before it is written into an ADR's Decision Drivers, Considered Options, or Consequences -- never asserted from a name, a summary, or prior familiarity alone, whether the code is an external tool or a sibling repo. If a claim can't be verified, say so in the ADR rather than stating it as fact.

If a project's stated "usable by others" goal doesn't specify its audience shape (CLI-only, importable-as-a-library, or both), ask before drafting an ADR whose Considered Options depend on that scope -- don't assume the broadest or narrowest reading.

Ponytail rung 2 ("already in this codebase?") extends to sibling repos in the same developer's or org's portfolio: check those before reaching for an external tool's design as precedent.

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
> Commands: `triage` | `add req` | `add test` | `create scaffold` | `check scaffold` | `check loop` | `create loop` | `land loop` | `sync wiki`

Then stop. Do not run triage automatically.

**Every command's report ends with a wire-back check -- and so does every
direct edit to a loop-governing file (`loop.md`, `agents/*.md`, this
`CLAUDE.md`), even outside a named command.** This check must produce a
visible verdict line every time, not a passive expectation to remember:
state "Wire-back check: generic (propagating) / project-specific (not
propagating) -- reason" before moving on. A silent, un-stated check is
indistinguishable from a forgotten one -- the check was widened once
already (from "command reports only" to "any direct edit") and still
failed to fire twice more after that, because nothing forced it to leave a
visible trace. If the change surfaced a lesson that would help a project
sharing none of this code, put it to ponytail. Then wire what survives now,
while the change is still on screen: anything about the loop mechanism
itself (Setup, Discover, GATE A/B/C, Cadence, Boundaries, or the
`create loop`/`check loop` commands that generate and audit it) goes into
`../02claude-code/.claude/agents/loop-scaffold.md`. Every other generic
lesson still goes into
`../02claude-code/.claude/templates/wiki-project-CLAUDE.md`. Most edits
surface nothing generic, and saying so explicitly is the correct outcome --
silence is not.

### `triage`

Read-only scan of all wiki files. Report without editing:

| Artifact | What to surface |
|---|---|
| `Requirements.md` | Open or In Progress reqs; Deferred reqs whose "Add when:" trigger in `Deferred.md` may now be met |
| `Decisions.md` / `decisions/` | ADRs in `Proposed` status; Accepted ADRs linked to a REQ that has since moved to Deferred |
| `Tests.md` | REQs with no TST coverage; tests with `Fail` status |
| `Conventions.md` | No triage -- static reference |
| `Deferred.md` | Sections for REQs no longer `Deferred` status -- should be removed, with any non-duplicate rationale migrated to `Conventions.md` first |
| `Implementation.md` | Accepted ADRs/REQs whose Decision Outcome or Consequences describe a standing, system-wide guarantee (not a one-off implementation detail) with no corresponding Implementation.md invariant entry |

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
   `README.md`. Pin every `Pipfile` dependency to its current latest stable
   version (resolve via PyPI, never guess) rather than `"*"` -- otherwise
   `check scaffold`'s Dependency pins check fails on a scaffold nobody has
   touched yet. Skip domain dirs (`input/`, `output/`, `templates/`,
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
| Makefile targets | Any CLI entry point (`__main__` block) in `app/` without a corresponding `Makefile` target; any target listed in the runner's own `help`-style output without a corresponding README mention (a target that exists but was never documented) |
| Dependency pins | Every package in the project's dependency manifest (`Pipfile`, `package.json`, etc.) is version-pinned (`==x.y.z` or a bounded range); a bare `"*"` (or unbounded equivalent) is a gap -- an unconstrained package can silently resolve to a breaking new major/pre-release version on a fresh `install`, with no code change to point to. Give it a `Makefile`/task-runner target (e.g. `make check-pins`) per this file's Design consultations note, not a raw command. This also becomes part of GATE C automatically once the target exists, since GATE C already names `check scaffold` as one of its components. |
| README structure | 5-point check, only when `README.md` was touched: (1) a Workflow overview near the top, tied to the actual Makefile/task-runner entry point, showing order and why, not a duplicate of the runner's own `help`-style command list; (2) one-time infra/ops setup split from day-to-day usage, pushed to the end (e.g. a "Maintainer setup" section); (3) citation/ADR/REQ links live as a small subnote under the heading, never in the heading text itself; (4) a step whose prose chains 2+ sequential actions/consequences is broken into a sub-list, not a run-on sentence; (5) a prerequisite is a one-clause `Requires: [link]` using a native anchor link, not a separate table. This is also part of GATE C, so future decision-record implementations touching `README.md` get it automatically. |

Output: a short report. No file edits in `../<prefix><name>`.

### check loop

Read-only audit of an autonomous-loop setup for this project. Given
`[repo folder]` (sibling code) and `[wiki folder]` (this wiki), invoke the
`loop-scaffold` agent in Audit mode:

> Agent(subagent_type: `loop-scaffold`, prompt: "Audit the loop at
> `[wiki folder]/.claude/loop.md` against `[repo folder]`.")

That agent's own Audit mode owns the full checklist and the post-run
prompt-audit step. No file edits either way.

### `land loop`

Lands verified loop work: merges the sibling repo's work branch into its
default branch and pushes. Human-triggered -- the loop never calls this, and
`Boundaries` in loop.md forbids it doing so.

**Refuse to start if the loop may still be running.** Two free signals, either
one is enough to stop:
- the wiki or `../<prefix><name>` has an unclean working tree
- `.claude/loop-state.json` was modified more recently than the wake cadence
  (`find <wiki>/.claude/loop-state.json -mmin -<cadence in minutes>`; macOS
  `find` rejects `-newermt` with a relative offset, ISO 8601 only)

A shared checkout with two agents in it produces branch switches mid-command.
Do not build a lockfile for this -- these two checks cost one command each.

1. `git -C ../<prefix><name> merge --ff-only <work-branch>`

   `--ff-only` IS the check. It fails rather than inventing a merge commit
   nobody reviewed. A diverged history is a human decision -- stop and report,
   never retry with a plain merge.

   `not something we can merge` means the work branch does not exist, which is
   the NORMAL state after a previous `land loop` and before the loop's first tick.
   Report "nothing to land" and stop. It needs no precondition check of its own
   -- the merge already distinguishes it from a real failure.

2. Run the project's test command on the default branch.

   On failure, re-run the same suite on the pre-merge commit and report only
   the failures that are NEW. Do not hardcode a list of known-failing tests --
   it rots, and a stale list hides the regression it was meant to excuse. Skip
   this second run when the suite passes.

3. Push the default branch.

   If the push output mentions bypassing a rule (e.g. GitHub's
   `remote: Bypassed rule violations for refs/heads/main`), record that in the
   report. It means a protection rule -- usually a pull-request requirement --
   was skipped because the pushing account may bypass it. Not an error; the
   push is human-authorized. It is worth seeing because it is silent otherwise.

4. Assert clean, do not tidy:
   - working tree clean in both repos
   - default branch not ahead of its remote

   Do NOT delete the work branch. After a fast-forward it points at the same
   commit as the default branch, and the next tick commits onto it again.
   Deleting it only forces Setup's `-b` path to run, which buys nothing.

Output: a short report -- what merged, test result, whether a rule was
bypassed, clean-state assertions. No file edits.

Deliberately absent: a ponytail review pass (GATE C already applies the
ponytail rubric to every diff the loop produces) and a commit step (the loop
commits its own work; anything uncommitted at `land loop` time is the
loop-may-be-running signal firing, not work for `land loop` to finish).

### `sync wiki`

Audits THIS wiki's `CLAUDE.md` against the canonical template at
`../02claude-code/.claude/templates/wiki-project-CLAUDE.md`, and extends it in
the same flow. Additive only.

1. **Applicability first.** Does this wiki have real ongoing implementation
   surface -- a sibling code repo, a pipeline, a spec the template's artifacts
   would track? If not, it is a personal wiki by design: report "not
   applicable" and stop. Template-absence is not a gap on a wiki that was never
   meant to have it, and "not applicable" is a complete, valid outcome.

2. **Compare, allowing for functional equivalents.** A document already doing a
   canonical artifact's job under a different name is NOT a gap. Check for the
   canonical artifacts and commands, and for any project document that exists
   but is not surfaced from `CLAUDE.md`.

3. **Present a gap table:** `Gap | Canonical expectation | This wiki's actual
   state`. Then put the proposed additions to ponytail.

   The gate is NARROW by design. Reject only what this project can never run --
   `create scaffold` where the sibling repo already exists -- or an artifact row
   for a file that does not exist. Do NOT reject a command because the project
   has no use for it YET: these commands exist so a project can ADOPT them, and
   a project cannot build a good loop without the audit that describes what a
   good one looks like. "Not needed today" is an argument for including it, not
   against.

4. **NEVER remove.** Lines here that are absent from the canonical template are
   this project's own, and a longer `CLAUDE.md` than canonical is the expected
   state, not drift. Adapt canonical wording to this project's paths, stack and
   vocabulary rather than pasting it verbatim.

5. **Writes `CLAUDE.md` only.** Never creates `Requirements.md`, `Tests.md`,
   `Decisions.md` or any other artifact -- those come into existence on their
   own triggers, per the wiki-structure rules above.

Output: a short report.

### `create loop`

Scaffolds an autonomous-loop setup. Signature:
`/wiki create loop [repo folder] [wiki folder] [docs/user instructions]`

Invoke the `loop-scaffold` agent in Generate mode:

> Agent(subagent_type: `loop-scaffold`, prompt: "Generate a loop for
> `[repo folder]` and `[wiki folder]`. `[docs/user instructions]`.")

That agent owns the full generation: the mandatory discover-source question,
`loop.md`, persisted subagents, permissions, and wire-back hooks. It will ask
the operator directly for anything it still needs (the discover-source
answer, the work-step definition) -- do not pre-answer on its behalf.

If `[docs/user instructions]` is not yet known, gather it first (what counts
as a unit of work, which project documents are authoritative, which are
stale) before invoking the agent, or let the agent ask if it comes up short.

The agent finishes by running its own Audit mode against what it generated
and must pass before handing back control.
