#!/bin/bash
# usage: gpt.sh [--read] [--fresh] [--wait] REPO "prompt"
# Hard cap per repo (Claude Code sessions only). Resume the repo's latest thread unless it is read-only
# and the call is a write call. A new session is allowed only in an empty repo, or once, read then write.
# This script never deletes. --read adds a prompt line because a resumed write thread keeps its sandbox.
set -uo pipefail
write="--write"; want="workspace-write"; mode=""; wait=""
while [ $# -gt 0 ]; do
  case $1 in --read) write=""; want="read-only";; --fresh) mode="--fresh";; --wait) wait=1;; *) break;; esac
  shift
done
repo=${1:?usage: gpt.sh [--read] [--fresh] [--wait] REPO prompt}; prompt=${2:?missing prompt}
repo=$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null) || { echo "not a git repo: $1" >&2; exit 2; }
companion=$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs 2>/dev/null | sort -V | tail -1)
[ -n "$companion" ] || { echo "codex plugin not found" >&2; exit 2; }
codex_run() { env -u CODEX_COMPANION_SESSION_ID node "$companion" "$@"; }   # unset: resume finds the latest thread across Claude sessions
sessions() {  # newest first: "<sandbox> <id>" for Claude Code sessions rooted at $repo
  local f meta
  for f in $(find ~/.codex/sessions -name '*.jsonl' -exec ls -t {} +); do
    meta=$(head -1 "$f")
    [ "$(jq -r '.payload.cwd' <<<"$meta")" = "$repo" ] && [ "$(jq -r '.payload.originator' <<<"$meta")" = "Claude Code" ] || continue
    echo "$(grep -m1 -o '"sandbox_policy":{"type":"[a-z-]*"' "$f" | sed 's/.*"type":"//;s/"//') $(jq -r '.payload.id' <<<"$meta")"
  done
}
# ponytail: the session-only cap can race before a background job creates its session file; accept this ceiling.
all=$(sessions); nr=$(grep -c '^read-only' <<<"$all"); nw=$(grep -c '^workspace-write' <<<"$all"); total=$((nr+nw))
if [ -z "$mode" ]; then   # resume unless there is no thread, or it is read-only and this call writes
  cand=$(codex_run task-resume-candidate --cwd "$repo" --json | jq -r '.candidate.threadId // empty')
  csb=$(awk -v id="$cand" '$2==id {print $1}' <<<"$all")
  mode=$([ -n "$cand" ] && { [ "$csb" = "workspace-write" ] || [ "$want" = "read-only" ]; } && echo --resume || echo --fresh)
fi
if [ "$mode" = "--fresh" ] && ! { [ "$total" -eq 0 ] || { [ "$total" -eq 1 ] && [ "$nr" -eq 1 ] && [ -n "$write" ]; }; }; then
  echo "STOP: a new $want session is not allowed in $repo ($nr read, $nw write sessions)."
  echo "Rule: a new write session ends new sessions; a new read session allows one more, a write one."
  echo "Sessions (newest first):"; sed 's/^/  /' <<<"$all"
  echo "To free a slot, run yourself: codex archive <id>   (or: codex delete <id>)"; exit 4
fi
[ -z "$write" ] && prompt="Read only: do not create, edit or delete any file. $prompt"
before=$(git -C "$repo" status --short)
printf 'before:\n%s\n' "${before:-clean}"
if [ -n "$wait" ]; then
  codex_run task --cwd "$repo" $mode $write "$prompt"
  after=$(git -C "$repo" status --short)
  printf 'after:\n%s\n' "${after:-clean}"
else
  launch=$(codex_run task --background --cwd "$repo" $mode $write "$prompt") || { rc=$?; printf '%s\n' "$launch"; exit "$rc"; }
  printf '%s\n' "$launch"
  job_id=$(sed -n 's/^.* started in the background as \([^ ]*\)\. Check .*$/\1/p' <<<"$launch")
  echo "after: run git -C $repo status --short when the job finishes"
fi
echo "jobs: node $companion status --cwd $repo --all"
if [ -z "$wait" ]; then   # an empty job id still works: the companion defaults to the latest job
  [ -n "$job_id" ] || echo "warning: job id not parsed; the status and result commands below show the latest job"
  echo "status: node $companion status ${job_id:-} --cwd $repo"
  echo "result: node $companion result ${job_id:-} --cwd $repo"
fi
