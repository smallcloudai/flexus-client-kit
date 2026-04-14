import json
import os
import logging
import re
import urllib.parse
from typing import Dict, Any, Optional
from flexus_client_kit.integrations.fi_localfile import _validate_file_security

from flexus_client_kit import ckit_cloudtool, ckit_mongo
from flexus_client_kit.format_utils import DEFAULT_SAFETY_VALVE, format_cat_output, grep_output

logger = logging.getLogger("mongo_store")

MONGO_STORE_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="mongo_store",
    description="Store and retrieve files in MongoDB, call with op=help for usage",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "enum": ["help", "list", "ls", "cat", "grep", "delete", "upload", "save", "render_download_link"],
                "description": "Operation: list/ls (list files), cat (read file), grep (search), delete, upload (from disk), save (content directly), render_download_link (show download card to user)",
            },
            "args": {
                "type": "object",
                "additionalProperties": False,
                "description": "All arguments required, set to null if not used for this operation",
                "properties": {
                    "path": {"type": ["string", "null"], "description": "File path or prefix for list"},
                    "lines_range": {"type": ["string", "null"], "description": "Line range for cat: '1:20', ':20', '21:'"},
                    "safety_valve": {"type": ["string", "null"], "description": "Max output size for cat, e.g. '10k'"},
                    "pattern": {"type": ["string", "null"], "description": "Python regex pattern for grep"},
                    "context": {"type": ["integer", "null"], "description": "Context lines around grep matches"},
                    "content": {"type": ["string", "null"], "description": "Content for save op (JSON string or text)"},
                },
                "required": ["path", "lines_range", "safety_valve", "pattern", "context", "content"],
            },
        },
        "required": ["op", "args"],
        "additionalProperties": False,
    },
)

# upload  - Upload a local file into MongoDB storage.
#           args: path (required)
#   mongo_store(op="upload", args={"path": "folder1/something_20250803.json"})


HELP = """
list    - List stored files filtered by optional prefix.
          args: path (optional, default "")

cat     - Read file contents
          args: path (required), optional lines_range ("1:20", ":20", "21:"), optional safety_valve (defaults to "10k")

save    - Save content directly to MongoDB (no local file needed).
          args: path (required), content (required, JSON string or text)

delete  - Delete a stored file by exact path (no wildcards).
          args: path (required)

grep    - Search file contents using Python regex using per-line matching
          args: path (default "."), pattern (required), context (0)
          Sometimes you need to grep .json files on disk, remember that all the strings inside are escaped in that case, making
          it a bit harder to match.

render_download_link  - Show a download card to the user for an already-stored file.
          The user sees a styled card with file icon, name, and download/preview button.
          args: path (required)

Examples:
  mongo_store(op="list", args={"path": "folder1/"})
  mongo_store(op="cat", args={"path": "folder1/something_20250803.json", "lines_range": "0:40", "safety_valve": "10k"})
  mongo_store(op="save", args={"path": "investigations/abc123.json", "content": "{...json...}"})
  mongo_store(op="delete", args={"path": "folder1/something_20250803.json"})
  mongo_store(op="grep", args={"path": "tasks.txt", "pattern": "TODO", "context": 2})
  mongo_store(op="render_download_link", args={"path": "reports/monthly.pdf"})
"""

# There's also a secret op="undelete" command that can bring deleted files


_MIME_TYPES = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml",
    ".pdf": "application/pdf", ".txt": "text/plain", ".csv": "text/csv",
    ".json": "application/json", ".html": "text/html", ".htm": "text/html",
    ".xml": "application/xml", ".md": "text/markdown",
    ".yaml": "application/yaml", ".yml": "application/yaml",
}


