#!/usr/bin/env bats

# Source make.sh to load all functions into scope
MAKE_SH="$(cd "$(dirname "$BATS_TEST_FILENAME")/.." && pwd)/make.sh"

setup() {
  source "$MAKE_SH"
  TMPDIR="$(mktemp -d)"
  FAKE_BIN="$(mktemp -d)"
}

teardown() {
  rm -rf "$TMPDIR" "$FAKE_BIN"
}

# --- check_gh ---

@test "check_gh: passes and prints version when gh is on PATH" {
  run check_gh
  [ "$status" -eq 0 ]
  [[ "$output" == *"[OK]"* ]]
  [[ "$output" == *"gh"* ]]
}

@test "check_gh: fails with error when gh is absent from PATH" {
  PATH="$FAKE_BIN" run check_gh
  [ "$status" -ne 0 ]
  [[ "$output" == *"[ERROR]"* ]]
  [[ "$output" == *"gh CLI not installed"* ]]
}

# --- check_bats ---

@test "check_bats: passes and prints version when bats is on PATH" {
  run check_bats
  [ "$status" -eq 0 ]
  [[ "$output" == *"[OK]"* ]]
  [[ "$output" == *"bats"* ]]
}

@test "check_bats: warns but exits 0 when bats is absent from PATH" {
  PATH="$FAKE_BIN" run check_bats
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN]"* ]]
  [[ "$output" == *"bats not installed"* ]]
}

# --- check_uvx ---

@test "check_uvx: passes and prints version when uvx is on PATH" {
  run check_uvx
  [ "$status" -eq 0 ]
  [[ "$output" == *"[OK]"* ]]
  [[ "$output" == *"uvx"* ]]
}

@test "check_uvx: warns but exits 0 when uvx is absent from PATH" {
  PATH="$FAKE_BIN" run check_uvx
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN]"* ]]
  [[ "$output" == *"uvx not installed"* ]]
}

# --- check_ledger ---

@test "check_ledger: passes and prints version when ledger is on PATH" {
  run check_ledger
  [ "$status" -eq 0 ]
  [[ "$output" == *"[OK]"* ]]
  [[ "$output" == *"ledger"* ]]
}

@test "check_ledger: warns but exits 0 when ledger is absent from PATH" {
  PATH="$FAKE_BIN" run check_ledger
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN]"* ]]
  [[ "$output" == *"ledger not installed"* ]]
}

# --- check_link ---

@test "check_link: reports not set up when neither symlink exists" {
  HOME="$TMPDIR" run check_link
  [ "$status" -eq 0 ]
  [[ "$output" == *"[NONE]"* ]]
}

@test "check_link: reports OK for both when both symlinks exist" {
  mkdir -p "$TMPDIR/.claude"
  ln -s /tmp "$TMPDIR/.claude/commands"
  ln -s /tmp "$TMPDIR/.claude/agents"
  HOME="$TMPDIR" run check_link
  [ "$status" -eq 0 ]
  [[ "$output" == *"[OK]"* ]]
  [[ "$output" != *"[NONE]"* ]]
}

@test "check_link: reports WARN when real directory exists instead of symlink" {
  mkdir -p "$TMPDIR/.claude/commands"
  HOME="$TMPDIR" run check_link
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN]"* ]]
}

# --- link_item ---

@test "link_item: fails with usage when no arguments given" {
  run link_item
  [ "$status" -ne 0 ]
  [[ "$output" == *"[Usage]"* ]]
}

@test "link_item: fails with usage when only one argument given" {
  run link_item /tmp
  [ "$status" -ne 0 ]
  [[ "$output" == *"[Usage]"* ]]
}

@test "link_item: creates symlink from source to dest" {
  local source="$TMPDIR/source" dest="$TMPDIR/dest"
  mkdir -p "$source"
  run link_item "$source" "$dest"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[OK]"* ]]
  [ -L "$dest" ]
}

@test "link_item: is idempotent when symlink already exists" {
  local dest="$TMPDIR/dest"
  ln -s /tmp "$dest"
  run link_item /tmp "$dest"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[SKIP]"* ]]
}

@test "link_item: warns but exits 0 when real directory already exists" {
  local dest="$TMPDIR/dest"
  mkdir -p "$dest"
  run link_item /tmp "$dest"
  [ "$status" -eq 0 ]
  [[ "$output" == *"[WARN]"* ]]
}
