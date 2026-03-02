import json
from typing import Any, Dict

from flexus_client_kit import ckit_cloudtool

PROVIDER_NAME = "google_ads"
METHOD_IDS = [
    "google_ads.ad_group_ad.create.v1",
    "google_ads.asset.create.v1",
    "google_ads.campaigns.mutate.v1",
    "google_ads.googleads.search_stream.v1",
    "google_ads.keyword_planner.generate_forecast_metrics.v1",
    "google_ads.keyword_planner.generate_historical_metrics.v1",
    "google_ads.keyword_planner.generate_keyword_ideas.v1",
    "google_ads.keywordplan.generate_historical_metrics.v1",
    "google_ads.search_stream.query.v1",
]


class IntegrationGoogleAds:
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
                f"methods: {', '.join(METHOD_IDS)}"
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
        return json.dumps({
            "ok": False,
            "error_code": "AUTH_REQUIRED",
            "provider": PROVIDER_NAME,
            "message": "Connect your Google Ads account via the integrations panel. Google Ads API requires OAuth2 user authorization and a developer token.",
        }, indent=2, ensure_ascii=False)
