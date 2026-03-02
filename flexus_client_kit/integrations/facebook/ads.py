from __future__ import annotations
import logging
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING
import httpx
from flexus_client_kit.integrations.facebook.models import AdFormat, CallToActionType
from flexus_client_kit.integrations.facebook.utils import validate_ad_account_id
from flexus_client_kit.integrations.facebook.exceptions import FacebookValidationError
if TYPE_CHECKING:
    from flexus_client_kit.integrations.facebook.client import FacebookAdsClient
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
        from flexus_client_kit.integrations.facebook.client import API_BASE, API_VERSION
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


async def get_ad(client: "FacebookAdsClient", ad_id: str) -> str:
    if not ad_id:
        return "ERROR: ad_id is required"
    if client.is_test_mode:
        return f"Ad {ad_id}:\n  Name: Test Ad\n  Status: PAUSED\n  Adset ID: 234567890\n  Creative ID: 987654321\n"
    data = await client.request(
        "GET", ad_id,
        params={"fields": "id,name,status,adset_id,creative,created_time,updated_time,effective_status,bid_amount"},
    )
    result = f"Ad {ad_id}:\n"
    result += f"  Name: {data.get('name', 'N/A')}\n"
    result += f"  Status: {data.get('status', 'N/A')} (effective: {data.get('effective_status', 'N/A')})\n"
    result += f"  Adset ID: {data.get('adset_id', 'N/A')}\n"
    creative = data.get("creative", {})
    if creative:
        result += f"  Creative ID: {creative.get('id', 'N/A')}\n"
    result += f"  Created: {data.get('created_time', 'N/A')}\n"
    return result


