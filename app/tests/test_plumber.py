"""Tests for plumber.py — run from app/ with: pipenv run pytest tests/ -v"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

# Import plumber module from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
import plumber


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ns(**kwargs):
    """Build a minimal argparse-like namespace."""
    return type("A", (), kwargs)()


def make_req(text: str, **kwargs) -> dict:
    rid = plumber.req_id(text)
    base = {
        "id": rid,
        "source_file": "doc/spec.md",
        "source_section": "",
        "text": text,
        "ambiguous": False,
        "created_at": "2026-01-01T00:00:00+00:00",
        "last_seen_commit": None,
    }
    base.update(kwargs)
    return base


def make_decision(did: str, rid: str, status: str = "pending", **kwargs) -> dict:
    base = {
        "id": did,
        "requirement_id": rid,
        "question": "Is this needed?",
        "decision": "Yes",
        "made_by": "llm",
        "confidence": 0.9,
        "status": status,
        "created_at": "2026-01-01T00:00:00+00:00",
        "resolved_at": None,
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# req_id
# ---------------------------------------------------------------------------

def test_req_id_format():
    # plumb:req-35123f42
    rid = plumber.req_id("The CLI reads the API key from ENV.")
    assert rid.startswith("req-")
    assert len(rid) == 12  # "req-" + 8 hex chars


def test_req_id_normalises_case_and_whitespace():
    # plumb:req-35123f42
    a = plumber.req_id("  Hello World  ")
    b = plumber.req_id("hello world")
    assert a == b


# ---------------------------------------------------------------------------
# parse_spec_from_text
# ---------------------------------------------------------------------------

def test_parse_spec_extracts_bullets():
    # plumb:req-958ba67c
    text = "## Section\n- The agent stores state in a .plumb/ directory.\n"
    results = plumber.parse_spec_from_text(text, "spec.md", {})
    assert len(results) == 1
    assert results[0]["text"] == "The agent stores state in a .plumb/ directory."


def test_parse_spec_skips_short_lines():
    # plumb:req-958ba67c
    text = "- Too short\n- This is a proper declarative requirement bullet.\n"
    results = plumber.parse_spec_from_text(text, "spec.md", {})
    assert len(results) == 1
    assert "proper" in results[0]["text"]


def test_parse_spec_skips_todo_lines():
    # plumb:req-958ba67c
    text = "- TODO: implement this later\n- The agent reads config from .plumb/config.json.\n"
    results = plumber.parse_spec_from_text(text, "spec.md", {})
    assert len(results) == 1
    assert "config" in results[0]["text"]


def test_parse_spec_strips_fenced_code_blocks():
    # plumb:req-958ba67c
    text = "- The agent uses regex.\n```python\n- fake bullet inside code\n```\n"
    results = plumber.parse_spec_from_text(text, "spec.md", {})
    assert len(results) == 1
    assert "regex" in results[0]["text"]


def test_parse_spec_tracks_section_headings():
    # plumb:req-8bd5738a
    text = "## Core\n- The agent stores requirements in JSON.\n## Decisions\n- The agent approves decisions.\n"
    results = plumber.parse_spec_from_text(text, "spec.md", {})
    assert results[0]["source_section"] == "Core"
    assert results[1]["source_section"] == "Decisions"


def test_parse_spec_preserves_existing_created_at():
    # plumb:req-8bd5738a
    existing_text = "The agent reads config from .plumb/config.json file."
    rid = plumber.req_id(existing_text)
    existing = {rid: {"created_at": "2025-01-01T00:00:00+00:00", "ambiguous": True}}
    text = f"- {existing_text}\n"
    results = plumber.parse_spec_from_text(text, "spec.md", existing)
    assert results[0]["created_at"] == "2025-01-01T00:00:00+00:00"
    assert results[0]["ambiguous"] is True


def test_parse_spec_generates_correct_id():
    # plumb:req-35123f42
    text_val = "The agent uses regex without any LLM call here."
    text = f"- {text_val}\n"
    results = plumber.parse_spec_from_text(text, "spec.md", {})
    expected = f"req-{hashlib.sha256(text_val.strip().lower().encode()).hexdigest()[:8]}"
    assert results[0]["id"] == expected


# ---------------------------------------------------------------------------
# compute_gaps
# ---------------------------------------------------------------------------

def test_compute_gaps_missing_both(tmp_path):
    # plumb:req-5b8b8fc0
    # plumb:req-de32845b
    req = make_req("The agent writes requirements to a JSON file here.")
    config = {"test_paths": [str(tmp_path / "tests")], "source_paths": [str(tmp_path / "src")]}
    (tmp_path / "tests").mkdir()
    (tmp_path / "src").mkdir()
    gaps = plumber.compute_gaps([req], config)
    assert len(gaps) == 1
    assert gaps[0]["has_test"] is False
    assert gaps[0]["has_code"] is False


def test_compute_gaps_covered_by_test(tmp_path):
    # plumb:req-5b8b8fc0
    req = make_req("The agent parses requirements from specification files.")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text("# parses requirements specification")
    (tmp_path / "src").mkdir()
    config = {"test_paths": [str(tmp_path / "tests")], "source_paths": [str(tmp_path / "src")]}
    gaps = plumber.compute_gaps([req], config)
    # has_test True, has_code False -> still a gap
    assert len(gaps) == 1
    assert gaps[0]["has_test"] is True
    assert gaps[0]["has_code"] is False


def test_compute_gaps_fully_covered_not_in_output(tmp_path):
    # plumb:req-5b8b8fc0
    req = make_req("The agent parses requirements from specification files.")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text("# parses requirements specification")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "plumber.py").write_text("# parses requirements specification")
    config = {"test_paths": [str(tmp_path / "tests")], "source_paths": [str(tmp_path / "src")]}
    gaps = plumber.compute_gaps([req], config)
    assert len(gaps) == 0


# ---------------------------------------------------------------------------
# Decision CRUD — using temp state files
# ---------------------------------------------------------------------------

@pytest.fixture()
def patched_state(tmp_path, monkeypatch):
    """Redirect all state file paths to tmp_path."""
    monkeypatch.setattr(plumber, "STATE_DIR", tmp_path / ".plumb")
    monkeypatch.setattr(plumber, "DECISIONS_FILE", tmp_path / ".plumb" / "decisions.jsonl")
    monkeypatch.setattr(plumber, "REQUIREMENTS_FILE", tmp_path / ".plumb" / "requirements.json")
    monkeypatch.setattr(plumber, "GAPS_FILE", tmp_path / ".plumb" / "gaps.json")
    monkeypatch.setattr(plumber, "CONFIG_FILE", tmp_path / ".plumb" / "config.json")
    (tmp_path / ".plumb").mkdir()
    return tmp_path


def write_decisions(patched_state, decisions):
    plumber.save_decisions(decisions)


def read_decisions(patched_state) -> list:
    return plumber.load_decisions()


def test_approve_single(patched_state):
    # plumb:req-2d973e4b
    rid = plumber.req_id("The agent stores state in a .plumb/ directory here.")
    dec = make_decision("dec-aaaa1111", rid, status="pending")
    write_decisions(patched_state, [dec])

    args = ns(id="dec-aaaa1111", all=False)
    plumber.cmd_approve(args)

    result = read_decisions(patched_state)
    assert result[0]["status"] == "approved"
    assert result[0]["resolved_at"] is not None


def test_approve_all(patched_state):
    # plumb:req-4d6a24b9
    rid = plumber.req_id("The agent stores state in a .plumb/ directory here.")
    decs = [
        make_decision("dec-0001", rid, status="pending"),
        make_decision("dec-0002", rid, status="pending"),
        make_decision("dec-0003", rid, status="approved"),
    ]
    write_decisions(patched_state, decs)

    args = ns(id=None, all=True)
    plumber.cmd_approve(args)

    result = read_decisions(patched_state)
    assert result[0]["status"] == "approved"
    assert result[1]["status"] == "approved"


def test_approve_all_only_affects_pending(patched_state):
    # plumb:req-4d6a24b9
    rid = plumber.req_id("The agent stores state in a .plumb/ directory here.")
    decs = [
        make_decision("dec-0001", rid, status="pending"),
        make_decision("dec-0002", rid, status="rejected"),
    ]
    write_decisions(patched_state, decs)

    args = ns(id=None, all=True)
    plumber.cmd_approve(args)

    result = read_decisions(patched_state)
    assert result[0]["status"] == "approved"
    assert result[1]["status"] == "rejected"  # untouched


def test_reject_sets_reason(patched_state):
    # plumb:req-9056c330
    rid = plumber.req_id("The agent stores state in a .plumb/ directory here.")
    dec = make_decision("dec-bbbb2222", rid, status="pending")
    write_decisions(patched_state, [dec])

    args = ns(id="dec-bbbb2222", reason="out of scope")
    plumber.cmd_reject(args)

    result = read_decisions(patched_state)
    assert result[0]["status"] == "rejected"
    assert result[0]["reject_reason"] == "out of scope"
    assert result[0]["resolved_at"] is not None


def test_ignore_sets_status(patched_state):
    # plumb:req-128d645f
    rid = plumber.req_id("The agent stores state in a .plumb/ directory here.")
    dec = make_decision("dec-cccc3333", rid, status="pending")
    write_decisions(patched_state, [dec])

    args = ns(id="dec-cccc3333")
    plumber.cmd_ignore(args)

    result = read_decisions(patched_state)
    assert result[0]["status"] == "ignored"
    assert result[0]["resolved_at"] is not None


def test_edit_updates_text_keeps_pending(patched_state):
    # plumb:req-a08e03fe
    rid = plumber.req_id("The agent stores state in a .plumb/ directory here.")
    dec = make_decision("dec-dddd4444", rid, status="pending", decision="Old text")
    write_decisions(patched_state, [dec])

    args = ns(id="dec-dddd4444", text="New clarified text")
    plumber.cmd_edit(args)

    result = read_decisions(patched_state)
    assert result[0]["decision"] == "New clarified text"
    assert result[0]["status"] == "pending"  # not auto-approved


def test_approve_missing_id_exits(patched_state):
    # plumb:req-2d973e4b
    write_decisions(patched_state, [])
    args = ns(id="dec-nonexistent", all=False)
    with pytest.raises(SystemExit):
        plumber.cmd_approve(args)


# ---------------------------------------------------------------------------
# coverage calculation
# ---------------------------------------------------------------------------

def test_coverage_all_gaps(patched_state, capsys):
    # plumb:req-af627f29
    reqs = [make_req("The agent stores state in a .plumb/ directory here.")]
    (patched_state / ".plumb" / "requirements.json").write_text(json.dumps(reqs))
    gaps = [{"requirement_id": reqs[0]["id"], "text": reqs[0]["text"],
             "has_test": False, "has_code": False}]
    (patched_state / ".plumb" / "gaps.json").write_text(json.dumps(gaps))
    (patched_state / ".plumb" / "decisions.jsonl").write_text("")

    args = ns()
    plumber.cmd_coverage(args)

    out = capsys.readouterr().out
    assert "0%" in out


def test_coverage_fully_covered(patched_state, capsys):
    # plumb:req-af627f29
    reqs = [make_req("The agent stores state in a .plumb/ directory here.")]
    (patched_state / ".plumb" / "requirements.json").write_text(json.dumps(reqs))
    (patched_state / ".plumb" / "gaps.json").write_text("[]")
    (patched_state / ".plumb" / "decisions.jsonl").write_text("")

    args = ns()
    plumber.cmd_coverage(args)

    out = capsys.readouterr().out
    assert "100%" in out


# ---------------------------------------------------------------------------
# State directory and stdlib-only
# ---------------------------------------------------------------------------

def test_state_stored_in_plumb_dir(patched_state):
    # plumb:req-01f97eee
    reqs = [make_req("The agent stores state in a .plumb/ directory here.")]
    plumber.save_requirements(reqs)
    assert (patched_state / ".plumb" / "requirements.json").exists()

    decisions = [make_decision("dec-0001", reqs[0]["id"])]
    plumber.save_decisions(decisions)
    assert (patched_state / ".plumb" / "decisions.jsonl").exists()


def test_no_third_party_imports():
    # plumb:req-7428faf1
    import ast, importlib
    src = (Path(__file__).parent.parent / "plumber.py").read_text()
    tree = ast.parse(src)
    stdlib = sys.stdlib_module_names
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module]
            for name in names:
                top = (name or "").split(".")[0]
                assert top in stdlib or top == "", f"Non-stdlib import found: {name}"


# ---------------------------------------------------------------------------
# status and decisions output
# ---------------------------------------------------------------------------

def test_status_shows_summary(patched_state, capsys):
    # plumb:req-8f985d78
    reqs = [make_req("The agent stores state in a .plumb/ directory here.")]
    (patched_state / ".plumb" / "requirements.json").write_text(json.dumps(reqs))
    (patched_state / ".plumb" / "gaps.json").write_text("[]")
    (patched_state / ".plumb" / "decisions.jsonl").write_text("")

    args = ns()
    plumber.cmd_status(args)

    out = capsys.readouterr().out
    assert "Requirements" in out
    assert "Gaps" in out
    assert "Pending" in out


def test_decisions_lists_only_pending(patched_state, capsys):
    # plumb:req-156c5ab4
    rid = plumber.req_id("The agent stores state in a .plumb/ directory here.")
    decs = [
        make_decision("dec-0001", rid, status="pending"),
        make_decision("dec-0002", rid, status="approved"),
    ]
    write_decisions(patched_state, decs)

    args = ns()
    plumber.cmd_decisions(args)

    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["id"] == "dec-0001"


# ---------------------------------------------------------------------------
# gaps writes file
# ---------------------------------------------------------------------------

def test_gaps_writes_json_file(patched_state):
    # plumb:req-de32845b
    reqs = [make_req("The agent writes gaps to a JSON output file here.")]
    (patched_state / ".plumb" / "requirements.json").write_text(json.dumps(reqs))
    config = {"test_paths": [], "source_paths": []}
    (patched_state / ".plumb" / "config.json").write_text(json.dumps(config))

    args = ns()
    plumber.cmd_gaps(args)

    gaps_file = patched_state / ".plumb" / "gaps.json"
    assert gaps_file.exists()
    data = json.loads(gaps_file.read_text())
    assert isinstance(data, list)
    assert data[0]["requirement_id"] == reqs[0]["id"]
    assert "has_test" in data[0]
    assert "has_code" in data[0]


# ---------------------------------------------------------------------------
# P4 — gaps closed count + stage
# ---------------------------------------------------------------------------

def test_gaps_reports_closed_count(patched_state, capsys):
    # plumb:req-82c7673a
    reqs = [make_req("The agent writes gaps to a JSON output file here.")]
    (patched_state / ".plumb" / "requirements.json").write_text(json.dumps(reqs))
    config = {"test_paths": [], "source_paths": []}
    (patched_state / ".plumb" / "config.json").write_text(json.dumps(config))

    # Seed a previous gaps.json with 2 gaps
    prev_gaps = [
        {"requirement_id": "req-aaa", "text": "old gap 1", "has_test": False, "has_code": False},
        {"requirement_id": "req-bbb", "text": "old gap 2", "has_test": False, "has_code": False},
    ]
    (patched_state / ".plumb" / "gaps.json").write_text(json.dumps(prev_gaps))

    args = ns()
    plumber.cmd_gaps(args)

    out = capsys.readouterr().out
    assert "closed" in out
    # prev=2, now=1 -> 1 closed
    assert "1 closed" in out


def test_stage_calls_git_add(patched_state, monkeypatch):
    # plumb:req-a389a385
    config = {"spec_paths": ["doc/spec.md"], "test_paths": ["app/tests/"], "source_paths": ["app/"]}
    (patched_state / ".plumb" / "config.json").write_text(json.dumps(config))

    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return type("R", (), {"returncode": 0, "stderr": ""})()

    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(plumber, "PROJECT_ROOT", patched_state)

    args = ns()
    plumber.cmd_stage(args)

    assert captured["cmd"][0:2] == ["git", "add"]
    assert str(patched_state / ".plumb") in captured["cmd"]
    assert "doc/spec.md" in captured["cmd"]
    assert "app/tests/" in captured["cmd"]


def test_create_decision_appends_pending(patched_state):
    args = ns(req_id="req-abc123", question="Should this be logged?",
              decision="Yes, log at INFO level.", made_by="claude", confidence=0.9)
    plumber.cmd_create_decision(args)

    decisions = read_decisions(patched_state)
    assert len(decisions) == 1
    assert decisions[0]["status"] == "pending"
    assert decisions[0]["requirement_id"] == "req-abc123"
    assert decisions[0]["decision"] == "Yes, log at INFO level."
    assert decisions[0]["id"].startswith("dec-")
