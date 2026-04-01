import logging
import time
from typing import Dict, Any, Optional, TYPE_CHECKING

import gql
import gql.transport.exceptions

from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_erp, erp_schema

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

logger = logging.getLogger("fi_crm")


LOG_CRM_ACTIVITY_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="log_crm_activity",
    description="Log a CRM activity (conversation, email, call, etc.) for a contact.",
    parameters={
        "type": "object",
        "properties": {
            "contact_id": {"type": "string", "order": 1},
            "activity_type": {"type": "string", "enum": ["WEB_CHAT", "MESSENGER_CHAT", "EMAIL", "CALL", "MEETING"], "order": 2},
            "direction": {"type": "string", "enum": ["INBOUND", "OUTBOUND"], "order": 3},
            "platform": {"type": "string", "description": "e.g. TELEGRAM, EMAIL, PHONE", "order": 4},
            "title": {"type": "string", "order": 5},
            "summary": {"type": "string", "order": 6},
        },
        "required": ["contact_id", "activity_type", "direction", "title"],
    },
)


LOG_CRM_ACTIVITIES_PROMPT = (
    "After the conversation has ended on a messenger platform (not after each message), "
    "or after sending an outbound message or email, call log_crm_activity with contact_id, type, direction, and a brief summary. "
    "Do this before finishing the task."
)


MANAGE_CRM_CONTACT_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="manage_crm_contact",
    description="Manage CRM contact for the current chat: create/patch, get_summary (with latest 2 deals/orders/activities), get_all_deals, get_all_orders, get_all_activities.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["create", "patch", "get_summary", "get_all_deals", "get_all_orders", "get_all_activities"], "order": 1},
            "args": {"type": "object", "description": "Contact fields; include contact_id for patch", "order": 2},
        },
        "required": ["op"],
    },
)

VERIFY_EMAIL_TOOL = ckit_cloudtool.CloudTool(
    strict=True,
    name="verify_email",
    description="Verify chat user's email: send_code sends a verification code, confirm_code checks it.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["send_code", "confirm_code"], "order": 1},
            "email": {"type": "string", "order": 2},
            "code": {"type": "string", "order": 3},
        },
        "required": ["op", "email", "code"],
        "additionalProperties": False,
    },
)

MANAGE_CRM_DEAL_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
    name="manage_crm_deal",
    description="Create or patch a CRM deal. Call op='help' to see available fields.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["help", "create", "patch"], "order": 1},
            "args": {"type": "object", "description": "Deal fields; include deal_id for patch", "order": 2},
        },
        "required": ["op"],
    },
)


async def find_contact_by_platform_id(http, ws_id: str, platform: str, identifier: str) -> Optional[str]:
    contacts = await ckit_erp.erp_table_data(
        http, "crm_contact", ws_id, erp_schema.CrmContact,
        filters=f"contact_platform_ids->{platform}:=:{identifier}", limit=1,
    )
    return contacts[0].contact_id if contacts else None


def _fmt_deal(d) -> str:
    return f"  {d.deal_id}: {d.deal_title} stage={d.deal_stage} value={d.deal_value} {d.deal_currency}"

def _fmt_order(o) -> str:
    return f"  {o.order_number or o.order_id}: {o.order_total} {o.order_currency} financial={o.order_financial_status} fulfillment={o.order_fulfillment_status}"

def _fmt_activity(a) -> str:
    return f"  {a.activity_id}: {a.activity_type} {a.activity_direction} — {a.activity_title}"

def _fmt_contact(c) -> list:
    lines = [f"Contact: {c.contact_first_name} {c.contact_last_name} ({c.contact_id})"]
    if c.contact_email: lines.append(f"Email: {c.contact_email}")
    if c.contact_phone: lines.append(f"Phone: {c.contact_phone}")
    if c.contact_tags: lines.append(f"Tags: {', '.join(c.contact_tags)}")
    if c.contact_bant_score >= 0: lines.append(f"BANT: {c.contact_bant_score}")
    if c.contact_notes: lines.append(f"Notes: {c.contact_notes[:200]}")
    return lines


