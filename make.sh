function check_gh {
  command -v gh > /dev/null 2>&1 || { echo "[ERROR][$FUNCNAME]: gh CLI not installed."; return 1; }
  echo "[OK]   gh CLI found ($(gh --version 2>&1 | head -1))"
}

function check_bats {
  command -v bats > /dev/null 2>&1 || { echo "[WARN][$FUNCNAME]: bats not installed. Tests will not run."; return 0; }
  echo "[OK]   bats found ($(bats --version 2>&1 | head -1))"
}

function check_uvx {
  command -v uvx > /dev/null 2>&1 || { echo "[WARN][$FUNCNAME]: uvx not installed. /showboat skill will not work."; return 0; }
  echo "[OK]   uvx found ($(uvx --version 2>&1 | head -1))"
}

function check_ledger {
  command -v ledger > /dev/null 2>&1 || { echo "[WARN][$FUNCNAME]: ledger not installed. /ledger skill will not work."; return 0; }
  echo "[OK]   ledger found ($(ledger --version 2>&1 | head -1))"
}

function check_joplin {
  local go_bin="$HOME/go/bin"
  if ! command -v joplin-butler > /dev/null 2>&1; then
    if [ -f "$go_bin/joplin-butler" ]; then
      echo "[WARN][$FUNCNAME]: joplin-butler not in PATH. Run 'make setup' to add $go_bin to PATH."
    else
      echo "[WARN][$FUNCNAME]: joplin-butler not installed. /joplin skill will not work."
    fi
    return 0
  fi
  echo "[OK]   joplin-butler found ($(joplin-butler --version 2>&1 | head -1))"
  if [ -z "${JOPLIN_TOKEN:-}" ]; then
    echo "[WARN][$FUNCNAME]: JOPLIN_TOKEN not set. Run 'make setup' or export it manually."
    return 0
  fi
  local port="${JOPLIN_PORT:-41184}"
  local ping_result
  ping_result=$(curl -s --max-time 2 "http://localhost:${port}/ping" 2>/dev/null)
  if [ "$ping_result" = "JoplinClipperServer" ]; then
    echo "[OK]   Joplin Web Clipper reachable on port ${port}"
  else
    echo "[WARN][$FUNCNAME]: Joplin Web Clipper not reachable on port ${port}. Ensure Joplin Desktop is running with Web Clipper enabled."
  fi
}

function setup_joplin {
  local go_bin="$HOME/go/bin"
  if command -v joplin-butler > /dev/null 2>&1; then
    echo "[SKIP] joplin-butler already in PATH"
  elif [ -f "$go_bin/joplin-butler" ]; then
    echo "export PATH=\"\$PATH:$go_bin\"" >> ~/.bash_profile
    export PATH="$PATH:$go_bin"
    echo "[OK]   joplin-butler added to PATH via ~/.bash_profile"
  else
    echo "[WARN][$FUNCNAME]: joplin-butler not installed. Install via: go install github.com/Garoth/joplin-butler@latest"
    return 0
  fi
  check_joplin || true
  if ! command -v joplin-butler > /dev/null 2>&1; then
    return 0
  fi
  if [ -z "${JOPLIN_TOKEN:-}" ]; then
    echo "[INFO] JOPLIN_TOKEN not set."
    echo "       Find your token in Joplin Desktop: Settings > Web Clipper Options."
    read -r -p "       Paste your Joplin token (leave blank to skip): " input_token
    if [ -n "$input_token" ]; then
      echo "export JOPLIN_TOKEN=\"$input_token\"" >> ~/.bash_profile
      export JOPLIN_TOKEN="$input_token"
      echo "[OK]   JOPLIN_TOKEN saved to ~/.bash_profile"
    else
      echo "[SKIP] JOPLIN_TOKEN not set."
    fi
  else
    echo "[SKIP] JOPLIN_TOKEN already set"
  fi
}

function check_obsidian {
  local obsidian_mac="/Applications/Obsidian.app/Contents/MacOS"
  local plist="/Applications/Obsidian.app/Contents/Info.plist"
  if command -v obsidian > /dev/null 2>&1; then
    local version
    version=$(/usr/libexec/PlistBuddy -c "Print CFBundleShortVersionString" "$plist" 2>/dev/null || echo "unknown")
    echo "[OK]   obsidian found (v${version})"
  elif [ -d "$obsidian_mac" ]; then
    echo "[WARN][$FUNCNAME]: obsidian not in PATH. /obsidian skill will not work."
  else
    echo "[WARN][$FUNCNAME]: obsidian not installed. /obsidian skill will not work."
  fi
}

function setup_obsidian {
  local obsidian_mac="/Applications/Obsidian.app/Contents/MacOS"
  if command -v obsidian > /dev/null 2>&1; then
    echo "[SKIP] obsidian already in PATH"
  elif [ -d "$obsidian_mac" ]; then
    echo "export PATH=\"\$PATH:$obsidian_mac\"" >> ~/.bash_profile
    export PATH="$PATH:$obsidian_mac"
    echo "[OK]   obsidian added to PATH via ~/.bash_profile"
  else
    echo "[WARN][$FUNCNAME]: obsidian not installed. /obsidian skill will not work."
  fi
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
  check_uvx || true
  check_ledger || true
  check_joplin || true
  check_obsidian || true
  check_link
  echo "=============="
}

function setup_commands {
  local base_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  echo "=== Claude Code Skills Setup ==="
  check_gh
  check_bats
  setup_joplin
  setup_obsidian
  link_item "$base_dir/.claude/commands" "$HOME/.claude/commands"
  link_item "$base_dir/.claude/agents" "$HOME/.claude/agents"
  echo "================================"
}
