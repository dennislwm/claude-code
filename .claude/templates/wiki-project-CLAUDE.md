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
- Status values: `Proposed`, `Accepted`, `Deprecated`, `Superseded`
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
> Commands: `triage` | `add req` | `add test` | `create scaffold` | `check scaffold`

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
