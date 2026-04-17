import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_erp
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit import erp_schema
from flexus_client_kit import ckit_bot_version
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_crm_automations
from flexus_client_kit.integrations import fi_resend
from flexus_client_kit.integrations import fi_shopify
from flexus_client_kit.integrations import fi_telegram
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit.integrations import fi_crm
from flexus_client_kit.integrations import fi_sched
from flexus_client_kit.integrations import fi_thread
from flexus_client_kit import ckit_scenario
from flexus_client_kit.integrations import fi_discord2
import gql.transport.exceptions

logger = logging.getLogger("bot_sales")

SALES_ROOTDIR = Path(__file__).parent
SALES_SKILLS = ckit_skills.static_skills_find(SALES_ROOTDIR, shared_skills_allowlist="*", integration_skills_allowlist="*")

SALES_SETUP_SCHEMA = json.loads((SALES_ROOTDIR / "setup_schema.json").read_text())
SALES_SETUP_SCHEMA += (
    fi_shopify.SHOPIFY_SETUP_SCHEMA
    + fi_crm_automations.CRM_AUTOMATIONS_SETUP_SCHEMA
    + fi_crm.CRM_SETUP_SCHEMA
    + fi_resend.RESEND_SETUP_SCHEMA
    + fi_slack.SLACK_SETUP_SCHEMA
    + fi_discord2.DISCORD_SETUP_SCHEMA
)

ERP_TABLES = ["crm_contact", "crm_activity", "crm_deal", "com_shop", "com_product", "com_product_variant"]

SALES_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    SALES_ROOTDIR,
    allowlist=[
        "skills",
        "flexus_policy_document",
        "print_widget",
        "erp[meta, data, crud, csv_import]",
        "crm[contact_info, manage_deal, verify_email]",
        "magic_desk",
        "slack",
        "telegram",
        "discord",
        "resend",
    ],
    builtin_skills=SALES_SKILLS,
)

TOOLS = [
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_crm_automations.CRM_AUTOMATION_TOOL,
    fi_shopify.SHOPIFY_TOOL,
    fi_shopify.SHOPIFY_CART_TOOL,
    fi_sched.SCHED_TOOL,
    fi_thread.THREAD_READ_TOOL,
    *[t for rec in SALES_INTEGRATIONS for t in rec.integr_tools],
]


async def sales_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(SALES_SETUP_SCHEMA, rcx.persona.persona_setup)

    integrations = await ckit_integrations_db.main_loop_integrations_init(SALES_INTEGRATIONS, rcx, setup)
    automations_integration = fi_crm_automations.IntegrationCrmAutomations(
        fclient, rcx, setup, available_erp_tables=ERP_TABLES,
    )
    shopify = fi_shopify.IntegrationShopify(fclient, rcx)
    sched = fi_sched.IntegrationSched(rcx)
    slack: fi_slack.IntegrationSlack = integrations["slack"]
    telegram: fi_telegram.IntegrationTelegram = integrations["telegram"]

    for me in rcx.messengers:
        me.accept_outside_messages_only_to_expert("very_limited")

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(rcx, toolcall, model_produced_args)

    @rcx.on_tool_call(fi_crm_automations.CRM_AUTOMATION_TOOL.name)
    async def toolcall_crm_automation(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await automations_integration.handle_crm_automation(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_shopify.SHOPIFY_TOOL.name)
    async def toolcall_shopify(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await shopify.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_shopify.SHOPIFY_CART_TOOL.name)
    async def toolcall_shopify_cart(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await shopify.handle_cart(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_sched.SCHED_TOOL.name)
    async def toolcall_sched(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await sched.called_by_model(toolcall, model_produced_args)

    @rcx.on_tool_call(fi_thread.THREAD_READ_TOOL.name)
    async def toolcall_thread_read(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_thread.handle_thread_read(rcx, toolcall, model_produced_args)

    @rcx.on_updated_task
    async def on_task_update(action: str, old_task: Optional[ckit_kanban.FPersonaKanbanTaskOutput], new_task: Optional[ckit_kanban.FPersonaKanbanTaskOutput]):
        if action == "DELETE":
            return
        if new_task.ktask_done_ts > 0 and old_task and old_task.ktask_done_ts == 0 and \
            new_task.ktask_human_id and new_task.ktask_fexp_name == "very_limited":
                await ckit_kanban.bot_kanban_post_into_inbox(
                    await fclient.use_http_on_behalf(rcx.persona.persona_id, ""),
                    rcx.persona.persona_id,
                    title="Read linked thread, find/create contact, log activity, score BANT: %s" % new_task.ktask_title[:60],
                    details_json=json.dumps({
                        "spawned_from_ktask_id": new_task.ktask_id,
                        "spawned_from_title": new_task.ktask_title,
                        "from_thread_id": new_task.ktask_inprogress_ft_id,
                        "human_id": new_task.ktask_human_id,
                    }),
                    provenance_message="sales_post_conversation",
                    fexp_name="post_conversation",
                )

    @telegram.on_incoming_activity
    async def telegram_activity_callback(a: fi_telegram.ActivityTelegram, already_posted: bool):
        if already_posted:
            return
        extra = {}
        http = await fclient.use_http_on_behalf(rcx.persona.persona_id, "")
        if contact_id := await fi_crm.find_contact_by_platform_id(http, rcx.persona.ws_id, "telegram", str(a.chat_id)):
            extra["contact_id"] = contact_id
        await telegram.inbound_activity_to_task(a, already_posted=False, extra_details=extra, provenance="sales_telegram_activity")

    @slack.on_incoming_activity
    async def slack_activity_callback(a: fi_slack.ActivitySlack, already_posted: bool):
        if already_posted:
            return
        extra = {}
        if a.message_author_id:
            if contact_id := await fi_crm.find_contact_by_platform_id(await fclient.use_http_on_behalf(rcx.persona.persona_id, ""), rcx.persona.ws_id, "slack", a.message_author_id):
                extra["contact_id"] = contact_id
        await slack.inbound_activity_to_task(a, already_posted_to_captured_thread=False, extra_details=extra, provenance="sales_slack_activity")

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.sales import sales_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(__file__)
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(ckit_bot_version.bot_name_from_file(__file__), bot_version), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=sales_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=sales_install.install,
        subscribe_to_erp_tables=ERP_TABLES,
    ))


if __name__ == "__main__":
    main()
