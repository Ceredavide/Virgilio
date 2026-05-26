#!/usr/bin/env python3
"""
Virgilio backend readiness check for Claude Code and Codex.

Purpose:
- Enforce that a project which selected Supabase has Supabase connected
  before app-code slices begin.
- Block obvious local fake backends when Supabase is the chosen backend.

This hook is intentionally conservative. It only activates when SPEC.md or
an active ADR mentions Supabase, so apps that do not require Supabase stay
out of its way.
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

ENV_FILE_NAMES = (
    ".env.local",
    ".env.development.local",
    ".env.development",
    ".env",
)

SUPABASE_URL_NAMES = {
    "NEXT_PUBLIC_SUPABASE_URL",
    "VITE_SUPABASE_URL",
    "EXPO_PUBLIC_SUPABASE_URL",
    "SUPABASE_URL",
}

SUPABASE_KEY_NAMES = {
    # Legacy anon key naming
    "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    "VITE_SUPABASE_ANON_KEY",
    "EXPO_PUBLIC_SUPABASE_ANON_KEY",
    "SUPABASE_ANON_KEY",
    # Modern publishable key naming (current Supabase docs)
    "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
    "VITE_SUPABASE_PUBLISHABLE_KEY",
    "EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_PUBLISHABLE_KEY",
    # Common simplified form
    "SUPABASE_KEY",
}

# Publishable keys carry a stable value prefix (`sb_publishable_...`). A value
# matching this pattern is a positive signal regardless of the variable name,
# in case the user renamed the env var.
SUPABASE_PUBLISHABLE_VALUE_PATTERN = re.compile(r"^sb_publishable_[A-Za-z0-9_-]+$")

PLACEHOLDER_MARKERS = (
    "your_",
    "your-",
    "replace",
    "changeme",
    "<",
    ">",
)

# A negative lookahead so a sentence about a Supabase sub-product
# ("does not use Supabase Storage") does not disable the whole hook.
_NOT_SUBPRODUCT = r"(?!\s+(?:storage|auth|realtime|functions?|edge|vault|studio|cli)\b)"

NEGATIVE_SUPABASE_PATTERNS = [
    r"\b(?:no|not|without|avoid)\s+supabase\b" + _NOT_SUBPRODUCT,
    r"\b(?:do not|does not|will not|must not)\s+use\s+supabase\b" + _NOT_SUBPRODUCT,
    r"\b(?:non usare|senza)\s+supabase\b" + _NOT_SUBPRODUCT,
]

LOCAL_DATA_JSON_PATTERN = r"(?:[A-Za-z0-9_./\-]*/)?\.data/[A-Za-z0-9_./\-]+\.json"
SHELL_LOCAL_DATA_WRITE_PATTERNS = [
    rf"(?:>|>>)\s*['\"]?{LOCAL_DATA_JSON_PATTERN}",
    rf"\btee\b(?:\s+-a)?\s+['\"]?{LOCAL_DATA_JSON_PATTERN}",
    rf"\btouch\b[^;&|]*['\"]?{LOCAL_DATA_JSON_PATTERN}",
    rf"\b(?:cp|mv|rm)\b[^;&|]*['\"]?{LOCAL_DATA_JSON_PATTERN}",
    rf"\bpython(?:3)?\b[^;&|]*(?:open\(\s*['\"]{LOCAL_DATA_JSON_PATTERN}['\"]\s*,\s*['\"][wa+]|Path\(\s*['\"]{LOCAL_DATA_JSON_PATTERN}['\"]\s*\)\.write_text)",
    rf"\bnode\b[^;&|]*(?:writeFile|appendFile)[^;&|]*['\"]{LOCAL_DATA_JSON_PATTERN}",
]


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


def path_is_code_extension(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    if "." not in name:
        return False
    return name.rsplit(".", 1)[-1].lower() in CODE_EXTENSIONS


def path_is_allowed_infrastructure(path: str) -> bool:
    clean = normalized(path)
    return clean.startswith(ALLOWED_INFRASTRUCTURE_PREFIXES) or any(
        f"/{prefix}" in clean for prefix in ALLOWED_INFRASTRUCTURE_PREFIXES
    )


def extract_apply_patch_targets(command: str) -> list[str]:
    return re.findall(
        r"\*\*\*\s+(?:Add File|Update File|Delete File):\s+(\S+)",
        command,
    )


def tool_target_paths(tool_input: Any) -> list[str]:
    if not isinstance(tool_input, dict):
        return []
    paths: list[str] = []
    for key in ("file_path", "path", "filename", "notebook_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            paths.append(value)
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, dict):
                path = edit.get("file_path")
                if isinstance(path, str) and path:
                    paths.append(path)
    return paths


def targets_include_app_code(paths: list[str]) -> bool:
    return any(
        path_is_code_extension(path) and not path_is_allowed_infrastructure(path)
        for path in paths
    )


def target_is_local_data_file(path: str) -> bool:
    clean = normalized(path)
    return clean.startswith(".data/") and clean.endswith(".json")


def command_writes_local_data_file(command: str) -> bool:
    return any(
        re.search(pattern, command, flags=re.IGNORECASE | re.DOTALL)
        for pattern in SHELL_LOCAL_DATA_WRITE_PATTERNS
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


def is_code_write_attempt(payload: dict[str, Any]) -> bool:
    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input") or {}

    if tool_name == "apply_patch":
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        if not isinstance(command, str):
            command = "\n".join(iter_strings(tool_input))
        targets = extract_apply_patch_targets(command)
        if targets:
            return targets_include_app_code(targets)
        paths = code_path_mentions(command)
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
        return targets_include_app_code(tool_target_paths(tool_input))

    text = "\n".join(iter_strings(tool_input))
    paths = code_path_mentions(text)
    return bool(paths) and not infrastructure_only(paths)


def is_active_adr(path: Path, text: str) -> bool:
    if "/docs/adr/" not in str(path).replace("\\", "/"):
        return True
    return not re.search(r"(?im)^\s*\*{0,2}status:\*{0,2}\s*superseded\b", text[:800])


def project_decision_text(root: Path) -> str:
    paths: list[Path] = []
    spec = root / "SPEC.md"
    if spec.is_file():
        paths.append(spec)
    adr_dir = root / "docs" / "adr"
    if adr_dir.is_dir():
        paths.extend(sorted(adr_dir.glob("*.md")))

    chunks: list[str] = []
    for path in paths:
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if is_active_adr(path, text):
            chunks.append(text)
    return "\n\n".join(chunks)


def supabase_is_selected(root: Path) -> bool:
    text = project_decision_text(root).lower()
    if "supabase" not in text:
        return False
    return not any(re.search(pattern, text) for pattern in NEGATIVE_SUPABASE_PATTERNS)


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        lines = path.read_text(errors="ignore").splitlines()
    except OSError:
        return values
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        values[name.strip()] = value.strip().strip("'\"")
    return values


def candidate_env_files(root: Path) -> list[Path]:
    paths = [root / name for name in ENV_FILE_NAMES]
    for parent_name in ("app", "apps", "packages"):
        parent = root / parent_name
        if not parent.is_dir():
            continue
        if parent_name == "app":
            paths.extend(parent / name for name in ENV_FILE_NAMES)
            continue
        for child in parent.iterdir():
            if child.is_dir():
                paths.extend(child / name for name in ENV_FILE_NAMES)
    return paths


def value_looks_real(value: str) -> bool:
    clean = value.strip()
    if len(clean) < 8:
        return False
    lowered = clean.lower()
    return not any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def supabase_credentials_present(root: Path) -> bool:
    env_values: dict[str, str] = {}
    for path in candidate_env_files(root):
        if path.is_file():
            env_values.update(parse_env_file(path))

    has_url = any(value_looks_real(env_values.get(name, "")) for name in SUPABASE_URL_NAMES)
    has_key = any(value_looks_real(env_values.get(name, "")) for name in SUPABASE_KEY_NAMES)
    if not has_key:
        # Value-level fallback: a `sb_publishable_...` value indicates a real
        # Supabase publishable key even if the user renamed the variable.
        has_key = any(
            SUPABASE_PUBLISHABLE_VALUE_PATTERN.match(value.strip())
            for value in env_values.values()
            if value_looks_real(value)
        )
    return has_url and has_key


def is_local_backend_attempt(payload: dict[str, Any]) -> bool:
    """True when a write targets a `.data/*.json` store file.

    Judged strictly by the target file path - never by file content, and
    never by a path merely mentioned inside content. Content scanning
    produced false positives (legitimate `fs`/`localStorage` use, comments
    that happen to name a path) and is intentionally not done for file edits.
    """
    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input") or {}

    if tool_name == "apply_patch":
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        if not isinstance(command, str):
            command = "\n".join(iter_strings(tool_input))
        targets = extract_apply_patch_targets(command)
    elif tool_name in CODE_MODIFYING_TOOLS:
        targets = tool_target_paths(tool_input)
    elif tool_name == "Bash":
        command = "\n".join(iter_strings(tool_input))
        return command_writes_local_data_file(command)
    else:
        return False

    return any(target_is_local_data_file(path) for path in targets)


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

    if not supabase_is_selected(root):
        allow()

    if is_local_backend_attempt(payload):
        block(
            "Virgilio blocked this change because this project selects Supabase, "
            "but the change writes a JSON file under .data/ as an app data store. "
            "Use the connected Supabase backend instead of a local file."
        )

    if not is_code_write_attempt(payload):
        allow()

    if not supabase_credentials_present(root):
        block(
            "Virgilio blocked this code change because SPEC.md or an ADR selects "
            "Supabase, but Supabase is not connected yet. Add the project URL and "
            "anon key to a local environment file such as .env.local before building "
            "stored-data or login slices."
        )

    allow()


if __name__ == "__main__":
    main()
