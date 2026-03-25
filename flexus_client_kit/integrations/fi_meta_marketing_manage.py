from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import httpx

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.integrations._fi_meta_helpers import (
    FacebookAdsClient,
    FacebookAPIError,
    FacebookAuthError,
    FacebookValidationError,
    FacebookTimeoutError,
    CampaignObjective,
    CallToActionType,
    AdFormat,
    CustomAudienceSubtype,
    InsightsDatePreset,
    API_BASE,
    API_VERSION,
    format_currency,
    validate_budget,
    validate_targeting_spec,
    validate_ad_account_id,
)

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

logger = logging.getLogger("meta_marketing_manage")

# Use case: "Create & manage ads with Marketing API"
PROVIDER_NAME = "meta_marketing_manage"

_HELP = """meta_marketing_manage: Create & manage ads with Meta Marketing API.
op=help | status | list_methods | call(args={method_id, ...})

Campaigns: list_campaigns, get_campaign, create_campaign, update_campaign,
  delete_campaign, duplicate_campaign, archive_campaign, bulk_update_campaigns
Ad Sets: list_adsets, list_adsets_for_account, get_adset, create_adset,
  update_adset, delete_adset, validate_targeting
Ads: list_ads, get_ad, create_ad, update_ad, delete_ad, preview_ad
Creatives: list_creatives, get_creative, create_creative, update_creative,
  delete_creative, preview_creative, upload_image, upload_video, list_videos
Audiences: list_custom_audiences, get_custom_audience, create_custom_audience,
  create_lookalike_audience, update_custom_audience, delete_custom_audience,
  add_users_to_audience
Pixels: list_pixels, create_pixel, get_pixel_stats
Targeting: search_interests, search_behaviors, get_reach_estimate, get_delivery_estimate
Rules: list_ad_rules, create_ad_rule, update_ad_rule, delete_ad_rule, execute_ad_rule
"""

# ── Campaigns ─────────────────────────────────────────────────────────────────

_CAMPAIGN_FIELDS = "id,name,status,objective,daily_budget,lifetime_budget"


async def _list_campaigns(client: FacebookAdsClient, ad_account_id: Optional[str], status_filter: Optional[str]) -> str:
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id required for list_campaigns"
    if client.is_test_mode:
        return "Found 2 campaigns:\n  Test Campaign 1 (ID: 123456789) - ACTIVE, Daily: 50.00 USD\n  Test Campaign 2 (ID: 987654321) - PAUSED, Daily: 100.00 USD\n"
    params: Dict[str, Any] = {"fields": _CAMPAIGN_FIELDS, "limit": 50}
    if status_filter:
        params["effective_status"] = f"['{status_filter}']"
    data = await client.request("GET", f"{account_id}/campaigns", params=params)
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


async def _get_campaign(client: FacebookAdsClient, campaign_id: str) -> str:
    if not campaign_id:
        return "ERROR: campaign_id is required"
    if client.is_test_mode:
        return f"Campaign {campaign_id}:\n  Name: Test Campaign\n  Status: ACTIVE\n  Objective: OUTCOME_TRAFFIC\n  Daily Budget: 50.00 USD\n"
    data = await client.request("GET", campaign_id, params={"fields": "id,name,status,objective,daily_budget,lifetime_budget,special_ad_categories,created_time,updated_time,start_time,stop_time,budget_remaining"})
    result = f"Campaign {campaign_id}:\n"
    result += f"  Name: {data.get('name', 'N/A')}\n"
    result += f"  Status: {data.get('status', 'N/A')}\n"
    result += f"  Objective: {data.get('objective', 'N/A')}\n"
    if data.get("daily_budget"):
        result += f"  Daily Budget: {format_currency(int(data['daily_budget']))}\n"
    if data.get("lifetime_budget"):
        result += f"  Lifetime Budget: {format_currency(int(data['lifetime_budget']))}\n"
    if data.get("budget_remaining"):
        result += f"  Budget Remaining: {format_currency(int(data['budget_remaining']))}\n"
    result += f"  Created: {data.get('created_time', 'N/A')}\n"
    return result


async def _create_campaign(client: FacebookAdsClient, ad_account_id: str, name: str, objective: str, daily_budget: Optional[int], lifetime_budget: Optional[int], status: str) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    if not name:
        return "ERROR: name required"
    try:
        CampaignObjective(objective)
    except ValueError:
        return f"ERROR: Invalid objective. Must be one of: {', '.join(o.value for o in CampaignObjective)}"
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
        budget_str = f"\n   Daily Budget: {format_currency(daily_budget)}" if daily_budget else ""
        return f"Campaign created: {name} (ID: mock_123456789)\n   Status: {status}, Objective: {objective}{budget_str}\n"
    payload: Dict[str, Any] = {"name": name, "objective": objective, "status": status, "special_ad_categories": []}
    if daily_budget:
        payload["daily_budget"] = daily_budget
    if lifetime_budget:
        payload["lifetime_budget"] = lifetime_budget
    result = await client.request("POST", f"{ad_account_id}/campaigns", data=payload)
    campaign_id = result.get("id")
    if not campaign_id:
        return f"Failed to create campaign. Response: {result}"
    output = f"Campaign created: {name} (ID: {campaign_id})\n   Status: {status}, Objective: {objective}\n"
    if daily_budget:
        output += f"   Daily Budget: {format_currency(daily_budget)}\n"
    return output


async def _update_campaign(client: FacebookAdsClient, campaign_id: str, name: Optional[str], status: Optional[str], daily_budget: Optional[int], lifetime_budget: Optional[int]) -> str:
    if not campaign_id:
        return "ERROR: campaign_id required"
    if not any([name, status, daily_budget, lifetime_budget]):
        return "ERROR: At least one field to update required"
    if status and status not in ["ACTIVE", "PAUSED"]:
        return "ERROR: status must be ACTIVE or PAUSED"
    if daily_budget:
        try:
            daily_budget = validate_budget(daily_budget)
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"
    updates = [f"name -> {name}"] if name else []
    if status:
        updates.append(f"status -> {status}")
    if daily_budget:
        updates.append(f"daily_budget -> {format_currency(daily_budget)}")
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
    result = await client.request("POST", campaign_id, data=data)
    if result.get("success"):
        return f"Campaign {campaign_id} updated:\n" + "\n".join(f"   - {u}" for u in updates)
    return f"Failed to update campaign. Response: {result}"


