"""
Facebook Campaign Operations

Operations for creating and managing advertising campaigns.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..models import Campaign, CampaignObjective, CampaignStatus, Insights
from ..utils import format_currency, validate_budget, normalize_insights_data
from ..exceptions import FacebookAPIError, FacebookValidationError

if TYPE_CHECKING:
    from ..client import FacebookAdsClient

logger = logging.getLogger("facebook.operations.campaigns")

# Fields to request from API
CAMPAIGN_FIELDS = "id,name,status,objective,daily_budget,lifetime_budget"
CAMPAIGN_DETAIL_FIELDS = (
    "id,name,status,objective,daily_budget,lifetime_budget,"
    "special_ad_categories,created_time,updated_time"
)


async def list_campaigns(
    client: "FacebookAdsClient",
    ad_account_id: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> str:
    """
    List campaigns for an ad account.

    Args:
        client: Authenticated Facebook client
        ad_account_id: Ad account ID (uses client default if not provided)
        status_filter: Filter by status (ACTIVE, PAUSED, ARCHIVED)

    Returns:
        Formatted string with campaign list
    """
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id parameter required for list_campaigns"

    if client.is_test_mode:
        return _mock_list_campaigns()

    params: Dict[str, Any] = {"fields": CAMPAIGN_FIELDS, "limit": 50}
    if status_filter:
        params["effective_status"] = f"['{status_filter}']"

    data = await client.get(f"{account_id}/campaigns", params=params)
    campaigns = data.get("data", [])

    if not campaigns:
        return "No campaigns found."

    result = f"Found {len(campaigns)} campaign{'s' if len(campaigns) != 1 else ''}:\n"
    for c in campaigns:
        budget_str = ""
        if c.get("daily_budget"):
            budget_str = f", Daily: {format_currency(int(c['daily_budget']))}"
        elif c.get("lifetime_budget"):
            budget_str = f", Lifetime: {format_currency(int(c['lifetime_budget']))}"

        result += f"  {c['name']} (ID: {c['id']}) - {c['status']}{budget_str}\n"

    return result


async def create_campaign(
    client: "FacebookAdsClient",
    ad_account_id: str,
    name: str,
    objective: str,
    status: str = "PAUSED",
    daily_budget: Optional[int] = None,
    lifetime_budget: Optional[int] = None,
    special_ad_categories: Optional[List[str]] = None,
) -> str:
    """
    Create a new campaign.

    Args:
        client: Authenticated Facebook client
        ad_account_id: Ad account ID
        name: Campaign name
        objective: Campaign objective (OUTCOME_TRAFFIC, etc.)
        status: Initial status (default PAUSED)
        daily_budget: Daily budget in cents
        lifetime_budget: Lifetime budget in cents
        special_ad_categories: Special ad categories if applicable

    Returns:
        Formatted result string
    """
    if not ad_account_id:
        return "ERROR: ad_account_id parameter required for create_campaign"
    if not name:
        return "ERROR: name parameter required for create_campaign"

    # Validate objective
    try:
        CampaignObjective(objective)
    except ValueError:
        valid = [o.value for o in CampaignObjective]
        return f"ERROR: Invalid objective. Must be one of: {', '.join(valid)}"

    # Validate budget if provided
    if daily_budget:
        try:
            daily_budget = validate_budget(daily_budget)
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"

    if lifetime_budget:
        try:
            lifetime_budget = validate_budget(lifetime_budget)
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"

    if client.is_test_mode:
        return _mock_create_campaign(name, objective, status, daily_budget)

    payload: Dict[str, Any] = {
        "name": name,
        "objective": objective,
        "status": status,
        "special_ad_categories": special_ad_categories or [],
    }
    if daily_budget:
        payload["daily_budget"] = daily_budget
    if lifetime_budget:
        payload["lifetime_budget"] = lifetime_budget

    result = await client.post(f"{ad_account_id}/campaigns", data=payload)

    campaign_id = result.get("id")
    if not campaign_id:
        return f"Failed to create campaign. Response: {result}"

    output = f"Campaign created: {name} (ID: {campaign_id})\n"
    output += f"   Status: {status}, Objective: {objective}\n"
    if daily_budget:
        output += f"   Daily Budget: {format_currency(daily_budget)}\n"
    if lifetime_budget:
        output += f"   Lifetime Budget: {format_currency(lifetime_budget)}\n"

    return output


async def update_campaign(
    client: "FacebookAdsClient",
    campaign_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    daily_budget: Optional[int] = None,
    lifetime_budget: Optional[int] = None,
) -> str:
    """
    Update an existing campaign.

    Args:
        client: Authenticated Facebook client
        campaign_id: Campaign ID to update
        name: New name (optional)
        status: New status (optional)
        daily_budget: New daily budget in cents (optional)
        lifetime_budget: New lifetime budget in cents (optional)

    Returns:
        Formatted result string
    """
    if not campaign_id:
        return "ERROR: campaign_id parameter is required"

    if not any([name, status, daily_budget, lifetime_budget]):
        return "ERROR: At least one field to update is required (name, status, daily_budget, or lifetime_budget)"

    if status and status not in ["ACTIVE", "PAUSED"]:
        return "ERROR: status must be either 'ACTIVE' or 'PAUSED'"

    if daily_budget:
        try:
            daily_budget = validate_budget(daily_budget)
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"

    if lifetime_budget:
        try:
            lifetime_budget = validate_budget(lifetime_budget)
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"

    updates = []
    if name:
        updates.append(f"name -> {name}")
    if status:
        updates.append(f"status -> {status}")
    if daily_budget:
        updates.append(f"daily_budget -> {format_currency(daily_budget)}")
    if lifetime_budget:
        updates.append(f"lifetime_budget -> {format_currency(lifetime_budget)}")

    if client.is_test_mode:
        return f"Campaign {campaign_id} updated:\n" + "\n".join(f"   - {u}" for u in updates)

    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if status:
        data["status"] = status
    if daily_budget is not None:
        data["daily_budget"] = daily_budget
    if lifetime_budget is not None:
        data["lifetime_budget"] = lifetime_budget

    result = await client.post(campaign_id, data=data)

    if result.get("success"):
        return f"Campaign {campaign_id} updated:\n" + "\n".join(f"   - {u}" for u in updates)
    else:
        return f"Failed to update campaign. Response: {result}"


async def duplicate_campaign(
    client: "FacebookAdsClient",
    campaign_id: str,
    new_name: str,
    ad_account_id: Optional[str] = None,
) -> str:
    """
    Create a copy of an existing campaign.

    The new campaign is created with PAUSED status.

    Args:
        client: Authenticated Facebook client
        campaign_id: Campaign ID to duplicate
        new_name: Name for the new campaign
        ad_account_id: Target ad account ID (optional)

    Returns:
        Formatted result string
    """
    if not campaign_id:
        return "ERROR: campaign_id parameter is required"
    if not new_name:
        return "ERROR: new_name parameter is required"

    if client.is_test_mode:
        return _mock_duplicate_campaign(campaign_id, new_name)

    # Fetch original campaign settings
    original = await client.get(
        campaign_id,
        params={"fields": "name,objective,status,daily_budget,lifetime_budget,special_ad_categories"}
    )

    # Use provided ad_account_id or client default
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id required for duplicate_campaign"

    create_data: Dict[str, Any] = {
        "name": new_name,
        "objective": original["objective"],
        "status": "PAUSED",
        "special_ad_categories": original.get("special_ad_categories", []),
    }
    if "daily_budget" in original:
        create_data["daily_budget"] = original["daily_budget"]
    if "lifetime_budget" in original:
        create_data["lifetime_budget"] = original["lifetime_budget"]

    new_campaign = await client.post(f"{account_id}/campaigns", data=create_data)

    return f"""Campaign duplicated successfully!

