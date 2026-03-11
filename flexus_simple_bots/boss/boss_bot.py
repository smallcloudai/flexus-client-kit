import asyncio
import datetime
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
from flexus_client_kit import ckit_external_auth
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.boss import boss_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_boss")


BOT_NAME = "boss"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION


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

PLAN_PROGRESS_ADD_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="plan_progress_add",
    description="Append a single line to learned_so_far or progress_documents in the progress section of a plan.",
    parameters={
        "type": "object",
        "properties": {
            "plan_slug": {"type": "string", "description": "Short kebab-case name, 2-4 words"},
            "field": {"type": "string", "enum": ["learned_so_far", "progress_documents"]},
            "line": {"type": "string"},
        },
        "required": ["plan_slug", "field", "line"],
        "additionalProperties": False,
    },
)


PLAN_SECTIONS = ["section01-input", "section02-draft-plan", "section03-progress", "section04-conclusion"]

PLAN_TEMPLATE_SCHEMA = {
    "section01-input": {
        "type": "object",
        "title": "Input",
        "properties": {
            "input_goal": {"type": "string", "order": 0, "ui:multiline": 10},
            "input_documents": {"type": "string", "order": 1, "ui:multiline": 6},
        },
        "additionalProperties": False,
    },
    "section02-draft-plan": {
        "type": "object",
        "title": "Draft",
        "properties": {
            "draft_tasks": {"type": "string", "order": 0, "ui:multiline": 13},
        },
        "additionalProperties": False,
    },
    "section03-progress": {
        "type": "object",
        "title": "Progress",
        "properties": {
            "task_ids": {"type": "array", "order": 0, "items": {"type": "string"}},
            "learned_so_far": {"type": "string", "order": 1, "ui:multiline": 5},
            "progress_documents": {"type": "string", "order": 2, "ui:multiline": 3},
        },
        "additionalProperties": False,
    },
    "section04-conclusion": {
        "type": "object",
        "title": "Conclusion",
        "properties": {
            "outcome_summary": {"type": "string", "order": 0, "ui:multiline": 10},
            "outcome_documents": {"type": "string", "order": 1, "ui:multiline": 6},
        },
        "additionalProperties": False,
    },
}

def _make_nullable(prop):
    p = {k: v for k, v in prop.items() if k not in ("order", "ui:multiline")}
    t = p.get("type", "string")
    p["type"] = [t, "null"] if isinstance(t, str) else t
    return p


def _plan_tool(section_key, name, description):
    section_schema = PLAN_TEMPLATE_SCHEMA[section_key]
    fields = list(section_schema["properties"].keys())
    props = {"plan_slug": {"type": "string", "description": "Short kebab-case name, 2-4 words"}}
    props.update({k: _make_nullable(section_schema["properties"][k]) for k in fields})
    return ckit_cloudtool.CloudTool(
        strict=True,
        name=name,
        description=description,
        parameters={
            "type": "object",
            "properties": props,
            "required": ["plan_slug", *fields],
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

PLAN_TOOLS = [PLAN_INPUT_TOOL, PLAN_DRAFT_TOOL, PLAN_PROGRESS_TOOL, PLAN_CONCLUSION_TOOL]

PLAN_SECTION_BY_TOOL = {
    "plan_input": _plan_input_meta,
    "plan_draft": _plan_draft_meta,
    "plan_progress": _plan_progress_meta,
    "plan_conclusion": _plan_conclusion_meta,
}


async def handle_plan_update(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    rcx: ckit_bot_exec.RobotContext,
    pdoc_integration: fi_pdoc.IntegrationPdoc,
) -> str:
    if rcx.running_test_scenario:
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, Path(__file__).read_text())
    plan_slug = args.get("plan_slug", "").strip()
    if not plan_slug:
        return "Error: plan_slug is required"
    section, fields = PLAN_SECTION_BY_TOOL[toolcall.fcall_name]
    data = {k: args[k] for k in fields if args.get(k) is not None}
    # models love to send literal \n instead of real newlines in human-readable text
    for k, v in data.items():
        if isinstance(v, str) and "\\n" in v and "\n" not in v:
            data[k] = v.replace("\\n", "\n")

    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/plans/{plan_slug}"

    existing = await pdoc_integration.pdoc_cat(path, caller_fuser_id)
    if existing is None:
        doc = {"plan": {"meta": {"created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}}}
    else:
        doc = existing.pdoc_content

    doc["plan"]["schema"] = PLAN_TEMPLATE_SCHEMA
    doc["plan"].setdefault(section, {}).update(data)
    doc["plan"]["meta"]["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if existing is None:
        await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)
    else:
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    filled = [s for s in PLAN_SECTIONS if doc["plan"].get(s)]
    unfilled = [s for s in PLAN_SECTIONS if not doc["plan"].get(s)]
    return f"✍️ {path}\n\nUpdated: {section}\nFilled: {', '.join(filled) or 'none'}\nUnfilled: {', '.join(unfilled) or 'none'}\n\nUse flexus_policy_document(op=\"cat\", args={{\"p\": \"{path}\"}}) to read it in full."


async def handle_plan_progress_add(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    rcx: ckit_bot_exec.RobotContext,
    pdoc_integration: fi_pdoc.IntegrationPdoc,
) -> str:
    if rcx.running_test_scenario:
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, Path(__file__).read_text())
    plan_slug = args.get("plan_slug", "").strip()
    field = args.get("field", "")
    line = args.get("line", "").strip()
    if not plan_slug or not field or not line:
        return "Error: plan_slug, field, and line are all required"
    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/plans/{plan_slug}"
    existing = await pdoc_integration.pdoc_cat(path, caller_fuser_id)
    if existing is None:
        return f"Error: plan {path} not found"
    doc = existing.pdoc_content
    section = doc["plan"].setdefault("section03-progress", {})
    prev = section.get(field, "").rstrip("\n")
    section[field] = (prev + "\n" + line).lstrip("\n")
    doc["plan"]["meta"]["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)
    return f"✍️ {path}\n\nAppended to {field}"


TOOLS = [
    *PLAN_TOOLS,
    PLAN_PROGRESS_ADD_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    MARKETPLACE_SEARCH_TOOL,
    MARKETPLACE_DESC_TOOL,
    MARKETPLACE_HIRE_OR_FIRE_TOOL,
    *[t for rec in boss_install.BOSS_INTEGRATIONS for t in rec.integr_tools],
]


async def boss_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(boss_install.BOSS_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(boss_install.BOSS_INTEGRATIONS, rcx, setup)
    pdoc_integration = integr_objects["flexus_policy_document"]

    for plan_tool in PLAN_TOOLS:
        @rcx.on_tool_call(plan_tool.name)
        async def toolcall_plan(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
            return await handle_plan_update(toolcall, model_produced_args, rcx, pdoc_integration)

    @rcx.on_tool_call(PLAN_PROGRESS_ADD_TOOL.name)
    async def toolcall_plan_progress_add(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await handle_plan_progress_add(toolcall, model_produced_args, rcx, pdoc_integration)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(
            rcx.workdir,
            rcx.personal_mongo,
            toolcall,
            model_produced_args,
        )

    @rcx.on_tool_call(MARKETPLACE_SEARCH_TOOL.name)
    async def toolcall_marketplace_search(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        q = model_produced_args.get("q", "").strip()
        if not q:
            return "Error: q (search query) is required"
        http = await fclient.use_http()
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
        http = await fclient.use_http()
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
        http = await fclient.use_http()
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
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=boss_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=boss_install.install,
    ))


if __name__ == "__main__":
    main()
