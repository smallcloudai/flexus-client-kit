"""
AdMonster Bot - Main Entry Point

WHAT: Advertising campaign manager bot for LinkedIn and Facebook/Meta platforms.
WHY: Automates ad management, A/B testing, analytics, and optimization.

ARCHITECTURE:
- Bot registers tool handlers for LinkedIn and Facebook APIs
- Facebook operations handled by flexus_client_kit.integrations.facebook package
- Uses MongoDB for persistent storage via fi_mongo_store
- OAuth tokens are fetched via external_auth_token GraphQL query (stored encrypted in DB)

EXECUTION FLOW:
1. main() parses args and creates FlexusClient
2. run_bots_in_this_group() starts bot instances for each persona in the group
3. admonster_main_loop() is the main loop for each bot instance
4. Tool calls from model are routed to appropriate handlers via @rcx.on_tool_call decorators
"""

import asyncio
import logging
import os
from typing import Dict, Any

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_mongo
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_linkedin
from flexus_client_kit.integrations.facebook import IntegrationFacebook, FACEBOOK_TOOL
from flexus_simple_bots.admonster import admonster_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_admonster")

# LinkedIn API credentials (optional - bot works without them for Facebook-only use)
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")


# Bot identity and versioning
BOT_NAME = "admonster"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

# UI accent color for marketplace display
ACCENT_COLOR = "#0077B5"


# Tools exposed to the AI model during chat
TOOLS = [
    fi_linkedin.LINKEDIN_TOOL,
    FACEBOOK_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
]


async def admonster_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    """
    Main loop for a single AdMonster bot instance.
    Called once per persona (bot instance) in the group.
    """
    setup = ckit_bot_exec.official_setup_mixing_procedure(admonster_install.admonster_setup_schema, rcx.persona.persona_setup)

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    mydb = mongo[rcx.persona.persona_id + "_db"]
    personal_mongo = mydb["personal_mongo"]

    # Platform-specific ad account IDs (no hidden defaults — fail-fast if not configured)
    ad_account_id = setup.get("ad_account_id", "")  # LinkedIn
    fb_ad_account_id = setup.get("facebook_ad_account_id", "")  # Facebook

    # Initialize LinkedIn integration
    linkedin_integration = None
    if (LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET) or rcx.running_test_scenario:
        try:
            linkedin_integration = fi_linkedin.IntegrationLinkedIn(
                fclient=fclient,
                rcx=rcx,
                app_id=LINKEDIN_CLIENT_ID,
                app_secret=LINKEDIN_CLIENT_SECRET,
                ad_account_id=ad_account_id,
            )
            logger.info("LinkedIn integration initialized for %s", rcx.persona.persona_id)
        except Exception as e:
            logger.warning("Failed to initialize LinkedIn integration: %s", e)

    # Initialize Facebook integration
    facebook_integration = None
    try:
        facebook_integration = IntegrationFacebook(
            fclient=fclient,
            rcx=rcx,
            ad_account_id=fb_ad_account_id,
        )
        logger.info("Facebook integration initialized for %s", rcx.persona.persona_id)
    except Exception as e:
        logger.warning("Failed to initialize Facebook integration: %s", e, exc_info=e)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_tool_call(fi_linkedin.LINKEDIN_TOOL.name)
    async def toolcall_linkedin(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not linkedin_integration:
            return "ERROR: LinkedIn integration not configured. Please set LINKEDIN_ACCESS_TOKEN in setup.\n"
        return await linkedin_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(FACEBOOK_TOOL.name)
    async def toolcall_facebook(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        """Handle facebook() tool calls via IntegrationFacebook."""
        if not facebook_integration:
            return "ERROR: Facebook integration not configured.\n"
        return await facebook_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(rcx.workdir, personal_mongo, toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group, scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION, group), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        fgroup_id=group,
        bot_main_loop=admonster_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=admonster_install.install,
    ))


if __name__ == "__main__":
    main()
