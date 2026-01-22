import asyncio
import json
import logging
from dataclasses import asdict
from typing import Dict, Any

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_kanban
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_erp
from flexus_client_kit.integrations import fi_gmail
from flexus_client_kit.integrations import fi_crm_automations
from flexus_client_kit.integrations import fi_telegram
from flexus_simple_bots.vix import vix_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_vix")

BOT_NAME = "vix"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

ERP_TABLES = ["crm_contact"]

TOOLS = [
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_erp.ERP_TABLE_META_TOOL,
    fi_erp.ERP_TABLE_DATA_TOOL,
    fi_erp.ERP_TABLE_CRUD_TOOL,
    fi_erp.ERP_CSV_IMPORT_TOOL,
    fi_gmail.GMAIL_TOOL,
    fi_crm_automations.CRM_AUTOMATION_TOOL,
    fi_telegram.TELEGRAM_TOOL,
]


async def vix_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    def get_setup():
        return ckit_bot_exec.official_setup_mixing_procedure(vix_install.vix_setup_schema, rcx.persona.persona_setup)

    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    dbname = rcx.persona.persona_id + "_db"
    mydb = mongo[dbname]
    personal_mongo = mydb["personal_mongo"]

    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
    erp_integration = fi_erp.IntegrationErp(fclient, rcx.persona.ws_id, personal_mongo)
    gmail_integration = fi_gmail.IntegrationGmail(fclient, rcx)
    automations_integration = fi_crm_automations.IntegrationCrmAutomations(
        fclient, rcx, get_setup, available_erp_tables=ERP_TABLES,
    )
    telegram = await fi_telegram.IntegrationTelegram.create(fclient, rcx, get_setup().get("TELEGRAM_BOT_TOKEN", ""))

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        await telegram.look_assistant_might_have_posted_something(msg)

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    @rcx.on_emessage("telegram")
    async def handle_telegram_emessage(emsg):
        await telegram.handle_emessage(emsg)

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(
            rcx.workdir,
            personal_mongo,
            toolcall,
            model_produced_args,
        )

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

    @rcx.on_tool_call(fi_erp.ERP_CSV_IMPORT_TOOL.name)
    async def toolcall_erp_csv_import(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await erp_integration.handle_csv_import(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_gmail.GMAIL_TOOL.name)
    async def toolcall_gmail(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await gmail_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_crm_automations.CRM_AUTOMATION_TOOL.name)
    async def toolcall_crm_automation(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await automations_integration.handle_crm_automation(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_telegram.TELEGRAM_TOOL.name)
    async def toolcall_telegram(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await telegram.called_by_model(toolcall, model_produced_args)

    async def telegram_activity_callback(a: fi_telegram.ActivityTelegram, already_posted: bool):
        logger.info("%s Telegram %s by @%s: %s", rcx.persona.persona_id, a.chat_type, a.message_author_name, a.message_text[:50])
        if not already_posted:
            title = "Telegram %s user=%r chat_id=%d\n%s" % (a.chat_type, a.message_author_name, a.chat_id, a.message_text)
            if a.attachments:
                title += f"\n[{len(a.attachments)} file(s) attached]"
            details = asdict(a)
            if a.attachments:
                details["attachments"] = f"{len(a.attachments)} files attached"
            await ckit_kanban.bot_kanban_post_into_inbox(
                fclient, rcx.persona.persona_id,
                title=title,
                details_json=json.dumps(details),
                provenance_message="vix_telegram_activity",
                fexp_name="sales",
            )

    telegram.set_activity_callback(telegram_activity_callback)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        await telegram.close()
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=vix_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=vix_install.install,
        subscribe_to_erp_tables=ERP_TABLES,
        subscribe_to_emessage_channels=["telegram"],
    ))


if __name__ == "__main__":
    main()
