from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.integrations._fi_meta_helpers import (
    FacebookAdsClient,
    FacebookAPIError,
    FacebookAuthError,
    FacebookValidationError,
    InsightsDatePreset,
)

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

logger = logging.getLogger("meta_marketing_metrics")

# Use case: "Measure ad performance data with Marketing API"
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

_DEFAULT_METRICS = "impressions,clicks,spend,reach,frequency,ctr,cpc,cpm,actions,cost_per_action_type"


def _days_to_preset(days: int) -> str:
    if days <= 1:
        return InsightsDatePreset.TODAY.value
    if days <= 7:
        return InsightsDatePreset.LAST_7D.value
    if days <= 14:
        return InsightsDatePreset.LAST_14D.value
    if days <= 28:
        return InsightsDatePreset.LAST_28D.value
    if days <= 30:
        return InsightsDatePreset.LAST_30D.value
    if days <= 90:
        return InsightsDatePreset.LAST_90D.value
    return InsightsDatePreset.MAXIMUM.value


def _format_insights(data: Dict[str, Any], label: str) -> str:
    result = f"Insights for {label}:\n\n"
    items = data.get("data", [])
    if not items:
        return f"No insights data found for {label}\n"
    for item in items:
        result += f"  Date: {item.get('date_start', 'N/A')} - {item.get('date_stop', 'N/A')}\n"
        result += f"  Impressions: {item.get('impressions', '0')}\n"
        result += f"  Clicks: {item.get('clicks', '0')}\n"
        result += f"  Spend: ${item.get('spend', '0')}\n"
        result += f"  Reach: {item.get('reach', '0')}\n"
        result += f"  CTR: {item.get('ctr', '0')}%\n"
        result += f"  CPC: ${item.get('cpc', '0')}\n"
        result += f"  CPM: ${item.get('cpm', '0')}\n"
        actions = item.get("actions", [])
        if actions:
            result += "  Actions:\n"
            for action in actions[:5]:
                result += f"    - {action.get('action_type', 'N/A')}: {action.get('value', '0')}\n"
        result += "\n"
    return result


async def _get_account_insights(client: FacebookAdsClient, ad_account_id: str, days: int, breakdowns: Optional[List[str]], metrics: Optional[str], date_preset: Optional[str]) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    if client.is_test_mode:
        return f"Account Insights for {ad_account_id} (last {days} days):\n  Impressions: 15,000\n  Clicks: 450\n  Spend: $120.00\n  CTR: 3.0%\n"
    params: Dict[str, Any] = {"fields": metrics or _DEFAULT_METRICS, "level": "account", "limit": 50}
    params["date_preset"] = date_preset or _days_to_preset(days)
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    data = await client.request("GET", f"{ad_account_id}/insights", params=params)
    return _format_insights(data, ad_account_id)


async def _get_campaign_insights(client: FacebookAdsClient, campaign_id: str, days: int, breakdowns: Optional[List[str]], metrics: Optional[str], date_preset: Optional[str]) -> str:
    if not campaign_id:
        return "ERROR: campaign_id required"
    if client.is_test_mode:
        return f"Campaign Insights for {campaign_id} (last {days} days):\n  Impressions: 10,000\n  Clicks: 300\n  Spend: $80.00\n  CTR: 3.0%\n"
    params: Dict[str, Any] = {"fields": metrics or _DEFAULT_METRICS, "limit": 50}
    params["date_preset"] = date_preset or _days_to_preset(days)
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    data = await client.request("GET", f"{campaign_id}/insights", params=params)
    return _format_insights(data, campaign_id)


async def _get_adset_insights(client: FacebookAdsClient, adset_id: str, days: int, breakdowns: Optional[List[str]], metrics: Optional[str], date_preset: Optional[str]) -> str:
    if not adset_id:
        return "ERROR: adset_id required"
    if client.is_test_mode:
        return f"Ad Set Insights for {adset_id} (last {days} days):\n  Impressions: 5,000\n  Clicks: 150\n  Spend: $40.00\n"
    params: Dict[str, Any] = {"fields": metrics or _DEFAULT_METRICS, "limit": 50}
    params["date_preset"] = date_preset or _days_to_preset(days)
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    data = await client.request("GET", f"{adset_id}/insights", params=params)
    return _format_insights(data, adset_id)


