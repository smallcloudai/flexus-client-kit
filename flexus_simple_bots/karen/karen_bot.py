import asyncio
import email.utils
import json
import logging
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_erp
from flexus_client_kit import ckit_ask_model
from flexus_client_kit import ckit_kanban
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_skills
from flexus_client_kit import erp_schema
from flexus_client_kit import ckit_mongo
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_crm_automations
from flexus_client_kit.integrations import fi_resend
from flexus_client_kit.integrations import fi_shopify
from flexus_client_kit.integrations import fi_telegram
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit.integrations import fi_crm
from flexus_client_kit.integrations import fi_sched
from flexus_client_kit.integrations import fi_repo_reader
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit import ckit_scenario
from flexus_client_kit.integrations import fi_discord2
from flexus_client_kit.integrations import fi_mcp
from flexus_simple_bots.version_common import SIMPLE_BOTS_COMMON_VERSION

logger = logging.getLogger("bot_karen")

BOT_NAME = "karen"
BOT_VERSION = SIMPLE_BOTS_COMMON_VERSION

KAREN_ROOTDIR = Path(__file__).parent
KAREN_SKILLS = ckit_skills.static_skills_find(KAREN_ROOTDIR, shared_skills_allowlist="*")
KAREN_MCPS = []

KAREN_SETUP_SCHEMA = json.loads((KAREN_ROOTDIR / "setup_schema.json").read_text())
KAREN_SETUP_SCHEMA += (
    fi_shopify.SHOPIFY_SETUP_SCHEMA
    + fi_crm_automations.CRM_AUTOMATIONS_SETUP_SCHEMA
    + fi_crm.CRM_SETUP_SCHEMA
    + fi_resend.RESEND_SETUP_SCHEMA
    + fi_slack.SLACK_SETUP_SCHEMA
    + fi_discord2.DISCORD_SETUP_SCHEMA
)
KAREN_SETUP_SCHEMA.extend(fi_mcp.mcp_setup_schema(KAREN_MCPS))

ERP_TABLES = ["crm_contact", "crm_activity", "crm_deal", "com_shop", "com_product", "com_product_variant", "com_order", "com_order_item", "com_refund"]

KAREN_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    KAREN_ROOTDIR,
    allowlist=[
        "skills",
        "flexus_policy_document",
        "print_widget",
        "erp[meta, data, crud, csv_import]",
        "crm[manage_contact, manage_deal, log_activity, verify_email]",
        "magic_desk",
        "slack",
        "telegram",
        "discord",
        "resend",
    ],
    builtin_skills=KAREN_SKILLS,
)

CATALOG_TABLES = {"com_product", "com_product_variant", "com_shop"}

PRODUCT_CATALOG_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="product_catalog",
    description=(
        "Query the product catalog. IMPORTANT: call with just the table name first (no options) to see available columns before filtering. "
        "Tables: com_product, com_product_variant (price, inventory, SKU), com_shop. "
        "Operators: =, !=, >, >=, <, <=, LIKE, ILIKE, CIEQL, IN, NOT_IN, IS_NULL, IS_NOT_NULL. "
        "LIKE/ILIKE use SQL wildcards: % matches any chars. CIEQL: Case Insensitive Equal. "
        "JSON path: prod_details->color:=:red. "
        "Relation dot-notation in filters: use relation.field to filter on included relations, "
        'e.g. filters="variants.pvar_inventory_status:=:IN_STOCK" when including variants. '
        "Examples: "
        'filters="prod_category:=:shoes" for single filter, '
        'filters={"AND": ["prod_category:=:shoes", "prod_tags:contains:summer"]} for multiple AND, '
        'filters={"OR": ["prod_name:ILIKE:%boot%", "prod_name:ILIKE:%sneaker%"]} for OR.'
    ),
    parameters={
        "type": "object",
        "properties": {
            "table": {"type": "string", "enum": ["com_product", "com_product_variant", "com_shop"], "order": 1},
            "options": {
                "type": "object",
                "description": "Query options",
                "order": 2,
                "properties": {
                    "skip": {"type": "integer", "description": "Number of rows to skip (default 0)", "order": 1001},
                    "limit": {"type": "integer", "description": "Maximum number of rows to return (default 100, max 1000)", "order": 1002},
                    "sort_by": {"type": "array", "items": {"type": "string"}, "description": 'Sort expressions ["column:ASC", "another:DESC"]', "order": 1003},
                    "filters": {"oneOf": [{"type": "string"}, {"type": "object"}], "description": 'String or object with AND/OR key, e.g. {"AND": ["col:op:val"]} or {"OR": [...]}', "order": 1004},
                    "include": {"type": "array", "items": {"type": "string"}, "description": 'Relation names to include, e.g. ["variants"]', "order": 1005},
                    "include_limit": {"type": "integer", "description": "Max items per included relation total across all rows (defaults to limit).", "order": 1006},
                },
            },
        },
        "required": ["table"],
    },
)


