"""
Facebook Ad Set Management

WHAT: Operations for creating and managing ad sets within campaigns.
WHY: Ad sets define targeting, budget allocation, and optimization goals.

OPERATIONS:
- create_adset: Create new ad set with targeting and budget
- list_adsets: List ad sets for a campaign
- update_adset: Modify ad set properties
- validate_targeting: Check targeting spec before creating

EXCEPTION HANDLING:
- handle() catches all exceptions and formats responses
- Operation functions only catch ValueError for validation errors
- FacebookAPIError and unexpected exceptions bubble up to handle()
"""

import json
import logging
from typing import Dict, Any

import httpx

from flexus_simple_bots.admonster.integrations import fb_utils

logger = logging.getLogger("fb_adset")


async def handle(integration, toolcall, model_produced_args: Dict[str, Any]) -> str:
    """
    Router for ad set operations. Catches all exceptions.
    
    FacebookAPIError → logger.info (expected external API error)
    Exception → logger.warning with stack trace (unexpected)
    """
    try:
        auth_error = await integration.ensure_headers()
        if auth_error:
            return auth_error
        
        op = model_produced_args.get("op", "")
        args = model_produced_args.get("args", {})
        
        for key in ["ad_account_id", "campaign_id"]:
            if key in model_produced_args and key not in args:
                args[key] = model_produced_args[key]
        
        if op == "create_adset":
            return await create_adset(integration, args)
        elif op == "list_adsets":
            return await list_adsets(integration, args)
        elif op == "update_adset":
            return await update_adset(integration, args)
        elif op == "validate_targeting":
            return await validate_targeting(integration, args)
        else:
            return f"Unknown adset operation: {op}\n\nAvailable operations:\n- create_adset\n- list_adsets\n- update_adset\n- validate_targeting"
    
    except fb_utils.FacebookAPIError as e:
        logger.info(f"Facebook API error in adset: {e}")
        return f"❌ Facebook API Error: {e.message}"
    except Exception as e:
        logger.warning(f"Ad set error: {e}", exc_info=e)
        return f"ERROR: {str(e)}"