def _guess_mime_type(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return _MIME_TYPES.get(ext, "application/octet-stream")


async def handle_mongo_store(
    rcx,
    toolcall: ckit_cloudtool.FCloudtoolCall,
    model_produced_args: Optional[Dict[str, Any]],
    persona_id: Optional[str] = None,
) -> str:
    if rcx.running_test_scenario:
        from flexus_client_kit import ckit_scenario
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, open(__file__).read())
    if not model_produced_args:
        return HELP

    mongo_collection = rcx.personal_mongo
    op = model_produced_args.get("op", "")
    args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
    if args_error:
        return f"{args_error}\n\n{HELP}"

    path = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", "").lstrip("/")

    if not op or "help" in op:
        return HELP

    if op == "save":
        if not path:
            return f"Error: path parameter required for save operation\n\n{HELP}"
        content = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "content", "")
        if not content:
            return f"Error: content parameter required for save operation\n\n{HELP}"
        path_error = validate_path(path)
        if path_error:
            return f"Error: {path_error}"
        file_data = content.encode("utf-8")
        existing_doc = await mongo_collection.find_one({"path": path}, {"mon_ctime": 1})
        was_overwritten = existing_doc is not None
        await ckit_mongo.mongo_store_file(mongo_collection, path, file_data, 60 * 60 * 24 * 365)
        result_msg = f"Saved {path} -> MongoDB ({len(file_data)} bytes)"
        if was_overwritten:
            result_msg += " [OVERWRITTEN]"
        return result_msg

    elif op == "upload":
        if not path:
            return f"Error: path parameter required for upload operation\n\n{HELP}"
        realpath = os.path.join(rcx.workdir, path)
        if not os.path.exists(realpath):
            return f"Error: File {path} does not exist"
        with open(realpath, 'rb') as f:
            file_data = f.read()
        path_error = validate_path(path)
        if path_error:
            return f"Error: {path_error}"
        mongo_path = path
        existing_doc = await mongo_collection.find_one({"path": mongo_path}, {"mon_ctime": 1})
        was_overwritten = existing_doc is not None
        result_id = await ckit_mongo.mongo_store_file(mongo_collection, mongo_path, file_data, 60 * 60 * 24 * 365)
        result_msg = f"Uploaded {path} -> MongoDB"
        if was_overwritten:
            result_msg += " [OVERWRITTEN existing file]"
        return result_msg

    elif op in ["list", "ls"]:
        if not path:
            path = ""
        elif path == "/":
            path = ""
        path_error = validate_path(path, allow_empty=True)
        if path_error:
            return f"Error: {path_error}"
        documents = await ckit_mongo.mongo_ls(mongo_collection, path)
        if not documents:
            return f"No files found with prefix: {path!r}"
        result = f"Found {len(documents)} files with prefix {path!r}:\n"
        for doc in documents:
            file_path = doc["path"]
            size = doc["mon_size"]
            result += f"  {file_path} (size: {size})\n"
        return result

    elif op == "cat":
        if not path:
            return f"Error: path parameter required for cat operation\n\n{HELP}"
        path_error = validate_path(path)
        if path_error:
            return f"Error: {path_error}"
        security_error = _validate_file_security(path)
        if security_error:
            return security_error
        document = await ckit_mongo.mongo_retrieve_file(mongo_collection, path)
        if not document:
            return f"Error: File {path} not found in MongoDB"
        # XXX decide is it json, image or text, remove guesswork
        file_data = document.get("data", document.get("json", None))
        lines_range = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "lines_range", "0:")
        safety_valve = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "safety_valve", DEFAULT_SAFETY_VALVE)
        return format_cat_output(path, file_data, lines_range, str(safety_valve))

    elif op == "grep":
        if not path:
            path = "."
        path_error = validate_path(path, allow_empty=True)
        if path_error:
            return f"Error: {path_error}"
        pattern = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "pattern", "")
        if not pattern:
            return "Error: pattern parameter required for grep operation"
        try:
            pattern = re.compile(pattern)
        except re.error:
            return "Error: invalid regex pattern"
        context = int(ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "context", "0"))

        document = await ckit_mongo.mongo_retrieve_file(mongo_collection, path)
        if not document:
            return f"Error: File {path} not found in MongoDB"
        if document.get("data"):
            content = document["data"].decode("utf-8")
        elif document.get("json"):
            content = json.dumps(document["json"], indent=2)

        result = grep_output(path, content, pattern, context)
        if not result:
            return f"No matches found for pattern in file"
        return result

    elif op == "delete":
        if not path:
            return f"Error: path parameter required for delete operation\n\n{HELP}"
        path_error = validate_path(path)
        if path_error:
            return f"Error: {path_error}"
        was_deleted = await ckit_mongo.mongo_rm(mongo_collection, path)
        if was_deleted:
            return f"Deleted {path} from MongoDB"
        else:
            return f"Error: File {path} not found in MongoDB"

    elif op == "render_download_link":
        if not path:
            return f"Error: path parameter required for `render_download_link` operation\n\n{HELP}"
        if not persona_id:
            return "Error: `render_download_link` operation requires persona_id (pass it to handle_mongo_store)"
        path_error = validate_path(path)
        if path_error:
            return f"Error: {path_error}"
        display_name = os.path.basename(path)
        mime = _guess_mime_type(path)
        enc_path = urllib.parse.quote(path, safe="/")
        enc_name = urllib.parse.quote(display_name, safe="")
        return f"📎DOWNLOAD:{persona_id}:{enc_path}:{enc_name}:{mime}"

    else:
        return HELP


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


async def download_file(mongo_collection, path, local_path):
    path = path.lstrip("/") if path else path
    if not path:
        raise RuntimeError(f"Error: path parameter required for download operation\n\n{HELP}")
    path_error = validate_path(path)
    if path_error:
        raise RuntimeError(f"Error: {path_error}")
    document = await ckit_mongo.mongo_retrieve_file(mongo_collection, path)
    if not document:
        raise RuntimeError(f"Error: File {path} not found in MongoDB")
    resolved_path = os.path.abspath(local_path)
    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
    resolved_path = os.path.abspath(local_path)
    if "data" in document:
        with open(resolved_path, 'wb') as f:
            f.write(document["data"])
    elif "json" in document:
        with open(resolved_path, 'w') as f:
            json.dump(document["json"], f, indent=2)
    else:
        raise RuntimeError("Error: File {path} has unknown format, cannot save it")
    return path
