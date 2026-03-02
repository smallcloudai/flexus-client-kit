from __future__ import annotations
import hashlib
import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from flexus_client_kit.integrations.facebook.models import CustomAudienceSubtype

if TYPE_CHECKING:
    from flexus_client_kit.integrations.facebook.client import FacebookAdsClient

logger = logging.getLogger("facebook.operations.audiences")

AUDIENCE_FIELDS = "id,name,subtype,description,approximate_count,delivery_status,created_time,updated_time"


async def list_custom_audiences(
    client: "FacebookAdsClient",
    ad_account_id: str,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if client.is_test_mode:
        return f"Custom Audiences for {ad_account_id}:\n  Test Audience (ID: 111222333) — CUSTOM — ~5,000 people\n"
    data = await client.request(
        "GET", f"{ad_account_id}/customaudiences",
        params={"fields": AUDIENCE_FIELDS, "limit": 100},
    )
    audiences = data.get("data", [])
    if not audiences:
        return f"No custom audiences found for {ad_account_id}"
    result = f"Custom Audiences for {ad_account_id} ({len(audiences)} total):\n\n"
    for a in audiences:
        count = a.get("approximate_count", "Unknown")
        result += f"  **{a.get('name', 'Unnamed')}** (ID: {a['id']})\n"
        result += f"     Type: {a.get('subtype', 'N/A')} | Size: ~{count} people\n"
        if a.get("description"):
            result += f"     Description: {a['description'][:80]}\n"
        result += "\n"
    return result


async def create_custom_audience(
    client: "FacebookAdsClient",
    ad_account_id: str,
    name: str,
    subtype: str = "CUSTOM",
    description: Optional[str] = None,
    customer_file_source: Optional[str] = None,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if not name:
        return "ERROR: name is required"
    try:
        CustomAudienceSubtype(subtype)
    except ValueError:
        valid = [s.value for s in CustomAudienceSubtype]
        return f"ERROR: Invalid subtype. Must be one of: {', '.join(valid)}"
    if client.is_test_mode:
        return f"Custom audience created:\n  Name: {name}\n  ID: mock_audience_123\n  Subtype: {subtype}\n"
    data: Dict[str, Any] = {
        "name": name,
        "subtype": subtype,
    }
    if description:
        data["description"] = description
    if customer_file_source:
        data["customer_file_source"] = customer_file_source
    result = await client.request("POST", f"{ad_account_id}/customaudiences", data=data)
    audience_id = result.get("id")
    if not audience_id:
        return f"Failed to create audience. Response: {result}"
    return f"Custom audience created:\n  Name: {name}\n  ID: {audience_id}\n  Subtype: {subtype}\n  Use add_users_to_audience to populate it.\n"


async def create_lookalike_audience(
    client: "FacebookAdsClient",
    ad_account_id: str,
    origin_audience_id: str,
    country: str,
    ratio: float = 0.01,
    name: Optional[str] = None,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if not origin_audience_id:
        return "ERROR: origin_audience_id is required"
    if not country:
        return "ERROR: country is required (e.g. 'US', 'GB')"
    if not 0.01 <= ratio <= 0.20:
        return "ERROR: ratio must be between 0.01 (1%) and 0.20 (20%)"
    audience_name = name or f"Lookalike ({country}, {int(ratio*100)}%) of {origin_audience_id}"
    if client.is_test_mode:
        return f"Lookalike audience created:\n  Name: {audience_name}\n  ID: mock_lookalike_456\n  Country: {country}\n  Ratio: {ratio*100:.0f}%\n"
    data: Dict[str, Any] = {
        "name": audience_name,
        "subtype": "LOOKALIKE",
        "origin_audience_id": origin_audience_id,
        "lookalike_spec": {
            "country": country,
            "ratio": ratio,
            "type": "similarity",
        },
    }
    result = await client.request("POST", f"{ad_account_id}/customaudiences", data=data)
    audience_id = result.get("id")
    if not audience_id:
        return f"Failed to create lookalike audience. Response: {result}"
    return f"Lookalike audience created:\n  Name: {audience_name}\n  ID: {audience_id}\n  Country: {country}\n  Ratio: {ratio*100:.0f}%\n  Source: {origin_audience_id}\n"


async def get_custom_audience(
    client: "FacebookAdsClient",
    audience_id: str,
) -> str:
    if not audience_id:
        return "ERROR: audience_id is required"
    if client.is_test_mode:
        return f"Audience {audience_id}:\n  Name: Test Audience\n  Subtype: CUSTOM\n  Size: ~5,000 people\n  Status: ready\n"
    data = await client.request(
        "GET", audience_id,
        params={"fields": AUDIENCE_FIELDS + ",rule,lookalike_spec,pixel_id"},
    )
    result = f"Audience {audience_id}:\n"
    result += f"  Name: {data.get('name', 'N/A')}\n"
    result += f"  Subtype: {data.get('subtype', 'N/A')}\n"
    result += f"  Size: ~{data.get('approximate_count', 'Unknown')} people\n"
    if data.get("description"):
        result += f"  Description: {data['description']}\n"
    if data.get("delivery_status"):
        delivery = data["delivery_status"]
        result += f"  Delivery Status: {delivery.get('code', 'N/A')} — {delivery.get('description', '')}\n"
    result += f"  Created: {data.get('created_time', 'N/A')}\n"
    return result


async def update_custom_audience(
    client: "FacebookAdsClient",
    audience_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    if not audience_id:
        return "ERROR: audience_id is required"
    if not any([name, description]):
        return "ERROR: At least one field to update is required (name, description)"
    if client.is_test_mode:
        updates = []
        if name:
            updates.append(f"name -> {name}")
        if description:
            updates.append(f"description -> {description}")
        return f"Audience {audience_id} updated:\n" + "\n".join(f"  - {u}" for u in updates)
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    result = await client.request("POST", audience_id, data=data)
    if result.get("success"):
        return f"Audience {audience_id} updated successfully."
    return f"Failed to update audience. Response: {result}"


async def delete_custom_audience(
    client: "FacebookAdsClient",
    audience_id: str,
) -> str:
    if not audience_id:
        return "ERROR: audience_id is required"
    if client.is_test_mode:
        return f"Audience {audience_id} deleted successfully."
    result = await client.request("DELETE", audience_id)
    if result.get("success"):
        return f"Audience {audience_id} deleted successfully."
    return f"Failed to delete audience. Response: {result}"


async def add_users_to_audience(
    client: "FacebookAdsClient",
    audience_id: str,
    emails: List[str],
    phones: Optional[List[str]] = None,
) -> str:
    if not audience_id:
        return "ERROR: audience_id is required"
    if not emails:
        return "ERROR: emails list is required and cannot be empty"
    hashed_emails = [hashlib.sha256(e.strip().lower().encode()).hexdigest() for e in emails]
    schema = ["EMAIL"]
    user_data = [[h] for h in hashed_emails]
    if phones:
        schema = ["EMAIL", "PHONE"]
        hashed_phones = [hashlib.sha256(''.join(c for c in p if c.isdigit()).encode()).hexdigest() for p in phones]
        user_data = [[e, p] for e, p in zip(hashed_emails, hashed_phones)]
    if client.is_test_mode:
        return f"Users added to audience {audience_id}:\n  Emails: {len(emails)} (SHA-256 hashed)\n  Schema: {schema}\n"
    payload: Dict[str, Any] = {
        "payload": {
            "schema": schema,
            "data": user_data,
        }
    }
    result = await client.request("POST", f"{audience_id}/users", data=payload)
    num_received = result.get("num_received", 0)
    num_invalid = result.get("num_invalid_entries", 0)
    return f"Users added to audience {audience_id}:\n  Received: {num_received}\n  Invalid: {num_invalid}\n  Accepted: {num_received - num_invalid}\n"