async def _delete_campaign(client: FacebookAdsClient, campaign_id: str) -> str:
    if not campaign_id:
        return "ERROR: campaign_id required"
    if client.is_test_mode:
        return f"Campaign {campaign_id} deleted successfully."
    result = await client.request("DELETE", campaign_id)
    return f"Campaign {campaign_id} deleted successfully." if result.get("success") else f"Failed to delete campaign. Response: {result}"


async def _duplicate_campaign(client: FacebookAdsClient, campaign_id: str, new_name: str, ad_account_id: Optional[str]) -> str:
    if not campaign_id or not new_name:
        return "ERROR: campaign_id and new_name required"
    if client.is_test_mode:
        return f"Campaign duplicated!\nOriginal: {campaign_id}\nNew ID: {campaign_id}_copy\nNew Name: {new_name}\nStatus: PAUSED\n"
    original = await client.request("GET", campaign_id, params={"fields": "name,objective,status,daily_budget,lifetime_budget,special_ad_categories"})
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id required for duplicate_campaign"
    create_data: Dict[str, Any] = {"name": new_name, "objective": original["objective"], "status": "PAUSED", "special_ad_categories": original.get("special_ad_categories", [])}
    if "daily_budget" in original:
        create_data["daily_budget"] = original["daily_budget"]
    new_campaign = await client.request("POST", f"{account_id}/campaigns", data=create_data)
    return f"Campaign duplicated!\nOriginal: {campaign_id}\nNew ID: {new_campaign.get('id')}\nNew Name: {new_name}\nStatus: PAUSED\n"


async def _archive_campaign(client: FacebookAdsClient, campaign_id: str) -> str:
    if not campaign_id:
        return "ERROR: campaign_id required"
    if client.is_test_mode:
        return f"Campaign {campaign_id} archived successfully."
    result = await client.request("POST", campaign_id, data={"status": "ARCHIVED"})
    return f"Campaign {campaign_id} archived successfully." if result.get("success") else f"Failed to archive campaign. Response: {result}"


async def _bulk_update_campaigns(client: FacebookAdsClient, campaigns: List[Dict[str, Any]]) -> str:
    if not campaigns or not isinstance(campaigns, list):
        return "ERROR: campaigns must be a non-empty list"
    if len(campaigns) > 50:
        return "ERROR: Maximum 50 campaigns at once"
    if client.is_test_mode:
        results = [f"   {c.get('id', 'unknown')} -> {c.get('status', 'unchanged')}" for c in campaigns]
        return f"Bulk update completed for {len(campaigns)} campaigns:\n" + "\n".join(results)
    results, errors = [], []
    for camp in campaigns:
        campaign_id = camp.get("id")
        if not campaign_id:
            errors.append("Missing campaign ID")
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
            result = await client.request("POST", campaign_id, data=data)
            if result.get("success"):
                results.append(f"   {campaign_id}: {', '.join(f'{k}={v}' for k, v in data.items())}")
            else:
                errors.append(f"{campaign_id}: Update failed")
        except (FacebookAPIError, ValueError) as e:
            errors.append(f"{campaign_id}: {e}")
    return f"Bulk update: {len(results)} ok, {len(errors)} errors\n" + ("\n".join(results) if results else "") + ("\nErrors:\n" + "\n".join(f"   {e}" for e in errors) if errors else "")


# ── Ad Sets ───────────────────────────────────────────────────────────────────

_ADSET_FIELDS = "id,name,status,optimization_goal,billing_event,daily_budget,lifetime_budget,targeting"


async def _list_adsets(client: FacebookAdsClient, campaign_id: str) -> str:
    if not campaign_id:
        return "ERROR: campaign_id required"
    if client.is_test_mode:
        return f"Ad Sets for Campaign {campaign_id}:\n  Test Ad Set (ID: 234567890) - ACTIVE, Daily: 20.00 USD\n"
    data = await client.request("GET", f"{campaign_id}/adsets", params={"fields": _ADSET_FIELDS, "limit": 50})
    adsets = data.get("data", [])
    if not adsets:
        return f"No ad sets found for campaign {campaign_id}"
    result = f"Ad Sets for Campaign {campaign_id} ({len(adsets)}):\n\n"
    for a in adsets:
        result += f"  {a['name']} (ID: {a['id']}) - {a['status']}, Opt: {a.get('optimization_goal', 'N/A')}\n"
    return result


async def _list_adsets_for_account(client: FacebookAdsClient, ad_account_id: str, status_filter: Optional[str]) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    if client.is_test_mode:
        return f"Ad Sets for {ad_account_id}:\n  Test Ad Set (ID: 234567890) — ACTIVE\n"
    params: Dict[str, Any] = {"fields": _ADSET_FIELDS + ",campaign_id", "limit": 100}
    if status_filter:
        params["filtering"] = json.dumps([{"field": "adset.delivery_info", "operator": "IN", "value": [status_filter.upper()]}])
    data = await client.request("GET", f"{ad_account_id}/adsets", params=params)
    adsets = data.get("data", [])
    if not adsets:
        return f"No ad sets found for {ad_account_id}"
    result = f"Ad Sets for {ad_account_id} ({len(adsets)}):\n\n"
    for a in adsets:
        result += f"  {a.get('name', 'Unnamed')} (ID: {a['id']}) - {a.get('status', 'N/A')}\n"
    return result


async def _get_adset(client: FacebookAdsClient, adset_id: str) -> str:
    if not adset_id:
        return "ERROR: adset_id required"
    if client.is_test_mode:
        return f"Ad Set {adset_id}:\n  Name: Test Ad Set\n  Status: ACTIVE\n  Optimization: LINK_CLICKS\n"
    data = await client.request("GET", adset_id, params={"fields": "id,name,status,optimization_goal,billing_event,bid_strategy,bid_amount,daily_budget,lifetime_budget,targeting,campaign_id,created_time"})
    result = f"Ad Set {adset_id}:\n"
    result += f"  Name: {data.get('name', 'N/A')}\n  Status: {data.get('status', 'N/A')}\n  Campaign: {data.get('campaign_id', 'N/A')}\n"
    result += f"  Optimization: {data.get('optimization_goal', 'N/A')}\n"
    if data.get("daily_budget"):
        result += f"  Daily Budget: {format_currency(int(data['daily_budget']))}\n"
    return result


