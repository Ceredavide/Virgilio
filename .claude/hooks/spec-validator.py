#!/usr/bin/env python3
"""
Virgilio spec-validator for Claude Code and compatible hook payloads.

Purpose:
- Enforce the specification-first rule.
- Block application-code writes when SPEC.md is missing from the project root.

Notes:
- PreToolUse hooks receive a JSON object on stdin.
- File edits normally arrive as Write/Edit/MultiEdit; shell commands arrive as Bash.
- This hook is intentionally conservative: it only blocks when it can detect that a
  command or patch is trying to create or modify source-code files.
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

ALLOWED_WITHOUT_SPEC = {
    "SPEC.md",
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "ARCHITECTURE.md",
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


def path_mentions(text: str) -> list[tuple[str, str]]:
    matches = re.findall(r"(?:^|[\s'\"`:/])([A-Za-z0-9_./\-]+\.([A-Za-z0-9]+))", text)
    return [(path, ext.lower()) for path, ext in matches]


def code_path_mentions(text: str) -> list[str]:
    return [path for path, ext in path_mentions(text) if ext in CODE_EXTENSIONS]


def mentions_allowed_infrastructure_only(text: str) -> bool:
    paths = code_path_mentions(text)
    allowed_prefixes = (
        ".codex/hooks/",
        ".claude/hooks/",
        ".virgilio/exploration/",
    )
    return bool(paths) and all(
        path.startswith(allowed_prefixes) or any(f"/{prefix}" in path for prefix in allowed_prefixes)
        for path in paths
    )


def mentions_code_path(text: str) -> bool:
    return bool(code_path_mentions(text))


def mentions_allowed_doc_only(text: str) -> bool:
    names = set(re.findall(r"[A-Za-z0-9_.-]+\.md", text))
    return bool(names) and names.issubset(ALLOWED_WITHOUT_SPEC)


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


def extract_target_paths(tool_input: Any) -> list[str]:
    """Return the explicit target file paths for a file-edit tool call.

    File-edit tools (Write, Edit, MultiEdit, common MCP filesystem tools)
    pass the target path in a dedicated field. Looking at the target,
    rather than at the full tool input, is what lets us distinguish "I am
    writing a .md file that happens to mention .py files in its body"
    from "I am writing a .py file".
    """
    if not isinstance(tool_input, dict):
        return []
    paths: list[str] = []
    for key in ("file_path", "path", "filename", "notebook_path"):
        v = tool_input.get(key)
        if isinstance(v, str) and v:
            paths.append(v)
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, dict):
                p = edit.get("file_path")
                if isinstance(p, str) and p:
                    paths.append(p)
    return paths


def path_is_allowed_without_spec(path: str) -> bool:
    """A target file location that is allowed even when SPEC.md is missing."""
    name = path.rsplit("/", 1)[-1]
    if name in ALLOWED_WITHOUT_SPEC:
        return True
    allowed_prefixes = (".codex/hooks/", ".claude/hooks/", ".virgilio/exploration/")
    relative = path[2:] if path.startswith("./") else path
    if relative.startswith(allowed_prefixes):
        return True
    return any(f"/{prefix}" in path for prefix in allowed_prefixes)


def path_is_code_extension(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    if "." not in name:
        return False
    return name.rsplit(".", 1)[-1].lower() in CODE_EXTENSIONS


def targets_force_block(target_paths: list[str]) -> bool:
    """True if any target is a code file the spec-first rule should block."""
    return any(
        path_is_code_extension(p) and not path_is_allowed_without_spec(p)
        for p in target_paths
    )


def is_code_write_attempt(payload: dict[str, Any]) -> bool:
    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input") or {}

    if tool_name == "Bash":
        text = "\n".join(iter_strings(tool_input))
        setup_attempt = is_project_setup_attempt(text)
        if not setup_attempt and not any(
            re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
            for pattern in WRITE_COMMAND_PATTERNS
        ):
            return False
        if setup_attempt:
            return True
        if mentions_allowed_doc_only(text) or mentions_allowed_infrastructure_only(text):
            return False
        return mentions_code_path(text)

    # File-edit tools expose the target file path explicitly. Trust the path,
    # not the file body.
    target_paths = extract_target_paths(tool_input)
    if target_paths:
        if all(path_is_allowed_without_spec(p) for p in target_paths):
            return False
        return targets_force_block(target_paths)

    # Fallback for tool calls that do not expose a target path (rare).
    text = "\n".join(iter_strings(tool_input))
    if mentions_allowed_doc_only(text) or mentions_allowed_infrastructure_only(text):
        return False
    return mentions_code_path(text)


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

    if (root / "SPEC.md").is_file():
        allow()

    if not is_code_write_attempt(payload):
        allow()

    block(
        "Virgilio blocked this code change because SPEC.md does not exist yet. "
        "If the user is defining an app, use the spec-coauthor skill to create a real "
        "plain-language SPEC.md. Do not create a fake or minimal SPEC.md just to unlock "
        "a small code request; provide a short example in chat instead when appropriate."
    )


if __name__ == "__main__":
    main()
