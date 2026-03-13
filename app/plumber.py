#!/usr/bin/env python3
"""
plumber.py — Plumber agent helper script (stdlib only).

Replaces all plumb/plumb-gaps CLI commands for the plumber Claude Code skill.

Usage:
    python3 plumber.py parse-spec
    python3 plumber.py gaps
    python3 plumber.py status
    python3 plumber.py decisions
    python3 plumber.py approve <id> [--all]
    python3 plumber.py reject <id> --reason "<text>"
    python3 plumber.py ignore <id>
    python3 plumber.py edit <id> "<text>"
    python3 plumber.py coverage
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (relative to project root, one level up from app/)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / ".plumb"
CONFIG_FILE = STATE_DIR / "config.json"
REQUIREMENTS_FILE = STATE_DIR / "requirements.json"
DECISIONS_FILE = STATE_DIR / "decisions.jsonl"
GAPS_FILE = STATE_DIR / "gaps.json"

DEFAULT_CONFIG = {
    "spec_paths": ["doc/spec.md"],
    "test_paths": ["app/tests/"],
    "source_paths": ["app/"],
}

STOP_WORDS = {
    "the", "a", "an", "is", "are", "and", "or", "of", "to", "in",
    "that", "it", "be", "with", "for", "on", "at", "by", "from",
    "this", "will", "should", "must", "can", "may", "has", "have",
    "given", "when", "if", "its", "not", "no", "all", "each",
}

BULLET_RE = re.compile(r"^[ \t]*[-*+]\s+(.+)$", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$")
SKIP_RE = re.compile(r"^(TODO|NOTE|FIXME|TBD)\b", re.IGNORECASE)

# Default decision text produced by the keyword hook — not a valid spec restatement
_HOOK_DECISION_TEXT = "Staged changes overlap with this requirement."

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def req_id(text: str) -> str:
    digest = hashlib.sha256(text.strip().lower().encode()).hexdigest()[:8]
    return f"req-{digest}"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        STATE_DIR.mkdir(exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        return DEFAULT_CONFIG.copy()
    return {**DEFAULT_CONFIG, **json.loads(CONFIG_FILE.read_text())}


def load_requirements() -> list:
    if not REQUIREMENTS_FILE.exists():
        return []
    return json.loads(REQUIREMENTS_FILE.read_text())


def save_requirements(reqs: list) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    REQUIREMENTS_FILE.write_text(json.dumps(reqs, indent=2))


def load_decisions() -> list:
    if not DECISIONS_FILE.exists():
        return []
    return [json.loads(l) for l in DECISIONS_FILE.read_text().splitlines() if l.strip()]


def save_decisions(decisions: list) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    DECISIONS_FILE.write_text(
        "\n".join(json.dumps(d) for d in decisions) + ("\n" if decisions else "")
    )


def current_commit() -> str | None:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"],
                           capture_output=True, text=True, cwd=PROJECT_ROOT)
        return r.stdout.strip() or None
    except Exception:
        return None


def _collect_files(paths: list, exts: tuple) -> list:
    files = []
    for p in paths:
        root = PROJECT_ROOT / p
        if root.is_dir():
            for f in root.rglob("*"):
                if f.suffix in exts and f.is_file():
                    files.append(f)
        elif root.is_file() and root.suffix in exts:
            files.append(root)
    return files


def _keywords(text: str) -> list:
    tokens = re.findall(r"[a-z]{4,}", text.lower())
    return [t for t in tokens if t not in STOP_WORDS][:4]


def _file_contains_any(path: Path, keywords: list) -> bool:
    try:
        content = path.read_text(encoding="utf-8", errors="replace").lower()
        return any(kw in content for kw in keywords)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# parse-spec
# ---------------------------------------------------------------------------

def parse_spec_from_text(text: str, source_file: str, existing: dict) -> list:
    """Extract requirements from spec text. existing maps req_id -> existing record."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"~~~.*?~~~", "", text, flags=re.DOTALL)

    commit = current_commit()
    results = []
    current_section = ""

    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            current_section = m.group(1).strip()
            continue
        m = BULLET_RE.match(line)
        if not m:
            continue
        raw = m.group(1).strip()
        if SKIP_RE.match(raw):
            continue
        if len(raw) < 15:
            continue

        rid = req_id(raw)
        old = existing.get(rid, {})
        results.append({
            "id": rid,
            "source_file": source_file,
            "source_section": current_section,
            "text": raw,
            "ambiguous": old.get("ambiguous", False),
            "created_at": old.get("created_at", now_iso()),
            "last_seen_commit": commit,
        })
    return results


