from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from flexus_client_kit.integrations.facebook.models import InsightsBreakdown, InsightsDatePreset

if TYPE_CHECKING:
    from flexus_client_kit.integrations.facebook.client import FacebookAdsClient

logger = logging.getLogger("facebook.operations.insights")

DEFAULT_METRICS = "impressions,clicks,spend,reach,frequency,ctr,cpc,cpm,actions,cost_per_action_type,video_avg_time_watched_actions,video_p100_watched_actions"


def _format_insights_data(data: Dict[str, Any], label: str) -> str:
    result = f"Insights for {label}:\n\n"
    items = data.get("data", [])
    if not items:
        return f"No insights data found for {label}\n"
    for item in items:
        result += f"  Date: {item.get('date_start', 'N/A')} — {item.get('date_stop', 'N/A')}\n"
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
        breakdowns = item.get("age") or item.get("gender") or item.get("country") or item.get("publisher_platform")
        if breakdowns:
            result += f"  Breakdown: {breakdowns}\n"
        result += "\n"
    return result


async def get_account_insights(
    client: "FacebookAdsClient",
    ad_account_id: str,
    days: int = 30,
    breakdowns: Optional[List[str]] = None,
    metrics: Optional[str] = None,
    date_preset: Optional[str] = None,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if client.is_test_mode:
        return f"Account Insights for {ad_account_id} (last {days} days):\n  Impressions: 15,000\n  Clicks: 450\n  Spend: $120.00\n  CTR: 3.0%\n"
    params: Dict[str, Any] = {
        "fields": metrics or DEFAULT_METRICS,
        "level": "account",
        "limit": 50,
    }
    if date_preset:
        params["date_preset"] = date_preset
    else:
        params["date_preset"] = _days_to_preset(days)
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    data = await client.request("GET", f"{ad_account_id}/insights", params=params)
    return _format_insights_data(data, ad_account_id)


async def get_campaign_insights(
    client: "FacebookAdsClient",
    campaign_id: str,
    days: int = 30,
    breakdowns: Optional[List[str]] = None,
    metrics: Optional[str] = None,
    date_preset: Optional[str] = None,
) -> str:
    if not campaign_id:
        return "ERROR: campaign_id is required"
    if client.is_test_mode:
        return f"Campaign Insights for {campaign_id} (last {days} days):\n  Impressions: 10,000\n  Clicks: 300\n  Spend: $80.00\n  CTR: 3.0%\n"
    params: Dict[str, Any] = {
        "fields": metrics or DEFAULT_METRICS,
        "limit": 50,
    }
    if date_preset:
        params["date_preset"] = date_preset
    else:
        params["date_preset"] = _days_to_preset(days)
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    data = await client.request("GET", f"{campaign_id}/insights", params=params)
    return _format_insights_data(data, campaign_id)


async def get_adset_insights(
    client: "FacebookAdsClient",
    adset_id: str,
    days: int = 30,
    breakdowns: Optional[List[str]] = None,
    metrics: Optional[str] = None,
    date_preset: Optional[str] = None,
) -> str:
    if not adset_id:
        return "ERROR: adset_id is required"
    if client.is_test_mode:
        return f"Ad Set Insights for {adset_id} (last {days} days):\n  Impressions: 5,000\n  Clicks: 150\n  Spend: $40.00\n  CTR: 3.0%\n"
    params: Dict[str, Any] = {
        "fields": metrics or DEFAULT_METRICS,
        "limit": 50,
    }
    if date_preset:
        params["date_preset"] = date_preset
    else:
        params["date_preset"] = _days_to_preset(days)
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    data = await client.request("GET", f"{adset_id}/insights", params=params)
    return _format_insights_data(data, adset_id)


async def get_ad_insights(
    client: "FacebookAdsClient",
    ad_id: str,
    days: int = 30,
    breakdowns: Optional[List[str]] = None,
    metrics: Optional[str] = None,
    date_preset: Optional[str] = None,
) -> str:
    if not ad_id:
        return "ERROR: ad_id is required"
    if client.is_test_mode:
        return f"Ad Insights for {ad_id} (last {days} days):\n  Impressions: 2,000\n  Clicks: 60\n  Spend: $15.00\n  CTR: 3.0%\n"
    params: Dict[str, Any] = {
        "fields": metrics or DEFAULT_METRICS,
        "limit": 50,
    }
    if date_preset:
        params["date_preset"] = date_preset
    else:
        params["date_preset"] = _days_to_preset(days)
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    data = await client.request("GET", f"{ad_id}/insights", params=params)
    return _format_insights_data(data, ad_id)


async def create_async_report(
    client: "FacebookAdsClient",
    ad_account_id: str,
    level: str = "campaign",
    fields: Optional[str] = None,
    date_preset: str = "last_30d",
    breakdowns: Optional[List[str]] = None,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    valid_levels = ["account", "campaign", "adset", "ad"]
    if level not in valid_levels:
        return f"ERROR: level must be one of: {', '.join(valid_levels)}"
    if client.is_test_mode:
        return f"Async report created:\n  Report Run ID: mock_report_run_123\n  Status: Job Created\n  Use get_async_report_status to check progress.\n"
    data: Dict[str, Any] = {
        "level": level,
        "fields": fields or DEFAULT_METRICS,
        "date_preset": date_preset,
    }
    if breakdowns:
        data["breakdowns"] = ",".join(breakdowns)
    result = await client.request("POST", f"{ad_account_id}/insights", data=data)
    report_run_id = result.get("report_run_id")
    if not report_run_id:
        return f"Failed to create async report. Response: {result}"
    return f"Async report created:\n  Report Run ID: {report_run_id}\n  Level: {level}\n  Date Preset: {date_preset}\n  Use get_async_report_status(report_run_id='{report_run_id}') to check progress.\n"


async def get_async_report_status(
    client: "FacebookAdsClient",
    report_run_id: str,
) -> str:
    if not report_run_id:
        return "ERROR: report_run_id is required"
    if client.is_test_mode:
        return f"Report {report_run_id} status: Job Completed (100%)\n  Use insights endpoint with async_status filter to retrieve results.\n"
    data = await client.request(
        "GET", report_run_id,
        params={"fields": "id,async_status,async_percent_completion,date_start,date_stop"},
    )
    status = data.get("async_status", "Unknown")
    pct = data.get("async_percent_completion", 0)
    result = f"Report {report_run_id}:\n"
    result += f"  Status: {status} ({pct}%)\n"
    if data.get("date_start"):
        result += f"  Date Range: {data['date_start']} — {data.get('date_stop', 'N/A')}\n"
    if status == "Job Completed":
        result += f"\n  Report is ready. Retrieve results at:\n  GET /{report_run_id}/insights\n"
    return result


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