async def _create_adset(client: FacebookAdsClient, ad_account_id: str, campaign_id: str, name: str, targeting: Dict[str, Any], optimization_goal: str, billing_event: str, daily_budget: Optional[int], lifetime_budget: Optional[int], status: str) -> str:
    if not ad_account_id or not campaign_id or not name or not targeting:
        return "ERROR: ad_account_id, campaign_id, name, targeting all required"
    targeting_valid, targeting_error = validate_targeting_spec(targeting)
    if not targeting_valid:
        return f"ERROR: Invalid targeting: {targeting_error}"
    if daily_budget:
        try:
            daily_budget = validate_budget(daily_budget)
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"
    if client.is_test_mode:
        countries = targeting.get('geo_locations', {}).get('countries', ['Not specified'])
        return f"Ad Set created!\nID: mock_adset_123\nName: {name}\nCampaign: {campaign_id}\nStatus: {status}\nOptimization: {optimization_goal}\nTargeting: {', '.join(countries)}\n"
    form_data: Dict[str, Any] = {
        "name": name, "campaign_id": campaign_id,
        "optimization_goal": optimization_goal, "billing_event": billing_event,
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "targeting": json.dumps(targeting), "status": status,
        "access_token": client.access_token,
    }
    if daily_budget:
        form_data["daily_budget"] = str(daily_budget)
    if lifetime_budget:
        form_data["lifetime_budget"] = str(lifetime_budget)
    result = await client.request("POST", f"{ad_account_id}/adsets", form_data=form_data)
    adset_id = result.get("id")
    if not adset_id:
        return f"Failed to create ad set. Response: {result}"
    return f"Ad Set created!\nID: {adset_id}\nName: {name}\nCampaign: {campaign_id}\nStatus: {status}\n"


async def _update_adset(client: FacebookAdsClient, adset_id: str, name: Optional[str], status: Optional[str], daily_budget: Optional[int], targeting: Optional[Dict[str, Any]]) -> str:
    if not adset_id:
        return "ERROR: adset_id required"
    if not any([name, status, daily_budget, targeting]):
        return "ERROR: At least one field to update required"
    if status and status not in ["ACTIVE", "PAUSED"]:
        return "ERROR: status must be ACTIVE or PAUSED"
    if daily_budget:
        try:
            daily_budget = validate_budget(daily_budget)
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"
    if client.is_test_mode:
        return f"Ad Set {adset_id} updated."
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if status:
        data["status"] = status
    if daily_budget is not None:
        data["daily_budget"] = daily_budget
    result = await client.request("POST", adset_id, data=data)
    return f"Ad Set {adset_id} updated." if result.get("success") else f"Failed to update. Response: {result}"


async def _delete_adset(client: FacebookAdsClient, adset_id: str) -> str:
    if not adset_id:
        return "ERROR: adset_id required"
    if client.is_test_mode:
        return f"Ad Set {adset_id} deleted."
    result = await client.request("DELETE", adset_id)
    return f"Ad Set {adset_id} deleted." if result.get("success") else f"Failed to delete. Response: {result}"


async def _validate_targeting(client: FacebookAdsClient, targeting_spec: Dict[str, Any], ad_account_id: Optional[str]) -> str:
    if not targeting_spec:
        return "ERROR: targeting_spec required"
    valid, error = validate_targeting_spec(targeting_spec)
    if not valid:
        return f"Invalid targeting: {error}"
    if client.is_test_mode:
        countries = targeting_spec.get('geo_locations', {}).get('countries', ['N/A'])
        return f"Targeting is valid!\nLocations: {', '.join(countries)}\nAge: {targeting_spec.get('age_min', 18)}-{targeting_spec.get('age_max', 65)}\n"
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id required for validate_targeting"
    result = await client.request("GET", f"{account_id}/targetingsentencelines", params={"targeting_spec": json.dumps(targeting_spec)})
    output = "Targeting is valid!\n"
    for line in result.get("targetingsentencelines", []):
        output += f"  - {line.get('content', '')}\n"
    return output


# ── Ads ───────────────────────────────────────────────────────────────────────

async def _list_ads(client: FacebookAdsClient, ad_account_id: Optional[str], adset_id: Optional[str], status_filter: Optional[str]) -> str:
    if not ad_account_id and not adset_id:
        return "ERROR: Either ad_account_id or adset_id required"
    parent = adset_id if adset_id else ad_account_id
    if client.is_test_mode:
        return f"Ads for {parent}:\n  Test Ad (ID: 111222333) — PAUSED\n"
    params: Dict[str, Any] = {"fields": "id,name,status,adset_id,creative{id},effective_status", "limit": 100}
    if status_filter:
        params["effective_status"] = f'["{status_filter.upper()}"]'
    data = await client.request("GET", f"{parent}/ads", params=params)
    ads = data.get("data", [])
    if not ads:
        return f"No ads found for {parent}"
    result = f"Ads for {parent} ({len(ads)}):\n\n"
    for ad in ads:
        result += f"  {ad.get('name', 'Unnamed')} (ID: {ad['id']}) - {ad.get('status', 'N/A')}\n"
    return result


async def _get_ad(client: FacebookAdsClient, ad_id: str) -> str:
    if not ad_id:
        return "ERROR: ad_id required"
    if client.is_test_mode:
        return f"Ad {ad_id}:\n  Name: Test Ad\n  Status: PAUSED\n"
    data = await client.request("GET", ad_id, params={"fields": "id,name,status,adset_id,creative,created_time,effective_status"})
    result = f"Ad {ad_id}:\n  Name: {data.get('name', 'N/A')}\n  Status: {data.get('status', 'N/A')}\n"
    result += f"  Adset: {data.get('adset_id', 'N/A')}\n"
    if data.get("creative"):
        result += f"  Creative: {data['creative'].get('id', 'N/A')}\n"
    return result


async def _create_ad(client: FacebookAdsClient, ad_account_id: str, adset_id: str, creative_id: str, name: Optional[str], status: str) -> str:
    if not ad_account_id or not adset_id or not creative_id:
        return "ERROR: ad_account_id, adset_id, creative_id all required"
    if status not in ["ACTIVE", "PAUSED"]:
        return "ERROR: status must be ACTIVE or PAUSED"
    if client.is_test_mode:
        return f"Ad created!\nID: mock_ad_123\nName: {name}\nAdset: {adset_id}\nStatus: {status}\n"
    data = {"name": name or "Ad", "adset_id": adset_id, "creative": {"creative_id": creative_id}, "status": status}
    result = await client.request("POST", f"{ad_account_id}/ads", data=data)
    ad_id = result.get("id")
    return f"Ad created!\nID: {ad_id}\nName: {name}\nAdset: {adset_id}\nStatus: {status}\n" if ad_id else f"Failed to create ad. Response: {result}"


