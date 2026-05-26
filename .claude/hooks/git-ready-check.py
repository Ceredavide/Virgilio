#!/usr/bin/env python3
"""
Virgilio Git readiness check for OpenAI Codex and compatible hook payloads.

Purpose:
- Enforce that Git is ready before app code changes begin.
- Run only after SPEC.md exists, so the specification-first hook remains first.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

CODE_EXTENSIONS = {
    "py", "js", "jsx", "ts", "tsx", "mjs", "cjs",
    "go", "rs", "java", "kt", "kts", "scala", "swift",
    "c", "cc", "cpp", "cxx", "h", "hpp",
    "rb", "php", "cs", "fs", "ex", "exs",
    "elm", "dart", "lua", "r", "jl", "nim", "zig", "v", "sol",
    "html", "css", "scss", "sass", "vue", "svelte",
    "sql", "graphql", "gql", "sh", "bash", "zsh", "fish",
}

WRITE_COMMAND_PATTERNS = [
    r"\bcat\s+.*?>",
    r"\becho\s+.*?>",
    r"\btee\b",
    r"\bprintf\s+.*?>",
    r"\btouch\b",
    r"\bmv\b",
    r"\bcp\b",
    r"\brm\b",
    r"\bmkdir\b",
    r"\bpython(?:3)?\b.*(?:open\(|write_text|Path\()",
    r"\bnode\b.*(?:writeFile|appendFile)",
    r"\bnpm\s+(?:create|init)",
    r"\bnpx\s+(?:create|degit)",
]

PROJECT_SETUP_COMMAND_PATTERNS = [
    r"\bnpm\s+(?:create|init)\b",
    r"\bnpx\s+(?:create(?:-[A-Za-z0-9_-]+)?|degit)\b",
    r"\bpnpm\s+(?:create|init)\b",
    r"\byarn\s+(?:create|init)\b",
    r"\bbun\s+(?:create|init)\b",
    r"\bcreate-react-app\b",
    r"\bexpo\s+init\b",
    r"\bng\s+new\b",
    r"\bvue\s+create\b",
]

APP_DIRECTORY_NAMES = (
    "src", "app", "pages", "components", "lib", "server", "api", "routes", "public",
)

CODE_MODIFYING_TOOLS = {
    "Write", "Edit", "MultiEdit", "str_replace", "create_file",
}

ALLOWED_INFRASTRUCTURE_PREFIXES = (
    ".codex/hooks/",
    ".claude/hooks/",
    ".virgilio/exploration/",
)


def read_payload() -> dict[str, Any]:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return {}


def project_root(payload: dict[str, Any]) -> Path:
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return Path(env_root).expanduser()

    cwd = Path(str(payload.get("cwd") or os.getcwd())).expanduser()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except Exception:
        return cwd


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_strings(child)


def normalized(path: str) -> str:
    normalized_path = path.replace("\\", "/")
    if normalized_path.startswith("./"):
        return normalized_path[2:]
    return normalized_path


def path_mentions(text: str) -> list[tuple[str, str]]:
    matches = re.findall(r"(?:^|[\s'\"`:/])([A-Za-z0-9_./\-]+\.([A-Za-z0-9]+))", text)
    return [(path, ext.lower()) for path, ext in matches]


def code_path_mentions(text: str) -> list[str]:
    return [path for path, ext in path_mentions(text) if ext in CODE_EXTENSIONS]


def infrastructure_only(paths: list[str]) -> bool:
    return bool(paths) and all(
        normalized(path).startswith(ALLOWED_INFRASTRUCTURE_PREFIXES)
        or any(f"/{prefix}" in normalized(path) for prefix in ALLOWED_INFRASTRUCTURE_PREFIXES)
        for path in paths
    )


def creates_app_directory(command: str) -> bool:
    if not re.search(r"\bmkdir\b", command):
        return False
    return any(
        re.search(rf"(?:^|[\s'\"`/])(?:\./)?{name}(?:/|[\s'\"`;]|$)", command)
        for name in APP_DIRECTORY_NAMES
    )


def is_project_setup_attempt(command: str) -> bool:
    return any(
        re.search(pattern, command, flags=re.IGNORECASE | re.DOTALL)
        for pattern in PROJECT_SETUP_COMMAND_PATTERNS
    ) or creates_app_directory(command)


def tool_file_path(tool_input: Any) -> str:
    if not isinstance(tool_input, dict):
        return ""
    for key in ("file_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def is_code_write_attempt(payload: dict[str, Any]) -> bool:
    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input") or {}

    if tool_name == "apply_patch":
        text = "\n".join(iter_strings(tool_input))
        paths = code_path_mentions(text)
        return bool(paths) and not infrastructure_only(paths)

    if tool_name == "Bash":
        command = "\n".join(iter_strings(tool_input))
        setup_attempt = is_project_setup_attempt(command)
        if not setup_attempt and not any(
            re.search(pattern, command, flags=re.IGNORECASE | re.DOTALL)
            for pattern in WRITE_COMMAND_PATTERNS
        ):
            return False
        paths = code_path_mentions(command)
        return setup_attempt or (bool(paths) and not infrastructure_only(paths))

    if tool_name in CODE_MODIFYING_TOOLS:
        path = tool_file_path(tool_input)
        if not path:
            return False
        suffix = Path(path).suffix.lstrip(".").lower()
        if suffix not in CODE_EXTENSIONS:
            return False
        return not infrastructure_only([path])

    text = "\n".join(iter_strings(tool_input))
    paths = code_path_mentions(text)
    return bool(paths) and not infrastructure_only(paths)


def git_is_initialized(root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def git_has_first_commit(root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def allow() -> None:
    sys.exit(0)


def block(reason: str) -> None:
    output = {
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
        "systemMessage": reason,
    }
    print(json.dumps(output), file=sys.stdout)
    print(reason, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    payload = read_payload()
    root = project_root(payload)

    if not (root / "SPEC.md").is_file():
        allow()

    if not is_code_write_attempt(payload):
        allow()

    if not git_is_initialized(root):
        block(
            "Virgilio blocked this code change because SPEC.md exists but Git is not set up yet. "
            "Initialize Git and create a first commit before changing app code."
        )

    if not git_has_first_commit(root):
        block(
            "Virgilio blocked this code change because Git has no first commit yet. "
            "Create an initial commit before changing app code."
        )

    allow()


if __name__ == "__main__":
    main()
