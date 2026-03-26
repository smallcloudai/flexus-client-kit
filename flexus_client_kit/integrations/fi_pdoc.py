import datetime
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from zoneinfo import ZoneInfo

import gql

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_scenario
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import gql_utils


logger = logging.getLogger("pdocs")


POLICY_DOCUMENT_PROMPT = """
## Policy Docs

Policy documents control how robots (and sometimes humans) behave. It's a storage for practical lessons learned so far,
summary of external documents, customer interviews, user instructions, as well as a place for staging documents to update the policy.
Documents have json structure, organized by path into folders. Last element of the path is the document name, similar to a
filesystem, folders exist only as a shorthand for shared paths. The convention for names is kebab lower case.
Call flexus_policy_document() without parameters for details on how to list, read and write those documents.
"""

POLICY_DOCUMENT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="flexus_policy_document",
    description="Tool to operate Policy Documents. Start with op=\"help\".",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["help", "list", "cat", "activate", "create", "create_qa", "create_from_template", "overwrite", "update_json_text", "cp", "mv", "rm"]},
            "args": {"type": "object"},   # model guesses p= to write here quite well for some reason, without help, must be something in prompt
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

flexus_policy_document(op="create_qa", args={"p": "/path", "top_tag": "hypothesis", "sections": {"formula": ["formula"], "ice": ["ease", "impact", "confidence"]}})
    Create a QA-format document. Section and question names are kebab-case.
    Tool auto-numbers (section01-name, question01-name), generates titles, sets q="" a="" on each question.
    Fails if document already exists.

flexus_policy_document(op="create_from_template", args={"template": "plan", "output_dir": "/plans", "slug": "my-thing"})
    Create a new policy document from a known template. Automatically prepends current date between
    output_dir and slug, e.g. /plans/20260325-my-thing. Fails if the document already exists.

flexus_policy_document(op="update_json_text", args={"p": "/folder/file", "json_path": "section1.field", "text": "new value", "expected_md5": "abc123"})
    Update a specific field in a document using json_path with dot notation.
    Example: "operations_overview.governance" updates doc["operations_overview"]["governance"]
    Pass expected_md5 (from a previous cat/update) to avoid overwriting concurrent changes.
    If md5 doesn't match, changes are not saved and latest content is returned so you can retry.

flexus_policy_document(op="cp", args={"p1": "/customer-research/interview-template", "p2": "/customer-research/interview-monsieur-dupont"})
    Copy a policy document.

flexus_policy_document(op="mv", args={"p1": "/customer-research/interview-monsieur-dupont", "p2": "/customer-research/interview-dupont-2026-03"})
    Move (rename) a policy document, overwrites destination if it exists.

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


@dataclass
class PdocUpdateJsonTextResult:
    latest_text: str
    md5_requested: str
    md5_found: str
    changes_saved: bool
    problem_message: str


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


PDOC_SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "pdoc-schemas"


def _load_pdoc_schema(template: str) -> Optional[dict]:
    f = PDOC_SCHEMAS_DIR / f"{template}.json"
    if not f.exists():
        return None
    return json.loads(f.read_text())


def _empty_value_for_field(field_schema: dict):
    t = field_schema.get("type", "string")
    if t == "object":
        return {k: _empty_value_for_field(v) for k, v in field_schema.get("properties", {}).items()}
    if t == "integer":
        return 0
    if t == "number" or t == "float":
        return 0.0
    if t == "boolean" or t == "bool":
        return False
    return ""


_KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def _kebab_title(name: str) -> str:
    return name.replace("-", " ").title()


