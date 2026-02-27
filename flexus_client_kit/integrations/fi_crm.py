import time
from typing import Dict, Any, Optional

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

LOG_CRM_ACTIVITIES_PROMPT = "After each conversation in a messenger platform or outbound message or email, call log_crm_activity with the contact_id, type, direction, and a brief summary. Do this before finishing the task."


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
        except Exception as e:
            return f"❌ {e}\n"
