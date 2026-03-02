import json
import logging
from typing import Any, Dict

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("google_calendar")

PROVIDER_NAME = "google_calendar"
METHOD_IDS = [
    "google_calendar.events.insert.v1",
    "google_calendar.events.list.v1",
]

_AUTH_REQUIRED = json.dumps(
    {
        "ok": False,
        "error_code": "AUTH_REQUIRED",
        "provider": PROVIDER_NAME,
        "message": (
            "Google Calendar requires per-user OAuth authentication. "
            "Connect your Google account via the Flexus integrations settings first."
        ),
    },
    indent=2,
    ensure_ascii=False,
)


class IntegrationGoogleCalendar:
    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return (
                f"provider={PROVIDER_NAME}\n"
                "op=help | status | list_methods | call\n"
                f"methods: {', '.join(METHOD_IDS)}\n"
                "note: Requires Google OAuth per-user authentication."
            )
        if op == "status":
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "auth_required",
                    "method_count": len(METHOD_IDS),
                    "message": "Connect your Google account to use Google Calendar.",
                },
                indent=2,
                ensure_ascii=False,
            )
        if op == "list_methods":
            return json.dumps(
                {"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS},
                indent=2,
                ensure_ascii=False,
            )
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        return _AUTH_REQUIRED
