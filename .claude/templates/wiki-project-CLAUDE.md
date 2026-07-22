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
> Commands: `triage` | `add req` | `add test` | `create scaffold` | `check scaffold` | `check loop` | `land` | `sync`

Then stop. Do not run triage automatically.

**Every command's report ends with a wire-back check.** If the run surfaced a
lesson that would help a project sharing none of this code, put it to ponytail,
then wire what survives into
`../02claude-code/.claude/templates/wiki-project-CLAUDE.md` now, while the
failure is still on screen. Most runs surface nothing generic, and saying
nothing is the correct outcome.

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
| Verifier subagent | A `<wiki>/.claude/agents/*.md` exists with `model`, `effort`, `tools`, and a rubric plus an output contract; it is referenced by name in loop.md; AND every command its own rubric names exists in this file. References run both ways: a rubric saying "run `check scaffold` per this wiki's CLAUDE.md" against a wiki that never defined `check scaffold` sends the verifier after something undefined on every diff, silently |
| State | loop.md names a loop-state location (e.g. `.claude/loop-state.json`) kept separate from human-facing files, and that file is GITIGNORED. Tracking it puts progress events in history and a merge conflict on every wake -- 47 lines of them in one day. Anything that must survive belongs in a REQ, an ADR or a commit message; if loop.md both calls the file wipeable and tracks it, that is the contradiction, not the gitignore |
| Permissions | The allow-list covers EVERY mutation class the loop performs -- file edits and writes as well as git verbs -- or a documented decision to run interactive-only. A partial allow-list is indistinguishable from none: each uncovered call still prompts |
| Tooling rules | loop.md's tooling rules match the tools actually available in the session (a rule mandating an unavailable tool stalls every iteration and forces a fallback), and forbid chained Bash -- `cd X && ...` and any `&&`, `\|\|`, `;`, or subshell join. Chaining is what defeats auto-allow: the same programs run unchained do not prompt. A pipe counts as chaining, so does `$(...)`, and so does `2>/dev/null` (which additionally hides the error that explains the failure). loop.md must also forbid editing by blind in-place regex (`sed -i`) and require the Edit tool: a regex rewrites every match at once with no diff, and one such call widened a fix across a whole file and took three more `sed` calls to undo, the last computing line ranges from a file the earlier two had already rewritten. Put these rules ABOVE the dispatch step, not in a tooling section at the end -- a rule 140 lines below the step being executed is a rule the loop has already walked past |
| Boundaries | loop.md forbids irreversible or external actions a working branch cannot undo (push/merge to main, production API writes, secret reads, external network calls) |
| ADR integration (if the loop produces ADRs) | Each loop-produced ADR uses the template's standard status lifecycle and is registered in `Decisions.md`; the loop does not re-propose a gap already carrying an ADR |
| Config placement | First ask whether each repo's work branch protects anything. Branch the CODE repo: automated edits must stay off the default branch until a human merges. Do NOT branch the wiki: every write there is a reviewed artifact, not generated code, and because loop config must live on the default branch anyway, a wiki work branch forces a commit-to-default-then-merge-forward dance for every config fix -- that produced 28 merge commits in one day and two config-placement mistakes. Where a work branch does exist, `loop.md`, the verifier subagent, and any loop settings live on the default branch, not only on the branch: deleting it must not destroy the loop. Work branches carry state and work product only |
| Terminal states | Every way the loop discards or declines work leaves a durable record where the exclusion check looks. An item discarded with no record -- or recorded only in a wipeable state file -- is rediscovered and redone |
| Everything the loop records is gated | Whatever artifact the loop writes -- a decision, a defect, a requirement -- passes a gate before it is recorded. A path that writes on the producing agent's say-so will file fabrications: applying a gate retroactively to four such entries discarded one whose every assertion the code contradicted, and reframed a second |
| Gates match the artifact | A **decision** needs verifying AND deciding: an automated gate plus a human one. A **defect** needs only verifying -- a bug is a bug, so a human gate adds nothing. Gate asymmetry is correct; identical gating for both is either too slow or too loose |
| Fixes prove themselves | Any change the loop makes ships a check that FAILS before it and passes after. A suite that was already green proves nothing about the path it never exercised -- that is how the defect being fixed survived the tests in the first place |
| Internal consistency | loop.md does not contradict ITSELF: every referenced step exists and sits within the flow it belongs to, no two gates or artifacts share a name, and no rule bars what another rule requires. Iteratively-edited specs accumulate contradictions precisely because each edit is locally correct on its own -- assume they are there rather than assuming the file is coherent |
| Allow-list matches the spec | Re-check this EVERY time a command is added to this file -- adding a command is an allow-list change, and nothing links the two. `land` shipped with none of its verbs (`merge`, `rev-parse`, `stash`, `branch`) allow-listed, so it would have prompted at every step; this row had passed three consecutive runs because the spec did not yet prescribe those forms. The allow-list patterns actually match the command FORMS loop.md prescribes. Patterns are prefix matches: `Bash(git checkout *)` does not match `git -C /path checkout ...`. Paths outside the project root (a sibling repo, a virtualenv holding dependency source) need explicit `Read()` entries whatever the command |

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

