import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit.integrations import fi_repo_reader
from flexus_client_kit.integrations import fi_discord2
from flexus_client_kit.integrations import fi_mcp
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_karen")


BOT_NAME = "karen"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

KAREN_ROOTDIR = Path(__file__).parent
KAREN_SKILLS = ckit_skills.static_skills_find(KAREN_ROOTDIR, shared_skills_allowlist="setting-up-external-knowledge-base")
KAREN_MCPS = []
KAREN_SETUP_SCHEMA = json.loads((KAREN_ROOTDIR / "setup_schema.json").read_text())
KAREN_SETUP_SCHEMA += fi_discord2.DISCORD_SETUP_SCHEMA
KAREN_SETUP_SCHEMA.extend(fi_mcp.mcp_setup_schema(KAREN_MCPS))

KAREN_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    KAREN_ROOTDIR,
    allowlist=[
        "flexus_policy_document",
        "print_widget",
        "slack",
        "telegram",
        "discord",
        "skills",
        "magic_desk",
    ],
    builtin_skills=KAREN_SKILLS,
)

TOOLS = [
    fi_repo_reader.REPO_READER_TOOL,
    *[t for rec in KAREN_INTEGRATIONS for t in rec.integr_tools],
]

async def karen_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(KAREN_SETUP_SCHEMA, rcx.persona.persona_setup)
    integrations = await ckit_integrations_db.main_loop_integrations_init(KAREN_INTEGRATIONS, rcx, setup)

    # SAFETY
    # What we are trying to prevent: an outside user via slack/telegram/etc having access to any tools that leak information
    # about the company, or do any actions like sending A2A to Boss, that would be really silly.
    # How: expert 'very_limited' only has allowlist of tools, all messengers informed about the destination expert that they
    # are allowed to post the outside messages to.
    for me in rcx.messengers:
        me.accept_outside_messages_only_to_expert("very_limited")

    @rcx.on_tool_call(fi_repo_reader.REPO_READER_TOOL.name)
    async def toolcall_repo_reader(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_repo_reader.handle_repo_reader(rcx, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        await integrations["discord"].close()
        await integrations["telegram"].close()
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.karen import karen_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=karen_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=karen_install.install,
    ))


if __name__ == "__main__":
    main()