async def update_ad(
    client: "FacebookAdsClient",
    ad_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    if not ad_id:
        return "ERROR: ad_id is required"
    if not any([name, status]):
        return "ERROR: At least one field to update is required (name, status)"
    if status and status not in ["ACTIVE", "PAUSED", "ARCHIVED", "DELETED"]:
        return "ERROR: status must be one of: ACTIVE, PAUSED, ARCHIVED, DELETED"
    if client.is_test_mode:
        updates = []
        if name:
            updates.append(f"name -> {name}")
        if status:
            updates.append(f"status -> {status}")
        return f"Ad {ad_id} updated:\n" + "\n".join(f"  - {u}" for u in updates)
    data: Dict[str, Any] = {}
    if name:
        data["name"] = name
    if status:
        data["status"] = status
    result = await client.request("POST", ad_id, data=data)
    if result.get("success"):
        return f"Ad {ad_id} updated successfully."
    return f"Failed to update ad. Response: {result}"


async def delete_ad(client: "FacebookAdsClient", ad_id: str) -> str:
    if not ad_id:
        return "ERROR: ad_id is required"
    if client.is_test_mode:
        return f"Ad {ad_id} deleted successfully."
    result = await client.request("DELETE", ad_id)
    if result.get("success"):
        return f"Ad {ad_id} deleted successfully."
    return f"Failed to delete ad. Response: {result}"


async def list_ads(
    client: "FacebookAdsClient",
    ad_account_id: Optional[str] = None,
    adset_id: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> str:
    if not ad_account_id and not adset_id:
        return "ERROR: Either ad_account_id or adset_id is required"
    parent = adset_id if adset_id else ad_account_id
    endpoint = f"{parent}/ads"
    if client.is_test_mode:
        return f"Ads for {parent}:\n  Test Ad (ID: 111222333444555) — PAUSED\n"
    params: Dict[str, Any] = {
        "fields": "id,name,status,adset_id,creative{id},effective_status",
        "limit": 100,
    }
    if status_filter:
        params["effective_status"] = f'["{status_filter.upper()}"]'
    data = await client.request("GET", endpoint, params=params)
    ads = data.get("data", [])
    if not ads:
        return f"No ads found for {parent}"
    result = f"Ads for {parent} ({len(ads)} total):\n\n"
    for ad in ads:
        creative_id = ad.get("creative", {}).get("id", "N/A") if ad.get("creative") else "N/A"
        result += f"  **{ad.get('name', 'Unnamed')}** (ID: {ad['id']})\n"
        result += f"     Status: {ad.get('status', 'N/A')} | Adset: {ad.get('adset_id', 'N/A')} | Creative: {creative_id}\n\n"
    return result


async def list_creatives(
    client: "FacebookAdsClient",
    ad_account_id: str,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if client.is_test_mode:
        return f"Creatives for {ad_account_id}:\n  Test Creative (ID: 987654321)\n"
    data = await client.request(
        "GET", f"{ad_account_id}/adcreatives",
        params={"fields": "id,name,status,object_story_spec,thumbnail_url", "limit": 100},
    )
    creatives = data.get("data", [])
    if not creatives:
        return f"No creatives found for {ad_account_id}"
    result = f"Ad Creatives for {ad_account_id} ({len(creatives)} total):\n\n"
    for c in creatives:
        result += f"  **{c.get('name', 'Unnamed')}** (ID: {c['id']})\n"
        if c.get("status"):
            result += f"     Status: {c['status']}\n"
        result += "\n"
    return result


async def get_creative(client: "FacebookAdsClient", creative_id: str) -> str:
    if not creative_id:
        return "ERROR: creative_id is required"
    if client.is_test_mode:
        return f"Creative {creative_id}:\n  Name: Test Creative\n  Status: ACTIVE\n"
    data = await client.request(
        "GET", creative_id,
        params={"fields": "id,name,status,object_story_spec,call_to_action_type,thumbnail_url,image_hash,video_id"},
    )
    result = f"Creative {creative_id}:\n"
    result += f"  Name: {data.get('name', 'N/A')}\n"
    result += f"  Status: {data.get('status', 'N/A')}\n"
    if data.get("call_to_action_type"):
        result += f"  CTA: {data['call_to_action_type']}\n"
    if data.get("image_hash"):
        result += f"  Image Hash: {data['image_hash']}\n"
    if data.get("video_id"):
        result += f"  Video ID: {data['video_id']}\n"
    return result


async def update_creative(
    client: "FacebookAdsClient",
    creative_id: str,
    name: Optional[str] = None,
) -> str:
    if not creative_id:
        return "ERROR: creative_id is required"
    if not name:
        return "ERROR: name is required (only name can be updated on existing creatives)"
    if client.is_test_mode:
        return f"Creative {creative_id} updated: name -> {name}"
    result = await client.request("POST", creative_id, data={"name": name})
    if result.get("success"):
        return f"Creative {creative_id} updated: name -> {name}"
    return f"Failed to update creative. Response: {result}"


async def delete_creative(client: "FacebookAdsClient", creative_id: str) -> str:
    if not creative_id:
        return "ERROR: creative_id is required"
    if client.is_test_mode:
        return f"Creative {creative_id} deleted successfully."
    result = await client.request("DELETE", creative_id)
    if result.get("success"):
        return f"Creative {creative_id} deleted successfully."
    return f"Failed to delete creative. Response: {result}"


async def preview_creative(
    client: "FacebookAdsClient",
    creative_id: str,
    ad_format: str = "DESKTOP_FEED_STANDARD",
) -> str:
    if not creative_id:
        return "ERROR: creative_id is required"
    try:
        AdFormat(ad_format)
    except ValueError:
        valid = [f.value for f in AdFormat]
        return f"ERROR: Invalid ad_format. Must be one of: {', '.join(valid)}"
    if client.is_test_mode:
        return f"Creative Preview for {creative_id}:\n  Format: {ad_format}\n  Preview URL: https://facebook.com/ads/preview/mock_{creative_id}\n"
    data = await client.request("GET", f"{creative_id}/previews", params={"ad_format": ad_format})
    previews = data.get("data", [])
    if not previews:
        return "No preview available for this creative"
    body = previews[0].get("body", "")
    if body:
        return f"Creative Preview for {creative_id} ({ad_format}):\n{body[:500]}...\n"
    return f"Preview available but no body content. Response: {previews[0]}"


async def upload_video(
    client: "FacebookAdsClient",
    video_url: str,
    ad_account_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    if not video_url:
        return "ERROR: video_url is required"
    account_id = ad_account_id or client.ad_account_id
    if not account_id:
        return "ERROR: ad_account_id is required"
    if client.is_test_mode:
        return f"Video uploaded from URL:\n  Video ID: mock_video_123\n  Account: {account_id}\n  URL: {video_url}\n"
    form_data: Dict[str, Any] = {
        "file_url": video_url,
        "access_token": client.access_token,
    }
    if title:
        form_data["title"] = title
    if description:
        form_data["description"] = description
    logger.info(f"Uploading video from URL to {account_id}/advideos")
    result = await client.request("POST", f"{account_id}/advideos", form_data=form_data)
    video_id = result.get("id")
    if not video_id:
        return f"Failed to upload video. Response: {result}"
    return f"Video uploaded successfully!\n  Video ID: {video_id}\n  Account: {account_id}\n  Use video_id in create_creative with video_data spec.\n"


async def list_videos(
    client: "FacebookAdsClient",
    ad_account_id: str,
) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id is required"
    if client.is_test_mode:
        return f"Videos for {ad_account_id}:\n  Test Video (ID: mock_video_123) — READY\n"
    data = await client.request(
        "GET", f"{ad_account_id}/advideos",
        params={"fields": "id,title,description,length,status,created_time", "limit": 50},
    )
    videos = data.get("data", [])
    if not videos:
        return f"No videos found for {ad_account_id}"
    result = f"Ad Videos for {ad_account_id} ({len(videos)} total):\n\n"
    for v in videos:
        result += f"  **{v.get('title', 'Untitled')}** (ID: {v['id']})\n"
        result += f"     Status: {v.get('status', 'N/A')} | Length: {v.get('length', 'N/A')}s\n"
        if v.get("description"):
            result += f"     Description: {v['description'][:80]}\n"
        result += "\n"
    return result


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
