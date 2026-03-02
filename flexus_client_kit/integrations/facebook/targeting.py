from __future__ import annotations
import json
import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flexus_client_kit.integrations.facebook.client import FacebookAdsClient

logger = logging.getLogger("facebook.operations.targeting")


async def search_interests(
    client: "FacebookAdsClient",
    q: str,
    limit: int = 20,
) -> str:
    if not q:
        return "ERROR: q (search query) is required"
    if client.is_test_mode:
        return f"Interests matching '{q}':\n  Travel (ID: 6003263) — ~600M people\n  Adventure Travel (ID: 6003021) — ~50M people\n"
    data = await client.request(
        "GET", "search",
        params={
            "type": "adinterest",
            "q": q,
            "limit": min(limit, 50),
            "locale": "en_US",
        },
    )
    items = data.get("data", [])
    if not items:
        return f"No interests found matching '{q}'"
    result = f"Interests matching '{q}' ({len(items)} results):\n\n"
    for item in items:
        audience_size = item.get("audience_size", "Unknown")
        path = " > ".join(item.get("path", []))
        result += f"  **{item.get('name', 'N/A')}** (ID: {item.get('id', 'N/A')})\n"
        result += f"     Audience: ~{audience_size:,} people\n" if isinstance(audience_size, int) else f"     Audience: {audience_size}\n"
        if path:
            result += f"     Category: {path}\n"
        result += "\n"
    return result


async def search_behaviors(
    client: "FacebookAdsClient",
    q: str,
    limit: int = 20,
) -> str:
    if not q:
        return "ERROR: q (search query) is required"
    if client.is_test_mode:
        return f"Behaviors matching '{q}':\n  Frequent Travelers (ID: 6002714) — ~120M people\n"
    data = await client.request(
        "GET", "search",
        params={
            "type": "adbehavior",
            "q": q,
            "limit": min(limit, 50),
            "locale": "en_US",
        },
    )
    items = data.get("data", [])
    if not items:
        return f"No behaviors found matching '{q}'"
    result = f"Behaviors matching '{q}' ({len(items)} results):\n\n"
    for item in items:
        audience_size = item.get("audience_size", "Unknown")
        result += f"  **{item.get('name', 'N/A')}** (ID: {item.get('id', 'N/A')})\n"
        result += f"     Audience: ~{audience_size:,} people\n" if isinstance(audience_size, int) else f"     Audience: {audience_size}\n"
        result += "\n"
    return result


async def get_reach_estimate(
    client: "FacebookAdsClient",
    ad_account_id: str,
    targeting: Dict[str, Any],
    optimization_goal: str = "LINK_CLICKS",
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if not targeting:
        return "ERROR: targeting spec is required"
    if client.is_test_mode:
        return f"Reach Estimate for {ad_account_id}:\n  Estimated Audience: 1,200,000 — 1,800,000 people\n  Optimization: {optimization_goal}\n"
    params: Dict[str, Any] = {
        "targeting_spec": json.dumps(targeting),
        "optimization_goal": optimization_goal,
    }
    data = await client.request("GET", f"{ad_account_id}/reachestimate", params=params)
    users = data.get("users", "Unknown")
    estimate_ready = data.get("estimate_ready", False)
    result = f"Reach Estimate for {ad_account_id}:\n"
    result += f"  Estimated Audience: {users:,} people\n" if isinstance(users, int) else f"  Estimated Audience: {users}\n"
    result += f"  Estimate Ready: {estimate_ready}\n"
    result += f"  Optimization Goal: {optimization_goal}\n"
    return result


async def get_delivery_estimate(
    client: "FacebookAdsClient",
    ad_account_id: str,
    targeting: Dict[str, Any],
    optimization_goal: str = "LINK_CLICKS",
    bid_amount: Optional[int] = None,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if not targeting:
        return "ERROR: targeting spec is required"
    if client.is_test_mode:
        return f"Delivery Estimate for {ad_account_id}:\n  Daily Min Spend: $5.00\n  Daily Max Spend: $50.00\n  Min Reach: 800\n  Max Reach: 3,200\n  Optimization: {optimization_goal}\n"
    params: Dict[str, Any] = {
        "targeting_spec": json.dumps(targeting),
        "optimization_goal": optimization_goal,
    }
    if bid_amount:
        params["bid_amount"] = bid_amount
    data = await client.request("GET", f"{ad_account_id}/delivery_estimate", params=params)
    estimates = data.get("data", [])
    if not estimates:
        return f"No delivery estimates found for {ad_account_id}"
    result = f"Delivery Estimate for {ad_account_id}:\n\n"
    for est in estimates:
        result += f"  Optimization: {est.get('optimization_goal', optimization_goal)}\n"
        daily = est.get("daily_outcomes_curve", [])
        if daily:
            first = daily[0]
            last = daily[-1]
            result += f"  Daily Spend Range: ${first.get('spend', 0)/100:.2f} — ${last.get('spend', 0)/100:.2f}\n"
            result += f"  Daily Reach Range: {first.get('reach', 0):,} — {last.get('reach', 0):,}\n"
        result += "\n"
    return result