def _build_qa_doc(top_tag: str, sections: dict) -> dict:
    result = {}
    for si, (sec_name, questions) in enumerate(sections.items(), 1):
        sec = {"title": _kebab_title(sec_name)}
        for qi, q_name in enumerate(questions, 1):
            sec[f"question{qi:02d}-{q_name}"] = {"q": "", "a": ""}
        result[f"section{si:02d}-{sec_name}"] = sec
    return {top_tag: {"meta": {"created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}, **result}}


def _pdoc_md5(content: Any) -> str:
    return hashlib.md5(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:8]


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

        r = ""

        try:
            if op == "list":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "/")
                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
                result = await self.pdoc_list(p, depth=5, fcall_untrusted_key=toolcall.fcall_untrusted_key)
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
                result = await self.pdoc_cat(p, fcall_untrusted_key=toolcall.fcall_untrusted_key)
                if not result:
                    return f"Policy document not found: {p}"
                content_str = json.dumps(result.pdoc_content, indent=2, ensure_ascii=False)
                content_md5 = _pdoc_md5(result.pdoc_content)
                if op == "activate":
                    r += f"✍️ {result.path}\nmd5={content_md5}\n\n"
                else:
                    r += f"📄 {result.path}\nmd5={content_md5}\n\n"
                r += content_str

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
                    await self.pdoc_create(p, text, fcall_untrusted_key=toolcall.fcall_untrusted_key)
                else:
                    await self.pdoc_overwrite(p, text, fcall_untrusted_key=toolcall.fcall_untrusted_key)
                saved_md5 = _pdoc_md5(json.loads(text))
                verb = "created" if op == "create" else "updated"
                r += f"✍️ {p}\nmd5={saved_md5}\n\n✓ Policy document {verb}"

            elif op == "create_qa":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                if not p:
                    return f"Error: p required\n\n{HELP}"
                top_tag = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "top_tag", "")
                sections = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "sections", None)
                if not top_tag or not sections or not isinstance(sections, dict):
                    return f"Error: top_tag and sections required\n\n{HELP}"
                if not _KEBAB_RE.match(top_tag):
                    return f"Error: top_tag must be kebab-case: {top_tag!r}"
                for sec_name, questions in sections.items():
                    if not _KEBAB_RE.match(sec_name):
                        return f"Error: section name must be kebab-case: {sec_name!r}"
                    if not isinstance(questions, list) or not questions:
                        return f"Error: section {sec_name!r} must have a non-empty list of question names"
                    for q_name in questions:
                        if not isinstance(q_name, str) or not _KEBAB_RE.match(q_name):
                            return f"Error: question name must be kebab-case: {q_name!r}"
                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
                doc = _build_qa_doc(top_tag, sections)
                await self.pdoc_create(p, json.dumps(doc, ensure_ascii=False), fcall_untrusted_key=toolcall.fcall_untrusted_key)
                r += f"✍️ {p}\nmd5={_pdoc_md5(doc)}\n\n✓ QA document created with {len(sections)} sections"

            elif op == "create_from_template":
                template = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "template", "")
                output_dir = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "output_dir", "")
                slug = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "slug", "")
                if not template or not output_dir or not slug:
                    return f"Error: template, output_dir, and slug are required\n\n{HELP}"
                output_dir = "/" + output_dir.strip().strip("/")
                slug = slug.strip()
                schema = _load_pdoc_schema(template)
                if schema is None:
                    return f"Error: template '{template}' not found"
                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
                tz = ZoneInfo(self.rcx.persona.ws_timezone)
                date_prefix = datetime.datetime.now(tz).strftime("%Y%m%d")
                p = f"{output_dir}/{date_prefix}-{slug}"
                keys = list(schema.keys())
                data = {keys[0]: _empty_value_for_field(schema[keys[0]])}
                for k in keys[1:]:
                    data[k] = None
                doc = {template: {
                    "meta": {"created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()},
                    "schema": schema,
                    **data,
                }}
                try:
                    await self.pdoc_create(p, json.dumps(doc, ensure_ascii=False), fcall_untrusted_key=toolcall.fcall_untrusted_key)
                except gql.transport.exceptions.TransportQueryError as e:
                    if "already exists" in str(e):
                        return (
                            f"Oops {p} already exists. Likely your previous attempt to create the same thing — "
                            f"load it with op=\"activate\" and continue filling out, "
                            f"or verify it's garbage using op=\"cat\" and then op=\"rm\"."
                        )
                    raise
                r += f"✍️ {p}\nmd5={_pdoc_md5(doc)}\n\n✓ Created from template '{template}'"

            elif op == "update_json_text":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                p = p or ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", "")
                json_path = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "json_path", "")
                text = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "text", "")
                expected_md5 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "expected_md5", "")
                if not p or not json_path or not text:
                    return f"Error: p, json_path, and text parameters required\n\n{HELP}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                upd = await self.pdoc_update_json_text(p, json_path, text, expected_md5, fcall_untrusted_key=toolcall.fcall_untrusted_key)
                if upd.changes_saved:
                    r += f"✍️ {p}\nmd5={upd.md5_found}\nchanges_saved=true\n\n✓ Updated {json_path}\n\n"
                else:
                    r += f"📄 {p}\nmd5_requested={upd.md5_requested}\nmd5_found={upd.md5_found}\nchanges_saved=false\n\n"
                    if upd.problem_message:
                        r += f"{upd.problem_message}\n\n"
                    else:
                        r += f"Document changed since you last read it, please retry.\n\n"
                r += upd.latest_text

            elif op == "cp":
                p1 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p1", "")
                p2 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p2", "")
                if not p1 or not p2:
                    return f"Error: p1 and p2 parameters required\n\n{HELP}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                await self.pdoc_cp(p1, p2, fcall_untrusted_key=toolcall.fcall_untrusted_key)
                r += f"✍️ {p2}\n\n✓ Copied from {p1}"

            elif op == "mv":
                p1 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p1", "")
                p2 = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p2", "")
                if not p1 or not p2:
                    return f"Error: p1 and p2 parameters required\n\n{HELP}"
                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())
                await self.pdoc_mv(p1, p2, fcall_untrusted_key=toolcall.fcall_untrusted_key)
                r += f"✍️ {p2}\n\n✓ Moved from {p1}"

            elif op == "rm":
                p = ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "p", "")
                p = p or ckit_cloudtool.try_best_to_find_argument(args, model_produced_args, "path", "")

                if not p:
                    return f"Error: p required\n\n{HELP}"

                if self.is_fake:
                    return await ckit_scenario.scenario_generate_tool_result_via_model(self.fclient, toolcall, open(__file__).read())

                await self.pdoc_rm(p, fcall_untrusted_key=toolcall.fcall_untrusted_key)
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

    def _auth_vars(self, fcall_untrusted_key: str = "", trust_me_bro_persona_id: str = "") -> dict:
        r = {}
        if fcall_untrusted_key:
            r["fcall_untrusted_key"] = fcall_untrusted_key
        else:
            r["trust_me_bro_persona_id"] = trust_me_bro_persona_id or self.rcx.persona.persona_id
        return r

    async def pdoc_list(self, p: str = "/", depth: int = 1, fcall_untrusted_key: str = "", trust_me_bro_persona_id: str = "") -> List[PdocListItem]:
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                gql.gql(f"""
                    query PdocList($fgroup_id: String!, $p: String!, $fcall_untrusted_key: String, $trust_me_bro_persona_id: String, $depth: Int) {{
                        policydoc_list(fgroup_id: $fgroup_id, p: $p, fcall_untrusted_key: $fcall_untrusted_key, trust_me_bro_persona_id: $trust_me_bro_persona_id, depth: $depth) {{
                            {gql_utils.gql_fields(PdocListItem)}
                        }}
                    }}
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "depth": depth, **self._auth_vars(fcall_untrusted_key, trust_me_bro_persona_id)},
            )
            items = result.get("policydoc_list", [])
            return [gql_utils.dataclass_from_dict(item, PdocListItem) for item in items]

    async def pdoc_cat(self, p: str, best_effort_to_find: bool = False, fcall_untrusted_key: str = "", trust_me_bro_persona_id: str = "") -> Optional[PdocDocument]:
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                gql.gql(f"""
                    query PdocCat($fgroup_id: String!, $p: String!, $fcall_untrusted_key: String, $trust_me_bro_persona_id: String, $best_effort_to_find: Boolean) {{
                        policydoc_cat(fgroup_id: $fgroup_id, p: $p, fcall_untrusted_key: $fcall_untrusted_key, trust_me_bro_persona_id: $trust_me_bro_persona_id, best_effort_to_find: $best_effort_to_find) {{
                            {gql_utils.gql_fields(PdocDocument)}
                        }}
                    }}
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "best_effort_to_find": best_effort_to_find, **self._auth_vars(fcall_untrusted_key, trust_me_bro_persona_id)},
            )
            doc = result.get("policydoc_cat")
            if not doc:
                return None
            return gql_utils.dataclass_from_dict(doc, PdocDocument)

    async def pdoc_create(self, p: str, text: str, fcall_untrusted_key: str = "", trust_me_bro_persona_id: str = "") -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocCreate($fgroup_id: String!, $p: String!, $text: String!, $fcall_untrusted_key: String, $trust_me_bro_persona_id: String) {
                        policydoc_create(fgroup_id: $fgroup_id, p: $p, text: $text, fcall_untrusted_key: $fcall_untrusted_key, trust_me_bro_persona_id: $trust_me_bro_persona_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "text": text, **self._auth_vars(fcall_untrusted_key, trust_me_bro_persona_id)},
            )

    async def pdoc_overwrite(self, p: str, text: str, fcall_untrusted_key: str = "", trust_me_bro_persona_id: str = "") -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocOverwrite($fgroup_id: String!, $p: String!, $text: String!, $fcall_untrusted_key: String, $trust_me_bro_persona_id: String) {
                        policydoc_overwrite(fgroup_id: $fgroup_id, p: $p, text: $text, fcall_untrusted_key: $fcall_untrusted_key, trust_me_bro_persona_id: $trust_me_bro_persona_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "text": text, **self._auth_vars(fcall_untrusted_key, trust_me_bro_persona_id)},
            )

    async def pdoc_update_json_text(self, p: str, json_path: str, text: str, expected_md5: str = "", fcall_untrusted_key: str = "", trust_me_bro_persona_id: str = "") -> PdocUpdateJsonTextResult:
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                gql.gql(f"""
                    mutation PdocUpdateJsonText($fgroup_id: String!, $p: String!, $json_path: String!, $text: String!, $fcall_untrusted_key: String, $trust_me_bro_persona_id: String, $expected_md5: String) {{
                        policydoc_update_json_text(fgroup_id: $fgroup_id, p: $p, json_path: $json_path, text: $text, fcall_untrusted_key: $fcall_untrusted_key, trust_me_bro_persona_id: $trust_me_bro_persona_id, expected_md5: $expected_md5) {{
                            {gql_utils.gql_fields(PdocUpdateJsonTextResult)}
                        }}
                    }}
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, "json_path": json_path, "text": text, "expected_md5": expected_md5, **self._auth_vars(fcall_untrusted_key, trust_me_bro_persona_id)},
            )
            return gql_utils.dataclass_from_dict(result["policydoc_update_json_text"], PdocUpdateJsonTextResult)

    async def pdoc_cp(self, p1: str, p2: str, fcall_untrusted_key: str = "", trust_me_bro_persona_id: str = "") -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocCp($fgroup_id: String!, $p1: String!, $p2: String!, $fcall_untrusted_key: String, $trust_me_bro_persona_id: String) {
                        policydoc_cp(fgroup_id: $fgroup_id, p1: $p1, p2: $p2, fcall_untrusted_key: $fcall_untrusted_key, trust_me_bro_persona_id: $trust_me_bro_persona_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p1": p1, "p2": p2, **self._auth_vars(fcall_untrusted_key, trust_me_bro_persona_id)},
            )

    async def pdoc_mv(self, p1: str, p2: str, fcall_untrusted_key: str = "", trust_me_bro_persona_id: str = "") -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocMv($fgroup_id: String!, $p1: String!, $p2: String!, $fcall_untrusted_key: String, $trust_me_bro_persona_id: String) {
                        policydoc_mv(fgroup_id: $fgroup_id, p1: $p1, p2: $p2, fcall_untrusted_key: $fcall_untrusted_key, trust_me_bro_persona_id: $trust_me_bro_persona_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p1": p1, "p2": p2, **self._auth_vars(fcall_untrusted_key, trust_me_bro_persona_id)},
            )

    async def pdoc_rm(self, p: str, fcall_untrusted_key: str = "", trust_me_bro_persona_id: str = "") -> None:
        http = await self.fclient.use_http()
        async with http as h:
            await h.execute(
                gql.gql("""
                    mutation PdocRm($fgroup_id: String!, $p: String!, $fcall_untrusted_key: String, $trust_me_bro_persona_id: String) {
                        policydoc_rm(fgroup_id: $fgroup_id, p: $p, fcall_untrusted_key: $fcall_untrusted_key, trust_me_bro_persona_id: $trust_me_bro_persona_id)
                    }
                """),
                variable_values={"fgroup_id": self.fgroup_id, "p": p, **self._auth_vars(fcall_untrusted_key, trust_me_bro_persona_id)},
            )
