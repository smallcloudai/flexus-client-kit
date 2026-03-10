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



SETUP_COLLEAGUES_HELP = """Usage:

boss_setup_colleagues(op='get', args={'bot_name': 'Frog'})
    View current setup for a colleague bot.

boss_setup_colleagues(op='update', args={'bot_name': 'Frog', 'set_key': 'greeting_style', 'set_val': 'excited'})
    Update a setup key for a colleague bot. Always run get operation before update.

boss_setup_colleagues(op='update', args={'bot_name': 'Frog', 'set_key': 'greeting_style'})
    Reset a setup key to default value (omit set_val). Always run get operation before update.
"""

BOT_BUG_REPORT_HELP = """Report a bug related to a bot's code, tools, or prompts (not configuration issues).
Always list bugs before reporting to avoid duplicates.

Usage:

bot_bug_report(op='report_bug', args={'bot_name': 'Karen 5', 'ft_id': 'ft_abc123', 'bug_summary': 'Bot fails to parse dates in ISO format'})
    Report a bug related to a bot's code, tools, or prompts.

bot_bug_report(op='list_reported_bugs', args={'bot_name': 'Frog'})
    List all reported bugs for a specific bot.
"""

MARKETPLACE_SEARCH_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="flexus_marketplace_search",
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
    name="flexus_marketplace_desc",
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

PLAN_TEMPLATE_SCHEMA = {
    "section01-input": {
        "type": "object",
        "title": "Input",
        "properties": {
            "input_goal": {
                "type": "string",
                "order": 0,
                "ui:multiline": 10,
            },
            "input_documents": {
                "type": "array", "order": 1,
                "items": {"type": "string"},
            },
        },
        "additionalProperties": False,
    },
    "section02-initial-todo": {
        "type": "object",
        "title": "Initial todo",
        "properties": {
            "initial_tasks": {
                "type": "array", "order": 0,
                "items": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "order": 0},
                        "task": {"type": "string", "order": 1},
                    },
                    "additionalProperties": False,
                },
            },
        },
        "additionalProperties": False,
    },
    "section03-progress": {
        "type": "object",
        "title": "Progress",
        "properties": {
            "task_ids": {
                "type": "array", "order": 0,
                "items": {"type": "string"},
            },
            "learned_so_far": {
                "type": "array", "order": 1,
                "items": {"type": "string"},
            },
            "documents": {
                "type": "array", "order": 2,
                "items": {"type": "string"},
            },
        },
        "additionalProperties": False,
    },
}

PLAN_TEMPLATE_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="plan_template",
    description="Create or update a plan document. Sections: section01-input, section02-initial-todo, section03-progress. Update one section at a time.",
    parameters={
        "type": "object",
        "properties": {
            "plan_slug": {"type": "string", "description": "Short kebab-case name for the plan, 2-4 words"},
            "section": {
                "type": "string",
                "enum": ["section01-input", "section02-initial-todo", "section03-progress"],
            },
            "data": {"type": "object", "description": "Section content matching the section schema"},
        },
        "required": ["plan_slug", "section", "data"],
    },
)


async def handle_plan_template(
    toolcall: ckit_cloudtool.FCloudtoolCall,
    args: Dict[str, Any],
    rcx: ckit_bot_exec.RobotContext,
    pdoc_integration: fi_pdoc.IntegrationPdoc,
) -> str:
    if rcx.running_test_scenario:
        return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, Path(__file__).read_text())
    plan_slug = args.get("plan_slug", "").strip()
    section = args.get("section", "")
    data = args.get("data")
    if not plan_slug or not section or not data:
        return "Error: plan_slug, section, and data are all required"
    if section not in ("section01-input", "section02-initial-todo", "section03-progress"):
        return f"Error: unknown section {section!r}"

    caller_fuser_id = ckit_external_auth.get_fuser_id_from_rcx(rcx, toolcall.fcall_ft_id)
    path = f"/plans/{plan_slug}"

    existing = await pdoc_integration.pdoc_cat(path, caller_fuser_id)
    if existing is None:
        doc = {"plan": {"meta": {"created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}}}
    else:
        doc = existing.pdoc_content

    doc["plan"]["schema"] = PLAN_TEMPLATE_SCHEMA
    doc["plan"][section] = data
    doc["plan"]["meta"]["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if existing is None:
        await pdoc_integration.pdoc_create(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)
    else:
        await pdoc_integration.pdoc_overwrite(path, json.dumps(doc, ensure_ascii=False), caller_fuser_id)

    filled = [s for s in ("section01-input", "section02-initial-todo", "section03-progress") if doc["plan"].get(s)]
    unfilled = [s for s in ("section01-input", "section02-initial-todo", "section03-progress") if not doc["plan"].get(s)]
    return f"✍️ {path}\n\nUpdated: {section}\nFilled: {', '.join(filled) or 'none'}\nUnfilled: {', '.join(unfilled) or 'none'}\n"


TOOLS = [
    PLAN_TEMPLATE_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    MARKETPLACE_SEARCH_TOOL,
    MARKETPLACE_DESC_TOOL,
    *[t for rec in boss_install.BOSS_INTEGRATIONS for t in rec.integr_tools],
]


async def boss_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(boss_install.BOSS_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(boss_install.BOSS_INTEGRATIONS, rcx, setup)
    pdoc_integration = integr_objects["flexus_policy_document"]

    @rcx.on_tool_call(PLAN_TEMPLATE_TOOL.name)
    async def toolcall_plan_template(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await handle_plan_template(toolcall, model_produced_args, rcx, pdoc_integration)

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
            }, indent=2, ensure_ascii=False))
        return "\n\n".join(parts)

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
