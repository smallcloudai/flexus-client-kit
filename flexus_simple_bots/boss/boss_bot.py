import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

import gql
from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_scenario
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit import ckit_bot_version

logger = logging.getLogger("bot_boss")


BOSS_ROOTDIR = Path(__file__).parent
BOSS_SKILLS = ckit_skills.static_skills_find(BOSS_ROOTDIR, shared_skills_allowlist="", integration_skills_allowlist="")
BOSS_SETUP_SCHEMA = json.loads((BOSS_ROOTDIR / "setup_schema.json").read_text())
BOSS_SETUP_SCHEMA += fi_slack.SLACK_SETUP_SCHEMA

BOSS_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    BOSS_ROOTDIR,
    allowlist=[
        "flexus_policy_document",
        "print_widget",
        "slack",
        "telegram",
        "erp[meta, data]",
        "skills",
    ],
    builtin_skills=BOSS_SKILLS,
)


MARKETPLACE_SEARCH_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="boss_marketplace_search",
    description="Search the Flexus marketplace for bots by keyword. Returns matching bot names, titles, tags, and whether already hired.",
    parameters={
        "type": "object",
        "properties": {
            "q": {"type": "string", "description": "Search query (matches name, title, description, tags)"},
        },
        "required": ["q"],
    },
)

MARKETPLACE_DESC_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="boss_marketplace_desc",
    description="Get detailed descriptions for specific marketplace bots by their marketable_name. Up to 20 names.",
    parameters={
        "type": "object",
        "properties": {
            "marketable_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of bot marketable_name values to get descriptions for",
            },
        },
        "required": ["marketable_names"],
    },
)

MARKETPLACE_HIRE_OR_FIRE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="boss_marketplace_hire_or_fire",
    description="Hire: provide marketable_name (snake case bot type from marketplace). Fire: provide persona_name (specific hired bot name like 'Bob 15').",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["hire", "fire"]},
            "marketable_name": {"type": "string", "description": "Marketplace bot name, for hire"},
            "persona_name": {"type": "string", "description": "Hired bot name (e.g. 'Bob 15'), for fire"},
            "stability_tolerance": {"type": "string", "enum": ["stable", "beta", "private"], "description": "Minimum stability level to accept when hiring, default stable"},
        },
        "required": ["op"],
    },
)

BOSS_SETUP_COLLEAGUES_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="boss_setup_colleagues",
    description="View or update colleague bot configuration.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["get_all", "update_one"]},
            "bot_name": {"type": "string", "description": "Colleague bot name"},
            "update_key": {"type": ["string", "null"]},
            "new_val": {"type": ["string", "null"], "description": "Set null to reset to default"},
        },
        "required": ["op", "bot_name", "update_key", "new_val"],
        "additionalProperties": False,
    },
)

BOSS_TREE_FETCH_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="boss_tree_fetch",
    description="Fetch the workspace tree: bots, kanban boards, tasks, policy documents — all in one view.",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
)

PLAN_PROGRESS_ADD_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="plan_progress_add",
    description="Append a single line to learned_so_far or progress_documents in the progress section of a plan.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Document path, e.g. /plans/my-plan"},
            "field": {"type": "string", "enum": ["learned_so_far", "progress_documents"]},
            "line": {"type": "string"},
            "expected_md5": {"type": ["string", "null"], "description": "md5 from last cat/update, to avoid overwriting concurrent changes"},
        },
        "required": ["path", "field", "line", "expected_md5"],
        "additionalProperties": False,
    },
)


PLAN_TEMPLATE_SCHEMA = fi_pdoc._load_pdoc_schema("plan")
PLAN_SECTIONS = ["section01-input", "section02-draft-plan", "section03-progress", "section04-conclusion"]
assert list(PLAN_TEMPLATE_SCHEMA.keys()) == PLAN_SECTIONS

def _make_nullable(prop):
    p = {k: v for k, v in prop.items() if k not in ("order", "ui:multiline")}
    t = p.get("type", "string")
    p["type"] = [t, "null"] if isinstance(t, str) else t
    return p


def _plan_tool(section_key, name, description):
    section_schema = PLAN_TEMPLATE_SCHEMA[section_key]
    fields = list(section_schema["properties"].keys())
    props = {"path": {"type": "string", "description": "Document path, e.g. /plans/my-plan"}}
    props.update({k: _make_nullable(section_schema["properties"][k]) for k in fields})
    props["expected_md5"] = {"type": ["string", "null"], "description": "md5 from last cat/update, to avoid overwriting concurrent changes"}
    return ckit_cloudtool.CloudTool(
        strict=True,
        name=name,
        description=description,
        parameters={
            "type": "object",
            "properties": props,
            "required": ["path", *fields, "expected_md5"],
            "additionalProperties": False,
        },
    ), (section_key, fields)