async def create_adset(integration, args: Dict[str, Any]) -> str:
    """Create a new ad set with targeting."""
    ad_account_id = args.get("ad_account_id", "")
    campaign_id = args.get("campaign_id", "")
    name = args.get("name", "")
    optimization_goal = args.get("optimization_goal", "LINK_CLICKS")
    billing_event = args.get("billing_event", "IMPRESSIONS")
    daily_budget = args.get("daily_budget")
    lifetime_budget = args.get("lifetime_budget")
    targeting = args.get("targeting", {})
    status = args.get("status", "PAUSED")
    start_time = args.get("start_time")
    end_time = args.get("end_time")
    bid_amount = args.get("bid_amount")
    promoted_object = args.get("promoted_object")
    
    # Fail-fast validation
    if not ad_account_id:
        return "ERROR: ad_account_id is required (e.g. act_123456)"
    if not campaign_id:
        return "ERROR: campaign_id is required"
    if not name:
        return "ERROR: name is required"
    if not targeting:
        return "ERROR: targeting is required"
    
    targeting_valid, targeting_error = fb_utils.validate_targeting_spec(targeting)
    if not targeting_valid:
        return f"ERROR: Invalid targeting: {targeting_error}"
    
    # Validate budgets if provided
    try:
        if daily_budget:
            fb_utils.validate_budget(daily_budget)
        if lifetime_budget:
            fb_utils.validate_budget(lifetime_budget)
    except ValueError as e:
        return f"ERROR: {str(e)}"
    
    if integration.is_fake:
        mock_adset = fb_utils.generate_mock_adset()
        mock_adset["campaign_id"] = campaign_id
        mock_adset["name"] = name
        mock_adset["optimization_goal"] = optimization_goal
        
        budget_line = ""
        if daily_budget:
            budget_line = f"Daily Budget: {fb_utils.format_currency(daily_budget)}\n"
        elif lifetime_budget:
            budget_line = f"Lifetime Budget: {fb_utils.format_currency(lifetime_budget)}\n"
        else:
            budget_line = "Budget: Using Campaign Budget (CBO)\n"
        
        return f"""✅ Ad Set created successfully!

ID: {mock_adset['id']}
Name: {mock_adset['name']}
Campaign ID: {mock_adset['campaign_id']}
Status: PAUSED
Optimization Goal: {optimization_goal}
Billing Event: {billing_event}
{budget_line}
Targeting:
  • Locations: {', '.join(targeting.get('geo_locations', {}).get('countries', ['Not specified']))}
  • Age: {targeting.get('age_min', 18)}-{targeting.get('age_max', 65)}

Ad set is paused. Activate it when ready to start delivery.
"""
    
    url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{ad_account_id}/adsets"
    
    # FB API expects form-data with JSON strings for complex fields
    bid_strategy = args.get("bid_strategy", "LOWEST_COST_WITHOUT_CAP")
    
    form_data = {
        "name": name,
        "campaign_id": campaign_id,
        "optimization_goal": optimization_goal,
        "billing_event": billing_event,
        "bid_strategy": bid_strategy,
        "targeting": json.dumps(targeting),
        "status": status,
        "access_token": integration.access_token,
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
    
    logger.info(f"Creating adset at {url} with form_data: {form_data}")
    
    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=form_data, timeout=30.0)
            if response.status_code != 200:
                logger.info(f"FB API error: status={response.status_code}, body={response.text}")
                error_msg = await fb_utils.handle_fb_api_error(response)
                raise fb_utils.FacebookAPIError(response.status_code, error_msg)
            return response.json()
    
    result = await fb_utils.retry_with_backoff(make_request)
    
    adset_id = result.get("id")
    if not adset_id:
        return f"❌ Failed to create ad set. Response: {result}"
    
    output = f"""✅ Ad Set created successfully!

ID: {adset_id}
Name: {name}
Campaign ID: {campaign_id}
Status: {status}
Optimization Goal: {optimization_goal}
Billing Event: {billing_event}
"""
    
    if daily_budget:
        output += f"Daily Budget: {fb_utils.format_currency(daily_budget)}\n"
    if lifetime_budget:
        output += f"Lifetime Budget: {fb_utils.format_currency(lifetime_budget)}\n"
    
    geo = targeting.get("geo_locations", {})
    countries = geo.get("countries", [])
    if countries:
        output += f"\nTargeting:\n  • Locations: {', '.join(countries)}\n"
    
    if "age_min" in targeting or "age_max" in targeting:
        age_min = targeting.get("age_min", 18)
        age_max = targeting.get("age_max", 65)
        output += f"  • Age: {age_min}-{age_max}\n"
    
    if status == "PAUSED":
        output += "\n⚠️ Ad set is paused. Activate it when ready to start delivery."
    
    return output


async def list_adsets(integration, args: Dict[str, Any]) -> str:
    """List ad sets for a campaign."""
    campaign_id = args.get("campaign_id", "")
    if not campaign_id:
        return "ERROR: campaign_id is required"
    
    if integration.is_fake:
        mock_adset = fb_utils.generate_mock_adset()
        mock_adset["campaign_id"] = campaign_id
        return f"""Ad Sets for Campaign {campaign_id}:

📊 {mock_adset['name']}
   ID: {mock_adset['id']}
   Status: {mock_adset['status']}
   Optimization: {mock_adset['optimization_goal']}
   Daily Budget: {fb_utils.format_currency(mock_adset['daily_budget'])}
   Targeting: {', '.join(mock_adset['targeting']['geo_locations']['countries'])}
"""
    
    url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{campaign_id}/adsets"
    params = {
        "fields": "id,name,status,optimization_goal,billing_event,daily_budget,lifetime_budget,targeting",
        "limit": 50
    }
    
    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=integration.headers, timeout=30.0)
            if response.status_code != 200:
                error_msg = await fb_utils.handle_fb_api_error(response)
                raise fb_utils.FacebookAPIError(response.status_code, error_msg)
            return response.json()
    
    data = await fb_utils.retry_with_backoff(make_request)
    adsets = data.get("data", [])
    
    if not adsets:
        return f"No ad sets found for campaign {campaign_id}"
    
    result = f"Ad Sets for Campaign {campaign_id} (found {len(adsets)}):\n\n"
    
    for adset in adsets:
        result += f"📊 {adset['name']}\n"
        result += f"   ID: {adset['id']}\n"
        result += f"   Status: {adset['status']}\n"
        result += f"   Optimization: {adset.get('optimization_goal', 'N/A')}\n"
        result += f"   Billing: {adset.get('billing_event', 'N/A')}\n"
        
        if 'daily_budget' in adset:
            result += f"   Daily Budget: {fb_utils.format_currency(int(adset['daily_budget']))}\n"
        elif 'lifetime_budget' in adset:
            result += f"   Lifetime Budget: {fb_utils.format_currency(int(adset['lifetime_budget']))}\n"
        
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


