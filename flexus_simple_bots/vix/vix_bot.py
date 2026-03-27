import asyncio
import email.utils
import json
import logging
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_erp
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit import erp_schema
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_crm_automations
from flexus_client_kit.integrations import fi_resend
from flexus_client_kit.integrations import fi_shopify
from flexus_client_kit.integrations import fi_telegram
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit.integrations import fi_crm
from flexus_client_kit.integrations import fi_sched
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_vix")

BOT_NAME = "vix"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

VIX_ROOTDIR = Path(__file__).parent
VIX_SKILLS = ckit_skills.static_skills_find(VIX_ROOTDIR, shared_skills_allowlist="*")
VIX_SKILLS_DEFAULT = ["stall-deals"]

VIX_SETUP_SCHEMA = json.loads((VIX_ROOTDIR / "setup_schema.json").read_text())
VIX_SETUP_SCHEMA += fi_shopify.SHOPIFY_SETUP_SCHEMA + fi_crm_automations.CRM_AUTOMATIONS_SETUP_SCHEMA + fi_resend.RESEND_SETUP_SCHEMA + fi_slack.SLACK_SETUP_SCHEMA

ERP_TABLES = ["crm_contact", "crm_activity", "crm_deal", "com_shop", "com_product", "com_product_variant", "com_order", "com_order_item", "com_refund"]
VIX_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    VIX_ROOTDIR,
    allowlist=[
        "skills",
        "flexus_policy_document",
        "print_widget",
        "erp[meta, data, crud, csv_import]",
        "crm[manage_contact, manage_deal, log_activity]",
        "magic_desk",
        "slack",
        "telegram",
        "resend",
    ],
    builtin_skills=VIX_SKILLS,
)

TOOLS = [
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_crm_automations.CRM_AUTOMATION_TOOL,
    fi_shopify.SHOPIFY_TOOL,
    fi_shopify.SHOPIFY_CART_TOOL,
    fi_sched.SCHED_TOOL,
    *[t for rec in VIX_INTEGRATIONS for t in rec.integr_tools],
]