async def _update_ad(client: FacebookAdsClient, ad_id: str, name: Optional[str], status: Optional[str]) -> str:
    if not ad_id:
        return "ERROR: ad_id required"
    if not any([name, status]):
        return "ERROR: name or status required"
    if status and status not in ["ACTIVE", "PAUSED", "ARCHIVED", "DELETED"]:
        return "ERROR: status must be ACTIVE, PAUSED, ARCHIVED or DELETED"
    if client.is_test_mode:
        return f"Ad {ad_id} updated."
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if status:
        data["status"] = status
    result = await client.request("POST", ad_id, data=data)
    return f"Ad {ad_id} updated." if result.get("success") else f"Failed to update. Response: {result}"


async def _delete_ad(client: FacebookAdsClient, ad_id: str) -> str:
    if not ad_id:
        return "ERROR: ad_id required"
    if client.is_test_mode:
        return f"Ad {ad_id} deleted."
    result = await client.request("DELETE", ad_id)
    return f"Ad {ad_id} deleted." if result.get("success") else f"Failed to delete. Response: {result}"


async def _preview_ad(client: FacebookAdsClient, ad_id: str, ad_format: str) -> str:
    if not ad_id:
        return "ERROR: ad_id required"
    try:
        AdFormat(ad_format)
    except ValueError:
        return f"ERROR: Invalid ad_format. Must be one of: {', '.join(f.value for f in AdFormat)}"
    if client.is_test_mode:
        return f"Ad Preview for {ad_id} ({ad_format}):\n  Preview URL: https://facebook.com/ads/preview/mock_{ad_id}\n"
    data = await client.request("GET", f"{ad_id}/previews", params={"ad_format": ad_format})
    previews = data.get("data", [])
    if not previews:
        return "No preview available"
    body = previews[0].get("body", "")
    return f"Ad Preview for {ad_id} ({ad_format}):\n{body[:500]}...\n" if body else f"Preview available but no body. Response: {previews[0]}"


# ── Creatives ─────────────────────────────────────────────────────────────────

async def _list_creatives(client: FacebookAdsClient, ad_account_id: str) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    if client.is_test_mode:
        return f"Creatives for {ad_account_id}:\n  Test Creative (ID: 987654321)\n"
    data = await client.request("GET", f"{ad_account_id}/adcreatives", params={"fields": "id,name,status,object_story_spec", "limit": 100})
    creatives = data.get("data", [])
    if not creatives:
        return f"No creatives found for {ad_account_id}"
    result = f"Ad Creatives for {ad_account_id} ({len(creatives)}):\n\n"
    for c in creatives:
        result += f"  {c.get('name', 'Unnamed')} (ID: {c['id']})\n"
    return result


async def _get_creative(client: FacebookAdsClient, creative_id: str) -> str:
    if not creative_id:
        return "ERROR: creative_id required"
    if client.is_test_mode:
        return f"Creative {creative_id}:\n  Name: Test Creative\n  Status: ACTIVE\n"
    data = await client.request("GET", creative_id, params={"fields": "id,name,status,object_story_spec,call_to_action_type,thumbnail_url,image_hash,video_id"})
    result = f"Creative {creative_id}:\n  Name: {data.get('name', 'N/A')}\n  Status: {data.get('status', 'N/A')}\n"
    if data.get("call_to_action_type"):
        result += f"  CTA: {data['call_to_action_type']}\n"
    return result


async def _create_creative(client: FacebookAdsClient, ad_account_id: str, name: str, page_id: str, message: Optional[str], link: Optional[str], image_hash: Optional[str], video_id: Optional[str], call_to_action_type: Optional[str]) -> str:
    if not name or not page_id:
        return "ERROR: name and page_id required"
    if not image_hash and not video_id:
        return "ERROR: image_hash or video_id required"
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id required"
    cta = call_to_action_type or "LEARN_MORE"
    try:
        CallToActionType(cta)
    except ValueError:
        return f"ERROR: Invalid call_to_action_type. Must be one of: {', '.join(c.value for c in CallToActionType)}"
    if client.is_test_mode:
        return f"Creative created!\nID: mock_creative_123\nName: {name}\nPage: {page_id}\nCTA: {cta}\n"
    link_data: Dict[str, Any] = {"call_to_action": {"type": cta}}
    if image_hash:
        link_data["image_hash"] = image_hash
    if link:
        link_data["link"] = link
    if message:
        link_data["message"] = message
    data: Dict[str, Any] = {"name": name, "object_story_spec": {"page_id": page_id, "link_data": link_data}}
    result = await client.request("POST", f"{account_id}/adcreatives", data=data)
    creative_id = result.get("id")
    return f"Creative created!\nID: {creative_id}\nName: {name}\nPage: {page_id}\nCTA: {cta}\n" if creative_id else f"Failed to create creative. Response: {result}"


async def _update_creative(client: FacebookAdsClient, creative_id: str, name: Optional[str]) -> str:
    if not creative_id or not name:
        return "ERROR: creative_id and name required"
    if client.is_test_mode:
        return f"Creative {creative_id} updated: name -> {name}"
    result = await client.request("POST", creative_id, data={"name": name})
    return f"Creative {creative_id} updated." if result.get("success") else f"Failed. Response: {result}"


async def _delete_creative(client: FacebookAdsClient, creative_id: str) -> str:
    if not creative_id:
        return "ERROR: creative_id required"
    if client.is_test_mode:
        return f"Creative {creative_id} deleted."
    result = await client.request("DELETE", creative_id)
    return f"Creative {creative_id} deleted." if result.get("success") else f"Failed. Response: {result}"


async def _preview_creative(client: FacebookAdsClient, creative_id: str, ad_format: str) -> str:
    if not creative_id:
        return "ERROR: creative_id required"
    try:
        AdFormat(ad_format)
    except ValueError:
        return f"ERROR: Invalid ad_format. Must be one of: {', '.join(f.value for f in AdFormat)}"
    if client.is_test_mode:
        return f"Creative Preview for {creative_id} ({ad_format}):\n  Preview URL: https://facebook.com/ads/preview/mock_{creative_id}\n"
    data = await client.request("GET", f"{creative_id}/previews", params={"ad_format": ad_format})
    previews = data.get("data", [])
    if not previews:
        return "No preview available"
    body = previews[0].get("body", "")
    return f"Creative Preview for {creative_id} ({ad_format}):\n{body[:500]}...\n" if body else "Preview available but no body."