### `land`

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
   the NORMAL state after a previous `land` and before the loop's first tick.
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
commits its own work; anything uncommitted at `land` time is the
loop-may-be-running signal firing, not work for `land` to finish).

### `sync`

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

Everything below is generated from THIS FILE alone. Never instruct the operator
to copy from another wiki: this template is distributable and lives on every
device, while sibling wikis do not -- on a fresh machine "copy the nearest
working loop" is a dead end.

Emit the generic sections VERBATIM and substitute only the `<...>` parts. The
cost is asymmetric, exactly as it is for the allow-list: a redundant section
costs nothing, a missing one costs a day of rediscovering it against a live
loop.

BEFORE emitting `loop.md`, ASK the operator and WAIT for an answer:

> What should discover READ to find a decision candidate?

This is the one input generation cannot recover -- everything else here derives
from this file or the sibling repo. Do not guess it, and do not emit `loop.md`
without it.

Answering it well is the hard part, and getting it wrong wastes every run. The
source is wherever REALITY CONTRADICTS THE CODE -- for a tool with users, their
reports; its own users, never its platform's. A project with no users YET takes
its demand from prospective users of comparable tools. Its own diagnostics over
live output are a DEFECT source, not a demand source: they find what is broken,
never what is missing.

Both instantiations agree on the negative: reading code, and researching the
platform a tool wraps, produce nothing usable. 13coda-cli spent five runs on the
pain of the platform it wraps -- every candidate a platform limit its CLI could
make no decision about -- while one report from a calling repo and two of its own
failure paths produced three real requirements. 13pylabel was generated on the
assumption it had no users, took its diagnostics as its demand source, and
produced zero decision records before the assumption was corrected.

A read-only defect diagnostic (a `check-*` command, a linter, a test suite) is a
DEFECT source, not a decision source. Say so and ask again. A loop generated with
only a defect source has unreachable Propose/GATE A/GATE B steps and degrades
into a defect fixer: 13pylabel was generated that way, has produced zero decision
records, and self-stops the moment its input queue is empty.

FALLBACK, generic to every loop: `../20playradar.wiki` -- a curated radar of the
operator's own technologies and techniques. Always available, so it covers the
dry season when a project-specific source yields nothing. A blip is a SOLUTION:
reframe it into the problem it would solve for THIS project, in the operator's
words, and let GATE A judge whether that problem is real. Do NOT pre-filter --
GATE A's rubric is ponytail, and "solution looking for a problem" is its rung 1.
GATE A's Rejected record retires that blip permanently, so the radar drains.

    # ponytail: every rejected blip costs a full tick (reframe + ADR + GATE A).
    # Acceptable while the radar is small; add a cheap pre-filter if dry seasons
    # start burning many ticks in a row.

Generates, all under the wiki's `.claude/`:

1. `loop.md`, in this order. The ORDER is load-bearing -- Bash discipline sits
   above dispatch because a rule 140 lines below the step being executed is one
   the loop has already walked past.

   - **Bash discipline (first, before anything else).** ONE command per Bash
     call. No `cd`, `&&`, `||`, `;`, pipe, `$(...)`, or `2>/dev/null` -- any of
     them makes the call prompt however ordinary the programs are, and
     `2>/dev/null` additionally hides the error explaining the failure.
     Crossing into the sibling repo changes nothing: use `git -C <abs path>` and
     absolute paths, never `cd`. NEVER edit with `sed -i` -- use the Edit tool;
     a blind in-place regex rewrites every match with no diff, and one such call
     widened a fix across a whole file and took three more to undo. Name the
     dependency-source path literally rather than deriving it with command
     substitution, and name the exact single-command test invocation.
   - **Setup** -- idempotent working-branch bootstrap. Branch the CODE repo
     (automated edits stay off its default branch until a human merges); do NOT
     branch the wiki (every write there is a reviewed artifact, and a wiki work
     branch forces a commit-to-default-then-merge-forward dance for every config
     fix -- 28 merge commits in one day at the first instantiation).
   - **Each iteration -- 0. BEFORE dispatch**, print any decision record still
     in the Proposed state: title, considered options, the trade-off. Printing
     is not a unit of work and never consumes the tick. Proposed means GATE B is
     INCOMPLETE, not resolved -- it matches no dispatch rung, so without this it
     is invisible to the loop forever while silently excluding its problem space
     from every future discovery.
   - **0. Dispatch**, exactly one, in order:
     a. any approved decision record -> implement it, lowest number first;
     b. else any open LOOP-SURFACED defect -> fix it, LAZIEST first (fewest
        lines and files, not oldest), skipping any marked `blocked:`;
     c. else -> discover new work, UNLESS a decision record is already parked
        awaiting the human gate. Never manufacture a second decision while the
        first awaits a call: each parked record excludes its problem space from
        future discovery, so an unanswered queue silently narrows the search
        space. Parked record and nothing at (b)? Self-stop naming the record.
        This is what makes decisions first-class -- ranking them above defects
        at (b) cannot, since a parked record has no work the loop can do and
        selecting it would only starve the defect queue on human inaction.
     Dispatch replaces an iteration counter. A counter bounds how long the loop
     runs; dispatch bounds what it may do, which is the property actually
     wanted, and it stops the queue growing unboundedly.
   - **1. Discover.** Discover's PRIMARY output is a DECISION CANDIDATE that
     carries into step 2. Name the decision source the operator gave above, and
     say what discover reads when that source is momentarily empty. Defects
     found along the way are SECONDARY -- often worth more than the decision
     that surfaced them, and lost if only mentioned in conversation, so they are
     gated and recorded, but they do NOT consume the tick.

     For defects, FIRST check whether this wiki already defines read-only
     diagnostic commands that report proposed fixes without applying them. If
     it does, THEY are the defect gate -- reuse them, and write no separate
     gate. A ladder that already ends in "unverified, never silently assume
     correct" and never writes has done the job; a second gate over it is
     duplication that will drift. (13pylabel needed no hand-written gate for
     exactly this reason; 13coda-cli needed one, because web research is
     open-ended judgement with no such command to lean on.)

     Otherwise put EVERY defect through a DEFECT GATE of three objective checks:
     the cited file:line trace verifies against the code; nothing sanctions the
     behaviour or forbids the obvious fix; not already covered.

     Either way: CONFIRMED -> record it. DISCARD/unverified -> record it as
     Rejected WITH the reason; never delete, or the same non-finding is
     re-filed next run. REFRAME -> correct the framing, then record.

     STATE THE EXIT. The tick ends at steps 2-4 or step 7 -- NEVER on a recorded
     defect. Ending it there starves the decision path: the candidate is
     discarded, dispatch (b) picks up the defect next tick, and the loop can
     only ever fix defects. A discover step that describes recording and then
     stops mid-air leaves the flow undefined.
   - **2. Propose** a decision record, status Proposed, >= 2 considered options,
     evidence URLs the human can check.
   - **3. GATE A (automated, ponytail)** -- CONFIRMED -> set status Rejected,
     append the findings VERBATIM under a `## Gate A Findings` heading, keep it
     registered, STOP. Never erase: the Rejected record is what stops the same
     work being rediscovered, and it keeps the reasoning with the artifact.
     PLAUSIBLE -> revise once. Pass -> proceed.
   - **4. GATE B (human)** -- accept / edit / defer / reject / no answer. PRINT
     the record's title, its considered options and the trade-off, then park it
     and continue. Do NOT branch on whether a human is present: there is no
     signal for that, and guessing wrong costs a decision the operator was
     sitting there ready to make. Commit Accepted AND Rejected records; an
     uncommitted Rejected record defeats its own purpose.
   - **5. Implement** on the work branch.
   - **6. GATE C (automated)** -- ponytail + the test suite + `check scaffold`.
   - **7. Fix a defect** (reached only from dispatch b). Apply the DECISION TEST
     first: if a second plausible approach can be named, STOP -- it is a
     decision, not a defect. Then write a test that FAILS against current code,
     make the smallest change that turns it green, and run GATE C.

     EVERY exit from step 7 that does not close the item must mark it
     `blocked: <reason>`, and dispatch skips anything so marked. Both
     non-closing exits use the SAME marker -- `blocked: is a decision, not a
     defect -- <the approaches named>` and `blocked: cannot fix -- <reason>` --
     because dispatch only needs "skip this, reason follows". Leaving an item
     Open because it failed the decision test livelocks the queue: dispatch
     selects it again next tick, it fails the same test, and nothing ever
     changes. The first instantiation hit this and it was fixed by hand in that
     project without fixing this spec, so it propagated into the first
     generated loop.
   - **State** -- `.claude/loop-state.json`, GITIGNORED, progress events only.
     Anything that must survive belongs in a requirement, a decision record or a
     commit message. Tracking it puts progress events in history and a conflict
     on every wake.
   - **Cadence** -- name the wakeup delay explicitly, and mark it if it is a
     testing value.
   - **Boundaries** -- work only on the branch; NEVER push to any remote.
     Merging and pushing are human actions: a protected default branch means an
     automated push either fails or silently bypasses the protection rule. Also
     escalate production writes, secret reads, and external network calls.

   Also add `.claude/loop-state.json` to the wiki's `.gitignore`, and CREATE it
   now containing `{"progress": []}`. `Edit(path)` allow-rules gate edits but
   `Write(path)` rules are INERT, so a loop-state file that does not exist yet
   forces a permission prompt on the first tick that records anything -- and no
   allow-list entry can prevent it. Creating it here makes every later write an
   Edit. Do not "tidy up" the empty file later; its existence is the fix.

