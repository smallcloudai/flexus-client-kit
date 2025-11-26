"""
Facebook Creative & Ads Management

WHAT: Operations for creating ad creatives and ads.
WHY: Creatives contain the actual ad content (images, text, links).

OPERATIONS:
- upload_image: Upload image and get hash for creative
- create_creative: Create ad creative with image, text, link
- create_ad: Create ad linking ad set to creative
- preview_ad: Generate ad preview for review

EXCEPTION HANDLING:
- handle() catches all exceptions and formats responses
- Operation functions only catch ValueError for validation errors
- FacebookAPIError and unexpected exceptions bubble up to handle()
"""

import logging
from typing import Dict, Any
from pathlib import Path

import httpx

from flexus_simple_bots.admonster.integrations import fb_utils

logger = logging.getLogger("fb_creative")


async def handle(integration, toolcall, model_produced_args: Dict[str, Any]) -> str:
    """
    Router for creative/ad operations. Catches all exceptions.
    
    FacebookAPIError → logger.info (expected external API error)
    Exception → logger.warning with stack trace (unexpected)
    """
    try:
        auth_error = await integration.ensure_headers()
        if auth_error:
            return auth_error
        
        op = model_produced_args.get("op", "")
        args = model_produced_args.get("args", {})
        
        for key in ["ad_account_id", "adset_id", "creative_id"]:
            if key in model_produced_args and key not in args:
                args[key] = model_produced_args[key]
        
        if op == "upload_image":
            return await upload_image(integration, args)
        elif op == "create_creative":
            return await create_creative(integration, args)
        elif op == "create_ad":
            return await create_ad(integration, args)
        elif op == "preview_ad":
            return await preview_ad(integration, args)
        else:
            return f"Unknown creative/ad operation: {op}\n\nAvailable operations:\n- upload_image\n- create_creative\n- create_ad\n- preview_ad"
    
    except fb_utils.FacebookAPIError as e:
        logger.info(f"Facebook API error in creative: {e}")
        return f"❌ Facebook API Error: {e.message}"
    except Exception as e:
        logger.warning(f"Creative/ad error: {e}", exc_info=e)
        return f"ERROR: {str(e)}"


async def upload_image(integration, args: Dict[str, Any]) -> str:
    """Upload an image for use in ad creatives."""
    ad_account_id = args.get("ad_account_id", integration.ad_account_id)
    image_path = args.get("image_path", "")
    image_url = args.get("image_url", "")
    
    if not image_path and not image_url:
        return "ERROR: Either image_path or image_url is required"
    
    try:
        ad_account_id = fb_utils.validate_ad_account_id(ad_account_id)
    except ValueError as e:
        return f"ERROR: {str(e)}"
    
    if integration.is_fake:
        return f"""✅ Image uploaded successfully!

Image Hash: abc123def456
Ad Account: {ad_account_id}

You can now use this image hash in create_creative()
"""
    
    url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{ad_account_id}/adimages"
    
    if image_url:
        form_data = {
            "url": image_url,
            "access_token": integration.access_token,
        }
        
        logger.info(f"Uploading image from URL to {url}")
        
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=form_data, timeout=60.0)
                if response.status_code != 200:
                    logger.info(f"FB API error: status={response.status_code}, body={response.text}")
                    error_msg = await fb_utils.handle_fb_api_error(response)
                    raise fb_utils.FacebookAPIError(response.status_code, error_msg)
                return response.json()
    
    elif image_path:
        image_file = Path(image_path)
        if not image_file.exists():
            return f"ERROR: Image file not found: {image_path}"
        
        with open(image_file, 'rb') as f:
            image_bytes = f.read()
        
        files = {"filename": (image_file.name, image_bytes, "image/jpeg")}
        form_data = {"access_token": integration.access_token}
        
        logger.info(f"Uploading image file to {url}")
        
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=form_data, files=files, timeout=60.0)
                if response.status_code != 200:
                    logger.info(f"FB API error: status={response.status_code}, body={response.text}")
                    error_msg = await fb_utils.handle_fb_api_error(response)
                    raise fb_utils.FacebookAPIError(response.status_code, error_msg)
                return response.json()
    
    result = await fb_utils.retry_with_backoff(make_request)
    
    images = result.get("images", {})
    if images:
        image_hash = list(images.values())[0].get("hash", "unknown")
        return f"""✅ Image uploaded successfully!

Image Hash: {image_hash}
Ad Account: {ad_account_id}

Use this hash in create_creative():
  facebook(op="create_creative", args={{
    "image_hash": "{image_hash}",
    ...
  }})
"""
    else:
        return f"❌ Failed to upload image. Response: {result}"


