import asyncio
import logging
import os
import json
from typing import Dict, Any

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_guest_chat
from flexus_client_kit.integrations import fi_gmail
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_erp
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_crm_automations
from flexus_client_kit.integrations import fi_telegram
from flexus_simple_bots.rick import rick_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_rick")


BOT_NAME = "rick"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


ERP_TABLES = ["crm_task", "crm_contact"]


TELEGRAM_INVITE_TOOL = ckit_cloudtool.CloudTool(
    name="generate_telegram_invite",
    description="Generate a Telegram invitation link for the current contact to continue the conversation in Telegram. Call this when the user asks to switch to Telegram or requests a messenger link.",
    parameters={
        "type": "object",
        "properties": {
            "contact_id": {
                "type": "string",
                "description": "The CRM contact ID for this user (from ERP contact record)"
            },
        },
        "required": ["contact_id"],
    }
)

GUEST_CHAT_INVITE_TOOL = ckit_cloudtool.CloudTool(
    name="generate_guest_url",
    description="Generate a guest chat invitation link for the current contact to continue the conversation as a guest user. Call this when you want to provide a web chat link for the customer to join as a guest if you are asked to send an outreach email to the user.",
    parameters={
        "type": "object",
        "properties": {
            "contact_id": {
                "type": "string",
                "description": "The CRM contact ID for this user (from ERP contact record)"
            },
        },
        "required": ["contact_id"],
    }
)

TOOLS = [
    fi_gmail.GMAIL_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_erp.ERP_TABLE_META_TOOL,
    fi_erp.ERP_TABLE_DATA_TOOL,
    fi_erp.ERP_TABLE_CRUD_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_crm_automations.CRM_AUTOMATION_TOOL,
    TELEGRAM_INVITE_TOOL,
    GUEST_CHAT_INVITE_TOOL,
]


async def rick_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    dbname = f"{rcx.persona.ws_id}__{rcx.persona.persona_id}"
    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    mydb = mongo[dbname]
    mongo_collection = mydb["personal_mongo"]

    gmail_integration = fi_gmail.IntegrationGmail(fclient, rcx)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
    erp_integration = fi_erp.IntegrationErp(fclient, rcx.persona.ws_id, mongo_collection)

    def get_setup():
        return ckit_bot_exec.official_setup_mixing_procedure(rick_install.rick_setup_schema, rcx.persona.persona_setup)

    automations_integration = fi_crm_automations.IntegrationCrmAutomations(
        fclient, rcx, get_setup, available_erp_tables=ERP_TABLES,
    )

    telegram_bot_token = os.getenv("RICK_TELEGRAM_BOT_TOKEN", None)
    telegram_bot_username = os.getenv("RICK_TELEGRAM_BOT_USERNAME", "flexus_rick_bot")
    telegram_integration = None

    if telegram_bot_token:
        telegram_integration = fi_telegram.IntegrationTelegram(
            fclient=fclient,
            rcx=rcx,
            telegram_bot_token=telegram_bot_token,
            bot_username=telegram_bot_username,
            enable_summarization=True,
            message_limit_threshold=80,
            budget_limit_threshold=0.8,
        )
        await telegram_integration.start_reactive()
        logger.info("Telegram integration enabled for Rick persona %s", rcx.persona.persona_id)
    else:
        logger.warning("Telegram integration disabled (no RICK_TELEGRAM_BOT_TOKEN)")

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        if telegram_integration:
            await telegram_integration.look_assistant_might_have_posted_something(msg)

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    @rcx.on_tool_call(fi_gmail.GMAIL_TOOL.name)
    async def toolcall_gmail(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await gmail_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_erp.ERP_TABLE_META_TOOL.name)
    async def toolcall_erp_meta(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await erp_integration.handle_erp_meta(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_erp.ERP_TABLE_DATA_TOOL.name)
    async def toolcall_erp_data(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await erp_integration.handle_erp_data(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_erp.ERP_TABLE_CRUD_TOOL.name)
    async def toolcall_erp_crud(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await erp_integration.handle_erp_crud(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(rcx.workdir, mongo_collection, toolcall, model_produced_args)

    @rcx.on_tool_call(TELEGRAM_INVITE_TOOL.name)
    async def toolcall_telegram_invite(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if not telegram_integration:
            return "Telegram integration is not enabled for this bot. Please contact your administrator to set up RICK_TELEGRAM_BOT_TOKEN."

        # Try both direct access and nested "args" key
        contact_id = ckit_cloudtool.try_best_to_find_argument(
            model_produced_args.get("args", {}),
            model_produced_args,
            "contact_id",
            ""
        )

        if not contact_id:
            return f"Error: contact_id is required to generate a Telegram invite. Received: {json.dumps(model_produced_args)}"

        import gql
        http_client = await fclient.use_http()
        async with http_client as http:
            result = await http.execute(
                gql.gql("""mutation GenerateTelegramInvite(
                    $platform: String!,
                    $ft_id: String!,
                    $contact_id: String!,
                    $ttl: Int!
                    $bot_username: String!
                ) {
                    generate_messenger_invite(
                        platform: $platform,
                        ft_id: $ft_id,
                        contact_id: $contact_id,
                        ttl: $ttl
                        bot_username: $bot_username
                    ) {
                        handle
                        link
                        expires_in
                        platform
                    }
                }"""),
                variable_values={
                    "platform": "telegram",
                    "ft_id": toolcall.fcall_ft_id,
                    "contact_id": contact_id,
                    "ttl": 600,
                    "bot_username": telegram_bot_username,
                },
            )

        invite = result["generate_messenger_invite"]

        return f"""Great! Here's your Telegram invitation:

🔗 Click this link: {invite['link']}
🔑 Or search for @{telegram_bot_username} and enter code: {invite['handle']}

⏰ This invitation expires in {invite['expires_in'] // 60} minutes.

Once you're connected, our conversation will continue seamlessly on Telegram!"""
    
    @rcx.on_tool_call(GUEST_CHAT_INVITE_TOOL.name)
    async def toolcall_guest_chat_invite(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        contact_id = ckit_cloudtool.try_best_to_find_argument(
            model_produced_args.get("args", {}),
            model_produced_args,
            "contact_id",
            ""
        )

        if not contact_id:
            return f"Error: contact_id is required to generate a guest chat invite. Received: {json.dumps(model_produced_args)}"
    
        result = await ckit_guest_chat.create_guest_accessible_thread_with_crm_context(
            fclient,
            rcx.persona.persona_id,
            rcx.persona.ws_id,
            rcx.persona.located_fgroup_id,
            contact_id,
            platform="web",
            title="Guest Chat Invitation",
            additional_context=None,
            skill="default",
        )

        guest_url = result["guest_url"]

        return f"Great! Here's your guest URL:\n\n🔗 {guest_url}"

    @rcx.on_tool_call(fi_crm_automations.CRM_AUTOMATION_TOOL.name)
    async def toolcall_crm_automation(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await automations_integration.handle_crm_automation(toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        if telegram_integration:
            await telegram_integration.close()
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=rick_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=rick_install.install,
        subscribe_to_erp_tables=ERP_TABLES,
    ))


if __name__ == "__main__":
    main()
