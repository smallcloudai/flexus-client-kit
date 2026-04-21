import asyncio
import datetime
import email.utils
import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional

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
from flexus_client_kit.integrations import fi_resend
from flexus_client_kit.integrations import fi_shopify
from flexus_client_kit.integrations import fi_telegram
from flexus_client_kit.integrations import fi_slack
from flexus_client_kit.integrations import fi_crm
from flexus_client_kit.integrations import fi_sched
from flexus_client_kit.integrations import fi_repo_reader
from flexus_client_kit.integrations import fi_pdoc
from flexus_client_kit.integrations import fi_thread
from flexus_client_kit import ckit_scenario
from flexus_client_kit.integrations import fi_discord2
from flexus_client_kit.integrations import fi_mcp
from flexus_client_kit import ckit_bot_version
import gql.transport.exceptions

logger = logging.getLogger("bot_karen")

KAREN_ROOTDIR = Path(__file__).parent
KAREN_SKILLS = ckit_skills.static_skills_find(KAREN_ROOTDIR, shared_skills_allowlist="*", integration_skills_allowlist="*")
KAREN_MCPS = []

KAREN_SETUP_SCHEMA = json.loads((KAREN_ROOTDIR / "setup_schema.json").read_text())
KAREN_SETUP_SCHEMA += (
    fi_shopify.SHOPIFY_SETUP_SCHEMA
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
        "crm[contact_info, manage_deal, verify_email]",
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

REPORT_SCHEMA = {
    "section01-crm": {
        "type": "object",
        "title": "CRM & Sales",
        "properties": {
            "new_contacts": {"type": "integer", "order": 0, "title": "New Contacts"},
            "deals_created": {"type": "integer", "order": 1, "title": "New Deals"},
            "deals_closed_won": {"type": "integer", "order": 2, "title": "Closed Won"},
            "deals_closed_lost": {"type": "integer", "order": 3, "title": "Closed Lost"},
            "orders": {"type": "integer", "order": 4, "title": "Orders"},
            "revenue": {"type": "number", "order": 5, "title": "Revenue"},
            "refunds": {"type": "integer", "order": 6, "title": "Refunds"},
            "refund_amount": {"type": "number", "order": 7, "title": "Refund Amount"},
        },
    },
    "section02-tasks": {
        "type": "object",
        "title": "Tasks",
        "properties": {
            "tasks_completed": {"type": "integer", "order": 0, "title": "Completed"},
            "tasks_success": {"type": "integer", "order": 1, "title": "Success"},
            "tasks_failed": {"type": "integer", "order": 2, "title": "Failed"},
            "tasks_inconclusive": {"type": "integer", "order": 3, "title": "Inconclusive"},
            "tasks_irrelevant": {"type": "integer", "order": 4, "title": "Irrelevant"},
        },
    },
    "section03-notes": {
        "type": "object",
        "title": "Notes",
        "properties": {
            "notable_incidents": {"type": "string", "order": 0, "title": "Notable Incidents"},
            "setup_problems": {"type": "string", "order": 1, "title": "Setup Problems"},
            "what_people_asked": {"type": "string", "order": 2, "title": "What People Asked"},
        },
    },
    "section04-resolution-summary": {
        "type": "object",
        "title": "Resolution Outcomes",
        "properties": {
            "resolved_success": {"type": "integer", "order": 0, "title": "Resolved: Success"},
            "resolved_fail": {"type": "integer", "order": 1, "title": "Resolved: Fail"},
            "resolved_inconclusive": {"type": "integer", "order": 2, "title": "Resolved: Inconclusive"},
            "resolved_escalated": {"type": "integer", "order": 3, "title": "Resolved: Escalated"},
            "sentiment_notes": {"type": "string", "order": 4, "title": "Sentiment Notes"},
        },
    },
    "section05-costs": {
        "type": "object",
        "title": "Token Costs",
        "properties": {
            "total_coins": {"type": "integer", "order": 0, "title": "Total Coins"},
            "total_cost_usd": {"type": "number", "order": 1, "title": "Total Cost (USD)"},
            "conversations_count": {"type": "integer", "order": 2, "title": "Conversations"},
            "avg_cost_per_conversation": {"type": "number", "order": 3, "title": "Avg Cost/Conversation (USD)"},
            "budget_utilization_pct": {"type": "number", "order": 4, "title": "Budget Utilization %"},
        },
    },
}

REPORT_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="karen_report",
    description=(
        "Generate a daily or weekly report. Queries CRM, deals, orders, and kanban, "
        "saves a schemed policy document to /support/reports/YYYYMMDD-daily or YYYYMMDD-weekly. "
        "Returns collected data so you can fill in the notes section and save the final document."
    ),
    parameters={
        "type": "object",
        "properties": {
            "report_type": {"type": "string", "enum": ["daily", "weekly"]},
        },
        "required": ["report_type"],
        "additionalProperties": False,
    },
)