async def _upload_image(client: FacebookAdsClient, image_path: Optional[str], image_url: Optional[str], ad_account_id: Optional[str]) -> str:
    if not image_path and not image_url:
        return "ERROR: image_path or image_url required"
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id required"
    if client.is_test_mode:
        return f"Image uploaded!\nImage Hash: mock_abc123\nAccount: {account_id}\n"
    endpoint = f"{account_id}/adimages"
    if image_url:
        result = await client.request("POST", endpoint, form_data={"url": image_url, "access_token": client.access_token})
    else:
        image_file = Path(image_path)
        if not image_file.exists():
            return f"ERROR: Image file not found: {image_path}"
        await client.ensure_auth()
        with open(image_file, 'rb') as f:
            image_bytes = f.read()
        url = f"{API_BASE}/{API_VERSION}/{endpoint}"
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(url, data={"access_token": client.access_token}, files={"filename": (image_file.name, image_bytes, "image/jpeg")}, timeout=60.0)
            if response.status_code != 200:
                return f"ERROR: Failed to upload image: {response.text}"
            result = response.json()
    images = result.get("images", {})
    if images:
        image_hash = list(images.values())[0].get("hash", "unknown")
        return f"Image uploaded!\nImage Hash: {image_hash}\nAccount: {account_id}\n"
    return f"Failed to upload image. Response: {result}"


async def _upload_video(client: FacebookAdsClient, video_url: str, ad_account_id: Optional[str], title: Optional[str], description: Optional[str]) -> str:
    if not video_url:
        return "ERROR: video_url required"
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id required"
    if client.is_test_mode:
        return f"Video uploaded!\nVideo ID: mock_video_123\nAccount: {account_id}\n"
    form_data: Dict[str, Any] = {"file_url": video_url, "access_token": client.access_token}
    if title:
        form_data["title"] = title
    if description:
        form_data["description"] = description
    result = await client.request("POST", f"{account_id}/advideos", form_data=form_data)
    video_id = result.get("id")
    return f"Video uploaded!\nVideo ID: {video_id}\nAccount: {account_id}\n" if video_id else f"Failed to upload video. Response: {result}"


async def _list_videos(client: FacebookAdsClient, ad_account_id: str) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    if client.is_test_mode:
        return f"Videos for {ad_account_id}:\n  Test Video (ID: mock_video_123) — READY\n"
    data = await client.request("GET", f"{ad_account_id}/advideos", params={"fields": "id,title,description,length,status", "limit": 50})
    videos = data.get("data", [])
    if not videos:
        return f"No videos found for {ad_account_id}"
    result = f"Ad Videos for {ad_account_id} ({len(videos)}):\n\n"
    for v in videos:
        result += f"  {v.get('title', 'Untitled')} (ID: {v['id']}) — {v.get('status', 'N/A')}\n"
    return result


# ── Audiences ─────────────────────────────────────────────────────────────────

_AUDIENCE_FIELDS = "id,name,subtype,description,approximate_count,delivery_status,created_time"


async def _list_custom_audiences(client: FacebookAdsClient, ad_account_id: str) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    if client.is_test_mode:
        return f"Custom Audiences for {ad_account_id}:\n  Test Audience (ID: 111222333) — CUSTOM — ~5,000 people\n"
    data = await client.request("GET", f"{ad_account_id}/customaudiences", params={"fields": _AUDIENCE_FIELDS, "limit": 100})
    audiences = data.get("data", [])
    if not audiences:
        return f"No custom audiences found for {ad_account_id}"
    result = f"Custom Audiences for {ad_account_id} ({len(audiences)}):\n\n"
    for a in audiences:
        result += f"  {a.get('name', 'Unnamed')} (ID: {a['id']}) — {a.get('subtype', 'N/A')} — ~{a.get('approximate_count', 'Unknown')} people\n"
    return result


async def _get_custom_audience(client: FacebookAdsClient, audience_id: str) -> str:
    if not audience_id:
        return "ERROR: audience_id required"
    if client.is_test_mode:
        return f"Audience {audience_id}:\n  Name: Test Audience\n  Subtype: CUSTOM\n  Size: ~5,000 people\n"
    data = await client.request("GET", audience_id, params={"fields": _AUDIENCE_FIELDS + ",rule,lookalike_spec,pixel_id"})
    return f"Audience {audience_id}:\n  Name: {data.get('name', 'N/A')}\n  Subtype: {data.get('subtype', 'N/A')}\n  Size: ~{data.get('approximate_count', 'Unknown')} people\n"


async def _create_custom_audience(client: FacebookAdsClient, ad_account_id: str, name: str, subtype: str, description: Optional[str], customer_file_source: Optional[str]) -> str:
    if not ad_account_id or not name:
        return "ERROR: ad_account_id and name required"
    try:
        CustomAudienceSubtype(subtype)
    except ValueError:
        return f"ERROR: Invalid subtype. Must be one of: {', '.join(s.value for s in CustomAudienceSubtype)}"
    if client.is_test_mode:
        return f"Custom audience created:\n  Name: {name}\n  ID: mock_audience_123\n  Subtype: {subtype}\n"
    data: Dict[str, Any] = {"name": name, "subtype": subtype}
    if description:
        data["description"] = description
    if customer_file_source:
        data["customer_file_source"] = customer_file_source
    result = await client.request("POST", f"{ad_account_id}/customaudiences", data=data)
    audience_id = result.get("id")
    return f"Audience created:\n  Name: {name}\n  ID: {audience_id}\n  Subtype: {subtype}\n" if audience_id else f"Failed. Response: {result}"


async def _create_lookalike_audience(client: FacebookAdsClient, ad_account_id: str, origin_audience_id: str, country: str, ratio: float, name: Optional[str]) -> str:
    if not ad_account_id or not origin_audience_id or not country:
        return "ERROR: ad_account_id, origin_audience_id, country required"
    if not 0.01 <= ratio <= 0.20:
        return "ERROR: ratio must be between 0.01 (1%) and 0.20 (20%)"
    audience_name = name or f"Lookalike ({country}, {int(ratio*100)}%) of {origin_audience_id}"
    if client.is_test_mode:
        return f"Lookalike audience created:\n  Name: {audience_name}\n  ID: mock_lookalike_456\n  Country: {country}\n  Ratio: {ratio*100:.0f}%\n"
    data: Dict[str, Any] = {"name": audience_name, "subtype": "LOOKALIKE", "origin_audience_id": origin_audience_id, "lookalike_spec": {"country": country, "ratio": ratio, "type": "similarity"}}
    result = await client.request("POST", f"{ad_account_id}/customaudiences", data=data)
    audience_id = result.get("id")
    return f"Lookalike created:\n  Name: {audience_name}\n  ID: {audience_id}\n  Country: {country}\n  Ratio: {ratio*100:.0f}%\n" if audience_id else f"Failed. Response: {result}"


