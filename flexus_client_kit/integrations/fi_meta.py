import json
from typing import Any, Dict

from flexus_client_kit import ckit_cloudtool

PROVIDER_NAME = 'meta'
METHOD_IDS = [
    "meta.adcreatives.create.v1",
    "meta.adcreatives.list.v1",
    "meta.adimages.create.v1",
    "meta.ads_insights.get.v1",
    "meta.adsets.create.v1",
    "meta.campaigns.create.v1",
    "meta.insights.query.v1",
]


class IntegrationMeta:
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
                "op=help\n"
                "op=status\n"
                "op=list_methods\n"
                "op=call(args={method_id: ...})\n"
                f"known_method_ids={len(METHOD_IDS)}"
            )
        if op == "status":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "status": "available", "method_count": len(METHOD_IDS)}, indent=2, ensure_ascii=False)
        if op == "list_methods":
            return json.dumps({"ok": True, "provider": PROVIDER_NAME, "method_ids": METHOD_IDS}, indent=2, ensure_ascii=False)
        method_id = str((args.get("args") or {}).get("method_id", "")).strip()
        return json.dumps({"ok": False, "error_code": "INTEGRATION_UNAVAILABLE", "provider": PROVIDER_NAME, "method_id": method_id, "message": "We don't have this integration, but we do have a frog and it can catch insects =)"}, indent=2, ensure_ascii=False)