PLAN_INPUT_TOOL, _plan_input_meta = _plan_tool(
    "section01-input", "plan_input", "Create or update the input section of a plan: goal and referenced documents.")
PLAN_DRAFT_TOOL, _plan_draft_meta = _plan_tool(
    "section02-draft-plan", "plan_draft", "Create or update the draft plan: tasks assigned to bots, one per line like 'BotName: do something'.")
PLAN_PROGRESS_TOOL, _plan_progress_meta = _plan_tool(
    "section03-progress", "plan_progress", "Update progress on a plan: task IDs, learnings, and produced documents.")
PLAN_CONCLUSION_TOOL, _plan_conclusion_meta = _plan_tool(
    "section04-conclusion", "plan_conclusion", "Close out a plan with a summary and outcome.")

PLAN_UPDATE_SECTION_TOOLS = [PLAN_INPUT_TOOL, PLAN_DRAFT_TOOL, PLAN_PROGRESS_TOOL, PLAN_CONCLUSION_TOOL]

PLAN_SECTION_BY_TOOL = {
    "plan_input": _plan_input_meta,
    "plan_draft": _plan_draft_meta,
    "plan_progress": _plan_progress_meta,
    "plan_conclusion": _plan_conclusion_meta,
}



async def handle_plan_update_section(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    rcx: ckit_bot_exec.RobotContext,
    pdoc_integration: fi_pdoc.IntegrationPdoc,
) -> str:
    if rcx.running_test_scenario:
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, Path(__file__).read_text())
    path = args.get("path", "").strip()
    if not path:
        return "Error: path is required"
    section, fields = PLAN_SECTION_BY_TOOL[toolcall.fcall_name]
    uk = toolcall.fcall_untrusted_key
    expected_md5 = args.get("expected_md5") or ""

    section_data = {k: args[k] for k in fields if args.get(k) is not None}
    for k, v in section_data.items():
        if isinstance(v, str) and "\\n" in v and "\n" not in v:
            section_data[k] = v.replace("\\n", "\n")
        if isinstance(v, str) and "&#10;" in v and "\n" not in v:
            section_data[k] = section_data[k].replace("&#10;", "\n")
    upd = await pdoc_integration.pdoc_update_at_location(path, [{"json_path": f"plan.{section}", "text": json.dumps(section_data, ensure_ascii=False)}], persona_id=rcx.persona.persona_id, fcall_untrusted_key=uk, expected_md5=expected_md5)
    if not upd.changes_saved:
        return f"📄 {path}\nmd5_requested={upd.md5_requested}\nmd5_found={upd.md5_found}\nchanges_saved=false\n\n{upd.problem_message or 'Document changed, please retry'}\n\n{upd.latest_text}"

    content = json.loads(upd.latest_text)
    plan = content.get("plan", {})
    filled = [s for s in PLAN_SECTIONS if plan.get(s)]
    unfilled = [s for s in PLAN_SECTIONS if not plan.get(s)]
    return f"✍️ {path}\nmd5={upd.md5_found}\n\nUpdated: {section}\nFilled: {', '.join(filled) or 'none'}\nUnfilled: {', '.join(unfilled) or 'none'}"


async def handle_plan_progress_add(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    rcx: ckit_bot_exec.RobotContext,
    pdoc_integration: fi_pdoc.IntegrationPdoc,
) -> str:
    if rcx.running_test_scenario:
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, Path(__file__).read_text())
    path = args.get("path", "").strip()
    field = args.get("field", "")
    line = args.get("line", "").strip()
    if not path or not field or not line:
        return "Error: path, field, and line are all required"
    uk = toolcall.fcall_untrusted_key
    expected_md5 = args.get("expected_md5") or ""
    existing = await pdoc_integration.pdoc_cat(path, persona_id=rcx.persona.persona_id, fcall_untrusted_key=uk)
    if existing is None:
        return f"Error: plan {path} not found"
    prev = existing.pdoc_content.get("plan", {}).get("section03-progress", {}).get(field, "").rstrip("\n")
    new_value = (prev + "\n" + line).lstrip("\n")
    upd = await pdoc_integration.pdoc_update_at_location(path, [{"json_path": f"plan.section03-progress.{field}", "text": new_value}], persona_id=rcx.persona.persona_id, fcall_untrusted_key=uk, expected_md5=expected_md5)
    if not upd.changes_saved:
        return f"📄 {path}\nmd5_requested={upd.md5_requested}\nmd5_found={upd.md5_found}\nchanges_saved=false\n\n{upd.problem_message or 'Document changed, please retry.'}\n\n{upd.latest_text}"
    return f"✍️ {path}\nmd5={upd.md5_found}\n\nAppended to {field}"


