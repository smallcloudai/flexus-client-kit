import asyncio
import logging
import time
from typing import Dict, Any

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_linkedin
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations.facebook.fi_facebook import IntegrationFacebook, FACEBOOK_TOOL
from flexus_simple_bots.admonster import admonster_install
from flexus_simple_bots.admonster import experiment_execution
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_admonster")

BOT_NAME = "admonster"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)
ACCENT_COLOR = "#0077B5"

ADMONSTER_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.integrations_load(
    admonster_install.ADMONSTER_ROOTDIR,
    allowlist=[
        "flexus_policy_document",
    ],
    builtin_skills=admonster_install.ADMONSTER_SKILLS,
)

TOOLS = [
    fi_linkedin.LINKEDIN_TOOL,
    FACEBOOK_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    experiment_execution.LAUNCH_EXPERIMENT_TOOL,
    *[t for rec in ADMONSTER_INTEGRATIONS for t in rec.integr_tools],
]


async def admonster_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(admonster_install.ADMONSTER_SETUP_SCHEMA, rcx.persona.persona_setup)

    integr_objects = await ckit_integrations_db.integrations_init_all(ADMONSTER_INTEGRATIONS, rcx)
    pdoc_integration: fi_pdoc.IntegrationPdoc = integr_objects["flexus_policy_document"]

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    personal_mongo = mongo[rcx.persona.persona_id + "_db"]["personal_mongo"]

    linkedin_integration = fi_linkedin.IntegrationLinkedIn(
        fclient=fclient,
        rcx=rcx,
        ad_account_id=setup.get("ad_account_id", ""),
    )

    # Facebook integration -- ad_account_id read from /company/ad-ops-config at runtime
    facebook_integration = IntegrationFacebook(fclient=fclient, rcx=rcx, ad_account_id="", pdoc_integration=pdoc_integration)

    @rcx.on_tool_call(fi_linkedin.LINKEDIN_TOOL.name)
    async def toolcall_linkedin(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not linkedin_integration:
            return "ERROR: LinkedIn integration not configured. Please set LINKEDIN_ACCESS_TOKEN in setup.\n"
        return await linkedin_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(FACEBOOK_TOOL.name)
    async def toolcall_facebook(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not facebook_integration:
            return "ERROR: Facebook integration not configured.\n"
        return await facebook_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(rcx.workdir, personal_mongo, toolcall, model_produced_args)

    experiment_integration = experiment_execution.IntegrationExperimentExecution(
        pdoc_integration=pdoc_integration,
        fclient=fclient,
        facebook_integration=facebook_integration,
    )

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        experiment_integration.track_experiment_task(t)

    @rcx.on_tool_call(experiment_execution.LAUNCH_EXPERIMENT_TOOL.name)
    async def toolcall_launch_experiment(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await experiment_integration.launch_experiment(toolcall, model_produced_args)

    # Load existing tasks to track active experiments on startup
    initial_tasks = await ckit_kanban.bot_get_all_tasks(fclient, rcx.persona.persona_id)
    active_tasks = [t for t in initial_tasks if t.ktask_done_ts == 0]
    for t in active_tasks:
        experiment_integration.track_experiment_task(t)
    logger.info(f"Initialized experiment tracking for {len(experiment_integration.tracked_experiments)} active experiments")

    last_experiment_check = 0
    experiment_check_interval = 3600  # hourly

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

            current_time = time.time()
            if current_time - last_experiment_check > experiment_check_interval:
                await experiment_integration.update_active_experiments()
                last_experiment_check = current_time
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=admonster_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=admonster_install.install,
    ))


if __name__ == "__main__":
    main()