async def _update_custom_audience(client: FacebookAdsClient, audience_id: str, name: Optional[str], description: Optional[str]) -> str:
    if not audience_id or not any([name, description]):
        return "ERROR: audience_id and at least one field (name, description) required"
    if client.is_test_mode:
        return f"Audience {audience_id} updated."
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    result = await client.request("POST", audience_id, data=data)
    return f"Audience {audience_id} updated." if result.get("success") else f"Failed. Response: {result}"


async def _delete_custom_audience(client: FacebookAdsClient, audience_id: str) -> str:
    if not audience_id:
        return "ERROR: audience_id required"
    if client.is_test_mode:
        return f"Audience {audience_id} deleted."
    result = await client.request("DELETE", audience_id)
    return f"Audience {audience_id} deleted." if result.get("success") else f"Failed. Response: {result}"


async def _add_users_to_audience(client: FacebookAdsClient, audience_id: str, emails: List[str], phones: Optional[List[str]]) -> str:
    if not audience_id or not emails:
        return "ERROR: audience_id and emails required"
    import hashlib
    hashed_emails = [hashlib.sha256(e.strip().lower().encode()).hexdigest() for e in emails]
    schema = ["EMAIL"]
    user_data = [[h] for h in hashed_emails]
    if phones:
        schema = ["EMAIL", "PHONE"]
        hashed_phones = [hashlib.sha256(''.join(c for c in p if c.isdigit()).encode()).hexdigest() for p in phones]
        user_data = [[e, p] for e, p in zip(hashed_emails, hashed_phones)]
    if client.is_test_mode:
        return f"Users added to audience {audience_id}:\n  Emails: {len(emails)} (SHA-256 hashed)\n"
    payload: Dict[str, Any] = {"payload": {"schema": schema, "data": user_data}}
    result = await client.request("POST", f"{audience_id}/users", data=payload)
    received = result.get("num_received", 0)
    invalid = result.get("num_invalid_entries", 0)
    return f"Users added to {audience_id}:\n  Received: {received}\n  Invalid: {invalid}\n  Accepted: {received - invalid}\n"


# ── Pixels ────────────────────────────────────────────────────────────────────

async def _list_pixels(client: FacebookAdsClient, ad_account_id: str) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    if client.is_test_mode:
        return f"Pixels for {ad_account_id}:\n  Test Pixel (ID: 111222333) — last fired: recently\n"
    data = await client.request("GET", f"{ad_account_id}/adspixels", params={"fields": "id,name,creation_time,last_fired_time", "limit": 50})
    pixels = data.get("data", [])
    if not pixels:
        return f"No pixels found for {ad_account_id}"
    result = f"Pixels for {ad_account_id} ({len(pixels)}):\n\n"
    for p in pixels:
        result += f"  {p.get('name', 'Unnamed')} (ID: {p['id']}) — last fired: {p.get('last_fired_time', 'Never')}\n"
    return result


async def _create_pixel(client: FacebookAdsClient, ad_account_id: str, name: str) -> str:
    if not ad_account_id or not name:
        return "ERROR: ad_account_id and name required"
    if client.is_test_mode:
        return f"Pixel created:\n  Name: {name}\n  ID: mock_pixel_789\n"
    result = await client.request("POST", f"{ad_account_id}/adspixels", data={"name": name})
    pixel_id = result.get("id")
    return f"Pixel created:\n  Name: {name}\n  ID: {pixel_id}\n" if pixel_id else f"Failed. Response: {result}"


async def _get_pixel_stats(client: FacebookAdsClient, pixel_id: str, start_time: Optional[str], end_time: Optional[str], aggregation: str) -> str:
    if not pixel_id:
        return "ERROR: pixel_id required"
    if aggregation not in ["day", "hour", "week", "month"]:
        return "ERROR: aggregation must be day, hour, week or month"
    if client.is_test_mode:
        return f"Pixel Stats for {pixel_id}:\n  PageView: 3,450\n  Purchase: 127\n  Lead: 89\n"
    params: Dict[str, Any] = {"aggregation": aggregation, "fields": "event_name,count", "limit": 200}
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    data = await client.request("GET", f"{pixel_id}/stats", params=params)
    stats = data.get("data", [])
    if not stats:
        return f"No stats found for pixel {pixel_id}"
    totals: Dict[str, int] = {}
    for entry in stats:
        event = entry.get("event_name", "Unknown")
        totals[event] = totals.get(event, 0) + int(entry.get("count", 0))
    result = f"Pixel Stats for {pixel_id}:\n\n"
    for event, count in sorted(totals.items(), key=lambda x: -x[1]):
        result += f"  {event}: {count:,} events\n"
    return result


# ── Targeting ─────────────────────────────────────────────────────────────────

async def _search_interests(client: FacebookAdsClient, q: str, limit: int) -> str:
    if not q:
        return "ERROR: q (search query) required"
    if client.is_test_mode:
        return f"Interests matching '{q}':\n  Travel (ID: 6003263) — ~600M people\n"
    data = await client.request("GET", "search", params={"type": "adinterest", "q": q, "limit": min(limit, 50), "locale": "en_US"})
    items = data.get("data", [])
    if not items:
        return f"No interests found matching '{q}'"
    result = f"Interests matching '{q}' ({len(items)}):\n\n"
    for item in items:
        audience_size = item.get("audience_size", "Unknown")
        result += f"  {item.get('name', 'N/A')} (ID: {item.get('id', 'N/A')}) — ~{audience_size:,} people\n" if isinstance(audience_size, int) else f"  {item.get('name', 'N/A')} (ID: {item.get('id', 'N/A')})\n"
    return result


async def _search_behaviors(client: FacebookAdsClient, q: str, limit: int) -> str:
    if not q:
        return "ERROR: q (search query) required"
    if client.is_test_mode:
        return f"Behaviors matching '{q}':\n  Frequent Travelers (ID: 6002714) — ~120M people\n"
    data = await client.request("GET", "search", params={"type": "adbehavior", "q": q, "limit": min(limit, 50), "locale": "en_US"})
    items = data.get("data", [])
    if not items:
        return f"No behaviors found matching '{q}'"
    result = f"Behaviors matching '{q}' ({len(items)}):\n\n"
    for item in items:
        result += f"  {item.get('name', 'N/A')} (ID: {item.get('id', 'N/A')})\n"
    return result


