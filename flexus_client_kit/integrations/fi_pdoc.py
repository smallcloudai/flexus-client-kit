import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import gql
import jsonschema

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_scenario
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import gql_utils


logger = logging.getLogger("pdocs")


POLICY_DOCUMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="flexus_policy_document",
    description="List, read, update Policy Documents. Start with op=\"help\".",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string"},
            "args": {"type": "object"},
        },
    },
)


HELP = """
flexus_policy_document()
    Shows this help.

flexus_policy_document(op="list")
flexus_policy_document(op="list", args={"p": "/customer-research/"})
    List documents and subfolders.
    Shows direct children only, documents and subfolders with document counts.

flexus_policy_document(op="cat", args={"p": "/folder/file"})
flexus_policy_document(op="activate", args={"p": "/folder/file"})
    Read a policy document. If it's "activate" the document will also appear for the user in the UI. Use "cat" to
    understand the current situation, use "activate" when starting to work on a document.

flexus_policy_document(op="create", args={"p": "/folder/file", "text": '{"structured": "doc"}'})
flexus_policy_document(op="overwrite", args={"p": "/folder/file", "text": '{"structured": "doc"}'})
    Write a new policy document. Normally use "create" variant that returns error if document already exists.
    Only use "overwrite" when you mean it.

flexus_policy_document(op="create_with_schema", args={"p": "/folder/file", "data": {"structured": "doc"}, "schema": {"type":"object","additionalProperties":false,"properties":{"structured":{"type":"string"}},"required":["structured"]}})
flexus_policy_document(op="overwrite_with_schema", args={"p": "/folder/file", "data": {"structured": "doc"}, "schema": {"type":"object","additionalProperties":false,"properties":{"structured":{"type":"string"}},"required":["structured"]}})
    Validate data against JSON schema, then write resulting JSON text.

flexus_policy_document(op="update_json_text", args={"p": "/folder/file", "json_path": "section1.field", "text": "new value"})
    Update a specific field in a document using json_path with dot notation.
    Example: "operations_overview.governance" updates doc["operations_overview"]["governance"]

flexus_policy_document(op="cp", args={"p1": "/customer-research/interview-template", "p2": "/customer-research/interview-monsieur-dupont"})
    Copy a policy document.

flexus_policy_document(op="rm", args={"p": "/customer-research/interview-monsieur-dupont"})
    Archive (soft delete) a policy document.

Typical paths:
/company/summary                                     -- A very compressed version of what the company is
/company/style-guide                                 -- brand colors, fonts
/gtm/discovery/{idea-slug}/idea                      -- bots save results and interact via documents

You are working within a UI that lets the user to edit any policy documents mentioned, bypassing your
function calls, kind of like IDE lets the user to change the source files.
The UI reacts to tool results that have a line "✍️ /path/to/document" to give user a link to that document to
view or edit. Some rules for operating within this UI:
- Never dump json onto the user, the user is unlikely to be a software engineer, and they see a user-friendly version of the content anyway in the UI.
- Don't mention document paths, for the same reason, read the files instead, and write a table or text with things from documents, using human readable non-technical text.
- If the user manually edits any documents - read them again to track changes, they might be crucial.
"""


@dataclass
class PdocListItem:
    path: str
    is_folder: bool
    doc_count: int


@dataclass
class PdocDocument:
    pdoc_id: str
    path: str
    pdoc_content: Any
    pdoc_created_ts: float
    pdoc_modified_ts: float


def _format_tree(items: List[PdocListItem], base_path: str) -> tuple:
    if not items:
        return "", 0, 0
    base = base_path.rstrip("/")

    # Build tree structure: {path_tuple: (name, is_folder, doc_count)}
    tree: dict = {}
    for item in items:
        rel = item.path[len(base):].lstrip("/") if item.path.startswith(base) else item.path.lstrip("/")
        parts = tuple(rel.split("/"))
        # Add intermediate folders
        for i in range(1, len(parts)):
            folder_parts = parts[:i]
            if folder_parts not in tree:
                tree[folder_parts] = (folder_parts[-1] + "/", True, 0)
        # Add the item itself
        name = parts[-1] + ("/" if item.is_folder else "")
        if item.is_folder and item.doc_count:
            name += f" ({item.doc_count})"
        tree[parts] = (name, item.is_folder, item.doc_count)

    sorted_paths = sorted(tree.keys())
    doc_count = sum(1 for _, (_, is_folder, _) in tree.items() if not is_folder)
    folder_count = sum(1 for _, (_, is_folder, _) in tree.items() if is_folder)

    def get_children(parent):
        plen = len(parent)
        return [p for p in sorted_paths if len(p) == plen + 1 and p[:plen] == parent]

    def render(parent, prefix=""):
        children = get_children(parent)
        lines = []
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            name, is_folder, _ = tree[child]
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + name)
            if is_folder:
                ext = "    " if is_last else "│   "
                lines.extend(render(child, prefix + ext))
        return lines

    return "\n".join(render(())) + "\n", doc_count, folder_count