Original Campaign ID: {campaign_id}
New Campaign ID: {new_campaign.get('id')}
New Campaign Name: {new_name}
Status: PAUSED (activate when ready)

Note: Only the campaign was copied. To copy ad sets and ads, use the Facebook Ads Manager UI.
"""


async def archive_campaign(
    client: "FacebookAdsClient",
    campaign_id: str,
) -> str:
    """
    Archive (soft delete) a campaign.

    Args:
        client: Authenticated Facebook client
        campaign_id: Campaign ID to archive

    Returns:
        Formatted result string
    """
    if not campaign_id:
        return "ERROR: campaign_id parameter is required"

    if client.is_test_mode:
        return f"Campaign {campaign_id} archived successfully.\n\nThe campaign is now hidden from active views but can be restored if needed."

    result = await client.post(campaign_id, data={"status": "ARCHIVED"})

    if result.get("success"):
        return f"Campaign {campaign_id} archived successfully.\n\nThe campaign is now hidden from active views but can be restored if needed."
    else:
        return f"Failed to archive campaign. Response: {result}"


async def bulk_update_campaigns(
    client: "FacebookAdsClient",
    campaigns: List[Dict[str, Any]],
) -> str:
    """
    Update multiple campaigns at once.

    Args:
        client: Authenticated Facebook client
        campaigns: List of dicts with 'id' and fields to update

    Returns:
        Formatted result string
    """
    if not campaigns:
        return "ERROR: campaigns parameter is required (list of {id, ...fields})"
    if not isinstance(campaigns, list):
        return "ERROR: campaigns must be a list"
    if len(campaigns) > 50:
        return "ERROR: Maximum 50 campaigns can be updated at once"

    if client.is_test_mode:
        results = []
        for camp in campaigns:
            campaign_id = camp.get("id", "unknown")
            status = camp.get("status", "unchanged")
            results.append(f"   {campaign_id} -> {status}")
        return f"Bulk update completed for {len(campaigns)} campaigns:\n" + "\n".join(results)

    results = []
    errors = []

    for camp in campaigns:
        campaign_id = camp.get("id")
        if not campaign_id:
            errors.append("Missing campaign ID in one of the campaigns")
            continue

        data: Dict[str, Any] = {}
        if "name" in camp:
            data["name"] = camp["name"]
        if "status" in camp:
            if camp["status"] not in ["ACTIVE", "PAUSED", "ARCHIVED"]:
                errors.append(f"{campaign_id}: Invalid status")
                continue
            data["status"] = camp["status"]
        if "daily_budget" in camp:
            try:
                data["daily_budget"] = validate_budget(camp["daily_budget"])
            except FacebookValidationError as e:
                errors.append(f"{campaign_id}: {e.message}")
                continue

        if not data:
            errors.append(f"{campaign_id}: No fields to update")
            continue

        try:
            result = await client.post(campaign_id, data=data)

            if result.get("success"):
                updates = ", ".join([f"{k}={v}" for k, v in data.items()])
                results.append(f"   {campaign_id}: {updates}")
            else:
                errors.append(f"{campaign_id}: Update failed")

        except FacebookAPIError as e:
            errors.append(f"{campaign_id}: {e.message}")
        except Exception as e:
            errors.append(f"{campaign_id}: {str(e)}")

    output = f"Bulk update completed:\n\n"
    output += f"Success: {len(results)}\n"
    output += f"Errors: {len(errors)}\n\n"

    if results:
        output += "Successful updates:\n" + "\n".join(results) + "\n\n"
    if errors:
        output += "Errors:\n" + "\n".join(f"   {e}" for e in errors)

    return output


async def get_insights(
    client: "FacebookAdsClient",
    campaign_id: str,
    days: int = 30,
) -> str:
    """
    Get campaign performance metrics.

    Args:
        client: Authenticated Facebook client
        campaign_id: Campaign ID
        days: Number of days to look back (30 or maximum)

    Returns:
        Formatted insights string
    """
    if not campaign_id:
        return "ERROR: campaign_id required"

    if client.is_test_mode:
        return _mock_get_insights(campaign_id, days)

    params = {
        "fields": "impressions,clicks,spend,cpc,ctr,reach,frequency",
        "date_preset": "last_30d" if days == 30 else "maximum",
    }

    data = await client.get(f"{campaign_id}/insights", params=params)

    if not data.get("data"):
        return f"No insights data found for campaign {campaign_id}"

    raw = data["data"][0]
    insights = normalize_insights_data(raw)

    return f"""Insights for Campaign {campaign_id} (Last {days} days):
  Impressions: {insights.impressions:,}
  Clicks: {insights.clicks:,}
  Spend: ${insights.spend:.2f}
  CTR: {insights.ctr:.2f}%
  CPC: ${insights.cpc:.2f}
  Reach: {insights.reach:,}
  Frequency: {insights.frequency:.2f}
