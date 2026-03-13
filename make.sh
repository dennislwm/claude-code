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

# Returns: "in_path", "found_not_in_path", or "not_installed"
function _binary_state {
  local cmd="$1" fallback_path="$2"
  if command -v "$cmd" > /dev/null 2>&1; then
    echo "in_path"
  elif [ -f "$fallback_path" ]; then
    echo "found_not_in_path"
  else
    echo "not_installed"
  fi
}

# Check a binary installed to ~/.local/bin
function _check_local_bin {
  local cmd="$1" label="${2:-$1}"
  local bin_path="$HOME/.local/bin/$cmd"
  case "$(_binary_state "$cmd" "$bin_path")" in
    in_path)           echo "[OK]   $label installed ($($cmd --version 2>&1 | head -1 || echo 'no version'))" ;;
    found_not_in_path) echo "[WARN][$label]: found at $bin_path but not in PATH." ;;
    not_installed)     echo "[NONE][$label]: not installed. Run 'make setup' to install." ;;
  esac
}

function check_joplin {
  local go_bin="$HOME/go/bin"
  case "$(_binary_state joplin-butler "$go_bin/joplin-butler")" in
    in_path)
      echo "[OK]   joplin-butler found ($(joplin-butler --version 2>&1 | head -1))" ;;
    found_not_in_path)
      echo "[WARN][$FUNCNAME]: joplin-butler not in PATH. Run 'make setup' to add $go_bin to PATH."; return 0 ;;
    not_installed)
      echo "[WARN][$FUNCNAME]: joplin-butler not installed. /joplin skill will not work."; return 0 ;;
  esac
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
  case "$(_binary_state joplin-butler "$go_bin/joplin-butler")" in
    in_path)
      echo "[SKIP] joplin-butler already in PATH" ;;
    found_not_in_path)
      echo "export PATH=\"\$PATH:$go_bin\"" >> ~/.bash_profile
      export PATH="$PATH:$go_bin"
      echo "[OK]   joplin-butler added to PATH via ~/.bash_profile" ;;
    not_installed)
      echo "[WARN][$FUNCNAME]: joplin-butler not installed. Install via: go install github.com/Garoth/joplin-butler@latest"
      return 0 ;;
  esac
  if ! command -v joplin-butler > /dev/null 2>&1; then return 0; fi
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

function check_plumb {
  command -v plumb > /dev/null 2>&1 || { echo "[WARN][$FUNCNAME]: plumb not installed. Run 'make plumb-install'."; return 0; }
  echo "[OK]   plumb found ($(plumb --version 2>&1 | head -1))"
  echo "[INFO] plumb is being phased out; plumber is the replacement."
  if [ -d ".plumb" ]; then
    echo "[OK]   .plumb initialized in current directory"
  else
    echo "[NONE][$FUNCNAME]: .plumb not found. Run 'plumb init' to initialize."
  fi
}

function check_plumb_gaps { _check_local_bin plumb-gaps; }
function check_plumber    { _check_local_bin plumber; }

function _install_local_bin {
  local src="$1" bin_path="$HOME/.local/bin/$2" label="$3"
  if [ ! -f "$src" ]; then
    echo "[ERROR][$label]: $src not found."
    return 1
  fi
  mkdir -p "$HOME/.local/bin"
  cp "$src" "$bin_path"
  chmod +x "$bin_path"
  echo "[OK]   $label installed to $bin_path"
}

function setup_plumb_gaps {
  local base_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  _install_local_bin "$base_dir/common/plumb_gaps.py" plumb-gaps plumb-gaps || return 1
  # Copy to target project if TARGET_PROJECT is set and has .plumb/ initialized
  local target="${TARGET_PROJECT:-}"
  if [ -n "$target" ] && [ -d "$target/.plumb" ]; then
    cp "$base_dir/common/plumb_gaps.py" "$target/plumb_gaps.py"
    echo "[OK]   plumb_gaps.py copied to $target/"
  else
    echo "[INFO] To add plumb_gaps.py to a project: TARGET_PROJECT=/path/to/project make setup"
    echo "       or: cp $HOME/.local/bin/plumb-gaps /path/to/project/plumb_gaps.py"
  fi
}

function setup_plumber {
  local base_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  _install_local_bin "$base_dir/app/plumber.py" plumber plumber
}

function setup_plumb_hook {
  local global_settings="$HOME/.claude/settings.json"
  local hook_cmd='[ -d .plumb ] && plumb extract --auto && plumb review || true'
  # Check if hook already present
  if [ -f "$global_settings" ] && grep -q 'plumb extract' "$global_settings" 2>/dev/null; then
    echo "[SKIP] plumb Stop hook already in $global_settings"
    return 0
  fi
  if [ ! -f "$global_settings" ]; then
    echo "[WARN][$FUNCNAME]: $global_settings not found. Create it manually or run Claude Code once first."
    return 0
  fi
  command -v python3 > /dev/null 2>&1 || { echo "[ERROR][$FUNCNAME]: python3 not found. Cannot merge hook into $global_settings."; return 1; }
  # Use python3 to merge the hook into existing settings JSON
  python3 - "$global_settings" "$hook_cmd" <<'EOF'
import json, sys
path, cmd = sys.argv[1], sys.argv[2]
with open(path) as f:
    s = json.load(f)
hooks = s.setdefault("hooks", {})
stop = hooks.setdefault("Stop", [])
entry = {"hooks": [{"type": "command", "command": cmd}]}
stop.append(entry)
with open(path, "w") as f:
    json.dump(s, f, indent=2)
    f.write("\n")
EOF
  echo "[OK]   plumb Stop hook added to $global_settings"
}

function check_obsidian {
  local obsidian_mac="/Applications/Obsidian.app/Contents/MacOS"
  local plist="/Applications/Obsidian.app/Contents/Info.plist"
  case "$(_binary_state obsidian "$obsidian_mac/obsidian")" in
    in_path)
      local version
      version=$(/usr/libexec/PlistBuddy -c "Print CFBundleShortVersionString" "$plist" 2>/dev/null || echo "unknown")
      echo "[OK]   obsidian found (v${version})" ;;
    found_not_in_path)
      echo "[WARN][$FUNCNAME]: obsidian not in PATH. /obsidian skill will not work." ;;
    not_installed)
      echo "[WARN][$FUNCNAME]: obsidian not installed. /obsidian skill will not work." ;;
  esac
}

function setup_obsidian {
  local obsidian_mac="/Applications/Obsidian.app/Contents/MacOS"
  case "$(_binary_state obsidian "$obsidian_mac/obsidian")" in
    in_path)
      echo "[SKIP] obsidian already in PATH" ;;
    found_not_in_path)
      echo "export PATH=\"\$PATH:$obsidian_mac\"" >> ~/.bash_profile
      export PATH="$PATH:$obsidian_mac"
      echo "[OK]   obsidian added to PATH via ~/.bash_profile" ;;
    not_installed)
      echo "[WARN][$FUNCNAME]: obsidian not installed. /obsidian skill will not work." ;;
  esac
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
  check_gh
  check_bats || true
  check_uvx || true
  check_ledger || true
  check_joplin || true
  check_obsidian || true
  check_plumb || true
  check_plumb_gaps || true
  check_plumber || true
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
  setup_plumb_hook
  setup_plumb_gaps
  setup_plumber
  echo "================================"
}