async def update_adset(integration, args: Dict[str, Any]) -> str:
    """Update an existing ad set."""
    adset_id = args.get("adset_id", "")
    if not adset_id:
        return "ERROR: adset_id is required"
    
    name = args.get("name")
    status = args.get("status")
    daily_budget = args.get("daily_budget")
    bid_amount = args.get("bid_amount")
    
    if not any([name, status, daily_budget, bid_amount]):
        return "ERROR: At least one field to update is required"
    
    if status and status not in ["ACTIVE", "PAUSED"]:
        return "ERROR: status must be 'ACTIVE' or 'PAUSED'"
    
    if integration.is_fake:
        updates = []
        if name:
            updates.append(f"name → {name}")
        if status:
            updates.append(f"status → {status}")
        if daily_budget:
            updates.append(f"daily_budget → {fb_utils.format_currency(daily_budget)}")
        return f"✅ Ad Set {adset_id} updated:\n" + "\n".join(f"   • {u}" for u in updates)
    
    url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{adset_id}"
    data = {}
    
    if name:
        data["name"] = name
    if status:
        data["status"] = status
    if daily_budget is not None:
        try:
            fb_utils.validate_budget(daily_budget)
        except ValueError as e:
            return f"ERROR: {str(e)}"
        data["daily_budget"] = daily_budget
    if bid_amount is not None:
        data["bid_amount"] = bid_amount
    
    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=integration.headers, timeout=30.0)
            if response.status_code != 200:
                error_msg = await fb_utils.handle_fb_api_error(response)
                raise fb_utils.FacebookAPIError(response.status_code, error_msg)
            return response.json()
    
    result = await fb_utils.retry_with_backoff(make_request)
    
    if result.get("success"):
        updates = []
        if name:
            updates.append(f"name → {name}")
        if status:
            updates.append(f"status → {status}")
        if daily_budget:
            updates.append(f"daily_budget → {fb_utils.format_currency(daily_budget)}")
        if bid_amount:
            updates.append(f"bid_amount → {bid_amount} cents")
        return f"✅ Ad Set {adset_id} updated:\n" + "\n".join(f"   • {u}" for u in updates)
    else:
        return f"❌ Failed to update ad set. Response: {result}"


async def validate_targeting(integration, args: Dict[str, Any]) -> str:
    """Validate targeting specification and get estimated audience size."""
    targeting_spec = args.get("targeting_spec", {})
    if not targeting_spec:
        return "ERROR: targeting_spec is required"
    
    valid, error = fb_utils.validate_targeting_spec(targeting_spec)
    if not valid:
        return f"❌ Invalid targeting: {error}"
    
    if integration.is_fake:
        return f"""✅ Targeting is valid!

Estimated Audience Size: ~1,000,000 - 1,500,000 people

Targeting Summary:
  • Locations: {', '.join(targeting_spec.get('geo_locations', {}).get('countries', ['Not specified']))}
  • Age: {targeting_spec.get('age_min', 18)}-{targeting_spec.get('age_max', 65)}
  • Device Platforms: {', '.join(targeting_spec.get('device_platforms', ['all']))}

This is a test validation. In production, Facebook will provide actual estimated reach.
"""
    
    ad_account_id = integration.ad_account_id
    url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{ad_account_id}/targetingsentencelines"
    params = {"targeting_spec": targeting_spec}
    
    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=integration.headers, timeout=30.0)
            if response.status_code != 200:
                error_msg = await fb_utils.handle_fb_api_error(response)
                raise fb_utils.FacebookAPIError(response.status_code, error_msg)
            return response.json()
    
    result = await fb_utils.retry_with_backoff(make_request)
    
    output = "✅ Targeting is valid!\n\n"
    
    if "targetingsentencelines" in result:
        output += "Targeting Summary:\n"
        for line in result["targetingsentencelines"]:
            output += f"  • {line.get('content', '')}\n"
    
    return output
