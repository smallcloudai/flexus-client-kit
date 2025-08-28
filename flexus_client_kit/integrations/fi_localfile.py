import json
import os
import logging
import re
from typing import Dict, Any, Optional

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("localfile")


LOCALFILE_TOOL = ckit_cloudtool.CloudTool(
    name="localfile",
    description="Read local files, call with op=\"help\" for usage",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "description": "Start with 'help' for usage"},
            "args": {"type": "object"},
        },
    },
)
# https://www.rgbdigital.com.au/picture/Picture.jpg
HELP = """
Help:

localfile(op="cat", args={"path": "folder1/something.json", "lines_range": "13:37", "safety_valve": "10k"})
    Open the local file and print what's inside. The lines_range and safety_valve are there to
    prevent large files from clogging your context window. A good strategy is to call
    cat without lines_range/safety_valve, you'll get default range "1:" and safety_valve of 10k chars.
    Most files will fit that, and in case your file doesn't this tool will provide all the
    line numbers for the next call.
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

    if op == "cat":
        if not path:
            return "Error: path parameter required for cat operation"

        path_error = validate_path(path)
        if path_error:
            return f"Error: {path_error}"

        realpath = os.path.join(workdir, path)
        if not os.path.exists(realpath):
            return f"Error: File {path} does not exist"
        with open(realpath, 'rb') as f:
            file_data = f.read()

        try:
            line_range = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "lines_range", "1:")
            safety_valve = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "safety_valve", "10k")
            pattern = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "pattern", "")
            return format_cat_output(path, file_data, line_range, safety_valve, pattern)

        except Exception as e:
            logger.error(f"Cat failed: {e}", exc_info=True)
            return f"Error reading file: {e}"

    else:
        return "Error: need a valid `op` parameter.\n" + HELP


def format_cat_output(
    path: str,
    file_data: bytes | str | list | dict,  # XXX bad idea, pick one type
    line_range: str,
    safety_valve: str,
    pattern: str = "",
    truncate_lines: bool = False,
) -> str:
    if safety_valve.lower().endswith('k'):
        safety_valve_int = int(safety_valve[:-1]) * 1024
    else:
        safety_valve_int = 10240

    if isinstance(file_data, bytes) and b'\x00' in file_data:
        return "%s exists, it's a binary file, cannot be printed as text, has %d bytes" % (path, len(file_data))

    if isinstance(file_data, bytes):
        content = file_data.decode('utf-8', errors='replace')
        lines = content.splitlines()
    elif isinstance(file_data, list):
        lines = [json.dumps(item) for item in file_data]
    elif isinstance(file_data, dict):
        content = json.dumps(file_data, indent=2)
        lines = content.splitlines()
    else:
        lines = file_data.splitlines()

    if ":" in line_range:
        start_str, end_str = line_range.split(":", 1)
        start = int(start_str) if start_str else 1
        end = int(end_str) if end_str else len(lines)
    else:
        start = end = int(line_range)

    start = max(1, start) - 1
    end = min(len(lines), end)

    compiled_pattern = None
    if pattern:
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            return f"Error: Invalid regex pattern '{pattern}': {e}"
    
    total_chars = 0

    header1 = "File: %s (total %d lines, %d bytes)" % (path, len(lines), len(file_data))

    result = []
    for i in range(start, end):
        line = lines[i]
        if compiled_pattern and not compiled_pattern.search(line):
            continue
        if truncate_lines and safety_valve_int - total_chars < len(line):
            truncate_idx = max(0, safety_valve_int - total_chars)
            line = line[:truncate_idx] + "..."
        if compiled_pattern:
            result.append(f"{i+1:4d}: {line}")
        else:
            result.append(line)
        total_chars += len(line) + 1
        if total_chars + len(line) > safety_valve_int:
            header2 = "Showing lines %d:%d, because safety_valve limit was hit\n" % (start+1, i+1)
            break
    else:
        header2 = "Showing all lines\n"

    return "\n".join([header1, header2, *result])


def validate_path(path: str, allow_empty: bool = False) -> Optional[str]:
    if not path:
        if allow_empty:
            return None
        return "Path cannot be empty"
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