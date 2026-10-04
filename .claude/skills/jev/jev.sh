#!/bin/bash
# usage: jev.sh choice|noul|score [menu.json|file.md#name [state-file]]   (menu on stdin if no file)
# state-file: raw text, becomes the menu's state (for unattended callers that cannot pipe)
# Any runtime failure (no key, network, http, bad answer) prints "unavailable (reason)" and
# exits 0, so a caller carries on without advice. Exit 2 is a caller bug: bad shape or menu.
set -uo pipefail
umask 077
URL=${JEV_URL:-https://api.typesafe.ai/v1/systemone}  # override only to test failure paths
t=${1:-}; case $t in choice|noul|score) ;; *) echo "supported: choice noul score" >&2; exit 2;; esac
unavail() { echo "unavailable ($1)"; exit 0; }
[ -n "${TYPESAFE_API_KEY:-}" ] || unavail "no key"
req=$(mktemp); out=$(mktemp); trap 'rm -f "$req" "$out"' EXIT
m=${2:-/dev/stdin}
case $m in *.md#*) rub=$(mktemp); trap 'rm -f "$req" "$out" "$rub"' EXIT   # file.md#name: fenced block "json rubric:name"
  awk -v n="${m#*#}" '$0=="```json rubric:" n {on=1; next} on && $0=="```" {exit} on' "${m%%#*}" > "$rub"; m=$rub;; esac
jq -ce --arg t "$t" --rawfile st "${3:-/dev/null}" '(if $st != "" then . + {state:$st} else . end)
  | select(.state and .instructions
    and ($t!="choice" or (.options|length)>=2)
    and ($t!="score" or ((.levels|length)>=2 and (.levels|length)<=10)))
  | {state, model:"jev-latest", questions:{q:({type:$t, instructions}
      + (if $t=="choice" then {criteria:.options} elif $t=="score" then {criteria:.levels}
         elif .criteria then {criteria} else {} end))}}' "$m" > "$req" 2>/dev/null \
  && [ -s "$req" ] || { echo "menu invalid for $t" >&2; exit 2; }
rc=0
code=$(printf 'header = "Authorization: Bearer %s"\n' "$TYPESAFE_API_KEY" |
  curl -sS -K - --max-time 15 --retry 1 --retry-delay 2 -o "$out" -w '%{http_code}' \
    -H 'Content-Type: application/json' -d @"$req" "$URL" 2>/dev/null) || rc=$?
[ "$rc" = 0 ] || unavail "$([ "$rc" = 28 ] && echo timeout || echo network)"
[ "$code" = 200 ] || unavail "http $code"
jq -r '.answers.q // empty | . as $a | if .type=="noul" then "noul=\(.noul) (probability of yes)"
  else "\(.type)=\(.choice // .score) confidence=\(.confidence) sum=\([.probabilities[]]|add)",
       (.probabilities|to_entries|sort_by(-.value)[]|"\(.value)\t\(.key)\t\($a.legend[.key]? // "")") end' "$out" 2>/dev/null | grep . \
  || unavail "bad answer"
