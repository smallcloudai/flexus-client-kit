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
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_linkedin
from flexus_client_kit.integrations import fi_facebook
from flexus_simple_bots.admonster import admonster_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_admonster")

LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")


BOT_NAME = "admonster"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)

ACCENT_COLOR = "#0077B5"


TOOLS = [
    fi_linkedin.LINKEDIN_TOOL,
    fi_facebook.FACEBOOK_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
]


async def admonster_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(admonster_install.admonster_setup_schema, rcx.persona.persona_setup)

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    personal_mongo = mydb["personal_mongo"]

    ad_account_id = setup.get("ad_account_id", "")
    fb_ad_account_id = setup.get("facebook_ad_account_id", "")

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
            logger.warning("Failed to initialize LinkedIn integration: %s", e)  # Bot init issue, not infra

    facebook_integration = None
    if rcx.running_test_scenario:
        try:
            facebook_integration = fi_facebook.IntegrationFacebook(
                fclient=fclient,
                rcx=rcx,
                ad_account_id=fb_ad_account_id,
            )
            logger.info("Facebook integration initialized for %s (test mode)", rcx.persona.persona_id)
        except Exception as e:
            logger.warning("Failed to initialize Facebook integration: %s", e, exc_info=e)  # Bot init issue
    else:
        try:
            facebook_integration = fi_facebook.IntegrationFacebook(
                fclient=fclient,
                rcx=rcx,
                ad_account_id=fb_ad_account_id,
            )
            logger.info("Facebook integration initialized for %s", rcx.persona.persona_id)
        except Exception as e:
            logger.warning("Failed to initialize Facebook integration: %s", e, exc_info=e)  # Bot init issue

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

    @rcx.on_tool_call(fi_facebook.FACEBOOK_TOOL.name)
    async def toolcall_facebook(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not facebook_integration:
            return "ERROR: Facebook integration not configured.\n"
        
        try:
            op = model_produced_args.get("op", "")
            
            if op.startswith("list_ad_accounts") or op.startswith("get_ad_account") or op.startswith("update_spending"):
                from flexus_simple_bots.admonster.integrations import fb_ad_account
                return await fb_ad_account.handle(facebook_integration, toolcall, model_produced_args)
            
            elif op.startswith("update_campaign") or op.startswith("duplicate_campaign") or op.startswith("archive_campaign") or op.startswith("bulk_update"):
                from flexus_simple_bots.admonster.integrations import fb_campaign
                return await fb_campaign.handle(facebook_integration, toolcall, model_produced_args)
            
            elif op.startswith("create_adset") or op.startswith("list_adsets") or op.startswith("update_adset") or op.startswith("validate_targeting"):
                from flexus_simple_bots.admonster.integrations import fb_adset
                return await fb_adset.handle(facebook_integration, toolcall, model_produced_args)
            
            elif op.startswith("upload_image") or op.startswith("create_creative") or op.startswith("create_ad") or op.startswith("preview_ad"):
                from flexus_simple_bots.admonster.integrations import fb_creative
                return await fb_creative.handle(facebook_integration, toolcall, model_produced_args)
            
            else:
                return await facebook_integration.called_by_model(toolcall, model_produced_args)
        
        except Exception as e:
            logger.warning(f"Facebook tool error: {e}", exc_info=e)  # Bot error, not infra
            return f"ERROR: {str(e)}"

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(
            rcx.workdir,
            personal_mongo,
            toolcall,
            model_produced_args,
        )

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    group, scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION_INT, group), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version=BOT_VERSION_INT,
        fgroup_id=group,
        bot_main_loop=admonster_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
    ))


if __name__ == "__main__":
    main()
