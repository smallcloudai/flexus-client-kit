import asyncio
import json
import logging
import time
from collections import deque
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_erp
from flexus_client_kit import erp_schema
from flexus_client_kit.integrations import fi_gmail
from flexus_client_kit.integrations import fi_pdoc
from flexus_simple_bots.rick import rick_install
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_rick")


BOT_NAME = "rick"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION
BOT_VERSION_INT = ckit_client.marketplace_version_as_int(BOT_VERSION)


TOOLS = [
    fi_gmail.GMAIL_TOOL,
    fi_pdoc.POLICY_DOCUMENT_TOOL,
]


async def rick_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(rick_install.rick_setup_schema, rcx.persona.persona_setup)

    gmail_integration = fi_gmail.IntegrationGmail(fclient, rcx)
    pdoc_integration = fi_pdoc.IntegrationPdoc(rcx, rcx.persona.ws_root_group_id)

    recent_tasks = deque(maxlen=100)

    @rcx.on_updated_message
    async def updated_message_in_db(msg: ckit_ask_model.FThreadMessageOutput):
        pass

    @rcx.on_updated_thread
    async def updated_thread_in_db(th: ckit_ask_model.FThreadOutput):
        pass

    @rcx.on_updated_task
    async def updated_task_in_db(t: ckit_kanban.FPersonaKanbanTaskOutput):
        pass

    @rcx.on_updated_erp_record("crm_task")
    async def updated_crm_task(task: erp_schema.CrmTask):
        recent_tasks.append(task)
        logger.info("CRM task added to recent queue: task_id=%s contact_id=%s type=%s", task.task_id, task.contact_id, task.task_type)

    @rcx.on_updated_erp_record("crm_contact")
    async def updated_crm_contact(contact: erp_schema.CrmContact):
        logger.info("New CRM contact: id=%s email=%s name=%s %s", contact.contact_id, contact.contact_email, contact.contact_first_name, contact.contact_last_name)
        if not setup.get("auto_welcome_email", True):
            logger.info("Auto welcome email disabled, skipping")
            return

        has_welcome_task_in_recent = any(
            t.contact_id == contact.contact_id and
            t.task_type == "email" and
            t.task_details.get("email_subtype") == "welcome"
            for t in recent_tasks
        )
        if has_welcome_task_in_recent:
            logger.info("Welcome email task already exists in recent tasks for contact_id=%s", contact.contact_id)
            return

        try:
            existing_tasks = await ckit_erp.query_erp_table(
                fclient,
                "crm_task",
                rcx.persona.ws_id,
                erp_schema.CrmTask,
                limit=100,
                filters=[
                    f"contact_id:=:{contact.contact_id}",
                    "task_type:=:email",
                    "task_details->email_subtype:=:welcome",
                ],
            )
            if existing_tasks:
                logger.info("Welcome email task already exists in ERP for contact_id=%s", contact.contact_id)
                return
        except Exception as e:
            logger.error("Error querying ERP for existing tasks: %s", e, exc_info=e)
            return

        try:
            task_details = {
                "email_subtype": "welcome",
                "contact_id": contact.contact_id,
                "contact_email": contact.contact_email,
                "contact_first_name": contact.contact_first_name,
                "contact_last_name": contact.contact_last_name,
                "description": f"Send welcome email to {contact.contact_first_name} {contact.contact_last_name} ({contact.contact_email})",
            }
            await ckit_kanban.bot_kanban_post_into_inbox(
                fclient,
                rcx.persona.persona_id,
                title=f"Welcome email: {contact.contact_first_name} {contact.contact_last_name}",
                details_json=json.dumps(task_details),
                provenance_message=f"New CRM contact detected: {contact.contact_email}",
            )
            logger.info("Created kanban welcome email task for contact_id=%s", contact.contact_id)

            crm_task = erp_schema.CrmTask(
                ws_id=rcx.persona.ws_id,
                contact_id=contact.contact_id,
                task_type="email",
                task_title=f"Welcome email: {contact.contact_first_name} {contact.contact_last_name}",
                task_notes=f"Auto-generated welcome email task for {contact.contact_email}",
                task_details=task_details,
            )
            await ckit_erp.create_erp_record(
                fclient,
                "crm_task",
                rcx.persona.ws_id,
                crm_task,
            )
            logger.info("Created ERP crm_task record for contact_id=%s", contact.contact_id)
        except Exception as e:
            logger.error("Error creating welcome email task: %s", e, exc_info=e)

    @rcx.on_tool_call(fi_gmail.GMAIL_TOOL.name)
    async def toolcall_gmail(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await gmail_integration.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_pdoc.POLICY_DOCUMENT_TOOL.name)
    async def toolcall_pdoc(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await pdoc_integration.called_by_model(toolcall, model_produced_args)

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
        bot_main_loop=rick_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        subscribe_to_erp_tables=["crm_contact", "crm_task"],
    ))


if __name__ == "__main__":
    main()
