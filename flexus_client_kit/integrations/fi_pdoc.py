import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import gql

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
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

flexus_policy_document(op="cat", args={"p": "/company"})
    Read a policy document.

flexus_policy_document(op="write", args={"p": "/company", "text": '{"section1": "value1"}'})
    Write or update a policy document with structured JSON content.

flexus_policy_document(op="update_json_text", args={"p": "/company", "json_path": "section1.field", "text": "new value"})
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

The native Flexus UI (not messanger integrations) supports editing policy documents, the UI reacts
to tool results that have a line "✍🏻/path/to/document" to give user a link to that document to
view or edit.
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
        fclient: ckit_client.FlexusClient,
        ws_root_group_id: str,
    ):
        self.fclient = fclient
        self.fgroup_id = ws_root_group_id
        self.problems = []

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

            elif op == "cat":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                if not p:
                    return f"Error: p required\n\n{HELP}"
                result = await self.pdoc_cat(p)
                r += f"📄 {result.path}\n\n"
                r += json.dumps(result.pdoc_content, indent=2)

            elif op == "write":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", "")
                if not p:
                    return f"Error: p required\n\n{HELP}"
                if not text:
                    return f"Error: text parameter required\n\n{HELP}"

                # Validate JSON
                try:
                    json.loads(text)
                except json.JSONDecodeError as e:
                    return f"Error: text must be valid JSON: {str(e)}"

                await self.pdoc_write(p, text, toolcall.fcall_ft_id)
                r += f"✍🏻 {p}\n\n✓ Policy document updated"

            elif op == "update_json_text":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                json_path = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "json_path", "")
                text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", "")
                if not p or not json_path or not text:
                    return f"Error: p, json_path, and text parameters required\n\n{HELP}"

                await self.pdoc_update_json_text(p, json_path, text, toolcall.fcall_ft_id)
                r += f"✍🏻 {p}\n\n✓ Updated {json_path}"

            elif op == "cp":
                p1 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p1", "")
                p2 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p2", "")
                if not p1 or not p2:
                    return f"Error: p1 and p2 parameters required\n\n{HELP}"

                await self.pdoc_cp(p1, p2, toolcall.fcall_ft_id)
                r += f"✍🏻 {p2}\n\n✓ Copied from {p1}"

            elif op == "rm":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                if not p:
                    return f"Error: p required\n\n{HELP}"

                await self.pdoc_rm(p, toolcall.fcall_ft_id)
                r += f"✓ Archived policy document: {p}"

            else:
                r += f"Unknown op {op!r}\n\n{HELP}"

        except Exception as e:
            logger.exception("Exception in pdoc operation")
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

    # XXX add pdoc_rewrite

    async def pdoc_write(self, p: str, text: str, ft_id: str) -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocWrite($fgroup_id: String!, $p: String!, $text: String!, $ft_id: String) {
                        policydoc_write(fgroup_id: $fgroup_id, p: $p, text: $text, ft_id: $ft_id)
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
