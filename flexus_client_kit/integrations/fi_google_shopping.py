import json
from typing import Any, Dict

from flexus_client_kit import ckit_cloudtool

PROVIDER_NAME = "google_shopping"
METHOD_IDS = [
    "google_shopping.reports.search_topic_trends.v1",
]


class IntegrationGoogleShopping:
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
                "note: requires Google Merchant Center OAuth connection"
            )
        if op == "status":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return json.dumps({"ok": False, "error_code": "METHOD_UNKNOWN", "method_id": method_id}, indent=2, ensure_ascii=False)
        return await self._dispatch(method_id, call_args)

    async def _dispatch(self, method_id: str, args: Dict[str, Any]) -> str:
        if method_id == "google_shopping.reports.search_topic_trends.v1":
            return json.dumps({
                "ok": False,
                "error_code": "AUTH_REQUIRED",
                "provider": PROVIDER_NAME,
                "method_id": method_id,
                "message": (
                    "Google Merchant Center Insights API requires OAuth with a Google account "
                    "that has Merchant Center access. Connect your account via the integrations panel. "
                    "This API provides search topic trend data — what consumers search for on Google Shopping."
                ),
            }, indent=2, ensure_ascii=False)
        return json.dumps({"ok": False, "error_code": "METHOD_UNIMPLEMENTED", "method_id": method_id}, indent=2, ensure_ascii=False)