async def vix_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(VIX_SETUP_SCHEMA, rcx.persona.persona_setup)

    integrations = await ckit_integrations_db.main_loop_integrations_init(VIX_INTEGRATIONS, rcx, setup)
    automations_integration = fi_crm_automations.IntegrationCrmAutomations(
        fclient, rcx, setup, available_erp_tables=ERP_TABLES,
    )
    email_respond_to = set(a.strip().lower() for a in setup.get("EMAIL_RESPOND_TO", "").split(",") if a.strip())
    shopify = fi_shopify.IntegrationShopify(fclient, rcx)
    sched = fi_sched.IntegrationSched(rcx)
    slack: fi_slack.IntegrationSlack = integrations["slack"]
    telegram: fi_telegram.IntegrationTelegram = integrations["telegram"]

    for me in rcx.messengers:
        me.accept_outside_messages_only_to_expert("sales")

    @rcx.on_emessage("EMAIL")
    async def handle_email(emsg):
        em = fi_resend.parse_emessage(emsg)
        body = em.body_text or em.body_html or "(empty)"
        try:
            display_name, addr = email.utils.parseaddr(em.from_full)
            addr = addr or em.from_addr
            contacts = await ckit_erp.query_erp_table(
                fclient, "crm_contact", rcx.persona.ws_id, erp_schema.CrmContact,
                filters=f"contact_email:CIEQL:{addr}", limit=1,
            )
            if contacts:
                contact_id = contacts[0].contact_id
            else:
                parts = display_name.split(None, 1) if display_name else [addr.split("@")[0]]
                contact_id = await ckit_erp.create_erp_record(fclient, "crm_contact", rcx.persona.ws_id, {
                    "ws_id": rcx.persona.ws_id,
                    "contact_email": addr.lower(),
                    "contact_first_name": parts[0],
                    "contact_last_name": parts[1] if len(parts) > 1 else "(unknown)",
                })
            await ckit_erp.create_erp_record(fclient, "crm_activity", rcx.persona.ws_id, {
                "ws_id": rcx.persona.ws_id,
                "activity_title": em.subject,
                "activity_type": "EMAIL",
                "activity_direction": "INBOUND",
                "activity_platform": "RESEND",
                "activity_contact_id": contact_id,
                "activity_summary": body[:500],
                "activity_occurred_ts": time.time(),
            })
        except Exception:
            logger.exception("Failed to create CRM activity for inbound email from %s", em.from_addr)
        if not email_respond_to.intersection(a.lower() for a in em.to_addrs):
            return
        title = "Email from %s: %s" % (em.from_addr, em.subject)
        if em.cc_addrs:
            title += " (cc: %s)" % ", ".join(em.cc_addrs)
        await ckit_kanban.bot_kanban_post_into_inbox(
            fclient,
            rcx.persona.persona_id,
            title=title,
            human_id="email:%s" % em.from_addr,
            details_json=json.dumps({"from": em.from_addr, "to": em.to_addrs, "cc": em.cc_addrs, "subject": em.subject, "body": body[:2000]}),
            provenance_message="vix_email_inbound",
        )

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(
            rcx.workdir,
            rcx.personal_mongo,
            toolcall,
            model_produced_args,
        )

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
            await ckit_erp.patch_erp_record(fclient, "crm_contact", rcx.persona.ws_id, contact_id, {"contact_platform_ids": {"telegram": str(a.chat_id)}})
        else:
            if contact_id := await fi_crm.find_contact_by_platform_id(fclient, rcx.persona.ws_id, "telegram", str(a.chat_id)):
                details["contact_id"] = contact_id
            title = "Telegram %s user=%r chat_id=%d\n%s" % (a.chat_type, a.message_author_name, a.chat_id, a.message_text)
            if a.attachments:
                title += f"\n[{len(a.attachments)} file(s) attached]"
        human_id = "telegram:%d" % a.chat_id
        if a.chat_type == "private":
            await ckit_kanban.bot_kanban_post_into_inprogress(
                fclient,
                rcx.persona.persona_id,
                title=title,
                human_id=human_id,
                details_json=json.dumps(details),
                provenance_message="vix_telegram_activity",
                fexp_name="sales",
                first_calls=[{"tool_name": "telegram", "tool_args": {"op": "capture", "args": {"chat_id": a.chat_id}}}],
            )
        else:
            await ckit_kanban.bot_kanban_post_into_inbox(
                fclient,
                rcx.persona.persona_id,
                title=title,
                human_id=human_id,
                details_json=json.dumps(details),
                provenance_message="vix_telegram_activity",
                fexp_name="sales",
            )

    @slack.on_incoming_activity
    async def slack_activity_callback(a: fi_slack.ActivitySlack, already_posted: bool):
        logger.info("%s Slack %s by @%s: %s", rcx.persona.persona_id, a.what_happened, a.message_author_name, a.message_text[:50])
        if already_posted:
            return
        details = asdict(a)
        if a.file_contents:
            details["file_contents"] = f"{len(a.file_contents)} files attached"
        to_capture = (a.channel_id or a.channel_name) + "/" + (a.thread_ts or a.message_ts)
        details["to_capture"] = to_capture
        if a.message_author_id:
            if contact_id := await fi_crm.find_contact_by_platform_id(fclient, rcx.persona.ws_id, "slack", a.message_author_id):
                details["contact_id"] = contact_id
        title = "Slack %s user=%r in #%s\n%s" % (a.what_happened, a.message_author_name, a.channel_name, a.message_text)
        if a.file_contents:
            title += f"\n[{len(a.file_contents)} file(s) attached]"
        human_id = "slack:%s" % a.message_author_id if a.message_author_id else ""
        if a.what_happened == "message/im":
            await ckit_kanban.bot_kanban_post_into_inprogress(
                fclient,
                rcx.persona.persona_id,
                title=title,
                human_id=human_id,
                details_json=json.dumps(details),
                provenance_message="vix_slack_activity",
                fexp_name="sales",
                first_calls=[{"tool_name": "slack", "tool_args": {"op": "capture", "args": {"channel_slash_thread": to_capture}}}],
            )
        else:
            await ckit_kanban.bot_kanban_post_into_inbox(
                fclient,
                rcx.persona.persona_id,
                title=title,
                human_id=human_id,
                details_json=json.dumps(details),
                provenance_message="vix_slack_activity",
                fexp_name="sales",
            )

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        await telegram.close()
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.vix import vix_install
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
