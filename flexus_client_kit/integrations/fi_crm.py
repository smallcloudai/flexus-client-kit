import time
from typing import Dict, Any, Optional

import gql.transport.exceptions

from flexus_client_kit import ckit_cloudtool, ckit_client, ckit_erp, erp_schema


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
    description="Create, patch, or delete a CRM contact. Call op='help' to see available fields.",
    parameters={
        "type": "object",
        "properties": {
            "op": {"type": "string", "enum": ["help", "create", "patch", "delete"], "order": 1},
            "args": {"type": "object", "description": "Contact fields; include contact_id for patch/delete", "order": 2},
        },
        "required": ["op"],
    },
)


async def find_contact_by_platform_id(fclient, ws_id: str, platform: str, identifier: str) -> Optional[str]:
    contacts = await ckit_erp.query_erp_table(
        fclient, "crm_contact", ws_id, erp_schema.CrmContact,
        filters=f"contact_platform_ids->{platform}:=:{identifier}", limit=1,
    )
    return contacts[0].contact_id if contacts else None


class IntegrationCrm:
    def __init__(self, fclient: ckit_client.FlexusClient, ws_id: str):
        self.fclient = fclient
        self.ws_id = ws_id

    async def handle_manage_crm_contact(self, toolcall: ckit_cloudtool.FCloudtoolCall, args: Dict[str, Any]) -> str:
        op = args.get("op", "")
        if op == "help":
            return ckit_erp.format_table_meta_text("crm_contact", erp_schema.CrmContact)
        fields = args.get("args", {})
        contact_id = fields.pop("contact_id", "").strip()
        try:
            if op == "create":
                new_id = await ckit_erp.create_erp_record(self.fclient, "crm_contact", self.ws_id, {"ws_id": self.ws_id, **fields})
                return f"✅ Contact created: {new_id}\n"
            elif op == "patch":
                if not contact_id:
                    return "❌ contact_id required for patch\n"
                await ckit_erp.patch_erp_record(self.fclient, "crm_contact", self.ws_id, contact_id, fields)
                return "✅ Contact updated\n"
            elif op == "delete":
                if not contact_id:
                    return "❌ contact_id required for delete\n"
                await ckit_erp.delete_erp_record(self.fclient, "crm_contact", self.ws_id, contact_id)
                return "✅ Contact deleted\n"
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
            await ckit_erp.create_erp_record(self.fclient, "crm_activity", self.ws_id, {
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
