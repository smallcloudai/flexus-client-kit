from __future__ import annotations
import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flexus_client_kit.integrations.facebook.client import FacebookAdsClient

logger = logging.getLogger("facebook.operations.pixels")


async def list_pixels(
    client: "FacebookAdsClient",
    ad_account_id: str,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if client.is_test_mode:
        return f"Pixels for {ad_account_id}:\n  Test Pixel (ID: 111222333) — ACTIVE — 1,250 events last 7 days\n"
    data = await client.request(
        "GET", f"{ad_account_id}/adspixels",
        params={"fields": "id,name,code,creation_time,last_fired_time,owner_business", "limit": 50},
    )
    pixels = data.get("data", [])
    if not pixels:
        return f"No pixels found for {ad_account_id}"
    result = f"Pixels for {ad_account_id} ({len(pixels)} total):\n\n"
    for p in pixels:
        result += f"  **{p.get('name', 'Unnamed')}** (ID: {p['id']})\n"
        result += f"     Last fired: {p.get('last_fired_time', 'Never')}\n"
        result += f"     Created: {p.get('creation_time', 'N/A')}\n\n"
    return result


async def create_pixel(
    client: "FacebookAdsClient",
    ad_account_id: str,
    name: str,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if not name:
        return "ERROR: name is required"
    if client.is_test_mode:
        return f"Pixel created:\n  Name: {name}\n  ID: mock_pixel_789\n  Install the pixel code on your website to start tracking events.\n"
    result = await client.request(
        "POST", f"{ad_account_id}/adspixels",
        data={"name": name},
    )
    pixel_id = result.get("id")
    if not pixel_id:
        return f"Failed to create pixel. Response: {result}"
    return f"Pixel created:\n  Name: {name}\n  ID: {pixel_id}\n  Install the pixel code on your website to start tracking events.\n  View stats with: get_pixel_stats(pixel_id='{pixel_id}')\n"


async def get_pixel_stats(
    client: "FacebookAdsClient",
    pixel_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    aggregation: str = "day",
) -> str:
    if not pixel_id:
        return "ERROR: pixel_id is required"
    valid_aggregations = ["day", "hour", "week", "month"]
    if aggregation not in valid_aggregations:
        return f"ERROR: aggregation must be one of: {', '.join(valid_aggregations)}"
    if client.is_test_mode:
        return f"Pixel Stats for {pixel_id}:\n  PageView: 3,450 events\n  Purchase: 127 events\n  AddToCart: 342 events\n  Lead: 89 events\n"
    params: Dict[str, Any] = {
        "aggregation": aggregation,
        "fields": "event_name,count,start_time,end_time",
        "limit": 200,
    }
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    data = await client.request("GET", f"{pixel_id}/stats", params=params)
    stats = data.get("data", [])
    if not stats:
        return f"No stats found for pixel {pixel_id}"
    event_totals: Dict[str, int] = {}
    for entry in stats:
        event = entry.get("event_name", "Unknown")
        count = int(entry.get("count", 0))
        event_totals[event] = event_totals.get(event, 0) + count
    result = f"Pixel Stats for {pixel_id}:\n\n"
    for event, count in sorted(event_totals.items(), key=lambda x: -x[1]):
        result += f"  {event}: {count:,} events\n"
    return result