"""


# =============================================================================
# Mock Responses (Test Mode)
# =============================================================================

def _mock_list_campaigns() -> str:
    return """Found 2 campaigns:
  Test Campaign 1 (ID: 123456789) - ACTIVE, Daily: 50.00 USD
  Test Campaign 2 (ID: 987654321) - PAUSED, Daily: 100.00 USD
"""


def _mock_create_campaign(
    name: str,
    objective: str,
    status: str,
    daily_budget: Optional[int],
) -> str:
    budget_str = ""
    if daily_budget:
        budget_str = f"\n   Daily Budget: {format_currency(daily_budget)}"

    return f"""Campaign created: {name} (ID: mock_123456789)
   Status: {status}, Objective: {objective}{budget_str}
"""


def _mock_duplicate_campaign(campaign_id: str, new_name: str) -> str:
    return f"""Campaign duplicated successfully!

Original Campaign ID: {campaign_id}
New Campaign ID: {campaign_id}_copy
New Campaign Name: {new_name}
Status: PAUSED (activate when ready)

Note: Only the campaign was copied. To copy ad sets and ads, use the Facebook Ads Manager UI.
"""


def _mock_get_insights(campaign_id: str, days: int) -> str:
    return f"""Insights for Campaign {campaign_id} (Last {days} days):
  Impressions: 125,000
  Clicks: 3,450
  Spend: $500.00
  CTR: 2.76%
  CPC: $0.14
  Reach: 95,000
  Frequency: 1.32
"""
