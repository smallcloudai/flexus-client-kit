"""
Facebook Ad Set Operations

Operations for creating and managing ad sets within campaigns.
Ad sets define targeting, budget allocation, and optimization goals.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..models import AdSet, OptimizationGoal, BillingEvent, BidStrategy
from ..utils import format_currency, validate_budget, validate_targeting_spec
from ..exceptions import FacebookAPIError, FacebookValidationError

if TYPE_CHECKING:
    from ..client import FacebookAdsClient

logger = logging.getLogger("facebook.operations.adsets")

# Fields to request from API
ADSET_FIELDS = (
    "id,name,status,optimization_goal,billing_event,"
    "daily_budget,lifetime_budget,targeting"
)


async def list_adsets(
    client: "FacebookAdsClient",
    campaign_id: str,
) -> str:
    """
    List ad sets for a campaign.

    Args:
        client: Authenticated Facebook client
        campaign_id: Campaign ID

    Returns:
        Formatted string with ad set list
    """
    if not campaign_id:
        return "ERROR: campaign_id is required"

    if client.is_test_mode:
        return _mock_list_adsets(campaign_id)

    data = await client.get(
        f"{campaign_id}/adsets",
        params={"fields": ADSET_FIELDS, "limit": 50}
    )
    adsets = data.get("data", [])

    if not adsets:
        return f"No ad sets found for campaign {campaign_id}"

    result = f"Ad Sets for Campaign {campaign_id} (found {len(adsets)}):\n\n"

    for adset in adsets:
        result += f"**{adset['name']}**\n"
        result += f"   ID: {adset['id']}\n"
        result += f"   Status: {adset['status']}\n"
        result += f"   Optimization: {adset.get('optimization_goal', 'N/A')}\n"
        result += f"   Billing: {adset.get('billing_event', 'N/A')}\n"

        if 'daily_budget' in adset:
            result += f"   Daily Budget: {format_currency(int(adset['daily_budget']))}\n"
        elif 'lifetime_budget' in adset:
            result += f"   Lifetime Budget: {format_currency(int(adset['lifetime_budget']))}\n"

        targeting = adset.get("targeting", {})
        if targeting:
            geo = targeting.get("geo_locations", {})
            countries = geo.get("countries", [])
            if countries:
                result += f"   Targeting: {', '.join(countries[:3])}"
                if len(countries) > 3:
                    result += f" +{len(countries)-3} more"
                result += "\n"

        result += "\n"

    return result


async def create_adset(
    client: "FacebookAdsClient",
    ad_account_id: str,
    campaign_id: str,
    name: str,
    targeting: Dict[str, Any],
    optimization_goal: str = "LINK_CLICKS",
    billing_event: str = "IMPRESSIONS",
    bid_strategy: str = "LOWEST_COST_WITHOUT_CAP",
    status: str = "PAUSED",
    daily_budget: Optional[int] = None,
    lifetime_budget: Optional[int] = None,
    bid_amount: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    promoted_object: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a new ad set with targeting.

    Args:
        client: Authenticated Facebook client
        ad_account_id: Ad account ID (e.g. act_123456)
        campaign_id: Campaign ID
        name: Ad set name
        targeting: Targeting specification
        optimization_goal: Optimization goal (default LINK_CLICKS)
        billing_event: Billing event (default IMPRESSIONS)
        bid_strategy: Bid strategy
        status: Initial status (default PAUSED)
        daily_budget: Daily budget in cents
        lifetime_budget: Lifetime budget in cents
        bid_amount: Bid amount in cents (for bid cap strategies)
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        promoted_object: Promoted object (page_id, etc.)

    Returns:
        Formatted result string
    """
    # Validation
    if not ad_account_id:
        return "ERROR: ad_account_id is required (e.g. act_123456)"
    if not campaign_id:
        return "ERROR: campaign_id is required"
    if not name:
        return "ERROR: name is required"
    if not targeting:
        return "ERROR: targeting is required"

    # Validate targeting
    targeting_valid, targeting_error = validate_targeting_spec(targeting)
    if not targeting_valid:
        return f"ERROR: Invalid targeting: {targeting_error}"

    # Validate budgets if provided
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
        return _mock_create_adset(campaign_id, name, optimization_goal, daily_budget, targeting)

    # FB API expects form-data with JSON strings for complex fields
    form_data: Dict[str, Any] = {
        "name": name,
        "campaign_id": campaign_id,
        "optimization_goal": optimization_goal,
        "billing_event": billing_event,
        "bid_strategy": bid_strategy,
        "targeting": json.dumps(targeting),
        "status": status,
        "access_token": client.access_token,
    }

    if daily_budget:
        form_data["daily_budget"] = str(daily_budget)
    if lifetime_budget:
        form_data["lifetime_budget"] = str(lifetime_budget)
    if start_time:
        form_data["start_time"] = start_time
    if end_time:
        form_data["end_time"] = end_time

    if bid_amount:
        form_data["bid_amount"] = str(bid_amount)
        if bid_strategy == "LOWEST_COST_WITHOUT_CAP":
            form_data["bid_strategy"] = "LOWEST_COST_WITH_BID_CAP"

    if promoted_object:
        form_data["promoted_object"] = json.dumps(promoted_object)

    logger.info(f"Creating adset for campaign {campaign_id}")

    result = await client.post(f"{ad_account_id}/adsets", form_data=form_data)

    adset_id = result.get("id")
    if not adset_id:
        return f"Failed to create ad set. Response: {result}"

    output = f"""Ad Set created successfully!

ID: {adset_id}
Name: {name}
Campaign ID: {campaign_id}
Status: {status}
Optimization Goal: {optimization_goal}
Billing Event: {billing_event}
"""

    if daily_budget:
        output += f"Daily Budget: {format_currency(daily_budget)}\n"
    if lifetime_budget:
        output += f"Lifetime Budget: {format_currency(lifetime_budget)}\n"

    geo = targeting.get("geo_locations", {})
    countries = geo.get("countries", [])
    if countries:
        output += f"\nTargeting:\n  - Locations: {', '.join(countries)}\n"

    if "age_min" in targeting or "age_max" in targeting:
        age_min = targeting.get("age_min", 18)
        age_max = targeting.get("age_max", 65)
        output += f"  - Age: {age_min}-{age_max}\n"

    if status == "PAUSED":
        output += "\nAd set is paused. Activate it when ready to start delivery."

    return output


