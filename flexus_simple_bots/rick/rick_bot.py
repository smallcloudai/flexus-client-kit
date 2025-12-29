import asyncio
import logging
from typing import Dict, Any

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_mongo
from flexus_client_kit.integrations import fi_gmail
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_erp
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_crm_automations
from flexus_client_kit.integrations import fi_telegram, fi_whatsapp
from flexus_simple_bots.rick import rick_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_rick")


BOT_NAME = "rick"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


ERP_TABLES = ["crm_task", "crm_contact"]


TOOLS = [
    fi_gmail.GMAIL_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_erp.ERP_TABLE_META_TOOL,
    fi_erp.ERP_TABLE_DATA_TOOL,
    fi_erp.ERP_TABLE_CRUD_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_crm_automations.CRM_AUTOMATION_TOOL,
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
    telegram_integration = fi_telegram.IntegrationTelegram(
        fclient,
        rcx,
    )
    whatsapp_integration = fi_whatsapp.IntegrationWhatsApp(
        fclient,
        rcx
    )

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        await telegram_integration.look_assistant_might_have_posted_something(msg)
        await whatsapp_integration.look_assistant_might_have_posted_something(msg)

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

    @rcx.on_tool_call(fi_crm_automations.CRM_AUTOMATION_TOOL.name)
    async def toolcall_crm_automation(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await automations_integration.handle_crm_automation(toolcall, model_produced_args)

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
        bot_main_loop=rick_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=rick_install.install,
        subscribe_to_erp_tables=ERP_TABLES,
    ))


if __name__ == "__main__":
    main()
