#!/bin/bash
# recall: bm25s keyword search over the current folder plus -s siblings.
# usage: recall.sh [-s sibling]... [-r] [--ext rst,py] "query"   |   recall.sh --selftest
set -eo pipefail
R=${RECALL_HOME:-$HOME/.recall}
V=${RECALL_VENV:-$R/venv}
here=$(cd "$(dirname "$0")" && pwd)

if [[ $1 == --selftest ]]; then
  t=$(mktemp -d); mkdir "$t/d"; echo "apple banana" > "$t/d/a.md"; echo "cherry grape" > "$t/d/b.md"
  out=$(cd "$t/d" && RECALL_HOME=$t/home RECALL_VENV=$V bash "$here/recall.sh" cherry)
  rm -rf "$t"; [[ $out == *b.md* ]] && echo "selftest ok"; exit
fi

exts=md,txt; sibs=(); rep=0
while [[ $# -gt 1 ]]; do case $1 in
  -s) sibs+=("$2"); shift 2 ;;
  -r) rep=1; shift ;;
  --ext) exts=md,txt,$2; shift 2 ;;
  *) break ;;
esac; done
q=$1
[[ -n $q ]] || { cat <<'EOF'; exit 0; }
recall: keyword search (bm25s) over the current folder.
usage: recall.sh [-s sibling]... [-r] [--ext rst,py] "query"
  -s NAME   also search sibling folder NAME (repeatable; a value containing / is used as a path)
  -r        reuse the folders and --ext from the last -s call in this folder
  --ext L   also index these extensions (default: md,txt)
examples:
  recall.sh "billing delays"
  recall.sh -s 16holovault.wiki "billing delays"
  recall.sh -r "another query"
EOF

mkdir -p "$R/last"
git -C "$R" rev-parse --is-inside-work-tree >/dev/null 2>&1 && { echo "refusing: $R is inside a git work tree" >&2; exit 1; }
[[ -x $V/bin/bm25 ]] || { echo "first use: installing bm25s into $V (about 200 MB, needs network)" >&2; python3 -m venv "$V" && "$V/bin/pip" install -q "bm25s[core]"; }

last=$R/last/$(printf %s "$PWD" | shasum | cut -c1-12)
if [[ $rep == 1 && -f $last ]]; then
  sibs=(); while IFS= read -r l; do sibs+=("$l"); done < <(sed '$d' "$last"); exts=$(tail -n 1 "$last")
elif [[ ${#sibs[@]} -gt 0 ]]; then
  { printf '%s\n' "${sibs[@]}"; echo "$exts"; } > "$last"
fi

f=("$(pwd -P)")
for s in "${sibs[@]}"; do [[ $s == */* ]] || s=$(dirname "$PWD")/$s; f+=("$(cd "$s" && pwd -P)"); done
key=$( { printf '%s\n' "${f[@]}" | sort -u; echo "$exts"; } | shasum | cut -c1-12)
d=$R/c/$(basename "$PWD")-$key; idx=$d/idx

n=(); for e in ${exts//,/ }; do n+=(-o -name "*.$e"); done
files() { find "${f[@]}" -type d \( -name '.*' -o -name node_modules \) -prune -o -type f \( "${n[@]:1}" \) "$@"; }

# rebuild when missing, a source is newer, or the file count changed (deletes); ponytail: one jq per file, batch if slow
if [[ ! -f $idx/params.index.json || -n $(files -newer "$idx/params.index.json" -print -quit) || $(files -print | wc -l | tr -d ' ') != $(cat "$d/count") ]]; then
  mkdir -p "$d"; tmp=$d/in.jsonl  # the CLI picks its format from the extension
  files -print | while IFS= read -r p; do jq -Rsc --arg p "$p" '{text: ($p + "\n" + .)}' "$p"; done > "$tmp"
  "$V/bin/bm25" index "$tmp" -c text -o "$idx" >/dev/null 2>&1 || { echo "index failed" >&2; exit 1; }; rm "$tmp"
  files -print | wc -l | tr -d ' ' > "$d/count"
fi

r=$(mktemp); "$V/bin/bm25" search -i "$idx" "$q" -k 5 -s "$r" >/dev/null 2>&1
echo "searched: ${f[*]} ($(cat "$d/count") files)"
jq -r '[.results[] | select(.score > 0)] | if length == 0 then "no matches" else .[] | (.document | split("\n")) as $l | "\(.score * 100 | round / 100)  \($l[0])\n    \($l[1:] | join(" ") | .[0:240])" end' "$r"
jq -c --arg q "$q" --arg t "$(date -u +%FT%TZ)" '{t:$t, q:$q, top:(.results[0].score // 0), gap:((.results[0].score // 0) - (.results[1].score // 0))}' "$r" >> "$d/queries.jsonl"; rm "$r"