async def _get_reach_estimate(client: FacebookAdsClient, ad_account_id: str, targeting: Dict[str, Any], optimization_goal: str) -> str:
    if not ad_account_id or not targeting:
        return "ERROR: ad_account_id and targeting required"
    if client.is_test_mode:
        return f"Reach Estimate for {ad_account_id}:\n  Estimated Audience: 1,200,000 — 1,800,000 people\n"
    data = await client.request("GET", f"{ad_account_id}/reachestimate", params={"targeting_spec": json.dumps(targeting), "optimization_goal": optimization_goal})
    users = data.get("users", "Unknown")
    return f"Reach Estimate:\n  Audience: {users:,} people\n  Goal: {optimization_goal}\n" if isinstance(users, int) else f"Reach Estimate:\n  Audience: {users}\n  Goal: {optimization_goal}\n"


async def _get_delivery_estimate(client: FacebookAdsClient, ad_account_id: str, targeting: Dict[str, Any], optimization_goal: str, bid_amount: Optional[int]) -> str:
    if not ad_account_id or not targeting:
        return "ERROR: ad_account_id and targeting required"
    if client.is_test_mode:
        return f"Delivery Estimate for {ad_account_id}:\n  Daily Min Spend: $5.00\n  Daily Max Spend: $50.00\n"
    params: Dict[str, Any] = {"targeting_spec": json.dumps(targeting), "optimization_goal": optimization_goal}
    if bid_amount:
        params["bid_amount"] = bid_amount
    data = await client.request("GET", f"{ad_account_id}/delivery_estimate", params=params)
    estimates = data.get("data", [])
    if not estimates:
        return f"No delivery estimates found for {ad_account_id}"
    result = f"Delivery Estimate for {ad_account_id}:\n\n"
    for est in estimates:
        daily = est.get("daily_outcomes_curve", [])
        if daily:
            first, last = daily[0], daily[-1]
            result += f"  Daily Spend: ${first.get('spend', 0)/100:.2f} — ${last.get('spend', 0)/100:.2f}\n"
            result += f"  Daily Reach: {first.get('reach', 0):,} — {last.get('reach', 0):,}\n"
    return result


# ── Rules ─────────────────────────────────────────────────────────────────────

async def _list_ad_rules(client: FacebookAdsClient, ad_account_id: str) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    if client.is_test_mode:
        return f"Ad Rules for {ad_account_id}:\n  Pause on low CTR (ID: 111222) — ENABLED\n"
    data = await client.request("GET", f"{ad_account_id}/adrules_library", params={"fields": "id,name,status,execution_spec", "limit": 50})
    rules = data.get("data", [])
    if not rules:
        return f"No ad rules found for {ad_account_id}"
    result = f"Ad Rules for {ad_account_id} ({len(rules)}):\n\n"
    for rule in rules:
        result += f"  {rule.get('name', 'Unnamed')} (ID: {rule['id']}) — {rule.get('status', 'N/A')}\n"
    return result


async def _create_ad_rule(client: FacebookAdsClient, ad_account_id: str, name: str, evaluation_spec: Dict[str, Any], execution_spec: Dict[str, Any], schedule_spec: Optional[Dict[str, Any]], status: str) -> str:
    if not ad_account_id or not name or not evaluation_spec or not execution_spec:
        return "ERROR: ad_account_id, name, evaluation_spec, execution_spec all required"
    if client.is_test_mode:
        return f"Ad rule created:\n  Name: {name}\n  ID: mock_rule_123\n  Status: {status}\n"
    data: Dict[str, Any] = {"name": name, "evaluation_spec": evaluation_spec, "execution_spec": execution_spec, "status": status}
    if schedule_spec:
        data["schedule_spec"] = schedule_spec
    result = await client.request("POST", f"{ad_account_id}/adrules_library", data=data)
    rule_id = result.get("id")
    return f"Ad rule created:\n  Name: {name}\n  ID: {rule_id}\n  Status: {status}\n" if rule_id else f"Failed. Response: {result}"


async def _update_ad_rule(client: FacebookAdsClient, rule_id: str, name: Optional[str], status: Optional[str]) -> str:
    if not rule_id or not any([name, status]):
        return "ERROR: rule_id and at least one field (name, status) required"
    if status and status not in ["ENABLED", "DISABLED", "DELETED"]:
        return "ERROR: status must be ENABLED, DISABLED or DELETED"
    if client.is_test_mode:
        return f"Ad rule {rule_id} updated."
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if status:
        data["status"] = status
    result = await client.request("POST", rule_id, data=data)
    return f"Ad rule {rule_id} updated." if result.get("success") else f"Failed. Response: {result}"


async def _delete_ad_rule(client: FacebookAdsClient, rule_id: str) -> str:
    if not rule_id:
        return "ERROR: rule_id required"
    if client.is_test_mode:
        return f"Ad rule {rule_id} deleted."
    result = await client.request("DELETE", rule_id)
    return f"Ad rule {rule_id} deleted." if result.get("success") else f"Failed. Response: {result}"


async def _execute_ad_rule(client: FacebookAdsClient, rule_id: str) -> str:
    if not rule_id:
        return "ERROR: rule_id required"
    if client.is_test_mode:
        return f"Ad rule {rule_id} executed."
    result = await client.request("POST", f"{rule_id}/execute", data={})
    return f"Ad rule {rule_id} executed." if result.get("success") else f"Failed. Response: {result}"


# ── Dispatch table ────────────────────────────────────────────────────────────