BOSS_LOCAL_TOOLS = [
    *PLAN_UPDATE_SECTION_TOOLS,
    PLAN_PROGRESS_ADD_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    MARKETPLACE_SEARCH_TOOL,
    MARKETPLACE_DESC_TOOL,
    MARKETPLACE_HIRE_OR_FIRE_TOOL,
    BOSS_SETUP_COLLEAGUES_TOOL,
    BOSS_TREE_FETCH_TOOL,
]

TOOLS = [
    *BOSS_LOCAL_TOOLS,
    *[t for rec in BOSS_INTEGRATIONS for t in rec.integr_tools],
]


async def boss_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(BOSS_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(BOSS_INTEGRATIONS, rcx, setup)
    pdoc_integration = integr_objects["flexus_policy_document"]

    for plan_tool in PLAN_UPDATE_SECTION_TOOLS:
        @rcx.on_tool_call(plan_tool.name)
        async def toolcall_plan_update_section(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
            return await handle_plan_update_section(toolcall, model_produced_args, rcx, pdoc_integration)

    @rcx.on_tool_call(PLAN_PROGRESS_ADD_TOOL.name)
    async def toolcall_plan_progress_add(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await handle_plan_progress_add(toolcall, model_produced_args, rcx, pdoc_integration)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(rcx, toolcall, model_produced_args)

    @rcx.on_tool_call(BOSS_SETUP_COLLEAGUES_TOOL.name)
    async def toolcall_setup_colleagues(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        op = model_produced_args.get("op", "get_all")
        bot_name = model_produced_args.get("bot_name", "").strip()
        update_key = model_produced_args.get("update_key") or None
        new_val = model_produced_args.get("new_val") or None
        backend_op = "update" if op == "update_one" else "get"
        if not bot_name:
            return "Error: bot_name is required"
        if op == "update_one" and not update_key:
            return "Error: update_key required for update_one"
        if op == "update_one" and not toolcall.confirmed_by_human:
            http = await fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
            async with http as h:
                try:
                    prev_val = (await h.execute(gql.gql("""
                        mutation BossGetColleagueSetup($ws_id: String!, $bot_name: String!, $op: String!, $key: String) {
                            boss_setup_colleagues(ws_id: $ws_id, bot_name: $bot_name, op: $op, key: $key)
                        }"""),
                        variable_values={"ws_id": rcx.persona.ws_id, "bot_name": bot_name, "op": "get", "key": update_key},
                    )).get("boss_setup_colleagues", "")
                except gql.transport.exceptions.TransportQueryError as e:
                    return f"Error: {e}"
            disp_val = new_val if new_val is not None else "(default)"
            if len(disp_val) < 100 and "\n" not in disp_val and len(prev_val) < 100 and "\n" not in prev_val:
                explanation = f"Update {bot_name} setup key '{update_key}':\nNew value: {disp_val}\nOld value: {prev_val}"
            else:
                new_lines = "\n".join(f"+ {line}" for line in disp_val.split("\n"))
                old_lines = "\n".join(f"- {line}" for line in prev_val.split("\n"))
                explanation = f"Update {bot_name} setup key '{update_key}':\n\n{new_lines}\n{old_lines}"
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_setup_key="boss_can_update_colleague_setup",
                confirm_command=f"update {bot_name}.{update_key}",
                confirm_explanation=explanation,
            )
        http = await fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        async with http as h:
            try:
                r = await h.execute(gql.gql("""
                    mutation BossSetupColleagues($ws_id: String!, $bot_name: String!, $op: String!, $key: String, $val: String) {
                        boss_setup_colleagues(ws_id: $ws_id, bot_name: $bot_name, op: $op, key: $key, val: $val)
                    }"""),
                    variable_values={"ws_id": rcx.persona.ws_id, "bot_name": bot_name, "op": backend_op, "key": update_key, "val": new_val},
                )
                return r.get("boss_setup_colleagues", f"Error: Failed to {op} setup for {bot_name}")
            except gql.transport.exceptions.TransportQueryError as e:
                logger.exception("handle_setup_colleagues error")
                return f"handle_setup_colleagues problem: {e}"

    @rcx.on_tool_call(BOSS_TREE_FETCH_TOOL.name)
    async def toolcall_tree_fetch(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        http = await fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        async with http as h:
            try:
                r = await h.execute(gql.gql("""
                    mutation BossTreeFetch($ws_id: String!) {
                        boss_tree_fetch(ws_id: $ws_id)
                    }"""),
                    variable_values={"ws_id": rcx.persona.ws_id},
                )
                return r.get("boss_tree_fetch", "Error: empty response")
            except gql.transport.exceptions.TransportQueryError as e:
                return f"Error: {e}"

    @rcx.on_tool_call(MARKETPLACE_SEARCH_TOOL.name)
    async def toolcall_marketplace_search(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        q = model_produced_args.get("q", "").strip()
        if not q:
            return "Error: q (search query) is required"
        http = await fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        async with http as h:
            r = await h.execute(gql.gql("""
                query BossMarketplaceSearch($q: String!, $ws_id: String!) {
                    marketplace_boss_search(q: $q, ws_id: $ws_id) {
                        marketable_name marketable_title1 marketable_title2 marketable_tags already_hired_persona_names
                    }
                }"""),
                variable_values={"q": q, "ws_id": rcx.persona.ws_id},
            )
        items = r.get("marketplace_boss_search", [])
        return f"{len(items)} bots found\n\n" + "\n".join(json.dumps(it) for it in items)

    @rcx.on_tool_call(MARKETPLACE_DESC_TOOL.name)
    async def toolcall_marketplace_desc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        names = model_produced_args.get("marketable_names", [])
        if not names or not isinstance(names, list):
            return "Error: marketable_names (list of strings) is required"
        if len(names) > 20:
            return "Error: max 20 names at a time"
        http = await fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        async with http as h:
            r = await h.execute(gql.gql("""
                query BossMarketplaceDesc($marketable_names: [String!]!, $ws_id: String!) {
                    marketplace_boss_desc(marketable_names: $marketable_names, ws_id: $ws_id) {
                        marketable_name marketable_title1 marketable_title2 marketable_description marketable_tags marketable_occupation
                        experts { fexp_name fexp_description }
                        versions { stability marketable_version }
                    }
                }"""),
                variable_values={"marketable_names": names, "ws_id": rcx.persona.ws_id},
            )
        items = r.get("marketplace_boss_desc", [])
        parts = [f"{len(items)} descriptions found"]
        for it in items:
            parts.append(json.dumps({
                "marketable_name": it["marketable_name"],
                "title1": it["marketable_title1"],
                "title2": it["marketable_title2"],
                "occupation": it["marketable_occupation"],
                "tags": it["marketable_tags"],
                "description": it["marketable_description"],
                "experts": it["experts"],
                "versions": it["versions"],
            }, indent=2, ensure_ascii=False))
        return "\n\n".join(parts)

    @rcx.on_tool_call(MARKETPLACE_HIRE_OR_FIRE_TOOL.name)
    async def toolcall_hire_or_fire(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        op = model_produced_args.get("op", "hire")
        mn = model_produced_args.get("marketable_name", "").strip() if op == "hire" else ""
        pn = model_produced_args.get("persona_name", "").strip() if op == "fire" else ""
        st = model_produced_args.get("stability_tolerance", "stable")
        if op == "hire" and not mn:
            return "Error: marketable_name is required for hire"
        if op == "fire" and not pn:
            return "Error: persona_name is required for fire"
        label = mn if op == "hire" else pn
        if not toolcall.confirmed_by_human and setup["confirm_hire_or_fire"]:
            raise ckit_cloudtool.NeedsConfirmation(
                confirm_explanation=f"Boss confirms significant changes to your workspace with you",
                confirm_command=f"{op} {label}",
                confirm_setup_key="confirm_hire_or_fire",
            )
        http = await fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        async with http as h:
            r = await h.execute(gql.gql("""
                mutation BossHireOrFire($ws_id: String!, $op: String!, $mn: String, $pn: String, $st: String!) {
                    marketplace_boss_hire_or_fire(ws_id: $ws_id, op: $op, marketable_name: $mn, persona_name: $pn, stability_tolerance: $st)
                }"""),
                variable_values={"ws_id": rcx.persona.ws_id, "op": op, "mn": mn or None, "pn": pn or None, "st": st},
            )
        pid = r.get("marketplace_boss_hire_or_fire", "")
        return f"{'Fired' if op == 'fire' else 'Hired'} {label}, persona_id={pid}"

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.boss import boss_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(__file__)
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(ckit_bot_version.bot_name_from_file(__file__), bot_version), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=boss_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=boss_install.install,
    ))


if __name__ == "__main__":
    main()