2. `agents/<verifier>.md` -- a cold grader that never implements or fixes:
   `model`, `effort`, `tools`, `skills: ponytail`. GRANT IT `Grep` AND `Glob`,
   not just `Read, Bash`. An agent whose only search tool is a shell WILL chain
   (`| head`, `;`, `cd &&`, `awk` programs, a `python3` heredoc that rewrote a
   durable file by line index) -- seven prompts in one session at 13pylabel,
   because prose telling it not to chain leaves it no other way to work. Grant
   the search tools and Bash shrinks to the one test command. Never claim in an
   agent body that Grep and Glob are unavailable unless verified: that claim was
   copied between projects and manufactured the problem it warned about. Its `description` and its
   BODY must both name every artifact it grades (a decision record, a diff, a
   defect claim); a body listing fewer than the description sends it after a
   rubric it has no definition for. Rubric = ponytail + the wiki placement
   ladder + objective passes (tests, `check scaffold`). Every command the rubric
   names must exist in the wiki's CLAUDE.md -- references run both ways.
   Output contract: worst-first plain-text findings blocks (plain text until
   ReportFindings is confirmed grantable to a subagent). Do NOT put
   output-formatting skills in the rubric: the verifier reports to the loop, not
   to a human, and the block format is answer-first by construction.