async def update_adset(
    client: "FacebookAdsClient",
    adset_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    daily_budget: Optional[int] = None,
    bid_amount: Optional[int] = None,
) -> str:
    """
    Update an existing ad set.

    Args:
        client: Authenticated Facebook client
        adset_id: Ad set ID
        name: New name (optional)
        status: New status (optional)
        daily_budget: New daily budget in cents (optional)
        bid_amount: New bid amount in cents (optional)

    Returns:
        Formatted result string
    """
    if not adset_id:
        return "ERROR: adset_id is required"

    if not any([name, status, daily_budget, bid_amount]):
        return "ERROR: At least one field to update is required"

    if status and status not in ["ACTIVE", "PAUSED"]:
        return "ERROR: status must be 'ACTIVE' or 'PAUSED'"

    if daily_budget:
        try:
            daily_budget = validate_budget(daily_budget)
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"

    updates = []
    if name:
        updates.append(f"name -> {name}")
    if status:
        updates.append(f"status -> {status}")
    if daily_budget:
        updates.append(f"daily_budget -> {format_currency(daily_budget)}")
    if bid_amount:
        updates.append(f"bid_amount -> {bid_amount} cents")

    if client.is_test_mode:
        return f"Ad Set {adset_id} updated:\n" + "\n".join(f"   - {u}" for u in updates)

    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if status:
        data["status"] = status
    if daily_budget is not None:
        data["daily_budget"] = daily_budget
    if bid_amount is not None:
        data["bid_amount"] = bid_amount

    result = await client.post(adset_id, data=data)

    if result.get("success"):
        return f"Ad Set {adset_id} updated:\n" + "\n".join(f"   - {u}" for u in updates)
    else:
        return f"Failed to update ad set. Response: {result}"


async def validate_targeting(
    client: "FacebookAdsClient",
    targeting_spec: Dict[str, Any],
    ad_account_id: Optional[str] = None,
) -> str:
    """
    Validate targeting specification and get estimated audience size.

    Args:
        client: Authenticated Facebook client
        targeting_spec: Targeting specification to validate
        ad_account_id: Ad account ID (uses client default if not provided)

    Returns:
        Formatted validation result
    """
    if not targeting_spec:
        return "ERROR: targeting_spec is required"

    # Local validation first
    valid, error = validate_targeting_spec(targeting_spec)
    if not valid:
        return f"Invalid targeting: {error}"

    geo = targeting_spec.get('geo_locations', {})
    countries = geo.get('countries', ['Not specified'])
    age_min = targeting_spec.get('age_min', 18)
    age_max = targeting_spec.get('age_max', 65)

    if client.is_test_mode:
        return f"""Targeting is valid!

Estimated Audience Size: ~1,000,000 - 1,500,000 people

Targeting Summary:
  - Locations: {', '.join(countries)}
  - Age: {age_min}-{age_max}
  - Device Platforms: {', '.join(targeting_spec.get('device_platforms', ['all']))}

This is a test validation. In production, Facebook will provide actual estimated reach.
"""

    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id required for validate_targeting"

    result = await client.get(
        f"{account_id}/targetingsentencelines",
        params={"targeting_spec": json.dumps(targeting_spec)}
    )

    output = "Targeting is valid!\n\n"

    if "targetingsentencelines" in result:
        output += "Targeting Summary:\n"
        for line in result["targetingsentencelines"]:
            output += f"  - {line.get('content', '')}\n"

    return output


# =============================================================================
# Mock Responses (Test Mode)
# =============================================================================

def _mock_list_adsets(campaign_id: str) -> str:
    return f"""Ad Sets for Campaign {campaign_id}:

**Test Ad Set**
   ID: 234567890123456
   Status: ACTIVE
   Optimization: LINK_CLICKS
   Daily Budget: 20.00 USD
   Targeting: US
"""


def _mock_create_adset(
    campaign_id: str,
    name: str,
    optimization_goal: str,
    daily_budget: Optional[int],
    targeting: Dict[str, Any],
) -> str:
    budget_line = ""
    if daily_budget:
        budget_line = f"Daily Budget: {format_currency(daily_budget)}\n"
    else:
        budget_line = "Budget: Using Campaign Budget (CBO)\n"

    countries = targeting.get('geo_locations', {}).get('countries', ['Not specified'])
    age_min = targeting.get('age_min', 18)
    age_max = targeting.get('age_max', 65)

    return f"""Ad Set created successfully!

ID: mock_adset_123456
Name: {name}
Campaign ID: {campaign_id}
Status: PAUSED
Optimization Goal: {optimization_goal}
Billing Event: IMPRESSIONS
{budget_line}
Targeting:
  - Locations: {', '.join(countries)}
  - Age: {age_min}-{age_max}

Ad set is paused. Activate it when ready to start delivery.
"""
