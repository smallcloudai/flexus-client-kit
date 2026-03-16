from __future__ import annotations

import logging
from typing import Any, Dict, TYPE_CHECKING

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.integrations.facebook.client import FacebookAdsClient
from flexus_client_kit.integrations.facebook.exceptions import (
    FacebookAPIError,
    FacebookAuthError,
    FacebookValidationError,
)
from flexus_client_kit.integrations.facebook.insights import (
    get_account_insights, get_campaign_insights, get_adset_insights, get_ad_insights,
    create_async_report, get_async_report_status,
)

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

logger = logging.getLogger("meta_marketing_metrics")

# Use case: "Measure ad performance data with Marketing API"
# Covers all insights endpoints: account, campaign, ad set, ad level, async reports.
PROVIDER_NAME = "meta_marketing_metrics"

_HELP = """meta_marketing_metrics: Measure ad performance with Meta Marketing API.
op=help | status | list_methods | call(args={method_id, ...})

  get_account_insights(ad_account_id, days?, breakdowns?, metrics?, date_preset?)
  get_campaign_insights(campaign_id, days?, breakdowns?, metrics?, date_preset?)
  get_adset_insights(adset_id, days?, breakdowns?, metrics?, date_preset?)
  get_ad_insights(ad_id, days?, breakdowns?, metrics?, date_preset?)
  create_async_report(ad_account_id, level?, fields?, date_preset?, breakdowns?)
  get_async_report_status(report_run_id)
"""

_HANDLERS: Dict[str, Any] = {
    "get_account_insights": lambda c, a: get_account_insights(c, a.get("ad_account_id", ""), int(a.get("days", 30)), a.get("breakdowns"), a.get("metrics"), a.get("date_preset")),
    "get_campaign_insights": lambda c, a: get_campaign_insights(c, a.get("campaign_id", ""), int(a.get("days", 30)), a.get("breakdowns"), a.get("metrics"), a.get("date_preset")),
    "get_adset_insights": lambda c, a: get_adset_insights(c, a.get("adset_id", ""), int(a.get("days", 30)), a.get("breakdowns"), a.get("metrics"), a.get("date_preset")),
    "get_ad_insights": lambda c, a: get_ad_insights(c, a.get("ad_id", ""), int(a.get("days", 30)), a.get("breakdowns"), a.get("metrics"), a.get("date_preset")),
    "create_async_report": lambda c, a: create_async_report(c, a.get("ad_account_id", ""), a.get("level", "campaign"), a.get("fields"), a.get("date_preset", "last_30d"), a.get("breakdowns")),
    "get_async_report_status": lambda c, a: get_async_report_status(c, a.get("report_run_id", "")),
}


class IntegrationMetaMarketingMetrics:
    # Wraps FacebookAdsClient and delegates all insights/metrics operations.
    def __init__(self, rcx: "ckit_bot_exec.RobotContext"):
        self.client = FacebookAdsClient(rcx.fclient, rcx)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
        try:
            args = model_produced_args or {}
            op = str(args.get("op", "help")).strip()
            if op == "help":
                return _HELP
            if op == "status":
                return await self._status()
            if op == "list_methods":
                return "\n".join(sorted(_HANDLERS.keys()))
            if op != "call":
                return "Error: unknown op. Use help/status/list_methods/call."
            call_args = args.get("args") or {}
            method_id = str(call_args.get("method_id", "")).strip()
            if not method_id:
                return "Error: args.method_id required for op=call."
            handler = _HANDLERS.get(method_id)
            if handler is None:
                return f"Error: unknown method_id={method_id!r}. Use op=list_methods to see available methods."
            return await handler(self.client, call_args)
        except FacebookAuthError as e:
            return e.message
        except FacebookAPIError as e:
            logger.info("meta_marketing_metrics api error: %s", e)
            return e.format_for_user()
        except FacebookValidationError as e:
            return f"Error: {e.message}"
        except Exception as e:
            logger.error("Unexpected error in meta_marketing_metrics op=%s", (model_produced_args or {}).get("op"), exc_info=e)
            return f"Error: {e}"

    async def _status(self) -> str:
        try:
            auth_error = await self.client.ensure_auth()
            if auth_error:
                return auth_error
            return "meta_marketing_metrics: connected. Use op=help to see available operations."
        except (FacebookAuthError, FacebookAPIError, FacebookValidationError) as e:
            return e.message
        except Exception as e:
            logger.error("Unexpected error in meta_marketing_metrics status", exc_info=e)
            return f"Error: {e}"