def cmd_parse_spec(args) -> None:
    config = load_config()
    existing = {r["id"]: r for r in load_requirements()}
    all_reqs = []

    for path_str in config.get("spec_paths", []):
        path = PROJECT_ROOT / path_str
        if not path.exists():
            print(f"[plumber] WARNING: spec path not found: {path}", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        all_reqs.extend(parse_spec_from_text(text, path_str, existing))

    if not all_reqs:
        print("[plumber] ERROR: parse-spec found 0 requirements. "
              "Ensure spec files contain declarative bullet-point requirements.", file=sys.stderr)
        sys.exit(1)

    save_requirements(all_reqs)
    print(f"[plumber] Parsed {len(all_reqs)} requirements -> {REQUIREMENTS_FILE}")


# ---------------------------------------------------------------------------
# gaps
# ---------------------------------------------------------------------------

def compute_gaps(reqs: list, config: dict) -> list:
    code_exts = (".py", ".js", ".ts", ".rb", ".go", ".java", ".sh")
    test_files = _collect_files(config.get("test_paths", []), code_exts)
    source_files = _collect_files(config.get("source_paths", []), code_exts)

    gaps = []
    for req in reqs:
        kws = _keywords(req["text"])
        has_test = bool(kws) and any(_file_contains_any(f, kws) for f in test_files)
        has_code = bool(kws) and any(_file_contains_any(f, kws) for f in source_files)
        if not has_test or not has_code:
            gaps.append({
                "requirement_id": req["id"],
                "text": req["text"],
                "has_test": has_test,
                "has_code": has_code,
            })
    return gaps


def cmd_gaps(args) -> None:
    config = load_config()
    reqs = load_requirements()
    prev_count = len(json.loads(GAPS_FILE.read_text())) if GAPS_FILE.exists() else None
    gaps = compute_gaps(reqs, config)
    STATE_DIR.mkdir(exist_ok=True)
    GAPS_FILE.write_text(json.dumps(gaps, indent=2))
    if prev_count is not None:
        closed = prev_count - len(gaps)
        print(f"[plumber] {len(gaps)} gap(s) — {closed} closed -> {GAPS_FILE}")
    else:
        print(f"[plumber] {len(gaps)} gap(s) -> {GAPS_FILE}")


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def cmd_status(args) -> None:
    reqs = load_requirements()
    decisions = load_decisions()
    gaps = json.loads(GAPS_FILE.read_text()) if GAPS_FILE.exists() else []
    pending = [d for d in decisions if d.get("status") == "pending"]

    no_test = sum(1 for g in gaps if not g["has_test"])
    no_code = sum(1 for g in gaps if not g["has_code"])

    print("=== Plumber Status ===")
    print(f"  Requirements : {len(reqs)}")
    print(f"  Gaps         : {len(gaps)} total ({no_test} missing tests, {no_code} missing code)")
    print(f"  Pending      : {len(pending)} decision(s)")
    if pending:
        for d in pending[:5]:
            print(f"    [{d['id']}] {d.get('question', '')[:72]}")
        if len(pending) > 5:
            print(f"    ... and {len(pending) - 5} more")


# ---------------------------------------------------------------------------
# decisions
# ---------------------------------------------------------------------------

def cmd_decisions(args) -> None:
    pending = [d for d in load_decisions() if d.get("status") == "pending"]
    print(json.dumps(pending, indent=2))


# ---------------------------------------------------------------------------
# Decision CRUD
# ---------------------------------------------------------------------------

def _find(decisions: list, did: str) -> int:
    for i, d in enumerate(decisions):
        if d["id"] == did:
            return i
    return -1


def _mutate_decision(did: str, updates: dict) -> None:
    """Load, update one decision by id, save, or exit on missing."""
    decisions = load_decisions()
    idx = _find(decisions, did)
    if idx == -1:
        print(f"[plumber] ERROR: decision not found: {did}", file=sys.stderr)
        sys.exit(1)
    decisions[idx].update(updates)
    save_decisions(decisions)


def cmd_approve(args) -> None:
    decisions = load_decisions()
    if getattr(args, "all", False):
        count = 0
        for d in decisions:
            if d.get("status") == "pending":
                d.update({"status": "approved", "resolved_at": now_iso()})
                count += 1
        save_decisions(decisions)
        print(f"[plumber] Approved {count} decision(s).")
        return

    if not getattr(args, "id", None):
        print("[plumber] ERROR: provide <id> or --all", file=sys.stderr)
        sys.exit(1)

    _mutate_decision(args.id, {"status": "approved", "resolved_at": now_iso()})
    print(f"[plumber] Approved {args.id}.")


def cmd_reject(args) -> None:
    if not args.reason:
        print("[plumber] ERROR: --reason is required", file=sys.stderr)
        sys.exit(1)
    _mutate_decision(args.id, {"status": "rejected", "reject_reason": args.reason,
                                "resolved_at": now_iso()})
    print(f"[plumber] Rejected {args.id}: {args.reason}")


def cmd_ignore(args) -> None:
    _mutate_decision(args.id, {"status": "ignored", "resolved_at": now_iso()})
    print(f"[plumber] Ignored {args.id}.")


def cmd_edit(args) -> None:
    if not getattr(args, "text", None):
        print("[plumber] ERROR: provide replacement text", file=sys.stderr)
        sys.exit(1)
    _mutate_decision(args.id, {"decision": args.text, "edited_at": now_iso()})
    print(f"[plumber] Updated {args.id}.")


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------

def cmd_sync(args) -> None:
    config = load_config()
    decisions = load_decisions()
    approved = [d for d in decisions if d.get("status") == "approved"]

    if not approved:
        print("[plumber] No approved decisions to sync.")
        return

    reqs = {r["id"]: r for r in load_requirements()}
    test_files = _collect_files(config.get("test_paths", []), (".py",))  # hoisted out of loop
    spec_updates = 0
    test_updates = 0
    written_stubs: set[str] = set()  # dedup guard: prevents duplicate test_<slug> functions

    for dec in approved:
        rid = dec.get("requirement_id")
        if not rid or rid not in reqs:
            continue
        req = reqs[rid]

        # Skip generic hook placeholder — not a meaningful spec restatement
        if dec.get("decision") == _HOOK_DECISION_TEXT:
            continue

        # 1. Update spec bullet (req-7ec7755f)
        spec_path = PROJECT_ROOT / req["source_file"]
        if spec_path.exists():
            content = spec_path.read_text()
            old = f"- {req['text']}"
            new = f"- {dec['decision']}"
            if old in content and old != new:
                spec_path.write_text(content.replace(old, new, 1))
                spec_updates += 1

        # 2. Generate test stub (req-1b82f41d)
        if test_files:
            fn = re.sub(r"[^a-z0-9]+", "_", dec["decision"].lower())[:40].strip("_")
            fn = fn or "stub"
            if fn not in written_stubs:
                stub = f'\ndef test_{fn}():\n    # plumb:{rid}\n    pass  # TODO: implement\n'
                with test_files[0].open("a") as f:
                    f.write(stub)
                written_stubs.add(fn)
                test_updates += 1

    # Re-run gaps silently (req-82c7673a), suppress cmd_gaps stdout
    gaps = compute_gaps(load_requirements(), config)
    STATE_DIR.mkdir(exist_ok=True)
    GAPS_FILE.write_text(json.dumps(gaps, indent=2))

    print(f"[plumber] Sync: {spec_updates} spec sections updated, {test_updates} tests generated.")


# ---------------------------------------------------------------------------
# check / hook / diff (generate decisions from staged diff)
# ---------------------------------------------------------------------------

def _check_diff(diff: str, existing_decisions: list | None = None) -> list:
    """Return new decision dicts from diff without saving. Shared by check/hook/diff."""
    if not diff.strip():
        return []
    added_lines = [
        line[1:] for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    if not added_lines:
        return []
    diff_keywords = set(re.findall(r"[a-z]{4,}", " ".join(added_lines).lower())) - STOP_WORDS
    if existing_decisions is None:
        existing_decisions = load_decisions()
    existing_req_ids = {d.get("requirement_id") for d in existing_decisions if d.get("status") == "pending"}
    created = []
    for req in load_requirements():
        req_kws = set(_keywords(req["text"]))
        if req_kws & diff_keywords and req["id"] not in existing_req_ids:
            did = f"dec-{hashlib.sha256((req['id'] + diff[:64]).encode()).hexdigest()[:8]}"
            created.append({
                "id": did,
                "requirement_id": req["id"],
                "question": f"Does this change affect: {req['text'][:80]}?",
                "decision": "Staged changes overlap with this requirement.",
                "made_by": "plumber",
                "confidence": 0.6,
                "status": "pending",
                "created_at": now_iso(),
                "resolved_at": None,
            })
            existing_req_ids.add(req["id"])
    return created


def _run_staged_diff_and_save() -> tuple[list, list]:
    """Run git diff --staged, create and save new decisions, return (all_decisions, new_decisions)."""
    result = subprocess.run(
        ["git", "diff", "--staged"],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    all_decisions = load_decisions()
    new_decisions = _check_diff(result.stdout, all_decisions)
    if new_decisions:
        all_decisions.extend(new_decisions)
        save_decisions(all_decisions)
    return all_decisions, new_decisions


def cmd_check(args) -> None:
    _, new = _run_staged_diff_and_save()
    print(f"[plumber] check: {len(new)} decision(s) created from staged diff.")


def cmd_hook(args) -> None:
    """Plumb-compatible pre-commit hook: check staged diff, output JSON, exit 1 if pending."""
    all_decisions, _ = _run_staged_diff_and_save()
    pending = [d for d in all_decisions if d.get("status") == "pending"]
    print(json.dumps({"pending_decisions": len(pending), "decisions": pending}))
    if pending:
        sys.exit(1)


def cmd_diff(args) -> None:
    """Preview decisions that would be created from staged diff, without saving."""
    result = subprocess.run(
        ["git", "diff", "--staged"],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    all_decisions = load_decisions()
    existing_pending = [d for d in all_decisions if d.get("status") == "pending"]
    preview = _check_diff(result.stdout, all_decisions)
    total = len(preview) + len(existing_pending)
    print(f"[plumber] diff: {total} decision(s) would be pending "
          f"({len(existing_pending)} existing + {len(preview)} new)")
    if total:
        print(json.dumps(existing_pending + preview, indent=2))


def cmd_install_hook(args) -> None:
    """Install plumber pre-commit hook to .git/hooks/pre-commit."""
    hook_dir = PROJECT_ROOT / ".git" / "hooks"
    hook_path = hook_dir / "pre-commit"
    if not hook_dir.exists():
        print("[plumber] ERROR: .git/hooks not found. Is this a git repo?", file=sys.stderr)
        sys.exit(1)
    script = (
        "#!/bin/sh\n"
        "# Plumber pre-commit hook — auto-installed by plumber.py install-hook\n"
        "cd \"$(git rev-parse --show-toplevel)/app\" || exit 1\n"
        "if command -v pipenv >/dev/null 2>&1; then\n"
        "  output=$(pipenv run python3 plumber.py hook 2>&1)\n"
        "else\n"
        "  output=$(python3 plumber.py hook 2>&1)\n"
        "fi\n"
        "exit_code=$?\n"
        "echo \"$output\"\n"
        "exit $exit_code\n"
    )
    hook_path.write_text(script)
    hook_path.chmod(0o755)
    print(f"[plumber] Installed pre-commit hook: {hook_path}")


# ---------------------------------------------------------------------------
# coverage
# ---------------------------------------------------------------------------

def cmd_coverage(args) -> None:
    reqs = load_requirements()
    decisions = load_decisions()
    gaps = json.loads(GAPS_FILE.read_text()) if GAPS_FILE.exists() else []

    total = len(reqs)
    if total == 0:
        print("[plumber] No requirements. Run parse-spec first.")
        return

    gap_map = {g["requirement_id"]: g for g in gaps}
    has_test = sum(1 for r in reqs
                   if r["id"] not in gap_map or gap_map[r["id"]]["has_test"])
    has_code = sum(1 for r in reqs
                   if r["id"] not in gap_map or gap_map[r["id"]]["has_code"])
    resolved = {d["requirement_id"] for d in decisions
                if d.get("status") in ("approved", "rejected", "ignored")
                and d.get("requirement_id")}

    print("=== Plumber Coverage ===")
    print(f"  Total requirements : {total}")
    print(f"  Spec -> Test       : {has_test}/{total} ({100 * has_test // total}%)")
    print(f"  Spec -> Code       : {has_code}/{total} ({100 * has_code // total}%)")
    print(f"  Decision resolution: {len(resolved)}/{total} ({100 * len(resolved) // total}%)")


# ---------------------------------------------------------------------------
# coverage-semantic (reads plumb's LLM analysis from code_coverage_map.json)
# ---------------------------------------------------------------------------

CODE_COVERAGE_MAP_FILE = STATE_DIR / "code_coverage_map.json"
SEMANTIC_COVERAGE_FILE = STATE_DIR / "semantic_coverage.json"


def _print_semantic_results(label: str, results: dict, reqs: list, verbose: bool) -> None:
    req_ids = {r["id"] for r in reqs}
    matched = {rid: v for rid, v in results.items() if rid in req_ids}
    stale = len(results) - len(matched)
    implemented = sum(1 for v in matched.values() if v.get("implemented"))
    total = len(reqs)
    pct = (implemented * 100 // total) if total else 0
    print(f"=== Plumber Semantic Coverage ({label}) ===")
    print(f"  Total requirements : {total}")
    print(f"  Matched to map     : {len(matched)}/{total}"
          + (f" ({stale} stale)" if stale else ""))
    print(f"  Spec -> Code       : {implemented}/{total} ({pct}%)")
    if verbose:
        print("\n  Not implemented:")
        req_map = {r["id"]: r["text"] for r in reqs}
        for rid, v in matched.items():
            if not v.get("implemented"):
                print(f"    {rid}: {req_map.get(rid, '')[:70]}")
                if v.get("evidence"):
                    print(f"      evidence: {v['evidence'][:80]}")


def cmd_coverage_semantic(args) -> None:
    reqs = load_requirements()
    verbose = args and getattr(args, "verbose", False)

    if CODE_COVERAGE_MAP_FILE.exists():
        data = json.loads(CODE_COVERAGE_MAP_FILE.read_text())
        _print_semantic_results("LLM via plumb", data.get("results", {}), reqs, verbose)
    elif SEMANTIC_COVERAGE_FILE.exists():
        data = json.loads(SEMANTIC_COVERAGE_FILE.read_text())
        _print_semantic_results("agent-native", data.get("results", {}), reqs, verbose)
    else:
        print("[plumber] No semantic coverage data found.\n"
              "  Option A: run `plumb coverage` (requires plumb CLI + API key)\n"
              "  Option B: ask Claude to analyze requirements and write .plumb/semantic_coverage.json",
              file=sys.stderr)


# ---------------------------------------------------------------------------
# create-decision
# ---------------------------------------------------------------------------

def cmd_create_decision(args) -> None:
    did = f"dec-{hashlib.sha256(args.question.strip().lower().encode()).hexdigest()[:8]}"
    dec = {
        "id": did,
        "requirement_id": args.req_id,
        "question": args.question,
        "decision": args.decision,
        "made_by": getattr(args, "made_by", "claude"),
        "confidence": getattr(args, "confidence", 0.85),
        "status": "pending",
        "created_at": now_iso(),
        "resolved_at": None,
    }
    decisions = load_decisions()
    decisions.append(dec)
    save_decisions(decisions)
    print(f"[plumber] Created decision {did}.")


# ---------------------------------------------------------------------------
# stage
# ---------------------------------------------------------------------------

def cmd_stage(args) -> None:
    config = load_config()
    paths = [str(STATE_DIR)] + config.get("spec_paths", []) + config.get("test_paths", [])
    result = subprocess.run(["git", "add"] + paths, capture_output=True, text=True, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"[plumber] ERROR: git add failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    print(f"[plumber] Staged: {' '.join(paths)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="plumber.py",
                                description="Plumber agent helper (stdlib only)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("parse-spec")
    sub.add_parser("gaps")
    sub.add_parser("status")
    sub.add_parser("decisions")

    ap = sub.add_parser("approve")
    ap.add_argument("id", nargs="?")
    ap.add_argument("--all", action="store_true")

    rp = sub.add_parser("reject")
    rp.add_argument("id")
    rp.add_argument("--reason", required=True)

    ip = sub.add_parser("ignore")
    ip.add_argument("id")

    ep = sub.add_parser("edit")
    ep.add_argument("id")
    ep.add_argument("text")

    sub.add_parser("check")
    sub.add_parser("hook")
    sub.add_parser("diff")
    sub.add_parser("install-hook")
    sub.add_parser("coverage")
    cs = sub.add_parser("coverage-semantic")
    cs.add_argument("--verbose", action="store_true")
    sub.add_parser("sync")
    sub.add_parser("stage")

    cd = sub.add_parser("create-decision")
    cd.add_argument("--req-id", required=True)
    cd.add_argument("--question", required=True)
    cd.add_argument("--decision", required=True)
    cd.add_argument("--made-by", default="claude")
    cd.add_argument("--confidence", type=float, default=0.85)
    return p


COMMANDS = {
    "parse-spec": cmd_parse_spec,
    "gaps": cmd_gaps,
    "status": cmd_status,
    "decisions": cmd_decisions,
    "approve": cmd_approve,
    "reject": cmd_reject,
    "ignore": cmd_ignore,
    "edit": cmd_edit,
    "check": cmd_check,
    "hook": cmd_hook,
    "diff": cmd_diff,
    "install-hook": cmd_install_hook,
    "coverage": cmd_coverage,
    "coverage-semantic": cmd_coverage_semantic,
    "sync": cmd_sync,
    "stage": cmd_stage,
    "create-decision": cmd_create_decision,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
