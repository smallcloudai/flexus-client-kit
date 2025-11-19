import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import gql

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_scenario
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import gql_utils


logger = logging.getLogger("pdocs")


POLICY_DOCUMENT_TOOL = ckit_cloudtool.CloudTool(
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

flexus_policy_document(op="update_json_text", args={"p": "/folder/file", "json_path": "section1.field", "text": "new value"})
    Update a specific field in a document using json_path with dot notation.
    Example: "operations_overview.governance" updates doc["operations_overview"]["governance"]

flexus_policy_document(op="cp", args={"p1": "/customer-research/interview-template", "p2": "/customer-research/interview-monsieur-dupont"})
    Copy a policy document.

flexus_policy_document(op="rm", args={"p": "/customer-research/interview-monsieur-dupont"})
    Archive (soft delete) a policy document.

Typical paths:
/company           -- heavily summarized version of all the other documents
/testing-this-week -- business adjustments, summarized changes for this week
/testing-today     -- the same, for today
/jtbd-this-week    -- what is planned for this week
/jtbd-today        -- for today
/customer-research/interview-template
/customer-research/interview-john-doe
/historic-week-20251020/company

You are working within a UI that lets the user to edit any policy documents mentioned, bypassing your
function calls, kind of like IDE lets the user to change the source files.
The UI reacts to tool results that have a line "✍🏻/path/to/document" to give user a link to that document to
view or edit. Some rules for sitting within this UI:
- Never dump json onto the user, the user is unlikely to be a software engineer, and they see a user-friendly version of the content anyway in the UI.
- Don't mention document paths, for the same reason, read the files instead and write a table with available ideas or hypothesis, using human readable text.
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


class IntegrationPdoc:
    def __init__(
        self,
        rcx: ckit_bot_exec.RobotContext,
        ws_root_group_id: str,
    ):
        self.rcx = rcx
        self.fclient = rcx.fclient
        self.fgroup_id = ws_root_group_id
        self.problems = []
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

        r = ""

        try:
            if op == "list":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "/")
                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
                result = await self.pdoc_list(p)
                r += f"Listing {p}\n\n"
                for item in result:
                    if item.is_folder:
                        r += f"  {item.path}/ ({item.doc_count} documents)\n"
                    else:
                        r += f"  {item.path}\n"
                doc_count = sum(1 for item in result if not item.is_folder)
                folder_count = sum(1 for item in result if item.is_folder)
                r += f"\n{doc_count} documents and {folder_count} folders\n"

            elif op == "cat" or op == "activate":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                if not p:
                    return f"Error: p required\n\n{HELP}"
                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
                result = await self.pdoc_cat(p)
                if op == "activate":
                    r += f"✍🏻 {result.path}\n\n"
                else:
                    r += f"📄 {result.path}\n\n"
                r += json.dumps(result.pdoc_content, indent=2, ensure_ascii=False)

            elif op == "overwrite" or op == "create":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", "")
                if not p:
                    return f"Error: p required\n\n{HELP}"
                if not text:
                    return f"Error: text parameter required\n\n{HELP}"

                try:
                    json.loads(text)
                except json.JSONDecodeError as e:
                    return f"Error: text must be valid JSON: {str(e)}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                if op == "create":
                    await self.pdoc_create(p, text, toolcall.fcall_ft_id)
                    r += f"✍🏻 {p}\n\n✓ Policy document created"
                else:
                    await self.pdoc_overwrite(p, text, toolcall.fcall_ft_id)
                    r += f"✍🏻 {p}\n\n✓ Policy document updated"

            elif op == "update_json_text":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                json_path = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "json_path", "")
                text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", "")
                if not p or not json_path or not text:
                    return f"Error: p, json_path, and text parameters required\n\n{HELP}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                await self.pdoc_update_json_text(p, json_path, text, toolcall.fcall_ft_id)
                r += f"✍🏻 {p}\n\n✓ Updated {json_path}"

            elif op == "cp":
                p1 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p1", "")
                p2 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p2", "")
                if not p1 or not p2:
                    return f"Error: p1 and p2 parameters required\n\n{HELP}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                await self.pdoc_cp(p1, p2, toolcall.fcall_ft_id)
                r += f"✍🏻 {p2}\n\n✓ Copied from {p1}"

            elif op == "rm":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                if not p:
                    return f"Error: p required\n\n{HELP}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                await self.pdoc_rm(p, toolcall.fcall_ft_id)
                r += f"✓ Archived policy document: {p}"

            else:
                r += f"Unknown op {op!r}\n\n{HELP}"

        except gql.transport.exceptions.TransportQueryError as e:
            logger.info(f"Error in pdoc operation", exc_info=True)
            return f"Error: {str(e)}"

        return r

    async def pdoc_list(self, p: str = "/") -> List[PdocListItem]:
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                gql.gql(f"""
                    query PdocList($fgroup_id: String!, $p: String!) {{
                        policydoc_list(fgroup_id: $fgroup_id, p: $p) {{
                            {gql_utils.gql_fields(PdocListItem)}
                        }}
                    }}
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p},
            )
            items = result.get("policydoc_list", [])
            return [gql_utils.dataclass_from_dict(item, PdocListItem) for item in items]

    async def pdoc_cat(self, p: str) -> PdocDocument:
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                gql.gql(f"""
                    query PdocCat($fgroup_id: String!, $p: String!) {{
                        policydoc_cat(fgroup_id: $fgroup_id, p: $p) {{
                            {gql_utils.gql_fields(PdocDocument)}
                        }}
                    }}
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p},
            )
            doc = result.get("policydoc_cat")
            if not doc:
                raise Exception(f"Policy document not found: {p}")
            return gql_utils.dataclass_from_dict(doc, PdocDocument)

    async def pdoc_create(self, p: str, text: str, ft_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocCreate($fgroup_id: String!, $p: String!, $text: String!, $ft_id: String) {
                        policydoc_create(fgroup_id: $fgroup_id, p: $p, text: $text, ft_id: $ft_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "text": text, "ft_id": ft_id},
            )

    async def pdoc_overwrite(self, p: str, text: str, ft_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocOverwrite($fgroup_id: String!, $p: String!, $text: String!, $ft_id: String) {
                        policydoc_overwrite(fgroup_id: $fgroup_id, p: $p, text: $text, ft_id: $ft_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "text": text, "ft_id": ft_id},
            )

    async def pdoc_update_json_text(self, p: str, json_path: str, text: str, ft_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocUpdateJsonText($fgroup_id: String!, $p: String!, $json_path: String!, $text: String!, $ft_id: String) {
                        policydoc_update_json_text(fgroup_id: $fgroup_id, p: $p, json_path: $json_path, text: $text, ft_id: $ft_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "json_path": json_path, "text": text, "ft_id": ft_id},
            )

    async def pdoc_cp(self, p1: str, p2: str, ft_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocCp($fgroup_id: String!, $p1: String!, $p2: String!, $ft_id: String) {
                        policydoc_cp(fgroup_id: $fgroup_id, p1: $p1, p2: $p2, ft_id: $ft_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p1": p1, "p2": p2, "ft_id": ft_id},
            )

    async def pdoc_rm(self, p: str, ft_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocRm($fgroup_id: String!, $p: String!, $ft_id: String) {
                        policydoc_rm(fgroup_id: $fgroup_id, p: $p, ft_id: $ft_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "ft_id": ft_id},
            )