EXPLORE_A_QUESTION_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="explore_a_question",
    description="Search EDSs or URLs for an answer. Spawns one subchat per entry. Each subchat searches, reads full docs, and returns sourced findings.",
    parameters={
        "type": "object",
        "properties": {
            "q": {"type": "string", "description": "What to search for, e.g. 'summarize the nature of business' or 'refund policy details'"},
            "eds": {"type": "array", "items": {"type": "string"}, "description": "List of EDS ids or websites (https://...) to search"},
        },
        "required": ["q", "eds"],
        "additionalProperties": False,
    },
)

SUPPORT_STATUS_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="support_collection_status",
    description="Check how complete the support knowledge base is: /support/summary existence, drafts in /support/, answer fill percentage, translation status. No parameters needed.",
    parameters={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
)

TOOLS = [
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_crm_automations.CRM_AUTOMATION_TOOL,
    fi_shopify.SHOPIFY_TOOL,
    fi_shopify.SHOPIFY_CART_TOOL,
    fi_sched.SCHED_TOOL,
    fi_repo_reader.REPO_READER_TOOL,
    SUPPORT_STATUS_TOOL,
    EXPLORE_A_QUESTION_TOOL,
    PRODUCT_CATALOG_TOOL,
    *[t for rec in KAREN_INTEGRATIONS for t in rec.integr_tools],
]


def _qa_fill_stats(doc: dict) -> dict:
    total_q, filled_q, total_a, filled_a, translated = 0, 0, 0, 0, True
    for k, v in doc.items():
        if k == "meta" or not isinstance(v, dict):
            continue
        for qk, qv in v.items():
            if not isinstance(qv, dict) or "q" not in qv or "a" not in qv:
                continue
            total_q += 1
            total_a += 1
            if qv["q"].strip():
                filled_q += 1
            else:
                translated = False
            if qv["a"].strip():
                filled_a += 1
    return {"total_q": total_q, "filled_q": filled_q, "total_a": total_a, "filled_a": filled_a, "translated": translated}


_DATE_PREFIX_RE = re.compile(r"^\d{8}-")