TOOLS = [
    fi_mongo_store.MONGO_STORE_TOOL,
    fi_shopify.SHOPIFY_TOOL,
    fi_sched.SCHED_TOOL,
    fi_repo_reader.REPO_READER_TOOL,
    SUPPORT_STATUS_TOOL,
    EXPLORE_A_QUESTION_TOOL,
    PRODUCT_CATALOG_TOOL,
    REPORT_TOOL,
    fi_thread.THREAD_READ_TOOL,
    *[t for rec in KAREN_INTEGRATIONS for t in rec.integr_tools],
]


_REQUIRED_SECTIONS = {
    "answering": ["tone-of-voice", "never-say", "offtopic"],
    "reporting": ["daily", "weekly"],
}


async def handle_support_status(pdoc: fi_pdoc.IntegrationPdoc, rcx: ckit_bot_exec.RobotContext, fcall_untrusted_key: str) -> str:
    def _qa_doc_check(content) -> dict | None:
        if not isinstance(content, dict):
            return None
        top_tag = next((k for k in content if k != "meta"), None)
        if not top_tag or not isinstance(content.get(top_tag), dict):
            return None
        doc = content[top_tag]
        total_q, filled_q, total_a, filled_a, translated = 0, 0, 0, 0, True
        found_sections = {}
        for k, v in doc.items():
            if k == "meta" or not isinstance(v, dict):
                continue
            sec_name = re.sub(r"^section\d+-", "", k)
            qs = set()
            for qk, qv in v.items():
                if not isinstance(qv, dict) or "q" not in qv or "a" not in qv:
                    continue
                qs.add(re.sub(r"^question\d+-", "", qk))
                total_q += 1
                total_a += 1
                q_text = qv["q"].strip()
                if q_text and q_text != "TRANSLATED":
                    filled_q += 1
                else:
                    translated = False
                if qv["a"].strip():
                    filled_a += 1
            found_sections[sec_name] = qs
        missing = []
        for sec, required_qs in _REQUIRED_SECTIONS.items():
            if sec not in found_sections:
                missing.append(f"section '{sec}'")
            else:
                for q in required_qs:
                    if q not in found_sections[sec]:
                        missing.append(f"question '{q}' in section '{sec}'")
        return {"total_q": total_q, "filled_q": filled_q, "total_a": total_a, "filled_a": filled_a, "translated": translated, "missing": missing}

    persona_id = rcx.persona.persona_id
    lines = []

    # check /support/summary
    summary = await pdoc.pdoc_cat("/support/summary", persona_id=persona_id, fcall_untrusted_key=fcall_untrusted_key)
    if summary:
        stats = _qa_doc_check(summary.pdoc_content)
        if stats:
            pct = (stats["filled_a"] * 100 // stats["total_a"]) if stats["total_a"] else 0
            lines.append(f"/support/summary exists — {stats['filled_a']}/{stats['total_a']} answers filled ({pct}%)")
            if not stats["translated"]:
                lines.append(f"   ⚠️ {stats['total_q'] - stats['filled_q']}/{stats['total_q']} questions not translated yet")
            if stats["missing"]:
                lines.append(f"   ⚠️ Missing: {', '.join(stats['missing'])}")
        else:
            lines.append("/support/summary exists (not QA format, can't measure fill percentage)")
    else:
        lines.append("/support/summary does not exist")
    lines.append("")

    # list drafts in /support/
    DATE_PREFIX_RE = re.compile(r"^\d{8}-")
    items = await pdoc.pdoc_list("/support/", persona_id=persona_id, fcall_untrusted_key=fcall_untrusted_key, depth=1)
    drafts = [it for it in items if not it.is_folder and it.path != "/support/summary"]
    if drafts:
        lines.append("Drafts in /support/")
        for d in drafts:
            doc = await pdoc.pdoc_cat(d.path, persona_id=persona_id, fcall_untrusted_key=fcall_untrusted_key)
            if not doc:
                lines.append(f"    {d.path} —- could not read")
                continue
            stats = _qa_doc_check(doc.pdoc_content)
            if stats:
                pct = (stats["filled_a"] * 100 // stats["total_a"]) if stats["total_a"] else 0
                untranslated = stats['total_q'] - stats['filled_q']
                t_status = f", {untranslated}/{stats['total_q']} questions need translation before user can answer." if not stats["translated"] else ""
                lines.append(f"    {d.path} —- has {stats['filled_a']}/{stats['total_a']} answers{t_status}")
                if stats["missing"]:
                    lines.append(f"    ⚠️ Missing: {', '.join(stats['missing'])}")
                name = d.path.rsplit("/", 1)[-1]
                if DATE_PREFIX_RE.match(name) and pct >= 80:
                    lines.append(f"    💡 Looks ready, ask user if you should: flexus_policy_document(op=\"mv\", args={{\"p1\": \"{d.path}\", \"p2\": \"/support/summary\"}})")
            else:
                lines.append(f"    {d.path} —- not QA format")
    else:
        lines.append("No drafts in /support/.")

    lines.append("")
    lines.append("To see if you have any External Data Sources set up to answer questions, run flexus_read_original(eds=null, op=null)")

    return "\n".join(lines)


async def handle_report(
    fclient: ckit_client.FlexusClient,
    rcx: ckit_bot_exec.RobotContext,
    pdoc: fi_pdoc.IntegrationPdoc,
    report_type: str,
    fcall_untrusted_key: str,
) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    if report_type == "weekly":
        t0 = (now - datetime.timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        t0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
    ts0 = t0.timestamp()
    pid = rcx.persona.persona_id
    ws_id = rcx.persona.ws_id
    http = await fclient.use_http_on_behalf(pid, fcall_untrusted_key)

    new_contacts = await ckit_erp.erp_table_data(http, "crm_contact", ws_id, erp_schema.CrmContact, filters=f"contact_created_ts:>=:{ts0}", limit=1000)
    deals = await ckit_erp.erp_table_data(http, "crm_deal", ws_id, erp_schema.CrmDeal, filters=f"deal_created_ts:>=:{ts0}", limit=1000)
    closed_deals = await ckit_erp.erp_table_data(http, "crm_deal", ws_id, erp_schema.CrmDeal, filters=f"deal_closed_ts:>=:{ts0}", include=["stage"], limit=1000)
    won = sum(1 for d in closed_deals if d.stage and d.stage.stage_status == "WON")
    lost = sum(1 for d in closed_deals if d.stage and d.stage.stage_status == "LOST")
    orders = await ckit_erp.erp_table_data(http, "com_order", ws_id, erp_schema.ComOrder, filters=f"order_created_ts:>=:{ts0}", limit=1000)
    revenue = float(sum(o.order_total for o in orders))
    refunds = await ckit_erp.erp_table_data(http, "com_refund", ws_id, erp_schema.ComRefund, filters=f"refund_created_ts:>=:{ts0}", limit=1000)
    refund_amount = float(sum(r.refund_amount for r in refunds))

    all_tasks = await ckit_kanban.bot_get_all_tasks(http, pid)
    done_tasks = [t for t in all_tasks if t.ktask_done_ts >= ts0]
    total_coins = sum(t.ktask_coins for t in done_tasks)
    total_budget = sum(t.ktask_budget for t in done_tasks)
    by_code = {}
    for t in done_tasks:
        c = (t.ktask_resolution_code or "UNKNOWN").upper()
        by_code[c] = by_code.get(c, 0) + 1

    data = {
        "section01-crm": {
            "new_contacts": len(new_contacts),
            "deals_created": len(deals),
            "deals_closed_won": won,
            "deals_closed_lost": lost,
            "orders": len(orders),
            "revenue": revenue,
            "refunds": len(refunds),
            "refund_amount": refund_amount,
        },
        "section02-tasks": {
            "tasks_completed": len(done_tasks),
            "tasks_success": by_code.get("SUCCESS", 0),
            "tasks_failed": by_code.get("FAIL", 0),
            "tasks_inconclusive": by_code.get("INCONCLUSIVE", 0),
            "tasks_irrelevant": by_code.get("IRRELEVANT", 0),
        },
        "section03-notes": {
            "notable_incidents": "",
            "setup_problems": "",
            "what_people_asked": "",
        },
        "section04-resolution-summary": {
            "resolved_success": by_code.get("SUCCESS", 0),
            "resolved_fail": by_code.get("FAIL", 0),
            "resolved_inconclusive": by_code.get("INCONCLUSIVE", 0),
            "resolved_escalated": by_code.get("ESCALATED", 0),
            "sentiment_notes": "",
        },
        "section05-costs": {
            "total_coins": total_coins,
            "total_cost_usd": round(total_coins / 1_000_000, 2),
            "conversations_count": len(done_tasks),
            "avg_cost_per_conversation": round(total_coins / max(len(done_tasks), 1) / 1_000_000, 4),
            "budget_utilization_pct": round(total_coins / max(total_budget, 1) * 100, 1),
        },
    }

    date_str = now.strftime("%Y%m%d")
    path = "/support/reports/%s-%s" % (date_str, report_type)
    doc = {
        "karen-report": {
            "meta": {
                "author": "auto generated",
                "created": date_str,
            },
            "schema": REPORT_SCHEMA,
            **data,
        }
    }
    doc_text = json.dumps(doc, ensure_ascii=False, indent=2)
    result = await pdoc.pdoc_overwrite(path, doc_text, persona_id=pid, fcall_untrusted_key=fcall_untrusted_key)

    return (
        "✍️ %s\nmd5=%s\n\n%s\n\n"
        "Task stats and resolution outcomes are pre-filled from kanban. "
        "Fill in the notes section, then save. Use flexus_policy_document(op=\"update_at_location\", "
        "args={\"p\": \"%s\", \"expected_md5\": \"%s\", \"updates\": [[\"karen-report.section03-notes.notable_incidents\", ...], ...]})"
    ) % (path, result.md5_after, doc_text, path, result.md5_after)


async def karen_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(KAREN_SETUP_SCHEMA, rcx.persona.persona_setup)

    integrations = await ckit_integrations_db.main_loop_integrations_init(KAREN_INTEGRATIONS, rcx, setup)
    pdoc_integration: fi_pdoc.IntegrationPdoc = integrations["flexus_policy_document"]
    email_respond_to = set(a.strip().lower() for a in setup.get("EMAIL_RESPOND_TO", "").split(",") if a.strip())
    shopify = fi_shopify.IntegrationShopify(fclient, rcx)
    sched = fi_sched.IntegrationSched(rcx)
    slack: fi_slack.IntegrationSlack | None = integrations.get("slack")
    telegram: fi_telegram.IntegrationTelegram | None = integrations.get("telegram")

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
        except gql.transport.exceptions.TransportQueryError as e:
            ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "CRM activity for inbound email from %s" % em.from_addr)
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
        return await fi_mongo_store.handle_mongo_store(rcx, toolcall, model_produced_args)

    @rcx.on_tool_call(fi_shopify.SHOPIFY_TOOL.name)
    async def toolcall_shopify(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await shopify.called_by_model(toolcall, model_produced_args)

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

    @rcx.on_tool_call(REPORT_TOOL.name)
    async def toolcall_report(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        if rcx.running_test_scenario:
            return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, open(__file__).read())
        return await handle_report(fclient, rcx, pdoc_integration, model_produced_args["report_type"], toolcall.fcall_untrusted_key)

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
        except gql.transport.exceptions.TransportQueryError as e:
            return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "product_catalog")
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
        if rcx.running_test_scenario:
            return await ckit_scenario.scenario_generate_tool_result_via_model(rcx.fclient, toolcall, "")
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
                questions.append('Search EDS "%s" to answer: %s\n\nUse flexus_vector_search(scopes=["%s"], ...) to find relevant documents. Report your findings with sources.' % (entry, q, entry))
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
                    title="Read linked thread, find/create contact, log activity: %s" % new_task.ktask_title[:60],
                    details_json=json.dumps({
                        "spawned_from_ktask_id": new_task.ktask_id,
                        "spawned_from_title": new_task.ktask_title,
                        "from_thread_id": new_task.ktask_inprogress_ft_id,
                        "human_id": new_task.ktask_human_id,
                    }),
                    provenance_message="karen_post_conversation",
                    fexp_name="post_conversation",
                )

    if telegram:
        @telegram.on_incoming_activity
        async def telegram_activity_callback(a: fi_telegram.ActivityTelegram, already_posted: bool):
            if already_posted:
                return
            extra = {}
            title = None
            http = await fclient.use_http_on_behalf(rcx.persona.persona_id, "")
            if a.message_text.startswith("/start c_"):  # deep links from email campaigns
                contact_id = a.message_text[9:].strip()
                extra["contact_id"] = contact_id
                title = "CRM contact opened Telegram chat, contact_id=%s chat_id=%d" % (contact_id, a.chat_id)
                await ckit_erp.erp_record_patch(http, "crm_contact", rcx.persona.ws_id, contact_id, {"contact_platform_ids": {"telegram": str(a.chat_id)}})
            else:
                if contact_id := await fi_crm.find_contact_by_platform_id(http, rcx.persona.ws_id, "telegram", str(a.chat_id)):
                    extra["contact_id"] = contact_id
            await telegram.inbound_activity_to_task(a, already_posted=False, extra_details=extra, provenance="karen_telegram_activity", title=title)

    if slack:
        @slack.on_incoming_activity
        async def slack_activity_callback(a: fi_slack.ActivitySlack, already_posted: bool):
            if already_posted:
                return
            extra = {}
            if a.message_author_id:
                if contact_id := await fi_crm.find_contact_by_platform_id(await fclient.use_http_on_behalf(rcx.persona.persona_id, ""), rcx.persona.ws_id, "slack", a.message_author_id):
                    extra["contact_id"] = contact_id
            await slack.inbound_activity_to_task(a, already_posted_to_captured_thread=False, extra_details=extra, provenance="karen_slack_activity")

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)

    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_simple_bots.karen import karen_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(__file__)
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(ckit_bot_version.bot_name_from_file(__file__), bot_version), endpoint="/v1/jailed-bot")
    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=karen_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=karen_install.install,
        subscribe_to_erp_tables=ERP_TABLES,
    ))


if __name__ == "__main__":
    main()