async def _get_ad_insights(client: FacebookAdsClient, ad_id: str, days: int, breakdowns: Optional[List[str]], metrics: Optional[str], date_preset: Optional[str]) -> str:
    if not ad_id:
        return "ERROR: ad_id required"
    if client.is_test_mode:
        return f"Ad Insights for {ad_id} (last {days} days):\n  Impressions: 2,000\n  Clicks: 60\n  Spend: $15.00\n"
    params: Dict[str, Any] = {"fields": metrics or _DEFAULT_METRICS, "limit": 50}
    params["date_preset"] = date_preset or _days_to_preset(days)
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    data = await client.request("GET", f"{ad_id}/insights", params=params)
    return _format_insights(data, ad_id)


async def _create_async_report(client: FacebookAdsClient, ad_account_id: str, level: str, fields: Optional[str], date_preset: str, breakdowns: Optional[List[str]]) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    valid_levels = ["account", "campaign", "adset", "ad"]
    if level not in valid_levels:
        return f"ERROR: level must be one of: {', '.join(valid_levels)}"
    if client.is_test_mode:
        return f"Async report created:\n  Report Run ID: mock_report_run_123\n  Level: {level}\n  Use get_async_report_status to check progress.\n"
    data: Dict[str, Any] = {"level": level, "fields": fields or _DEFAULT_METRICS, "date_preset": date_preset}
    if breakdowns:
        data["breakdowns"] = ",".join(breakdowns)
    result = await client.request("POST", f"{ad_account_id}/insights", data=data)
    report_run_id = result.get("report_run_id")
    return f"Async report created:\n  Report Run ID: {report_run_id}\n  Level: {level}\n  Date Preset: {date_preset}\n" if report_run_id else f"Failed to create report. Response: {result}"


async def _get_async_report_status(client: FacebookAdsClient, report_run_id: str) -> str:
    if not report_run_id:
        return "ERROR: report_run_id required"
    if client.is_test_mode:
        return f"Report {report_run_id}: Job Completed (100%)\n"
    data = await client.request("GET", report_run_id, params={"fields": "id,async_status,async_percent_completion,date_start,date_stop"})
    status = data.get("async_status", "Unknown")
    pct = data.get("async_percent_completion", 0)
    result = f"Report {report_run_id}:\n  Status: {status} ({pct}%)\n"
    if data.get("date_start"):
        result += f"  Date Range: {data['date_start']} - {data.get('date_stop', 'N/A')}\n"
    return result


_HANDLERS: Dict[str, Any] = {
    "get_account_insights": lambda c, a: _get_account_insights(c, a.get("ad_account_id", ""), int(a.get("days", 30)), a.get("breakdowns"), a.get("metrics"), a.get("date_preset")),
    "get_campaign_insights": lambda c, a: _get_campaign_insights(c, a.get("campaign_id", ""), int(a.get("days", 30)), a.get("breakdowns"), a.get("metrics"), a.get("date_preset")),
    "get_adset_insights": lambda c, a: _get_adset_insights(c, a.get("adset_id", ""), int(a.get("days", 30)), a.get("breakdowns"), a.get("metrics"), a.get("date_preset")),
    "get_ad_insights": lambda c, a: _get_ad_insights(c, a.get("ad_id", ""), int(a.get("days", 30)), a.get("breakdowns"), a.get("metrics"), a.get("date_preset")),
    "create_async_report": lambda c, a: _create_async_report(c, a.get("ad_account_id", ""), a.get("level", "campaign"), a.get("fields"), a.get("date_preset", "last_30d"), a.get("breakdowns")),
    "get_async_report_status": lambda c, a: _get_async_report_status(c, a.get("report_run_id", "")),
}


class IntegrationMetaMarketingMetrics:
    def __init__(self, rcx: "ckit_bot_exec.RobotContext"):
        self.client = FacebookAdsClient(rcx.fclient, rcx)

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
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
                return f"Error: unknown method_id={method_id!r}. Use op=list_methods."
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
