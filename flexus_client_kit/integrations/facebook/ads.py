from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING
import httpx
from .models import AdFormat, CallToActionType
from .utils import validate_ad_account_id
from .exceptions import FacebookValidationError
if TYPE_CHECKING:
    from ..client import FacebookAdsClient
logger = logging.getLogger("facebook.operations.ads")
async def upload_image(
    client: "FacebookAdsClient",
    image_path: Optional[str] = None,
    image_url: Optional[str] = None,
    ad_account_id: Optional[str] = None,
) -> str:
    if not image_path and not image_url:
        return "ERROR: Either image_path or image_url is required"
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        try:
            account_id = validate_ad_account_id(account_id)
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"
    if client.is_test_mode:
        return f"""Image uploaded successfully!
Image Hash: abc123def456
Ad Account: {account_id}
You can now use this image hash in create_creative()
"""
    endpoint = f"{account_id}/adimages"
    if image_url:
        form_data = {
            "url": image_url,
            "access_token": client.access_token,
        }
        logger.info(f"Uploading image from URL to {endpoint}")
        result = await client.request("POST", endpoint, form_data=form_data)
    elif image_path:
        image_file = Path(image_path)
        if not image_file.exists():
            return f"ERROR: Image file not found: {image_path}"
        await client.ensure_auth()
        with open(image_file, 'rb') as f:
            image_bytes = f.read()
        from ..client import API_BASE, API_VERSION
        files = {"filename": (image_file.name, image_bytes, "image/jpeg")}
        form_data = {"access_token": client.access_token}
        url = f"{API_BASE}/{API_VERSION}/{endpoint}"
        logger.info(f"Uploading image file to {url}")
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(url, data=form_data, files=files, timeout=60.0)
            if response.status_code != 200:
                return f"ERROR: Failed to upload image: {response.text}"
            result = response.json()
    images = result.get("images", {})
    if images:
        image_hash = list(images.values())[0].get("hash", "unknown")
        return f"""Image uploaded successfully!
Image Hash: {image_hash}
Ad Account: {account_id}
Use this hash in create_creative():
  facebook(op="create_creative", args={{
    "image_hash": "{image_hash}",
    ...
  }})
"""
    else:
        return f"Failed to upload image. Response: {result}"
async def create_creative(
    client: "FacebookAdsClient",
    name: str,
    page_id: str,
    image_hash: str,
    link: str,
    message: Optional[str] = None,
    headline: Optional[str] = None,
    description: Optional[str] = None,
    call_to_action_type: str = "LEARN_MORE",
    ad_account_id: Optional[str] = None,
) -> str:
    if not name:
        return "ERROR: name is required"
    if not page_id:
        return "ERROR: page_id is required"
    if not image_hash:
        return "ERROR: image_hash is required (use upload_image first)"
    if not link:
        return "ERROR: link is required"
    try:
        CallToActionType(call_to_action_type)
    except ValueError:
        valid = [c.value for c in CallToActionType]
        return f"ERROR: Invalid call_to_action_type. Must be one of: {', '.join(valid)}"
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id is required"
    if client.is_test_mode:
        return f"""Creative created successfully!
Creative ID: 987654321
Name: {name}
Page ID: {page_id}
Image Hash: {image_hash}
Link: {link}
CTA: {call_to_action_type}
Now create an ad using this creative:
  facebook(op="create_ad", args={{
    "adset_id": "...",
    "creative_id": "987654321",
    ...
  }})
"""
    link_data: Dict[str, Any] = {
        "image_hash": image_hash,
        "link": link,
        "call_to_action": {"type": call_to_action_type}
    }
    if message:
        link_data["message"] = message
    if headline:
        link_data["name"] = headline
    if description:
        link_data["description"] = description
    data = {
        "name": name,
        "object_story_spec": {
            "page_id": page_id,
            "link_data": link_data
        }
    }
    result = await client.request("POST", f"{account_id}/adcreatives", data=data)
    creative_id = result.get("id")
    if not creative_id:
        return f"Failed to create creative. Response: {result}"
    return f"""Creative created successfully!
Creative ID: {creative_id}
Name: {name}
Page ID: {page_id}
Image Hash: {image_hash}
Link: {link}
CTA: {call_to_action_type}
Now create an ad using this creative:
  facebook(op="create_ad", args={{
    "adset_id": "YOUR_ADSET_ID",
    "creative_id": "{creative_id}",
    "name": "Your Ad Name"
  }})
"""
async def create_ad(
    client: "FacebookAdsClient",
    name: str,
    adset_id: str,
    creative_id: str,
    status: str = "PAUSED",
    ad_account_id: Optional[str] = None,
) -> str:
    if not name:
        return "ERROR: name is required"
    if not adset_id:
        return "ERROR: adset_id is required"
    if not creative_id:
        return "ERROR: creative_id is required"
    if status not in ["ACTIVE", "PAUSED"]:
        return "ERROR: status must be 'ACTIVE' or 'PAUSED'"
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id is required"
    if client.is_test_mode:
        status_msg = (
            "Ad is paused. Activate it when ready to start delivery."
            if status == "PAUSED"
            else "Ad is active and will start delivery."
        )
        return f"""Ad created successfully!
Ad ID: 111222333444555
Name: {name}
Ad Set ID: {adset_id}
Creative ID: {creative_id}
Status: {status}
{status_msg}
Preview your ad:
  facebook(op="preview_ad", args={{"ad_id": "111222333444555"}})
"""
    data = {
        "name": name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": status
    }
    result = await client.request("POST", f"{account_id}/ads", data=data)
    ad_id = result.get("id")
    if not ad_id:
        return f"Failed to create ad. Response: {result}"
    status_msg = (
        "Ad is paused. Activate it when ready to start delivery."
        if status == "PAUSED"
        else "Ad is active and will start delivery."
    )
    return f"""Ad created successfully!
Ad ID: {ad_id}
Name: {name}
Ad Set ID: {adset_id}
Creative ID: {creative_id}
Status: {status}
{status_msg}
Preview your ad:
  facebook(op="preview_ad", args={{"ad_id": "{ad_id}"}})
"""
async def preview_ad(client: "FacebookAdsClient", ad_id: str, ad_format: str = "DESKTOP_FEED_STANDARD") -> str:
    if not ad_id:
        return "ERROR: ad_id is required"
    try:
        AdFormat(ad_format)
    except ValueError:
        valid = [f.value for f in AdFormat]
        return f"ERROR: Invalid ad_format. Must be one of: {', '.join(valid)}"
    if client.is_test_mode:
        return f"""Ad Preview for {ad_id}:
Format: {ad_format}
Preview URL: https://facebook.com/ads/preview/mock_{ad_id}
Note: This is a mock preview. In production, Facebook will provide actual preview HTML/URL.
"""
    data = await client.request("GET", f"{ad_id}/previews", params={"ad_format": ad_format})
    previews = data.get("data", [])
    if not previews:
        return "No preview available for this ad"
    preview = previews[0]
    body = preview.get("body", "")
    if body:
        return f"""Ad Preview for {ad_id}:
Format: {ad_format}
Preview HTML available (truncated):
{body[:500]}...
To view full preview, open the ad in Facebook Ads Manager.
"""
    else:
        return f"Preview generated but no body content available. Response: {preview}"