class IntegrationPdoc:
    def __init__(
        self,
        rcx: ckit_bot_exec.RobotContext,
        ws_root_group_id: str,
    ):
        assert ws_root_group_id
        self.rcx = rcx
        self.fclient = rcx.fclient
        self.fgroup_id = ws_root_group_id
        self.is_fake = rcx.running_test_scenario

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Optional[Dict[str, Any]]) -> str:
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "help")
        args, args_error = ckit_cloudtool.sanitize_args(model_produced_args)
        if args_error:
            return args_error

        if op == "help":
            return HELP

        fuser_id = ckit_external_auth.get_fuser_id_from_rcx(self.rcx, toolcall.fcall_ft_id)
        r = ""

        try:
            if op == "list":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "/")
                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
                result = await self.pdoc_list(p, fuser_id, depth=5)
                tree_text, doc_count, folder_count = _format_tree(result, p)
                r += f"Listing {p}\n\n"
                r += tree_text
                r += f"\n{doc_count} documents and {folder_count} folders\n"

            elif op == "cat" or op == "read" or op == "activate":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                p = p or ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", "")
                if not p:
                    return f"Error: p required\n\n{HELP}"
                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
                result = await self.pdoc_cat(p, fuser_id)
                if not result:
                    return f"Policy document not found: {p}"
                if op == "activate":
                    r += f"✍️ {result.path}\n\n"
                else:
                    r += f"📄 {result.path}\n\n"
                r += json.dumps(result.pdoc_content, indent=2, ensure_ascii=False)

            elif op == "overwrite" or op == "create":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                p = p or ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", "")

                text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", "")
                if not p:
                    return f"Error: p required\n\n{HELP}"
                if not text:
                    return f"Error: text parameter required\n\n{HELP}"

                try:
                    # XXX from flexus_backend.flexus_v1 import official_json_validator
                    json.loads(text)
                except json.JSONDecodeError as e:
                    return f"Error: text must be valid JSON: {str(e)}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                if op == "create":
                    await self.pdoc_create(p, text, fuser_id)
                    r += f"✍️ {p}\n\n✓ Policy document created"
                else:
                    await self.pdoc_overwrite(p, text, fuser_id)
                    r += f"✍️ {p}\n\n✓ Policy document updated"

            elif op == "create_with_schema" or op == "overwrite_with_schema":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                p = p or ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", "")
                data = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "data", None)
                schema = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "schema", None)
                if not p:
                    return f"Error: p required\n\n{HELP}"
                if data is None or schema is None:
                    return f"Error: data and schema parameters required\n\n{HELP}"
                if not isinstance(schema, dict):
                    return "Error: schema must be a JSON object"
                try:
                    jsonschema.validate(data, schema)
                except jsonschema.ValidationError as e:
                    return f"Error: data does not match schema: {e.message}"
                text = json.dumps(data, ensure_ascii=False)
                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
                if op == "create_with_schema":
                    await self.pdoc_create(p, text, fuser_id)
                    r += f"✍️ {p}\n\n✓ Policy document created (validated by schema)"
                else:
                    await self.pdoc_overwrite(p, text, fuser_id)
                    r += f"✍️ {p}\n\n✓ Policy document updated (validated by schema)"

            elif op == "update_json_text":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                p = p or ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", "")

                json_path = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "json_path", "")
                text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", "")
                if not p or not json_path or not text:
                    return f"Error: p, json_path, and text parameters required\n\n{HELP}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                await self.pdoc_update_json_text(p, json_path, text, fuser_id)
                r += f"✍️ {p}\n\n✓ Updated {json_path}"

            elif op == "cp":
                p1 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p1", "")
                p2 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p2", "")
                if not p1 or not p2:
                    return f"Error: p1 and p2 parameters required\n\n{HELP}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                await self.pdoc_cp(p1, p2, fuser_id)
                r += f"✍️ {p2}\n\n✓ Copied from {p1}"

            elif op == "rm":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                p = p or ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", "")

                if not p:
                    return f"Error: p required\n\n{HELP}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                await self.pdoc_rm(p, fuser_id)
                r += f"🗑 {p}\n\n"

            else:
                r += f"Unknown op {op!r}\n\n{HELP}"

        except gql.transport.exceptions.TransportQueryError as e:
            # UGLY: this is a exception-as-flow-control anti-pattern but one of the exceptions is actually helpful:
            # "400: Document already exists" -- model will recover by changing name or switching to overwrite (and returning bool instead is even more ugly)
            if "already exists" in str(e):
                logger.info(f"Error in pdoc operation: %s", str(e))
            else:
                logger.error(f"Error in pdoc operation: %s", exc_info=e)
            return f"Error: {str(e)}"

        return r

    async def pdoc_list(self, p: str = "/", fuser_id: str = None, depth: int = 1) -> List[PdocListItem]:
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                gql.gql(f"""
                    query PdocList($fgroup_id: String!, $p: String!, $fuser_id: String, $depth: Int) {{
                        policydoc_list(fgroup_id: $fgroup_id, p: $p, fuser_id: $fuser_id, depth: $depth) {{
                            {gql_utils.gql_fields(PdocListItem)}
                        }}
                    }}
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "fuser_id": fuser_id, "depth": depth},
            )
            items = result.get("policydoc_list", [])
            return [gql_utils.dataclass_from_dict(item, PdocListItem) for item in items]

    async def pdoc_cat(self, p: str, fuser_id: str = None, best_effort_to_find: bool = False) -> Optional[PdocDocument]:
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                gql.gql(f"""
                    query PdocCat($fgroup_id: String!, $p: String!, $fuser_id: String, $best_effort_to_find: Boolean) {{
                        policydoc_cat(fgroup_id: $fgroup_id, p: $p, fuser_id: $fuser_id, best_effort_to_find: $best_effort_to_find) {{
                            {gql_utils.gql_fields(PdocDocument)}
                        }}
                    }}
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "fuser_id": fuser_id, "best_effort_to_find": best_effort_to_find},
            )
            doc = result.get("policydoc_cat")
            if not doc:
                return None
            return gql_utils.dataclass_from_dict(doc, PdocDocument)

    async def pdoc_create(self, p: str, text: str, fuser_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocCreate($fgroup_id: String!, $p: String!, $text: String!, $fuser_id: String) {
                        policydoc_create(fgroup_id: $fgroup_id, p: $p, text: $text, fuser_id: $fuser_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "text": text, "fuser_id": fuser_id},
            )

    async def pdoc_overwrite(self, p: str, text: str, fuser_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocOverwrite($fgroup_id: String!, $p: String!, $text: String!, $fuser_id: String) {
                        policydoc_overwrite(fgroup_id: $fgroup_id, p: $p, text: $text, fuser_id: $fuser_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "text": text, "fuser_id": fuser_id},
            )

    async def pdoc_update_json_text(self, p: str, json_path: str, text: str, fuser_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocUpdateJsonText($fgroup_id: String!, $p: String!, $json_path: String!, $text: String!, $fuser_id: String) {
                        policydoc_update_json_text(fgroup_id: $fgroup_id, p: $p, json_path: $json_path, text: $text, fuser_id: $fuser_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "json_path": json_path, "text": text, "fuser_id": fuser_id},
            )

    async def pdoc_cp(self, p1: str, p2: str, fuser_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocCp($fgroup_id: String!, $p1: String!, $p2: String!, $fuser_id: String) {
                        policydoc_cp(fgroup_id: $fgroup_id, p1: $p1, p2: $p2, fuser_id: $fuser_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p1": p1, "p2": p2, "fuser_id": fuser_id},
            )

    async def pdoc_rm(self, p: str, fuser_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocRm($fgroup_id: String!, $p: String!, $fuser_id: String) {
                        policydoc_rm(fgroup_id: $fgroup_id, p: $p, fuser_id: $fuser_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "fuser_id": fuser_id},
            )
