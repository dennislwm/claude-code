#!/usr/bin/env python3
"""Generate .plumb/gaps.json from existing plumb coverage data.

Derives gaps from:
  - .plumb/requirements.json       (all requirements)
  - .plumb/code_coverage_map.json  (spec-to-code: implemented flag)
  - test_paths from .plumb/config.json (spec-to-test: # plumb: req-xxx markers)

Run from any project root: plumb-gaps
Output: .plumb/gaps.json
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

MARKER_RE = re.compile(r"#\s*plumb:\s*(req-[a-f0-9]+(?:,\s*req-[a-f0-9]+)*)")


def find_repo_root() -> Path:
    here = Path.cwd()
    for parent in [here, *here.parents]:
        if (parent / ".plumb").is_dir():
            return parent
    raise SystemExit("No .plumb/ directory found. Run from a project root with plumb initialized.")


def load_config(repo_root: Path) -> dict:
    config_path = repo_root / ".plumb" / "config.json"
    if not config_path.exists():
        raise SystemExit("No .plumb/config.json found.")
    return json.loads(config_path.read_text())


def load_requirements(repo_root: Path) -> list[dict]:
    req_path = repo_root / ".plumb" / "requirements.json"
    if not req_path.exists():
        raise SystemExit("No .plumb/requirements.json found. Run plumb parse-spec first.")
    return json.loads(req_path.read_text())


def get_tested_ids(repo_root: Path, test_paths: list[str]) -> set[str]:
    tested = set()
    for path_str in test_paths:
        test_dir = repo_root / path_str
        if not test_dir.exists():
            continue
        for f in test_dir.rglob("*.py"):
            for match in MARKER_RE.finditer(f.read_text()):
                for rid in re.findall(r"req-[a-f0-9]+", match.group(1)):
                    tested.add(rid)
    return tested


def get_implemented_ids(repo_root: Path) -> set[str]:
    cache_path = repo_root / ".plumb" / "code_coverage_map.json"
    if not cache_path.exists():
        return set()
    cache = json.loads(cache_path.read_text())
    return {
        rid
        for rid, res in cache.get("results", {}).items()
        if res.get("implemented")
    }


def main():
    repo_root = find_repo_root()
    config = load_config(repo_root)
    test_paths = config.get("test_paths", [])

    requirements = load_requirements(repo_root)
    tested_ids = get_tested_ids(repo_root, test_paths)
    implemented_ids = get_implemented_ids(repo_root)

    all_ids = {r["id"]: r["text"] for r in requirements}

    unimplemented = [
        {"id": rid, "text": text}
        for rid, text in all_ids.items()
        if rid not in implemented_ids
    ]
    untested = [
        {"id": rid, "text": text}
        for rid, text in all_ids.items()
        if rid not in tested_ids
    ]
    both = [
        {"id": rid, "text": text}
        for rid, text in all_ids.items()
        if rid not in implemented_ids and rid not in tested_ids
    ]

    gaps = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_requirements": len(requirements),
            "unimplemented": len(unimplemented),
            "untested": len(untested),
            "both": len(both),
        },
        "unimplemented": unimplemented,
        "untested": untested,
        "both": both,
    }

    gaps_file = repo_root / ".plumb" / "gaps.json"
    gaps_file.write_text(json.dumps(gaps, indent=2) + "\n")

    print(f"Total requirements : {len(requirements)}")
    print(f"Unimplemented      : {len(unimplemented)}")
    print(f"Untested           : {len(untested)}")
    print(f"Both gaps          : {len(both)}")
    print(f"Written to         : {gaps_file}")


if __name__ == "__main__":
    main()
