import json
import os
import logging
import re
import glob
from typing import Dict, Any, Optional, List, Tuple, NamedTuple

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.format_utils import format_text_output, grep_output, DEFAULT_SAFETY_VALVE

logger = logging.getLogger("localfile")


FORBIDDEN_FILES = ['.env', '.env.local', '.env.production', '.env.development', 'secrets.yaml', 'secrets.yml']
FORBIDDEN_PATTERNS = ['.env.', 'secret', 'password', 'key', 'token', 'credential']

MAX_FILE_SIZE = 1024 * 1024
MAX_SEARCH_SIZE = 10 * 1024 * 1024


def _validate_file_security(filepath: str) -> Optional[str]:
    filename = os.path.basename(filepath).lower()
    if filename in FORBIDDEN_FILES:
        return f"Reading {filename} is forbidden for security reasons"
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in filename:
            return f"Reading files containing '{pattern}' is forbidden for security reasons"
    return None


def _is_binary_file(filepath: str) -> bool:
    with open(filepath, 'rb') as f:
        chunk = f.read(1024)
        return b'\x00' in chunk


def _validate_file_for_reading(workdir: str, path: str) -> Tuple[Optional[str], Optional[str]]:
    path_error = validate_path(path)
    if path_error:
        return None, path_error

    realpath = os.path.join(workdir, path)
    if not os.path.exists(realpath):
        return None, f"File {path} does not exist"

    security_error = _validate_file_security(realpath)
    if security_error:
        return None, security_error

    file_size = os.path.getsize(realpath)
    if file_size > MAX_FILE_SIZE:
        return None, f"File {path} is too large ({file_size} bytes). Maximum allowed size is {MAX_FILE_SIZE} bytes"

    if _is_binary_file(realpath):
        return None, f"File {path} appears to be binary and cannot be read as text"

    return realpath, None


def _glob_files(realpath: str, include: str, recursive: bool) -> List[str]:
    if os.path.isfile(realpath):
        return [realpath]

    if recursive:
        search_pattern = os.path.join(realpath, "**", include)
        return [f for f in glob.glob(search_pattern, recursive=True) if os.path.isfile(f)]
    else:
        search_pattern = os.path.join(realpath, include)
        return [f for f in glob.glob(search_pattern) if os.path.isfile(f)]


def _parse_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"


def validate_path(path: str, allow_empty: bool = False) -> Optional[str]:
    if not path:
        return None if allow_empty else "Path cannot be empty"
    try:
        path.encode('ascii')
    except UnicodeEncodeError:
        return "Path must be ASCII only"
    forbidden_chars = '@%!$&*?'
    for char in forbidden_chars:
        if char in path:
            return f"Path contains forbidden character '{char}'"
    if ".." in path or path.startswith("/") or "\\" in path:
        return "Path contains traversal sequences"
    return None


LOCALFILE_TOOL = ckit_cloudtool.CloudTool(
    name="localfile",
    description="Read local files, call with op=\"help\" for usage",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
        "required": ["op"]
    },
)

HELP = """
cat     - Read file contents
          args: path (required), lines_range, start inclusive, end exclusive ("0:", "10:20"), safety_valve ("10k")

replace - Replace text in file, shows git-style diff
          args: path (required), find (required), replace, count (-1=all, N=limit)

find    - Find files by name pattern
          args: path (default "."), pattern (required, e.g. "*.py", "test_*")

grep    - Search file contents with context and formatting
          args: path (default "."), pattern (required), recursive (true), include ("*"), context (0)

ls      - List directory contents (dirs have "/" suffix)
          args: path (default ".")

Examples:
  localfile(op="cat", args={"path": "folder1/something_20250803.json", "lines_range": 0:40", "safety_valve": "10k"})
  localfile(op="replace", args={"path": "config.yaml", "find": "old", "replace": "new", "count": -1})
  localfile(op="find", args={"pattern": "*.py"})
  localfile(op="grep", args={"pattern": "TODO", "context": 2, "include": "*.py"})
  localfile(op="ls", args={"path": "src"})
"""


async def handle_localfile(
    workdir: str,
    model_produced_args: Optional[Dict[str, Any]],
) -> str:
    if not model_produced_args:
        return HELP

    op = model_produced_args.get("op", "")
    args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
    if args_error:
        return args_error

    path = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", "")

    if not op or "help" in op:
        return HELP

    try:
        if op == "cat":
            return handle_cat(workdir, path, args, model_produced_args)
        elif op == "replace":
            return handle_replace(workdir, path, args, model_produced_args)
        elif op == "find":
            return handle_find(workdir, path, args, model_produced_args)
        elif op == "grep":
            return handle_grep(workdir, path, args, model_produced_args)
        elif op == "ls":
            return handle_ls(workdir, path)
        else:
            return "Error: need a valid `op` parameter.\n" + HELP
    except Exception as e:
        logger.error(f"Operation {op} failed: {e}", exc_info=True)
        return f"Error: {e}"