async def create_creative(integration, args: Dict[str, Any]) -> str:
    """Create an ad creative."""
    ad_account_id = args.get("ad_account_id", integration.ad_account_id)
    name = args.get("name", "")
    page_id = args.get("page_id", "")
    image_hash = args.get("image_hash", "")
    link = args.get("link", "")
    message = args.get("message", "")
    call_to_action_type = args.get("call_to_action_type", "LEARN_MORE")
    
    if not name:
        return "ERROR: name is required"
    if not page_id:
        return "ERROR: page_id is required"
    if not image_hash:
        return "ERROR: image_hash is required (use upload_image first)"
    if not link:
        return "ERROR: link is required"
    
    try:
        ad_account_id = fb_utils.validate_ad_account_id(ad_account_id)
    except ValueError as e:
        return f"ERROR: {str(e)}"
    
    if integration.is_fake:
        return f"""✅ Creative created successfully!

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
    
    url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{ad_account_id}/adcreatives"
    
    data = {
        "name": name,
        "object_story_spec": {
            "page_id": page_id,
            "link_data": {
                "image_hash": image_hash,
                "link": link,
                "call_to_action": {"type": call_to_action_type}
            }
        }
    }
    if message:
        data["object_story_spec"]["link_data"]["message"] = message
    
    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=integration.headers, timeout=30.0)
            if response.status_code != 200:
                error_msg = await fb_utils.handle_fb_api_error(response)
                raise fb_utils.FacebookAPIError(response.status_code, error_msg)
            return response.json()
    
    result = await fb_utils.retry_with_backoff(make_request)
    
    creative_id = result.get("id")
    if not creative_id:
        return f"❌ Failed to create creative. Response: {result}"
    
    return f"""✅ Creative created successfully!

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


async def create_ad(integration, args: Dict[str, Any]) -> str:
    """Create an ad from a creative."""
    ad_account_id = args.get("ad_account_id", integration.ad_account_id)
    adset_id = args.get("adset_id", "")
    creative_id = args.get("creative_id", "")
    name = args.get("name", "")
    status = args.get("status", "PAUSED")
    
    if not adset_id:
        return "ERROR: adset_id is required"
    if not creative_id:
        return "ERROR: creative_id is required"
    if not name:
        return "ERROR: name is required"
    if status not in ["ACTIVE", "PAUSED"]:
        return "ERROR: status must be 'ACTIVE' or 'PAUSED'"
    
    try:
        ad_account_id = fb_utils.validate_ad_account_id(ad_account_id)
    except ValueError as e:
        return f"ERROR: {str(e)}"
    
    if integration.is_fake:
        return f"""✅ Ad created successfully!

Ad ID: 111222333444555
Name: {name}
Ad Set ID: {adset_id}
Creative ID: {creative_id}
Status: {status}

{("⚠️ Ad is paused. Activate it when ready to start delivery." if status == "PAUSED" else "✅ Ad is active and will start delivery.")}

Preview your ad:
  facebook(op="preview_ad", args={{"ad_id": "111222333444555"}})
"""
    
    url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{ad_account_id}/ads"
    
    data = {
        "name": name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": status
    }
    
    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=integration.headers, timeout=30.0)
            if response.status_code != 200:
                error_msg = await fb_utils.handle_fb_api_error(response)
                raise fb_utils.FacebookAPIError(response.status_code, error_msg)
            return response.json()
    
    result = await fb_utils.retry_with_backoff(make_request)
    
    ad_id = result.get("id")
    if not ad_id:
        return f"❌ Failed to create ad. Response: {result}"
    
    output = f"""✅ Ad created successfully!

Ad ID: {ad_id}
Name: {name}
Ad Set ID: {adset_id}
Creative ID: {creative_id}
Status: {status}
"""
    
    if status == "PAUSED":
        output += "\n⚠️ Ad is paused. Activate it when ready to start delivery."
    else:
        output += "\n✅ Ad is active and will start delivery."
    
    output += f"""

Preview your ad:
  facebook(op="preview_ad", args={{"ad_id": "{ad_id}"}})
"""
    
    return output


async def preview_ad(integration, args: Dict[str, Any]) -> str:
    """Generate preview URL/HTML for an ad."""
    ad_id = args.get("ad_id", "")
    ad_format = args.get("ad_format", "DESKTOP_FEED_STANDARD")
    
    if not ad_id:
        return "ERROR: ad_id is required"
    
    valid_formats = [
        "DESKTOP_FEED_STANDARD",
        "MOBILE_FEED_STANDARD",
        "INSTAGRAM_STANDARD",
        "INSTAGRAM_STORY",
        "MOBILE_BANNER",
        "MOBILE_INTERSTITIAL",
        "MOBILE_NATIVE",
        "RIGHT_COLUMN_STANDARD",
    ]
    
    if ad_format not in valid_formats:
        return f"ERROR: Invalid ad_format. Must be one of: {', '.join(valid_formats)}"
    
    if integration.is_fake:
        return f"""Ad Preview for {ad_id}:

Format: {ad_format}
Preview URL: https://facebook.com/ads/preview/mock_{ad_id}

Note: This is a mock preview. In production, Facebook will provide actual preview HTML/URL.
"""
    
    url = f"{fb_utils.API_BASE}/{fb_utils.API_VERSION}/{ad_id}/previews"
    params = {"ad_format": ad_format}
    
    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=integration.headers, timeout=30.0)
            if response.status_code != 200:
                error_msg = await fb_utils.handle_fb_api_error(response)
                raise fb_utils.FacebookAPIError(response.status_code, error_msg)
            return response.json()
    
    result = await fb_utils.retry_with_backoff(make_request)
    
    data = result.get("data", [])
    if not data:
        return "No preview available for this ad"
    
    preview = data[0]
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
