import asyncio
import json
import logging
import time
from collections import deque
from typing import Dict, Any, Optional

from pymongo import AsyncMongoClient

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_erp
from flexus_client_kit import ckit_mongo
from flexus_client_kit import erp_schema
from flexus_client_kit.integrations import fi_gmail
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_erp
from flexus_client_kit.integrations import fi_mongo_store
from flexus_simple_bots.rick import rick_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_rick")


BOT_NAME = "rick"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


TOOLS = [
    fi_gmail.GMAIL_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
    fi_erp.ERP_TABLE_META_TOOL,
    fi_erp.ERP_TABLE_DATA_TOOL,
    fi_erp.ERP_TABLE_CRUD_TOOL,
    fi_mongo_store.MONGO_STORE_TOOL,
]


async def rick_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(rick_install.rick_setup_schema, rcx.persona.persona_setup)

    dbname = f"{rcx.persona.ws_id}__{rcx.persona.persona_id}"
    mongo_conn_str = await ckit_mongo.mongo_fetch_creds(fclient, rcx.persona.persona_id)
    mongo = AsyncMongoClient(mongo_conn_str)
    mydb = mongo[dbname]
    mongo_collection = mydb["personal_mongo"]

    gmail_integration = fi_gmail.IntegrationGmail(fclient, rcx)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)
    erp_integration = fi_erp.IntegrationErp(fclient, rcx.persona.ws_id, mongo_collection)

    recent_tasks: Dict[str, erp_schema.CrmTask] = {}

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    @rcx.on_erp_change("crm_task")
    async def on_task_change(action: str, new_record: Optional[erp_schema.CrmTask], old_record: Optional[erp_schema.CrmTask]):
        if action == "DELETE" and old_record:
            recent_tasks.pop(old_record.task_id, None)
        elif action in ["INSERT", "UPDATE"] and new_record:
            if old_record:
                recent_tasks.pop(old_record.task_id, None)
            recent_tasks[new_record.task_id] = new_record
            if len(recent_tasks) > 100:
                del recent_tasks[next(iter(recent_tasks))]
            logger.info("CRM task cached: task_id=%s contact_id=%s type=%s", new_record.task_id, new_record.contact_id, new_record.task_type)

    @rcx.on_erp_change("crm_contact")
    async def on_contact_change(action: str, new_record: Optional[erp_schema.CrmContact], old_record: Optional[erp_schema.CrmContact]):
        if action in ["INSERT", "UPDATE"]:
            logger.info("CRM contact %s: id=%s email=%s", action, new_record.contact_id, new_record.contact_email)
            if not setup["auto_welcome_email"]:
                return

            if any(t.contact_id == new_record.contact_id and t.task_type == "email" and t.task_details.get("email_subtype") == "welcome" for t in recent_tasks.values()):
                return

            existing = await ckit_erp.query_erp_table(
                fclient, "crm_task", rcx.persona.ws_id, erp_schema.CrmTask, limit=1,
                filters=[f"contact_id:=:{new_record.contact_id}", "task_type:=:email", "task_details->email_subtype:=:welcome"],
            )
            if existing:
                return

            task_title = f"Welcome email: {new_record.contact_first_name} {new_record.contact_last_name}"
            task_description = (
                f"Send a personalized welcome email to {new_record.contact_first_name} {new_record.contact_last_name} ({new_record.contact_email}) following the template and company strategy."
                f"After email is sent, mark the crm task with title \"{task_title}\" as completed."
            )
            task_details = {
                "email_subtype": "welcome",
                "contact_id": new_record.contact_id,
                "description": task_description,
            }
            if new_record.contact_address_city or new_record.contact_address_state:
                task_details["location"] = f"{new_record.contact_address_city}, {new_record.contact_address_state}".strip(", ")
            if new_record.contact_utm_first_source:
                task_details["source"] = new_record.contact_utm_first_source
            await ckit_kanban.bot_kanban_post_into_inbox(
                fclient, rcx.persona.persona_id,
                title=task_title,
                details_json=json.dumps(task_details),
                provenance_message=f"CRM contact {action.lower()}",
            )
            await ckit_erp.create_erp_record(
                fclient, "crm_task", rcx.persona.ws_id,
                erp_schema.CrmTask(
                    ws_id=rcx.persona.ws_id, contact_id=new_record.contact_id, task_type="email",
                    task_title=task_title,
                    task_details=task_details,
                ),
            )

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
        subscribe_to_erp_tables=["crm_contact", "crm_task"],
    ))


if __name__ == "__main__":
    main()
