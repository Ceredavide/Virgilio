#!/usr/bin/env python3
"""
Tests for the Virgilio spec-validator hooks (Claude Code and Codex variants).

Each case crafts a tool-call payload, pipes it to the hook on stdin from a
fresh temp directory that does not contain SPEC.md, and asserts the exit
code: 0 means allow, 2 means block.

The temp directory is outside the worktree's git repo, so the hook's
project-root detection falls back to the temp directory itself.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_HOOK = REPO_ROOT / ".claude" / "hooks" / "spec-validator.py"
CODEX_HOOK = REPO_ROOT / ".codex" / "hooks" / "spec-validator.py"


def run_hook(hook_path: Path, payload: dict, cwd: Path) -> int:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    proc = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd),
    )
    return proc.returncode


def payload(tool_name: str, tool_input: dict, cwd: Path) -> dict:
    return {"tool_name": tool_name, "tool_input": tool_input, "cwd": str(cwd)}


CLAUDE_CASES = [
    {
        "name": "README.md whose content cites .py files",
        "build": lambda t: payload(
            "Write",
            {
                "file_path": str(t / "README.md"),
                "content": "This README mentions spec-validator.py and git-ready-check.py.",
            },
            t,
        ),
        "expected": 0,
    },
    {
        "name": "SPEC.md whose content cites other .md and .py files",
        "build": lambda t: payload(
            "Write",
            {
                "file_path": str(t / "SPEC.md"),
                "content": "Refers to project-summary.md and foo.py and bar.ts.",
            },
            t,
        ),
        "expected": 0,
    },
    {
        "name": "src/foo.py is a real code write",
        "build": lambda t: payload(
            "Write",
            {
                "file_path": str(t / "src" / "foo.py"),
                "content": "print('hi')",
            },
            t,
        ),
        "expected": 2,
    },
    {
        "name": ".virgilio/exploration/sketch.html is allowed infra",
        "build": lambda t: payload(
            "Write",
            {
                "file_path": str(t / ".virgilio" / "exploration" / "sketch.html"),
                "content": "<html>example</html>",
            },
            t,
        ),
        "expected": 0,
    },
    {
        "name": "Bash echo > foo.py is a real code write via shell",
        "build": lambda t: payload(
            "Bash",
            {"command": f"echo print > {t}/foo.py"},
            t,
        ),
        "expected": 2,
    },
    {
        "name": "Bash git status is read-only and allowed",
        "build": lambda t: payload(
            "Bash",
            {"command": "git status"},
            t,
        ),
        "expected": 0,
    },
    {
        "name": "Edit README.md with code-path content is still allowed",
        "build": lambda t: payload(
            "Edit",
            {
                "file_path": str(t / "README.md"),
                "old_string": "old text",
                "new_string": "new text talking about foo.py",
            },
            t,
        ),
        "expected": 0,
    },
    {
        "name": "MultiEdit on README.md is allowed",
        "build": lambda t: payload(
            "MultiEdit",
            {
                "file_path": str(t / "README.md"),
                "edits": [
                    {"old_string": "a", "new_string": "b talking about foo.py"},
                ],
            },
            t,
        ),
        "expected": 0,
    },
]

CODEX_CASES = [
    {
        "name": "apply_patch README.md mentioning .py",
        "build": lambda t: payload(
            "apply_patch",
            {
                "command": (
                    "*** Begin Patch\n"
                    "*** Add File: README.md\n"
                    "+This README mentions spec-validator.py.\n"
                    "*** End Patch"
                )
            },
            t,
        ),
        "expected": 0,
    },
    {
        "name": "apply_patch SPEC.md mentioning other .md and .py",
        "build": lambda t: payload(
            "apply_patch",
            {
                "command": (
                    "*** Begin Patch\n"
                    "*** Add File: SPEC.md\n"
                    "+Refers to project-summary.md and foo.py.\n"
                    "*** End Patch"
                )
            },
            t,
        ),
        "expected": 0,
    },
    {
        "name": "apply_patch src/foo.py is a real code write",
        "build": lambda t: payload(
            "apply_patch",
            {
                "command": (
                    "*** Begin Patch\n"
                    "*** Add File: src/foo.py\n"
                    "+print('hi')\n"
                    "*** End Patch"
                )
            },
            t,
        ),
        "expected": 2,
    },
    {
        "name": "apply_patch .virgilio/exploration/sketch.html is allowed infra",
        "build": lambda t: payload(
            "apply_patch",
            {
                "command": (
                    "*** Begin Patch\n"
                    "*** Add File: .virgilio/exploration/sketch.html\n"
                    "+<html>example</html>\n"
                    "*** End Patch"
                )
            },
            t,
        ),
        "expected": 0,
    },
    {
        "name": "apply_patch mixed README.md + src/foo.py blocks because of the code file",
        "build": lambda t: payload(
            "apply_patch",
            {
                "command": (
                    "*** Begin Patch\n"
                    "*** Add File: README.md\n"
                    "+text\n"
                    "*** Add File: src/foo.py\n"
                    "+print('hi')\n"
                    "*** End Patch"
                )
            },
            t,
        ),
        "expected": 2,
    },
]


def run_suite(label: str, hook_path: Path, cases: list) -> tuple[int, int]:
    print(f"\n=== {label} ===")
    passed = 0
    failed = 0
    for case in cases:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            (tmp / "src").mkdir(exist_ok=True)
            (tmp / ".virgilio" / "exploration").mkdir(parents=True, exist_ok=True)
            actual = run_hook(hook_path, case["build"](tmp), tmp)
        expected = case["expected"]
        ok = actual == expected
        verb_expected = "allow" if expected == 0 else "block"
        verb_actual = "allow" if actual == 0 else ("block" if actual == 2 else f"exit {actual}")
        if ok:
            passed += 1
            print(f"  [PASS] {case['name']}: {verb_actual} (expected {verb_expected})")
        else:
            failed += 1
            print(f"  [FAIL] {case['name']}: got {verb_actual}, expected {verb_expected}")
    return passed, failed


def main() -> int:
    cp, cf = run_suite("Claude spec-validator", CLAUDE_HOOK, CLAUDE_CASES)
    xp, xf = run_suite("Codex spec-validator", CODEX_HOOK, CODEX_CASES)
    total_p = cp + xp
    total_f = cf + xf
    print(f"\nResult: {total_p} passed, {total_f} failed")
    return 0 if total_f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
