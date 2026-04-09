import asyncio
import json
import logging
from pathlib import Path

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit import ckit_bot_version

logger = logging.getLogger("clerk")

CLERKWING_ROOTDIR = Path(__file__).parent
CLERKWING_SKILLS = ckit_skills.static_skills_find(CLERKWING_ROOTDIR, shared_skills_allowlist="", integration_skills_allowlist="")
CLERKWING_SETUP_SCHEMA = json.loads((CLERKWING_ROOTDIR / "setup_schema.json").read_text())

CLERKWING_INTEGRATIONS = ckit_integrations_db.static_integrations_load(
    CLERKWING_ROOTDIR,
    allowlist=[
        "gmail",
        "google_calendar",
        "jira",
    ],
    builtin_skills=CLERKWING_SKILLS,
)

TOOLS = [*[t for rec in CLERKWING_INTEGRATIONS for t in rec.integr_tools]]


async def clerkwing_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(CLERKWING_SETUP_SCHEMA, rcx.persona.persona_setup)
    await ckit_integrations_db.main_loop_integrations_init(CLERKWING_INTEGRATIONS, rcx, setup)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.clerkwing import clerkwing_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(__file__)
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(ckit_bot_version.bot_name_from_file(__file__), bot_version), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=clerkwing_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=clerkwing_install.install,
    ))


if __name__ == "__main__":
    main()
