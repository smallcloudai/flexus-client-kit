import json
import logging
from typing import Any, Dict

from flexus_client_kit import ckit_cloudtool

logger = logging.getLogger("usertesting")

PROVIDER_NAME = "usertesting"
METHOD_IDS = [
    "usertesting.tests.create.v1",
    "usertesting.tests.sessions.list.v1",
    "usertesting.results.transcript.get.v1",
]

_ENTERPRISE_RESPONSE = json.dumps(
    {
        "ok": False,
        "error_code": "INTEGRATION_ENTERPRISE",
        "provider": PROVIDER_NAME,
        "message": "UserTesting requires an enterprise account. Contact UserTesting sales to get API access.",
    },
    indent=2,
    ensure_ascii=False,
)


class IntegrationUsertesting:
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
                "note: Enterprise-only provider. Contact UserTesting sales for API access."
            )
        if op == "status":
            return json.dumps(
                {
                    "ok": True,
                    "provider": PROVIDER_NAME,
                    "status": "enterprise_only",
                    "method_count": len(METHOD_IDS),
                    "message": "UserTesting requires an enterprise account. Contact UserTesting sales to get API access.",
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
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps(
                {"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id},
                indent=2,
                ensure_ascii=False,
            )
        return _ENTERPRISE_RESPONSE
