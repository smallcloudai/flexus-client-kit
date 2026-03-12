import json
import logging
import os
from typing import Any, Dict, Optional

from flexus_client_kit import ckit_cloudtool


logger = logging.getLogger("lucid")

PROVIDER_NAME = "lucid"
METHOD_IDS = [
    "lucid.demand.projects.list.v1",
    "lucid.demand.projects.create.v1",
    "lucid.demand.projects.get.v1",
    "lucid.demand.quotas.status.get.v1",
]

# Lucid Marketplace / Cint Marketplace access is provisioned by consultant-led onboarding.
# Required values:
# - LUCID_API_KEY
# Optional values:
# - LUCID_ENV=sandbox to target the sandbox endpoint
# Public documentation confirms auth, environments, and demand/supply concepts, but the concrete
# demand-side endpoint map is distributed through the consultant-led guide and Postman collection.
# This file therefore exposes explicit fail-fast method contracts until those exact resource paths
# are handed to Flexus by the provisioning team.
LUCID_SETUP_SCHEMA: list[dict[str, Any]] = []


class IntegrationLucid:
    def __init__(self, rcx=None) -> None:
        self.rcx = rcx

    def _api_key(self) -> str:
        return str(os.environ.get("LUCID_API_KEY", "")).strip()

    def _status(self) -> str:
        env = str(os.environ.get("LUCID_ENV", "production")).strip().lower() or "production"
        return json.dumps(
            {
                "ok": True,
                "provider": PROVIDER_NAME,
                "status": "provisioning_needed" if self._api_key() else "missing_credentials",
                "method_count": len(METHOD_IDS),
                "auth_type": "api_key_header",
                "required_env": ["LUCID_API_KEY"],
                "optional_env": ["LUCID_ENV"],
                "environment": env,
                "products": ["Marketplace Demand API"],
                "message": "Exact demand endpoint paths come from the Lucid/Cint consultant guide and Postman collection.",
            },
            indent=2,
            ensure_ascii=False,
        )

    def _help(self) -> str:
        return (
            f"provider={PROVIDER_NAME}\n"
            "op=help | status | list_methods | call\n"
            f"methods: {', '.join(METHOD_IDS)}\n"
            "notes:\n"
            "- Authentication uses Authorization API key headers.\n"
            "- Sandbox and production environments are known, but exact demand endpoints must be sourced from the provisioning guide.\n"
            "- This integration fails fast instead of inventing endpoint paths.\n"
        )

    def _error(self, method_id: str, code: str, message: str, **extra: Any) -> str:
        payload: Dict[str, Any] = {
            "ok": False,
            "provider": PROVIDER_NAME,
            "method_id": method_id,
            "error_code": code,
            "message": message,
        }
        payload.update(extra)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        args = model_produced_args or {}
        op = str(args.get("op", "help")).strip()
        if op == "help":
            return self._help()
        if op == "status":
            return self._status()
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        if op != "call":
            return "Error: unknown op. Use help/status/list_methods/call."
        call_args = args.get("args") or {}
        method_id = str(call_args.get("method_id", "")).strip()
        if not method_id:
            return "Error: args.method_id required for op=call."
        if method_id not in METHOD_IDS:
            return self._error(method_id, "METHOD_UNKNOWN", "Unknown Lucid method.")
        if not self._api_key():
            return self._error(method_id, "AUTH_MISSING", "Set LUCID_API_KEY in the runtime environment.")
        return self._error(
            method_id,
            "OFFICIAL_DOCS_GAP",
            "Lucid demand endpoint paths are not published in a fetchable public reference. Use the consultant-provided Postman collection and then replace this placeholder with the exact resource paths.",
            required_inputs=["consultant_postman_collection", "environment_base_url", "approved_api_key"],
        )
