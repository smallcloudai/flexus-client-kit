import asyncio
import json
import logging
import time
from dataclasses import asdict
from typing import Dict, Any

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_mongo
from flexus_client_kit import ckit_erp
from flexus_client_kit import ckit_kanban
from flexus_client_kit import erp_schema
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_erp
from flexus_client_kit.integrations import fi_crm_automations
from flexus_client_kit.integrations import fi_resend
from flexus_client_kit.integrations import fi_telegram
from flexus_simple_bots.vix import vix_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_vix")

BOT_NAME = "vix"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

ERP_TABLES = ["crm_contact", "crm_activity", "crm_deal"]

TOOLS = [
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_erp.ERP_TABLE_META_TOOL,
    fi_erp.ERP_TABLE_DATA_TOOL,
    fi_erp.ERP_TABLE_CRUD_TOOL,
    fi_erp.ERP_CSV_IMPORT_TOOL,
    fi_crm_automations.CRM_AUTOMATION_TOOL,
    fi_resend.RESEND_TOOL,
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
    automations_integration = fi_crm_automations.IntegrationCrmAutomations(
        fclient, rcx, get_setup, available_erp_tables=ERP_TABLES,
    )
    resend_domains = json.loads(get_setup().get("DOMAINS", "{}"))
    email_respond_to = set(a.strip().lower() for a in get_setup().get("EMAIL_RESPOND_TO", "").split(",") if a.strip())
    resend_integration = fi_resend.IntegrationResend(fclient, rcx, resend_domains, email_respond_to)
    email_reg = [f"*@{d}" for d in resend_domains] + list(email_respond_to)
    if email_reg:
        await fi_resend.register_email_addresses(fclient, rcx, email_reg)
    telegram = fi_telegram.IntegrationTelegram(fclient, rcx)
    await telegram.register_webhook_and_start()

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        await telegram.look_assistant_might_have_posted_something(msg)

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    @rcx.on_emessage("EMAIL")
    async def handle_email(emsg):
        email = fi_resend.parse_emessage(emsg)
        body = email.body_text or email.body_html or "(empty)"
        try:
            contacts = await ckit_erp.query_erp_table(
                fclient, "crm_contact", rcx.persona.ws_id, erp_schema.CrmContact,
                filters=f"contact_email:ILIKE:{email.from_addr}", limit=1,
            )
            if contacts:
                await ckit_erp.create_erp_record(fclient, "crm_activity", rcx.persona.ws_id, {
                    "ws_id": rcx.persona.ws_id,
                    "activity_title": email.subject,
                    "activity_type": "EMAIL",
                    "activity_direction": "INBOUND",
                    "activity_platform": "RESEND",
                    "activity_contact_id": contacts[0].contact_id,
                    "activity_summary": body[:500],
                    "activity_occurred_ts": time.time(),
                })
        except Exception as e:
            logger.warning("Failed to create CRM activity for inbound email from %s: %s", email.from_addr, e)
        if not email_respond_to.intersection(a.lower() for a in email.to_addrs):
            return
        title = "Email from %s: %s" % (email.from_addr, email.subject)
        if email.cc_addrs:
            title += " (cc: %s)" % ", ".join(email.cc_addrs)
        await ckit_kanban.bot_kanban_post_into_inbox(
            fclient, rcx.persona.persona_id,
            title=title, details_json=json.dumps({"from": email.from_addr, "to": email.to_addrs, "cc": email.cc_addrs, "subject": email.subject, "body": body[:2000]}),
            provenance_message="vix_email_inbound",
        )

    @rcx.on_emessage("TELEGRAM")
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

    @rcx.on_tool_call(fi_resend.RESEND_TOOL.name)
    async def toolcall_resend(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await resend_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_crm_automations.CRM_AUTOMATION_TOOL.name)
    async def toolcall_crm_automation(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await automations_integration.handle_crm_automation(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_telegram.TELEGRAM_TOOL.name)
    async def toolcall_telegram(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await telegram.called_by_model(toolcall, model_produced_args)

    @telegram.on_incoming_activity
    async def telegram_activity_callback(a: fi_telegram.ActivityTelegram, already_posted: bool):
        logger.info("%s Telegram %s by @%s: %s", rcx.persona.persona_id, a.chat_type, a.message_author_name, a.message_text[:50])
        if already_posted:
            return
        details = asdict(a)
        if a.attachments:
            details["attachments"] = f"{len(a.attachments)} files attached"
        if a.message_text.startswith("/start c_"): # Handle /start c_{contact_id} deep links (e.g. from email campaigns)
            contact_id = a.message_text[9:].strip()
            details["contact_id"] = contact_id
            title = "CRM contact opened Telegram chat, contact_id=%s chat_id=%d" % (contact_id, a.chat_id)
        else:
            title = "Telegram %s user=%r chat_id=%d\n%s" % (a.chat_type, a.message_author_name, a.chat_id, a.message_text)
            if a.attachments:
                title += f"\n[{len(a.attachments)} file(s) attached]"
        await ckit_kanban.bot_kanban_post_into_inbox(
            fclient, rcx.persona.persona_id,
            title=title,
            details_json=json.dumps(details),
            provenance_message="vix_telegram_activity",
            fexp_name="sales",
        )

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
    ))


if __name__ == "__main__":
    main()
