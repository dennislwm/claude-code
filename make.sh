function check_gh {
  command -v gh > /dev/null 2>&1 || { echo "[ERROR][$FUNCNAME]: gh CLI not installed."; return 1; }
  echo "[OK]   gh CLI found ($(gh --version | head -1))"
}

function check_bats {
  command -v bats > /dev/null 2>&1 || { echo "[WARN][$FUNCNAME]: bats not installed. Tests will not run."; return 0; }
  echo "[OK]   bats found ($(bats --version))"
}

function check_ledger {
  command -v ledger > /dev/null 2>&1 || { echo "[WARN][$FUNCNAME]: ledger not installed. /ledger skill will not work."; return 0; }
  echo "[OK]   ledger found ($(ledger --version 2>&1 | head -1))"
}

function check_link {
  for subdir in commands agents; do
    local dest="$HOME/.claude/$subdir"
    if [ -L "$dest" ]; then
      echo "[OK]   ~/.claude/$subdir symlink exists"
    elif [ -d "$dest" ]; then
      echo "[WARN][$FUNCNAME]: Real directory (not symlink) exists at $dest"
    else
      echo "[NONE][$FUNCNAME]: ~/.claude/$subdir not set up"
    fi
  done
}

function link_item {
  if [ -z "$1" ] || [ -z "$2" ]; then
    echo "[Usage][$FUNCNAME]: $FUNCNAME SOURCE DEST"
    return 1
  fi
  local source="$1" dest="$2"
  # Guards below mirror check_link: skip if already linked, warn if real dir exists
  if [ -L "$dest" ]; then
    echo "[SKIP] Symlink already exists at $dest"
    return 0
  fi
  if [ -d "$dest" ]; then
    echo "[WARN][$FUNCNAME]: Real directory already exists at $dest, skipping"
    return 0
  fi
  mkdir -p "$(dirname "$dest")"
  ln -s "$source" "$dest"
  echo "[OK]   Created symlink $dest -> $source"
}

function list_items {
  # Usage: list_items DIR PREFIX WIDTH
  local dir="$1" prefix="${2:-}" width="${3:-28}"
  local found=0
  for f in "$dir"/*.md; do
    [ -f "$f" ] || continue
    [ "$(basename "$f")" = "README.md" ] && continue
    local name desc
    name=$(basename "$f" .md)
    desc=$(grep -m1 '^description:' "$f" | sed 's/description: *//' | cut -c1-60)
    printf "  %s%-${width}s %s\n" "$prefix" "$name" "$desc"
    found=1
  done
  [ "$found" -eq 0 ] && echo "  (none)" || true
}

function show_status {
  echo "=== Status ==="
  check_gh || true
  check_bats || true
  check_ledger || true
  check_link
  echo "=============="
}

function setup_commands {
  local base_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  echo "=== Claude Code Skills Setup ==="
  check_gh
  check_bats
  link_item "$base_dir/.claude/commands" "$HOME/.claude/commands"
  link_item "$base_dir/.claude/agents" "$HOME/.claude/agents"
  echo "================================"
}