_HANDLERS: Dict[str, Any] = {
    "list_campaigns": lambda c, a: _list_campaigns(c, a.get("ad_account_id"), a.get("status")),
    "get_campaign": lambda c, a: _get_campaign(c, a.get("campaign_id", "")),
    "create_campaign": lambda c, a: _create_campaign(c, a.get("ad_account_id", ""), a.get("name", ""), a.get("objective", "OUTCOME_AWARENESS"), a.get("daily_budget"), a.get("lifetime_budget"), a.get("status", "PAUSED")),
    "update_campaign": lambda c, a: _update_campaign(c, a.get("campaign_id", ""), a.get("name"), a.get("status"), a.get("daily_budget"), a.get("lifetime_budget")),
    "delete_campaign": lambda c, a: _delete_campaign(c, a.get("campaign_id", "")),
    "duplicate_campaign": lambda c, a: _duplicate_campaign(c, a.get("campaign_id", ""), a.get("new_name", ""), a.get("ad_account_id")),
    "archive_campaign": lambda c, a: _archive_campaign(c, a.get("campaign_id", "")),
    "bulk_update_campaigns": lambda c, a: _bulk_update_campaigns(c, a.get("campaigns", [])),
    "list_adsets": lambda c, a: _list_adsets(c, a.get("campaign_id", "")),
    "list_adsets_for_account": lambda c, a: _list_adsets_for_account(c, a.get("ad_account_id", ""), a.get("status_filter")),
    "get_adset": lambda c, a: _get_adset(c, a.get("adset_id", "")),
    "create_adset": lambda c, a: _create_adset(c, a.get("ad_account_id", ""), a.get("campaign_id", ""), a.get("name", ""), a.get("targeting", {}), a.get("optimization_goal", "LINK_CLICKS"), a.get("billing_event", "IMPRESSIONS"), a.get("daily_budget"), a.get("lifetime_budget"), a.get("status", "PAUSED")),
    "update_adset": lambda c, a: _update_adset(c, a.get("adset_id", ""), a.get("name"), a.get("status"), a.get("daily_budget"), a.get("targeting")),
    "delete_adset": lambda c, a: _delete_adset(c, a.get("adset_id", "")),
    "validate_targeting": lambda c, a: _validate_targeting(c, a.get("targeting_spec", a.get("targeting", {})), a.get("ad_account_id")),
    "list_ads": lambda c, a: _list_ads(c, a.get("ad_account_id"), a.get("adset_id"), a.get("status_filter")),
    "get_ad": lambda c, a: _get_ad(c, a.get("ad_id", "")),
    "create_ad": lambda c, a: _create_ad(c, a.get("ad_account_id", ""), a.get("adset_id", ""), a.get("creative_id", ""), a.get("name"), a.get("status", "PAUSED")),
    "update_ad": lambda c, a: _update_ad(c, a.get("ad_id", ""), a.get("name"), a.get("status")),
    "delete_ad": lambda c, a: _delete_ad(c, a.get("ad_id", "")),
    "preview_ad": lambda c, a: _preview_ad(c, a.get("ad_id", ""), a.get("ad_format", "DESKTOP_FEED_STANDARD")),
    "list_creatives": lambda c, a: _list_creatives(c, a.get("ad_account_id", "")),
    "get_creative": lambda c, a: _get_creative(c, a.get("creative_id", "")),
    "create_creative": lambda c, a: _create_creative(c, a.get("ad_account_id", ""), a.get("name", ""), a.get("page_id", ""), a.get("message"), a.get("link"), a.get("image_hash"), a.get("video_id"), a.get("call_to_action_type")),
    "update_creative": lambda c, a: _update_creative(c, a.get("creative_id", ""), a.get("name")),
    "delete_creative": lambda c, a: _delete_creative(c, a.get("creative_id", "")),
    "preview_creative": lambda c, a: _preview_creative(c, a.get("creative_id", ""), a.get("ad_format", "DESKTOP_FEED_STANDARD")),
    "upload_image": lambda c, a: _upload_image(c, a.get("image_path"), a.get("image_url"), a.get("ad_account_id")),
    "upload_video": lambda c, a: _upload_video(c, a.get("video_url", ""), a.get("ad_account_id"), a.get("title"), a.get("description")),
    "list_videos": lambda c, a: _list_videos(c, a.get("ad_account_id", "")),
    "list_custom_audiences": lambda c, a: _list_custom_audiences(c, a.get("ad_account_id", "")),
    "get_custom_audience": lambda c, a: _get_custom_audience(c, a.get("audience_id", "")),
    "create_custom_audience": lambda c, a: _create_custom_audience(c, a.get("ad_account_id", ""), a.get("name", ""), a.get("subtype", "CUSTOM"), a.get("description"), a.get("customer_file_source")),
    "create_lookalike_audience": lambda c, a: _create_lookalike_audience(c, a.get("ad_account_id", ""), a.get("origin_audience_id", ""), a.get("country", ""), float(a.get("ratio", 0.01)), a.get("name")),
    "update_custom_audience": lambda c, a: _update_custom_audience(c, a.get("audience_id", ""), a.get("name"), a.get("description")),
    "delete_custom_audience": lambda c, a: _delete_custom_audience(c, a.get("audience_id", "")),
    "add_users_to_audience": lambda c, a: _add_users_to_audience(c, a.get("audience_id", ""), a.get("emails", []), a.get("phones")),
    "list_pixels": lambda c, a: _list_pixels(c, a.get("ad_account_id", "")),
    "create_pixel": lambda c, a: _create_pixel(c, a.get("ad_account_id", ""), a.get("name", "")),
    "get_pixel_stats": lambda c, a: _get_pixel_stats(c, a.get("pixel_id", ""), a.get("start_time"), a.get("end_time"), a.get("aggregation", "day")),
    "search_interests": lambda c, a: _search_interests(c, a.get("q", ""), int(a.get("limit", 20))),
    "search_behaviors": lambda c, a: _search_behaviors(c, a.get("q", ""), int(a.get("limit", 20))),
    "get_reach_estimate": lambda c, a: _get_reach_estimate(c, a.get("ad_account_id", ""), a.get("targeting", {}), a.get("optimization_goal", "LINK_CLICKS")),
    "get_delivery_estimate": lambda c, a: _get_delivery_estimate(c, a.get("ad_account_id", ""), a.get("targeting", {}), a.get("optimization_goal", "LINK_CLICKS"), a.get("bid_amount")),
    "list_ad_rules": lambda c, a: _list_ad_rules(c, a.get("ad_account_id", "")),
    "create_ad_rule": lambda c, a: _create_ad_rule(c, a.get("ad_account_id", ""), a.get("name", ""), a.get("evaluation_spec", {}), a.get("execution_spec", {}), a.get("schedule_spec"), a.get("status", "ENABLED")),
    "update_ad_rule": lambda c, a: _update_ad_rule(c, a.get("rule_id", ""), a.get("name"), a.get("status")),
    "delete_ad_rule": lambda c, a: _delete_ad_rule(c, a.get("rule_id", "")),
    "execute_ad_rule": lambda c, a: _execute_ad_rule(c, a.get("rule_id", "")),
}


# ── Integration class ─────────────────────────────────────────────────────────

class IntegrationMetaMarketingManage:
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
            logger.info("meta_marketing_manage api error: %s", e)
            return e.format_for_user()
        except FacebookValidationError as e:
            return f"Error: {e.message}"
        except Exception as e:
            logger.error("Unexpected error in meta_marketing_manage op=%s", (model_produced_args or {}).get("op"), exc_info=e)
            return f"Error: {e}"

    async def _status(self) -> str:
        try:
            auth_error = await self.client.ensure_auth()
            if auth_error:
                return auth_error
            return "meta_marketing_manage: connected. Use op=help to see available operations."
        except (FacebookAuthError, FacebookAPIError, FacebookValidationError) as e:
            return e.message
        except Exception as e:
            logger.error("Unexpected error in meta_marketing_manage status", exc_info=e)
            return f"Error: {e}"