3. Permissions posture -- either a scoped `.claude/settings*.json` allow-list, or
   a documented decision to run interactive-only.

   Emit this allow-list. It is not a guess: it is what one real loop converged on
   after eight rounds of removing prompts. Substitute the `<...>` paths; keep
   every other entry verbatim, one line per proven pattern. A dead rule in a
   project that never matches it costs nothing, while a MISSING rule costs a
   prompt mid-tick -- and since config loads at session start, fixing that means
   stopping the loop and relaunching. Add, never trim.

   ```json
   {
     "permissions": {
       "allow": [
         "Read(//<abs path to sibling code repo>/**)",
         "Read(//<abs path to dependency source root>/**)",
         "Edit(**)",
         "Edit(.claude/loop-state.json)",
         "Edit(//<abs path to sibling code repo>/**)",
         "Bash(<test command with its env prefix> *)",
         "Bash(<test runner> *)",
         "Bash(make test*)",
         "Bash(git status *)",
         "Bash(git log *)",
         "Bash(git diff *)",
         "Bash(git add *)",
         "Bash(git commit *)",
         "Bash(git rm *)",
         "Bash(git checkout *)",
         "Bash(git -C <abs path to wiki> status *)",
         "Bash(git -C <abs path to wiki> log *)",
         "Bash(git -C <abs path to wiki> diff *)",
         "Bash(git -C <abs path to wiki> add *)",
         "Bash(git -C <abs path to wiki> commit *)",
         "Bash(git -C <abs path to wiki> rm *)",
         "Bash(git -C <abs path to wiki> checkout *)",
         "Bash(git -C <abs path to sibling code repo> status *)",
         "Bash(git -C <abs path to sibling code repo> log *)",
         "Bash(git -C <abs path to sibling code repo> diff *)",
         "Bash(git -C <abs path to sibling code repo> add *)",
         "Bash(git -C <abs path to sibling code repo> commit *)",
         "Bash(git -C <abs path to sibling code repo> rm *)",
         "Bash(git -C <abs path to sibling code repo> checkout *)",
         "Bash(ls *)",
         "Bash(grep *)",
         "Bash(find *)",
         "Bash(wc *)",
         "Bash(gh api *)",
         "Bash(gh search *)"
       ]
     }
   }
   ```

   These notes stay HERE, never inside the JSON -- `settings.json` admits no
   comments, and a `//` line makes it unparseable:

   - **`Write(path)` rules are INERT.** Only `Edit(path)` gates file edits, and
     `Edit` covers every file-editing tool including Write. A `Write(**)` entry
     looks live and does nothing. Never emit one.
   - **Patterns are prefix matches.** `Bash(git checkout *)` does not match
     `git -C /path checkout ...`, which is why both forms appear above, for both
     repos.
   - **`Edit(**)` is scoped to the project root.** A sibling repo needs its own
     absolute `Edit(//...)` entry, and dependency source needs an absolute
     `Read(//...)`.
   - **`.claude/**` counts as settings** and prompts separately, so
     `loop-state.json` is named explicitly. Scope it to that one file -- never
     `.claude/**`, which would hand over `settings.json` and the agent
     definitions too.
   - **Three entries are stack-specific** (the test command, its runner, and
     `make test`). Swap them for your stack's equivalents; if unsure, add
     yours alongside rather than replacing.
   - **The list above is a FLOOR, not the whole list.** Walk every command the
     loop invokes -- especially the ones this wiki already defines and the loop
     reuses as its discovery stage -- and add the verbs each one implies,
     including any tool (WebFetch, WebSearch) it needs. A discovery stage that
     shells out to a sibling CLI or a project script contributes verbs no
     generic list can predict, and the loop prompts at the first thing it does.

**Finish by running `check loop` on what you just generated. It MUST pass.**
Any finding is a defect in THIS command, not in the scaffold: fix it here
first, then regenerate. Patching the output and leaving the generator broken is
how a hand-fix at one project silently propagates into every later one -- which
is exactly how the step-7 livelock reached the first generated loop.

The **work step is project-specific**: `[docs/user instructions]` defines what a
unit of work is, which project documents are authoritative, and which are stale
and must be ignored. Everything else above is generic and ships verbatim. The
first instantiation (`13coda-cli.wiki`) specialized the work step into "a defect
fix if one is queued, else a newly discovered pain point proposed as an ADR",
and validated this shape by closing three requirements with GATE C passing on
each.

**A loop with only one output type jams on everything else it finds.** If the
loop can only emit decisions, the defects it turns up while investigating have
nowhere to go: it records them and moves on, generating work it never does. Give
each artifact its own path and its own gates -- and put one test between them:
**if a second plausible approach can be named, it is a decision, not a defect.**
One obvious change (a missing call, an unchecked return) is a defect; anything
with alternatives needs the human gate a defect path deliberately lacks. Naming
the second approach IS the evidence, which keeps the test falsifiable rather than
a matter of taste.

**Changing the discover source changes the defect POPULATION the fix step
receives.** 13pylabel's fix step demanded a failing test before any repair,
correct while its only source produced code defects; a source that also reports
doc/code disagreements made that rule unsatisfiable overnight, and neither
`blocked:` exit fitted a one-line comment fix. Scope it: a failing test is
required for a change to CODE, while a doc-only fix ships without one -- the
diff is the check and GATE C still grades it, ponytail being GATE C's rubric and
already holding that trivial one-liners need no test. Re-read the fix step
whenever the source changes.

Decide where demand comes from before tuning anything else (the rule lives with
the question `create loop` asks, above); gates were
straightforward by comparison.
