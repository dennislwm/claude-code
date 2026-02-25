# Makefile — all available make commands

*2026-02-25T14:33:03Z by Showboat 0.6.1*
<!-- showboat-id: dd1d3796-d777-4996-9754-6d7620be79b2 -->

make help lists all available targets, skills, and agents in this project.

```bash
make help
```

```output

=== Targets ===
  help     List targets, skills, and agents
  setup    Set up skills for this or a new project
  status   Check if the local machine has already been set up
  test     Run all unit tests

=== Skills ===
  /ace                          
  /gcm                          
  /gh-run-view                  View a summary or logs of a GitHub Actions workflow run
  /ledger                       Translate natural language questions into ledger CLI command
  /showboat                     Build executable demo documents that prove agent work using 

=== Agents ===
  building                      Use this agent when you need help with test-driven developme
  card-grader                   Use this agent when you need to assess card condition for pr
  cost-efficiency-reviewer      Use this agent when you need to review code changes for toke
  github-actions-devops         Use this agent when you need help with GitHub Actions workfl
  github-actions-mermaid        
  shapeup                       Use this agent when you need help with ShapeUp methodology i
  shaping                       Use this agent when you need help with iterative shaping pro

```

make setup creates symlinks from ~/.claude/commands and ~/.claude/agents to this repo. Skips gracefully if already set up.

```bash
make setup
```

```output
=== Claude Code Skills Setup ===
[OK]   gh CLI found (gh version 2.68.1 (2025-03-06))
[OK]   bats found (Bats 1.13.0)
[SKIP] Symlink already exists at /Users/dennislwm/.claude/commands
[SKIP] Symlink already exists at /Users/dennislwm/.claude/agents
================================
```

make status checks all required CLI tools are present. Each check_ function reports [OK], [WARN], or [ERROR].

```bash
make status
```

```output
=== Status ===
[OK]   gh CLI found (gh version 2.68.1 (2025-03-06))
[OK]   bats found (Bats 1.13.0)
[OK]   uvx found (uvx 0.10.6 (Homebrew 2026-02-24))
[OK]   ledger found (Ledger 3.3.2-20230330, the command-line accounting tool)
[OK]   ~/.claude/commands symlink exists
[OK]   ~/.claude/agents symlink exists
==============
```

make test runs the full bats test suite. All 16 tests cover each check_ function and link_item utility.

```bash
make test
```

```output
[OK]   bats found (Bats 1.13.0)
1..16
ok 1 check_gh: passes and prints version when gh is on PATH
ok 2 check_gh: fails with error when gh is absent from PATH
ok 3 check_bats: passes and prints version when bats is on PATH
ok 4 check_bats: warns but exits 0 when bats is absent from PATH
ok 5 check_uvx: passes and prints version when uvx is on PATH
ok 6 check_uvx: warns but exits 0 when uvx is absent from PATH
ok 7 check_ledger: passes and prints version when ledger is on PATH
ok 8 check_ledger: warns but exits 0 when ledger is absent from PATH
ok 9 check_link: reports not set up when neither symlink exists
ok 10 check_link: reports OK for both when both symlinks exist
ok 11 check_link: reports WARN when real directory exists instead of symlink
ok 12 link_item: fails with usage when no arguments given
ok 13 link_item: fails with usage when only one argument given
ok 14 link_item: creates symlink from source to dest
ok 15 link_item: is idempotent when symlink already exists
ok 16 link_item: warns but exits 0 when real directory already exists
```