def handle_cat(workdir: str, path: str, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
    if not path:
        return "Error: path parameter required for cat operation"

    realpath, error = _validate_file_for_reading(workdir, path)
    if error:
        return f"Error: {error}"

    with open(realpath, 'rb') as f:
        content = f.read().decode('utf-8', errors='replace')
    lines_range = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "lines_range", "0:")
    safety_valve = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "safety_valve", DEFAULT_SAFETY_VALVE)
    return format_text_output(path, content, lines_range, str(safety_valve))


def handle_find(workdir: str, path: str, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
    path = path or "."

    path_error = validate_path(path, allow_empty=True)
    if path_error:
        return f"Error: {path_error}"

    realpath = os.path.join(workdir, path)
    if not os.path.exists(realpath):
        return f"Error: Path {path} does not exist"

    pattern = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "pattern", "")
    if not pattern:
        return "Error: pattern parameter required for find operation"

    found_files = [os.path.relpath(f, workdir) for f in _glob_files(realpath, pattern, recursive=True)]
    return "\n".join(found_files) if found_files else f"No files found matching '{pattern}'"


def handle_grep(workdir: str, path: str, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
    if not path:
        path = "."
    path_error = validate_path(path, allow_empty=True)
    if path_error:
        return f"Error: {path_error}"
    realpath = os.path.join(workdir, path)
    if not os.path.exists(realpath):
        return f"Error: Path {path} does not exist"
    pattern = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "pattern", "")
    if not pattern:
        return "Error: pattern parameter required for grep operation"
    try:
        pattern = re.compile(pattern)
    except re.error:
        return "Error: invalid regex pattern"
    recursive = _parse_bool(
        ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "recursive", "true"),
        default=True
    )
    include = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "include", "*")
    context = int(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "context", "0"))
    files_to_search = _glob_files(realpath, include, recursive)
    if not files_to_search:
        return f"No files found in {path}"

    results = []
    files_with_matches = 0
    for filepath in files_to_search:
        with open(filepath, "r") as f:
            content = f.read()
        result = grep_output(os.path.relpath(filepath, workdir), content, pattern, context)
        if result:
            files_with_matches += 1
            results.append(result)
    if not results:
        return f"No matches found for pattern in {len(files_to_search)} files"

    summary = f"Found pattern in {files_with_matches}/{len(files_to_search)} files:"
    return summary + "\n" + "\n".join(results)


def handle_replace(workdir: str, path: str, args: Dict[str, Any], model_produced_args: Dict[str, Any]) -> str:
    if not path:
        return "Error: path parameter required for replace operation"

    realpath, error = _validate_file_for_reading(workdir, path)
    if error:
        return f"Error: {error}"

    find_text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "find", "")
    replace_text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "replace", "")
    count = int(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "count", "-1"))

    if not find_text:
        return "Error: find parameter required for replace operation"

    with open(realpath, 'r', encoding='utf-8') as f:
        content = f.read()

    if count == -1:
        new_content = content.replace(find_text, replace_text)
        replacements = content.count(find_text)
    else:
        new_content = content.replace(find_text, replace_text, count)
        replacements = min(content.count(find_text), count)

    if replacements == 0:
        return f"No matches found for '{find_text}' in {path}"

    with open(realpath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    old_lines = content.splitlines()
    new_lines = new_content.splitlines()

    diff_output = [f"Updated {path} ({replacements} replacement{'s' if replacements > 1 else ''}):\n"]

    for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines), 1):
        if old_line != new_line:
            diff_output.append(f"  {i:4d} - {old_line}")
            diff_output.append(f"  {i:4d} + {new_line}")

    if len(new_lines) > len(old_lines):
        for i in range(len(old_lines), len(new_lines)):
            diff_output.append(f"  {i+1:4d} + {new_lines[i]}")
    elif len(old_lines) > len(new_lines):
        for i in range(len(new_lines), len(old_lines)):
            diff_output.append(f"  {i+1:4d} - {old_lines[i]}")

    return "\n".join(diff_output)


def handle_ls(workdir: str, path: str) -> str:
    path = path or "."

    path_error = validate_path(path, allow_empty=True)
    if path_error:
        return f"Error: {path_error}"

    realpath = os.path.join(workdir, path)
    if not os.path.exists(realpath):
        return f"Error: Path {path} does not exist"
    if not os.path.isdir(realpath):
        return f"Error: {path} is not a directory"

    try:
        entries = []
        for item in sorted(os.listdir(realpath)):
            full_path = os.path.join(realpath, item)
            is_dir = os.path.isdir(full_path)

            if not is_dir and _validate_file_security(full_path):
                continue

            suffix = "/" if is_dir else ""
            rel_path = os.path.join(path, item) if path != "." else item
            entries.append(f"{rel_path}{suffix}")

        return "\n".join(entries) if entries else f"No entries found in {path}"
    except Exception as e:
        return f"Error listing directory: {e}"
