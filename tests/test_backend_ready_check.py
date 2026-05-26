#!/usr/bin/env python3
"""
Tests for the backend-ready hook (Claude Code and Codex).

The hook should only enforce Supabase readiness when the project docs say
Supabase is part of the backend. Apps that do not require Supabase must not
be blocked by this hook.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / ".claude" / "hooks" / "backend-ready-check.py"


def run_hook(payload: dict, cwd: Path) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    proc = subprocess.run(
        ["python3", str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd),
    )
    decision = ""
    if proc.returncode == 2:
        try:
            decision = json.loads(proc.stdout).get("decision", "")
        except json.JSONDecodeError:
            decision = ""
    if proc.returncode == 0:
        decision = "allow"
    return proc.returncode, decision


def payload(tool_name: str, tool_input: dict, cwd: Path) -> dict:
    return {"tool_name": tool_name, "tool_input": tool_input, "cwd": str(cwd)}


def write_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
    (root / "README.md").write_text("# Test\n")
    subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=root, capture_output=True, check=True)


def apply_patch_payload(path: str, body: str, cwd: Path) -> dict:
    return payload(
        "apply_patch",
        {
            "command": (
                "*** Begin Patch\n"
                f"*** Add File: {path}\n"
                f"{body}\n"
                "*** End Patch"
            )
        },
        cwd,
    )


def run_case(name: str, setup, call, expected: int) -> bool:
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        write_git_repo(tmp)
        setup(tmp)
        code, decision = run_hook(call(tmp), tmp)
    expected_decision = "allow" if expected == 0 else "block"
    verb_actual = decision or f"exit {code}"
    ok = code == expected and decision == expected_decision
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}: {verb_actual} (expected {expected_decision})")
    return ok


def setup_no_spec(_: Path) -> None:
    pass


def setup_static_spec(root: Path) -> None:
    (root / "SPEC.md").write_text(
        "# Static Site\n\n"
        "## 6. Data the app remembers\n\n"
        "The app does not remember user data.\n"
    )


def setup_supabase_spec(root: Path) -> None:
    (root / "SPEC.md").write_text(
        "# CasaSplit\n\n"
        "## 6. Data the app remembers\n\n"
        "Expenses must persist and be shared between roommates.\n\n"
        "## 9. Security and access control\n\n"
        "Users log in with Supabase Auth.\n"
    )


def setup_supabase_adr(root: Path) -> None:
    setup_static_spec(root)
    adr_dir = root / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0001-backend.md").write_text(
        "# ADR 0001: Use Supabase\n\n"
        "Status: accepted\n\n"
        "We will use Supabase as the database and auth backend.\n"
    )


def setup_supabase_env(root: Path) -> None:
    setup_supabase_spec(root)
    (root / ".env.local").write_text(
        "NEXT_PUBLIC_SUPABASE_URL=https://example.supabase.co\n"
        "NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiJ9.test\n"
    )


def setup_supabase_env_todo_key(root: Path) -> None:
    setup_supabase_spec(root)
    (root / ".env.local").write_text(
        "NEXT_PUBLIC_SUPABASE_URL=https://example.supabase.co\n"
        "NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJItodoSampleAnonKeyValue\n"
    )


def setup_supabase_subproduct_note(root: Path) -> None:
    (root / "SPEC.md").write_text(
        "# CasaSplit\n\n"
        "## 6. Data the app remembers\n\n"
        "Expenses must persist and be shared between roommates.\n\n"
        "## 9. Security and access control\n\n"
        "Users log in with Supabase Auth.\n"
        "The app does not use Supabase Storage for receipts.\n"
    )


def setup_superseded_supabase_adr(root: Path) -> None:
    setup_static_spec(root)
    adr_dir = root / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "0001-backend.md").write_text(
        "# ADR 0001: Use Supabase\n\n"
        "**Status:** superseded\n\n"
        "We once planned to use Supabase for the database and auth backend.\n"
    )


CASES = [
    {
        "name": "no SPEC means backend hook stays out of the way",
        "setup": setup_no_spec,
        "call": lambda t: apply_patch_payload("src/app.ts", "+console.log('hi')", t),
        "expected": 0,
    },
    {
        "name": "SPEC without Supabase allows code writes",
        "setup": setup_static_spec,
        "call": lambda t: apply_patch_payload("src/app.ts", "+console.log('hi')", t),
        "expected": 0,
    },
    {
        "name": "Supabase SPEC blocks app code until credentials exist",
        "setup": setup_supabase_spec,
        "call": lambda t: apply_patch_payload("src/app.ts", "+console.log('hi')", t),
        "expected": 2,
    },
    {
        "name": "Supabase ADR also blocks app code until credentials exist",
        "setup": setup_supabase_adr,
        "call": lambda t: apply_patch_payload("src/app.ts", "+console.log('hi')", t),
        "expected": 2,
    },
    {
        "name": "Supabase credentials allow normal app code",
        "setup": setup_supabase_env,
        "call": lambda t: apply_patch_payload("src/app.ts", "+console.log('hi')", t),
        "expected": 0,
    },
    {
        "name": "writing a .data/*.json store file is blocked",
        "setup": setup_supabase_env,
        "call": lambda t: apply_patch_payload(".data/expenses.json", "+[]", t),
        "expected": 2,
    },
    {
        "name": "writing a .data/*.json store file through Bash is blocked",
        "setup": setup_supabase_env,
        "call": lambda t: payload(
            "Bash",
            {"command": "mkdir -p .data && printf '[]' > .data/expenses.json"},
            t,
        ),
        "expected": 2,
    },
    {
        "name": "Supabase SPEC still allows documentation edits",
        "setup": setup_supabase_spec,
        "call": lambda t: apply_patch_payload("README.md", "+Docs only.", t),
        "expected": 0,
    },
    {
        "name": "localStorage for a UI preference is not a local backend",
        "setup": setup_supabase_env,
        "call": lambda t: apply_patch_payload(
            "src/Theme.tsx", "+localStorage.setItem('userTheme', 'dark');", t
        ),
        "expected": 0,
    },
    {
        "name": "reading a local config JSON with fs is allowed",
        "setup": setup_supabase_env,
        "call": lambda t: apply_patch_payload(
            "src/config.ts",
            "+import fs from 'fs';\n+const cfg = JSON.parse(fs.readFileSync('app.config.json', 'utf8'));",
            t,
        ),
        "expected": 0,
    },
    {
        "name": "a code file that only mentions .data/x.json in a comment is allowed",
        "setup": setup_supabase_env,
        "call": lambda t: apply_patch_payload(
            "src/legacy.ts", "+// migrated away from .data/cache.json", t
        ),
        "expected": 0,
    },
    {
        "name": "reading a .data JSON file with cat is allowed",
        "setup": setup_supabase_env,
        "call": lambda t: payload("Bash", {"command": "cat .data/expenses.json"}, t),
        "expected": 0,
    },
    {
        "name": "a SPEC that bans only Supabase Storage still requires Supabase",
        "setup": setup_supabase_subproduct_note,
        "call": lambda t: apply_patch_payload("src/app.ts", "+console.log('hi')", t),
        "expected": 2,
    },
    {
        "name": "a real anon key containing 'todo' counts as connected",
        "setup": setup_supabase_env_todo_key,
        "call": lambda t: apply_patch_payload("src/app.ts", "+console.log('hi')", t),
        "expected": 0,
    },
    {
        "name": "a superseded Supabase ADR does not activate the hook",
        "setup": setup_superseded_supabase_adr,
        "call": lambda t: apply_patch_payload("src/app.ts", "+console.log('hi')", t),
        "expected": 0,
    },
]


def test_claude_project_dir() -> bool:
    """The hook resolves the project via CLAUDE_PROJECT_DIR, like sibling hooks."""
    with tempfile.TemporaryDirectory() as proj_str, tempfile.TemporaryDirectory() as away_str:
        proj = Path(proj_str)
        setup_supabase_spec(proj)  # Supabase selected, no credentials
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = str(proj)
        call = payload(
            "Write",
            {"file_path": str(proj / "src" / "app.ts"), "content": "x"},
            away_str,
        )
        proc = subprocess.run(
            ["python3", str(HOOK)],
            input=json.dumps(call),
            capture_output=True,
            text=True,
            env=env,
            cwd=away_str,
        )
    ok = proc.returncode == 2
    verdict = "block" if proc.returncode == 2 else ("allow" if proc.returncode == 0 else f"exit {proc.returncode}")
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] hook resolves the project via CLAUDE_PROJECT_DIR: {verdict} (expected block)")
    return ok


def main() -> int:
    print("\n=== backend-ready hook ===")
    passed = 0
    failed = 0
    for case in CASES:
        if run_case(case["name"], case["setup"], case["call"], case["expected"]):
            passed += 1
        else:
            failed += 1
    if test_claude_project_dir():
        passed += 1
    else:
        failed += 1
    print(f"\nResult: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