CRM_SETUP_SCHEMA = [
    {
        "bs_name": "VERIFY_FROM",
        "bs_type": "string_long",
        "bs_default": "",
        "bs_group": "CRM",
        "bs_order": 1,
        "bs_importance": 0,
        "bs_description": "From address for identity verification emails sent to contacts (e.g. verify@yourdomain.com).",
    },
]


class IntegrationCrm:
    def __init__(self, rcx: 'ckit_bot_exec.RobotContext'):
        self.rcx = rcx
        self.ws_id = rcx.persona.ws_id

    async def _http(self, toolcall: ckit_cloudtool.FCloudtoolCall):
        return await self.rcx.fclient.use_http_on_behalf(self.rcx.persona.persona_id, toolcall.fcall_untrusted_key)

    async def handle_verify_email(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        op = args.get("op", "")
        email = args.get("email", "")
        pid = self.rcx.persona.persona_id
        ft_id = toolcall.fcall_ft_id
        http = await self._http(toolcall)
        try:
            async with http as h:
                if op == "send_code":
                    r = await h.execute(gql.gql("""mutation VerifyThreadEmailSend($pid: String!, $email: String!, $ft_id: String!) {
                        verify_thread_email_send(persona_id: $pid, email: $email, ft_id: $ft_id)
                    }"""), variable_values={"pid": pid, "email": email, "ft_id": ft_id})
                    return r["verify_thread_email_send"]
                if op == "confirm_code":
                    code = args.get("code", "")
                    if not code:
                        return "❌ code is required for confirm_code\n"
                    r = await h.execute(gql.gql("""mutation VerifyThreadEmailConfirm($pid: String!, $ft_id: String!, $email: String!, $code: String!) {
                        verify_thread_email_confirm(persona_id: $pid, ft_id: $ft_id, email: $email, code: $code)
                    }"""), variable_values={"pid": pid, "ft_id": ft_id, "email": email, "code": code})
                    return r["verify_thread_email_confirm"]
        except gql.transport.exceptions.TransportQueryError as e:
            return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, op)
        return f"❌ Unknown op: {op}\n"

    async def handle_manage_crm_contact(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        op = args.get("op", "")

        if op.startswith("get_"):
            t = self.rcx.latest_threads.get(toolcall.fcall_ft_id)
            searchable = t.thread_fields.ft_app_searchable if t and t.thread_fields.ft_app_searchable else None
            contact_id = None
            if searchable and "/" in searchable:
                platform, pid = searchable.split("/", 1)
                contact_id = await find_contact_by_platform_id(await self._http(toolcall), self.ws_id, platform, pid)
            if not contact_id:
                return "No verified contact in this chat. Use verify_crm_identity first.\n"
            http = await self._http(toolcall)
            try:
                if op == "get_summary":
                    contacts = await ckit_erp.erp_table_data(http, "crm_contact", self.ws_id, erp_schema.CrmContact, filters=f"contact_id:=:{contact_id}", limit=1)
                    if not contacts:
                        return f"Contact {contact_id} not found\n"
                    lines = _fmt_contact(contacts[0])
                    deals = await ckit_erp.erp_table_data(http, "crm_deal", self.ws_id, erp_schema.CrmDeal, filters=f"deal_contact_id:=:{contact_id}", limit=6)
                    orders = await ckit_erp.erp_table_data(http, "com_order", self.ws_id, erp_schema.ComOrder, filters=f"order_contact_id:=:{contact_id}", limit=6)
                    activities = await ckit_erp.erp_table_data(http, "crm_activity", self.ws_id, erp_schema.CrmActivity, filters=f"activity_contact_id:=:{contact_id}", limit=6)
                    def _cnt(rows):
                        return "5+" if len(rows) == 6 else str(len(rows))
                    if deals: lines += [f"\nDeals ({_cnt(deals)}):"] + [_fmt_deal(d) for d in deals[:2]]
                    if orders: lines += [f"\nOrders ({_cnt(orders)}):"] + [_fmt_order(o) for o in orders[:2]]
                    if activities: lines += [f"\nActivities ({_cnt(activities)}):"] + [_fmt_activity(a) for a in activities[:2]]
                    lines.append("\nUse get_all_deals/get_all_orders/get_all_activities for full lists.")
                    return "\n".join(lines) + "\n"
                if op == "get_all_deals":
                    rows = await ckit_erp.erp_table_data(http, "crm_deal", self.ws_id, erp_schema.CrmDeal, filters=f"deal_contact_id:=:{contact_id}", limit=50)
                    return "No deals.\n" if not rows else f"Deals ({len(rows)}):\n" + "\n".join(_fmt_deal(d) for d in rows) + "\n"
                if op == "get_all_orders":
                    rows = await ckit_erp.erp_table_data(http, "com_order", self.ws_id, erp_schema.ComOrder, filters=f"order_contact_id:=:{contact_id}", limit=50)
                    return "No orders.\n" if not rows else f"Orders ({len(rows)}):\n" + "\n".join(_fmt_order(o) for o in rows) + "\n"
                if op == "get_all_activities":
                    rows = await ckit_erp.erp_table_data(http, "crm_activity", self.ws_id, erp_schema.CrmActivity, filters=f"activity_contact_id:=:{contact_id}", limit=50)
                    return "No activities.\n" if not rows else f"Activities ({len(rows)}):\n" + "\n".join(_fmt_activity(a) for a in rows) + "\n"
            except gql.transport.exceptions.TransportQueryError as e:
                return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, op)
            return f"❌ Unknown op: {op}\n"

        fields = args.get("args", {})
        contact_id = str(fields.pop("contact_id", "") or "").strip()
        if "contact_email" in fields:
            t = self.rcx.latest_threads.get(toolcall.fcall_ft_id)
            verified = (t.thread_fields.ft_app_specific or {}).get("verified_email", "") if t else ""
            if fields["contact_email"].lower() != verified:
                return "❌ Email verification is required to store a contact email. Please ask the user to verify their email first.\n"
        try:
            if op == "create":
                new_id = await ckit_erp.erp_record_create(await self._http(toolcall), "crm_contact", self.ws_id, {"ws_id": self.ws_id, **fields})
                return f"✅ Created: {new_id}\n"
            elif op == "patch":
                if not contact_id:
                    return "❌ contact_id required for patch\n"
                await ckit_erp.erp_record_patch(await self._http(toolcall), "crm_contact", self.ws_id, contact_id, fields)
                return "✅ Updated\n"
            else:
                return f"❌ Unknown op: {op}\n"
        except gql.transport.exceptions.TransportQueryError as e:
            return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "fi_crm")

    async def handle_manage_crm_deal(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        op = args.get("op", "")
        if op == "help":
            return ckit_erp.format_table_meta_text("crm_deal", erp_schema.CrmDeal)
        fields = args.get("args", {})
        deal_id = str(fields.pop("deal_id", "") or "").strip()
        try:
            if op == "create":
                new_id = await ckit_erp.erp_record_create(await self._http(toolcall), "crm_deal", self.ws_id, {"ws_id": self.ws_id, **fields})
                return f"✅ Created: {new_id}\n"
            elif op == "patch":
                if not deal_id:
                    return "❌ deal_id required for patch\n"
                await ckit_erp.erp_record_patch(await self._http(toolcall), "crm_deal", self.ws_id, deal_id, fields)
                return "✅ Updated\n"
            else:
                return f"❌ Unknown op: {op}\n"
        except gql.transport.exceptions.TransportQueryError as e:
            return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "fi_crm")

    async def handle_log_crm_activity(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        contact_id = args.get("contact_id", "").strip()
        activity_type = args.get("activity_type", "").strip()
        direction = args.get("direction", "").strip()
        title = args.get("title", "").strip()
        if not contact_id or not activity_type or not direction or not title:
            return "❌ contact_id, activity_type, direction, and title are required"
        try:
            await ckit_erp.erp_record_create(await self._http(toolcall), "crm_activity", self.ws_id, {
                "ws_id": self.ws_id,
                "activity_title": title,
                "activity_type": activity_type,
                "activity_direction": direction,
                "activity_platform": args.get("platform", ""),
                "activity_contact_id": contact_id,
                "activity_ft_id": toolcall.fcall_ft_id,
                "activity_summary": args.get("summary", ""),
                "activity_occurred_ts": time.time(),
            })
            return "✅ Activity logged\n"
        except gql.transport.exceptions.TransportQueryError as e:
            return ckit_cloudtool.gql_error_4xx_to_model_reraise_5xx(e, "fi_crm")