async def handle_support_status(pdoc: fi_pdoc.IntegrationPdoc, rcx: ckit_bot_exec.RobotContext, fcall_untrusted_key: str) -> str:
    persona_id = rcx.persona.persona_id
    lines = []

    # check /support/summary
    summary = await pdoc.pdoc_cat("/support/summary", persona_id=persona_id, fcall_untrusted_key=fcall_untrusted_key)
    if summary:
        content = summary.pdoc_content
        top_tag = next((k for k in content if k != "meta"), None) if isinstance(content, dict) else None
        if top_tag and isinstance(content.get(top_tag), dict):
            stats = _qa_fill_stats(content[top_tag])
            pct = (stats["filled_a"] * 100 // stats["total_a"]) if stats["total_a"] else 0
            lines.append(f"/support/summary exists — {stats['filled_a']}/{stats['total_a']} answers filled ({pct}%)")
            if not stats["translated"]:
                lines.append(f"   ⚠️ {stats['total_q'] - stats['filled_q']}/{stats['total_q']} questions not translated yet")
        else:
            lines.append("/support/summary exists (not QA format, can't measure fill percentage)")
    else:
        lines.append("/support/summary does not exist")
    lines.append("")

    # list drafts in /support/
    items = await pdoc.pdoc_list("/support/", persona_id=persona_id, fcall_untrusted_key=fcall_untrusted_key, depth=1)
    drafts = [it for it in items if not it.is_folder and it.path != "/support/summary"]
    if drafts:
        lines.append("Drafts in /support/")
        for d in drafts:
            doc = await pdoc.pdoc_cat(d.path, persona_id=persona_id, fcall_untrusted_key=fcall_untrusted_key)
            if not doc:
                lines.append(f"    {d.path} —- could not read")
                continue
            content = doc.pdoc_content
            top_tag = next((k for k in content if k != "meta"), None) if isinstance(content, dict) else None
            if top_tag and isinstance(content.get(top_tag), dict):
                stats = _qa_fill_stats(content[top_tag])
                pct = (stats["filled_a"] * 100 // stats["total_a"]) if stats["total_a"] else 0
                untranslated = stats['total_q'] - stats['filled_q']
                t_status = f", {untranslated}/{stats['total_q']} questions need translation before user can answer." if not stats["translated"] else ""
                lines.append(f"    {d.path} —- has {stats['filled_a']}/{stats['total_a']} answers{t_status}")
                name = d.path.rsplit("/", 1)[-1]
                if _DATE_PREFIX_RE.match(name) and pct >= 80:
                    lines.append(f"    💡 Looks ready, ask user if you should: flexus_policy_document(op=\"mv\", args={{\"p1\": \"{d.path}\", \"p2\": \"/support/summary\"}})")
            else:
                lines.append(f"    {d.path} —- not QA format")
    else:
        lines.append("No drafts in /support/.")

    return "\n".join(lines)


async def karen_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(KAREN_SETUP_SCHEMA, rcx.persona.persona_setup)

    integrations = await ckit_integrations_db.main_loop_integrations_init(KAREN_INTEGRATIONS, rcx, setup)
    automations_integration = fi_crm_automations.IntegrationCrmAutomations(
        fclient, rcx, setup, available_erp_tables=ERP_TABLES,
    )
    pdoc_integration: fi_pdoc.IntegrationPdoc = integrations["flexus_policy_document"]
    email_respond_to = set(a.strip().lower() for a in setup.get("EMAIL_RESPOND_TO", "").split(",") if a.strip())
    shopify = fi_shopify.IntegrationShopify(fclient, rcx)
    sched = fi_sched.IntegrationSched(rcx)
    slack: fi_slack.IntegrationSlack = integrations["slack"]
    telegram: fi_telegram.IntegrationTelegram = integrations["telegram"]

    for me in rcx.messengers:
        me.accept_outside_messages_only_to_expert("very_limited")

    @rcx.on_emessage("EMAIL")
    async def handle_email(emsg):
        em = fi_resend.parse_emessage(emsg)
        body = em.body_text or em.body_html or "(empty)"
        try:
            display_name, addr = email.utils.parseaddr(em.from_full)
            addr = addr or em.from_addr
            http = await fclient.use_http_on_behalf(rcx.persona.persona_id, "")
            contacts = await ckit_erp.erp_table_data(
                http, "crm_contact", rcx.persona.ws_id, erp_schema.CrmContact,
                filters=f"contact_email:CIEQL:{addr}", limit=1,
            )
            if contacts:
                contact_id = contacts[0].contact_id
            else:
                parts = display_name.split(None, 1) if display_name else [addr.split("@")[0]]
                contact_id = await ckit_erp.erp_record_create(http, "crm_contact", rcx.persona.ws_id, {
                    "ws_id": rcx.persona.ws_id,
                    "contact_email": addr.lower(),
                    "contact_first_name": parts[0],
                    "contact_last_name": parts[1] if len(parts) > 1 else "(unknown)",
                })
            await ckit_erp.erp_record_create(http, "crm_activity", rcx.persona.ws_id, {
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
            await fclient.use_http_on_behalf(rcx.persona.persona_id, ""),
            rcx.persona.persona_id,
            title=title,
            human_id="email:%s" % em.from_addr,
            details_json=json.dumps({"from": em.from_addr, "to": em.to_addrs, "cc": em.cc_addrs, "subject": em.subject, "body": body[:2000]}),
            provenance_message="karen_email_inbound",
            fexp_name="very_limited",
        )

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if rcx.running_test_scenario:
            return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, open(fi_mongo_store.__file__).read())
        return await fi_mongo_store.handle_mongo_store(rcx.workdir, rcx.personal_mongo, toolcall, model_produced_args)

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

    @rcx.on_tool_call(fi_repo_reader.REPO_READER_TOOL.name)
    async def toolcall_repo_reader(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_repo_reader.handle_repo_reader(rcx, toolcall, model_produced_args)

    @rcx.on_tool_call(SUPPORT_STATUS_TOOL.name)
    async def toolcall_support_status(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if rcx.running_test_scenario:
            return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, open(__file__).read())
        return await handle_support_status(pdoc_integration, rcx, toolcall.fcall_untrusted_key)

    @rcx.on_tool_call(PRODUCT_CATALOG_TOOL.name)
    async def toolcall_product_catalog(toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        table = args.get("table", "")
        if table not in CATALOG_TABLES:
            return "❌ table must be one of: %s" % ", ".join(sorted(CATALOG_TABLES))
        schema_class = erp_schema.ERP_TABLE_TO_SCHEMA[table]
        opts = args.get("options") or {}
        if not opts:
            return ckit_erp.format_table_meta_text(table, schema_class)
        http = await fclient.use_http_on_behalf(rcx.persona.persona_id, toolcall.fcall_untrusted_key)
        try:
            rows = await ckit_erp.erp_table_data(
                http, table, rcx.persona.ws_id, schema_class,
                skip=opts.get("skip", 0),
                limit=min(opts.get("limit", 100), 1000),
                sort_by=opts.get("sort_by", []),
                filters=opts.get("filters", {}),
                include=opts.get("include", []),
                include_limit=opts.get("include_limit", opts.get("limit", 100)),
            )
        except Exception as e:
            return "❌ Query error: %s" % e
        from flexus_client_kit.integrations.fi_erp import _rows_to_text
        display_text, full_json = _rows_to_text(
            [ckit_erp.dataclass_or_dict_to_dict(r) for r in rows], table,
        )
        if full_json and rcx.personal_mongo is not None:
            mongo_path = "catalog_query/%s_%d.json" % (table, int(time.time()))
            try:
                await ckit_mongo.mongo_overwrite(rcx.personal_mongo, mongo_path, full_json.encode("utf-8"), ttl=86400)
                display_text += "\n\n💾 Full results: mongo_store(op='cat', args={'path': '%s'})" % mongo_path
            except Exception:
                pass
        return display_text

    @rcx.on_tool_call(EXPLORE_A_QUESTION_TOOL.name)
    async def toolcall_explore_a_question(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        q = model_produced_args["q"]
        eds_list = model_produced_args["eds"]
        if not eds_list:
            return "Error: eds list is empty, provide at least one entry."
        if len(eds_list) > 10:
            return "Error: too many entries, max 10."
        for entry in eds_list:
            is_url = entry.startswith("http://") or entry.startswith("https://")
            if not is_url and (len(entry) > 20 or not entry.isascii() or " " in entry):
                return "Error: EDS ID %r must be ASCII, no spaces, max 20 chars." % entry
        questions = []
        titles = []
        for entry in eds_list:
            if entry.startswith("http://") or entry.startswith("https://"):
                questions.append("Fetch and read %s to answer: %s\n\nUse web() tool to fetch the page. Report your findings with sources." % (entry, q))
                titles.append("Explore: %s (%s)" % (q[:40], entry[:40]))
            else:
                questions.append('Search EDS "%s" to answer: %s\n\nUse flexus_vector_search(scopes=["%s"], ...) and flexus_read_original() to find and read relevant documents. Report your findings with sources.' % (entry, q, entry))
                titles.append("Explore: %s (EDS %s)" % (q[:60], entry))
        subchats = await ckit_ask_model.bot_subchat_create_multiple(
            client=fclient,
            who_is_asking="karen_explore_a_question",
            persona_id=rcx.persona.persona_id,
            first_question=questions,
            first_calls=["null" for _ in eds_list],
            title=titles,
            fcall_id=toolcall.fcall_id,
            fexp_name="explore",
        )
        raise ckit_cloudtool.WaitForSubchats(subchats)

    @telegram.on_incoming_activity
    async def telegram_activity_callback(a: fi_telegram.ActivityTelegram, already_posted: bool):
        logger.info("%s Telegram %s by @%s: %s", rcx.persona.persona_id, a.chat_type, a.message_author_name, a.message_text[:50])
        if already_posted:
            return
        details = asdict(a)
        if a.attachments:
            details["attachments"] = f"{len(a.attachments)} files attached"
        http = await fclient.use_http_on_behalf(rcx.persona.persona_id, "")
        if a.message_text.startswith("/start c_"):  # deep links from email campaigns
            contact_id = a.message_text[9:].strip()
            details["contact_id"] = contact_id
            title = "CRM contact opened Telegram chat, contact_id=%s chat_id=%d" % (contact_id, a.chat_id)
            await ckit_erp.erp_record_patch(http, "crm_contact", rcx.persona.ws_id, contact_id, {"contact_platform_ids": {"telegram": str(a.chat_id)}})
        else:
            if contact_id := await fi_crm.find_contact_by_platform_id(http, rcx.persona.ws_id, "telegram", str(a.chat_id)):
                details["contact_id"] = contact_id
            title = "Telegram %s user=%r chat_id=%d\n%s" % (a.chat_type, a.message_author_name, a.chat_id, a.message_text)
            if a.attachments:
                title += f"\n[{len(a.attachments)} file(s) attached]"
        human_id = "telegram:%d" % a.chat_id
        if a.chat_type == "private":
            await ckit_kanban.bot_kanban_post_into_inprogress(
                await fclient.use_http_on_behalf(rcx.persona.persona_id, ""),
                rcx.persona.persona_id,
                title=title,
                human_id=human_id,
                details_json=json.dumps(details),
                provenance_message="karen_telegram_activity",
                fexp_name="very_limited",
                first_calls=[{"tool_name": "telegram", "tool_args": {"op": "capture", "args": {"chat_id": a.chat_id}}}],
            )
        else:
            await ckit_kanban.bot_kanban_post_into_inbox(
                await fclient.use_http_on_behalf(rcx.persona.persona_id, ""),
                rcx.persona.persona_id,
                title=title,
                human_id=human_id,
                details_json=json.dumps(details),
                provenance_message="karen_telegram_activity",
                fexp_name="very_limited",
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
            if contact_id := await fi_crm.find_contact_by_platform_id(await fclient.use_http_on_behalf(rcx.persona.persona_id, ""), rcx.persona.ws_id, "slack", a.message_author_id):
                details["contact_id"] = contact_id
        title = "Slack %s user=%r in #%s\n%s" % (a.what_happened, a.message_author_name, a.channel_name, a.message_text)
        if a.file_contents:
            title += f"\n[{len(a.file_contents)} file(s) attached]"
        human_id = "slack:%s" % a.message_author_id if a.message_author_id else ""
        if a.what_happened == "message/im":
            await ckit_kanban.bot_kanban_post_into_inprogress(
                await fclient.use_http_on_behalf(rcx.persona.persona_id, ""),
                rcx.persona.persona_id,
                title=title,
                human_id=human_id,
                details_json=json.dumps(details),
                provenance_message="karen_slack_activity",
                fexp_name="very_limited",
                first_calls=[{"tool_name": "slack", "tool_args": {"op": "capture", "args": {"channel_slash_thread": to_capture}}}],
            )
        else:
            await ckit_kanban.bot_kanban_post_into_inbox(
                await fclient.use_http_on_behalf(rcx.persona.persona_id, ""),
                rcx.persona.persona_id,
                title=title,
                human_id=human_id,
                details_json=json.dumps(details),
                provenance_message="karen_slack_activity",
                fexp_name="very_limited",
            )

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        await integrations["discord"].close()
        await telegram.close()
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.karen import karen_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, BOT_VERSION), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        marketable_name=BOT_NAME,
        marketable_version_str=BOT_VERSION,
        bot_main_loop=karen_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=karen_install.install,
        subscribe_to_erp_tables=ERP_TABLES,
    ))


if __name__ == "__main__":
    main()
