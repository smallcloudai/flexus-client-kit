import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit.integrations import fi_mcp
from flexus_client_kit import ckit_bot_version
from flexus_simple_bots.tasktopus.fakefibery import fakefibery_fakemcp
from flexus_simple_bots.tasktopus.fakefibery import fakefibery_situation1

logger = logging.getLogger("bot_tasktopus")

BOT_NAME = ckit_bot_version.bot_name_from_file(__file__)

TASKTOPUS_ROOTDIR = Path(__file__).parent
TASKTOPUS_MCPS = [
    "fibery",
]

TASKTOPUS_SETUP_SCHEMA = json.loads((TASKTOPUS_ROOTDIR / "setup_schema.json").read_text())
TASKTOPUS_SETUP_SCHEMA.extend(fi_mcp.mcp_setup_schema(TASKTOPUS_MCPS))

TASKTOPUS_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    TASKTOPUS_ROOTDIR,
    allowlist=["flexus_policy_document", "slack"],
    builtin_skills=[],
)

TOOLS = [
    fakefibery_fakemcp.FAKEFIBERY_TOOL,
    *[t for rec in TASKTOPUS_INTEGRATIONS for t in rec.integr_tools],
    *fi_mcp.mcp_tools(TASKTOPUS_MCPS),
]


async def tasktopus_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(TASKTOPUS_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(TASKTOPUS_INTEGRATIONS, rcx, setup)
    sl: Optional[fi_slack.IntegrationSlack] = integr_objects.get("slack")
    if sl is not None:
        sl.accept_outside_messages_only_to_expert("one_on_one_messenger")
    await fi_mcp.mcp_launch(TASKTOPUS_MCPS, rcx, setup)

    fb = fakefibery_situation1.build()

    @rcx.on_tool_call(fakefibery_fakemcp.FAKEFIBERY_TOOL.name)
    async def toolcall_fakefibery(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        args = model_produced_args or {}
        return fb.handle(args.get("op", "list"), args.get("name", ""), args.get("args", {}))

    @rcx.on_updated_task
    async def updated_task_in_db(action: str, old_task: Optional[ckit_kanban.FPersonaKanbanTaskOutput], new_task: Optional[ckit_kanban.FPersonaKanbanTaskOutput]):
        logger.info("task %s: %s", action, new_task)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.tasktopus import tasktopus_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(__file__)
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, bot_version), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=tasktopus_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=tasktopus_install.install,
    ))


if __name__ == "__main__":
    main()
