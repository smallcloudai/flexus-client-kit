"""
Facebook Ads Integration - Shared Utilities

This module provides shared utilities for all Facebook Ads operations:
- Error handling and retry logic
- Rate limiting management
- Data validation and formatting
- Mock data for testing
"""

import asyncio
import hashlib
import logging
import time
from typing import Dict, Any, Optional, List

import httpx

logger = logging.getLogger("fb_utils")

API_BASE = "https://graph.facebook.com"
API_VERSION = "v19.0"


class FacebookAPIError(Exception):
    """Facebook API specific errors"""
    def __init__(self, code: int, message: str, error_type: str = ""):
        self.code = code
        self.message = message
        self.error_type = error_type
        super().__init__(f"Facebook API Error {code}: {message}")


async def handle_fb_api_error(response: httpx.Response) -> str:
    """Parse and format Facebook API errors with user-friendly messages"""
    try:
        error_data = response.json()
        if "error" in error_data:
            err = error_data["error"]
            code = err.get("code", 0)
            message = err.get("message", "Unknown error")
            error_type = err.get("type", "")
            
            if code == 190:
                return "❌ Authentication failed. Please reconnect Facebook in /profile page."
            elif code in [17, 32, 4, 80004]:
                return "⏱️ Rate limit reached. Please try again in a few minutes."
            elif code == 100:
                return f"❌ Invalid parameters: {message}"
            elif code == 2635:
                return "❌ Ad account is disabled. Please check Facebook Business Manager."
            elif code == 1487387:
                return f"❌ Budget too low: {message}"
            elif code == 80004:
                return "❌ Insufficient permissions. Please reconnect Facebook with required permissions."
            else:
                return f"❌ Facebook API Error ({code}): {message}"
    except Exception as e:
        logger.error(f"Error parsing FB API error: {e}", exc_info=e)
        return f"❌ Facebook API Error: {response.text[:200]}"


async def retry_with_backoff(func, max_retries: int = 3, initial_delay: float = 1.0):
    """Retry async function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            if attempt == max_retries - 1:
                raise
            delay = initial_delay * (2 ** attempt)
            logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s due to: {e}")
            await asyncio.sleep(delay)
        except FacebookAPIError as e:
            if e.code in [17, 32, 4, 80004]:
                if attempt == max_retries - 1:
                    raise
                delay = initial_delay * (2 ** attempt) * 2
                logger.warning(f"Rate limit hit, retry {attempt + 1}/{max_retries} after {delay}s")
                await asyncio.sleep(delay)
            else:
                raise


def validate_ad_account_id(ad_account_id: str) -> str:
    """Ensure ad_account_id has act_ prefix"""
    if not ad_account_id:
        raise ValueError("ad_account_id is required")
    ad_account_id = str(ad_account_id).strip()
    if not ad_account_id.startswith("act_"):
        return f"act_{ad_account_id}"
    return ad_account_id


def validate_budget(budget: int, min_budget: int = 100, currency: str = "USD") -> bool:
    """Validate budget is above minimum (in cents)"""
    if not isinstance(budget, int):
        raise ValueError("Budget must be an integer (cents)")
    if budget < min_budget:
        raise ValueError(f"Budget must be at least {format_currency(min_budget, currency)}")
    return True


def validate_targeting_spec(spec: Dict[str, Any]) -> tuple[bool, str]:
    """Validate basic targeting specification structure"""
    try:
        if not spec:
            return False, "Targeting spec cannot be empty"
        
        if "geo_locations" not in spec:
            return False, "geo_locations is required in targeting"
        
        geo = spec["geo_locations"]
        if not geo.get("countries") and not geo.get("regions") and not geo.get("cities"):
            return False, "At least one geo_location (country, region, or city) is required"
        
        if "age_min" in spec:
            age_min = spec["age_min"]
            if not isinstance(age_min, int) or age_min < 13 or age_min > 65:
                return False, "age_min must be between 13 and 65"
        
        if "age_max" in spec:
            age_max = spec["age_max"]
            if not isinstance(age_max, int) or age_max < 13 or age_max > 65:
                return False, "age_max must be between 13 and 65"
        
        if "age_min" in spec and "age_max" in spec:
            if spec["age_min"] > spec["age_max"]:
                return False, "age_min cannot be greater than age_max"
        
        return True, ""
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def format_currency(cents: int, currency: str = "USD") -> str:
    """Format cents to currency string"""
    return f"{cents/100:.2f} {currency}"


def parse_date_preset(preset: str) -> str:
    """Validate and normalize date preset"""
    valid_presets = [
        "today", "yesterday", "last_3d", "last_7d", "last_14d", "last_30d",
        "last_90d", "this_month", "last_month", "this_quarter", "last_quarter",
        "this_year", "last_year", "maximum"
    ]
    if preset not in valid_presets:
        raise ValueError(f"Invalid date preset. Must be one of: {', '.join(valid_presets)}")
    return preset


def normalize_insights_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize insights data from Facebook API to consistent format"""
    try:
        normalized = {
            "impressions": int(raw_data.get("impressions", 0)),
            "clicks": int(raw_data.get("clicks", 0)),
            "spend": float(raw_data.get("spend", 0.0)),
            "reach": int(raw_data.get("reach", 0)),
            "frequency": float(raw_data.get("frequency", 0.0)),
        }
        
        ctr = raw_data.get("ctr")
        if ctr:
            normalized["ctr"] = float(ctr)
        elif normalized["impressions"] > 0:
            normalized["ctr"] = (normalized["clicks"] / normalized["impressions"]) * 100
        else:
            normalized["ctr"] = 0.0
        
        cpc = raw_data.get("cpc")
        if cpc:
            normalized["cpc"] = float(cpc)
        elif normalized["clicks"] > 0:
            normalized["cpc"] = normalized["spend"] / normalized["clicks"]
        else:
            normalized["cpc"] = 0.0
        
        cpm = raw_data.get("cpm")
        if cpm:
            normalized["cpm"] = float(cpm)
        elif normalized["impressions"] > 0:
            normalized["cpm"] = (normalized["spend"] / normalized["impressions"]) * 1000
        else:
            normalized["cpm"] = 0.0
        
        actions = raw_data.get("actions", [])
        normalized["actions"] = {}
        if isinstance(actions, list):
            for action in actions:
                action_type = action.get("action_type", "unknown")
                value = int(action.get("value", 0))
                normalized["actions"][action_type] = value
        
        return normalized
    
    except Exception as e:
        logger.error(f"Error normalizing insights data: {e}", exc_info=e)
        return raw_data


def hash_for_audience(value: str, field_type: str) -> str:
    """
    Hash data for Custom Audiences (PII must be hashed)
    
    Args:
        value: The value to hash (email, phone, etc)
        field_type: Type of field (EMAIL, PHONE, FN, LN, etc)
    
    Returns:
        SHA256 hash of normalized value
    """
    value = value.strip().lower()
    
    if field_type == "EMAIL":
        pass
    elif field_type == "PHONE":
        value = ''.join(c for c in value if c.isdigit())
    elif field_type in ["FN", "LN", "CT", "ST"]:
        value = value.replace(" ", "")
    
    return hashlib.sha256(value.encode()).hexdigest()


class RateLimiter:
    """Simple rate limiter for Facebook API calls"""
    
    def __init__(self, max_calls_per_hour: int = 200):
        self.max_calls = max_calls_per_hour
        self.calls: List[float] = []
        self.lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        async with self.lock:
            now = time.time()
            hour_ago = now - 3600
            
            self.calls = [t for t in self.calls if t > hour_ago]
            
            if len(self.calls) >= self.max_calls:
                oldest_call = min(self.calls)
                wait_time = (oldest_call + 3600) - now
                if wait_time > 0:
                    logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    self.calls = []
            
            self.calls.append(now)
    
    def update_from_headers(self, headers: Dict[str, str]):
        """Update rate limit info from response headers"""
        usage = headers.get("X-Business-Use-Case-Usage") or headers.get("X-App-Usage")
        if usage:
            try:
                import json
                usage_data = json.loads(usage)
                call_count = usage_data.get("call_count", 0)
                total_cputime = usage_data.get("total_cputime", 0)
                total_time = usage_data.get("total_time", 0)
                
                logger.debug(f"FB API usage: calls={call_count}, cpu={total_cputime}, time={total_time}")
                
                if call_count > 75:
                    logger.warning(f"Facebook API usage high: {call_count}% of limit")
            except Exception as e:
                logger.debug(f"Could not parse rate limit headers: {e}")


def generate_mock_campaign() -> Dict[str, Any]:
    """Generate mock campaign data for testing"""
    return {
        "id": "123456789012345",
        "name": "Test Campaign",
        "status": "ACTIVE",
        "objective": "OUTCOME_TRAFFIC",
        "daily_budget": 5000,
        "created_time": "2025-01-01T00:00:00+0000",
        "updated_time": "2025-01-15T12:00:00+0000",
    }


def generate_mock_adset() -> Dict[str, Any]:
    """Generate mock ad set data for testing"""
    return {
        "id": "234567890123456",
        "campaign_id": "123456789012345",
        "name": "Test Ad Set",
        "status": "ACTIVE",
        "optimization_goal": "LINK_CLICKS",
        "billing_event": "IMPRESSIONS",
        "daily_budget": 2000,
        "targeting": {
            "geo_locations": {"countries": ["US"]},
            "age_min": 25,
            "age_max": 45,
        },
    }


def generate_mock_insights() -> Dict[str, Any]:
    """Generate mock insights data for testing"""
    return {
        "impressions": "12345",
        "clicks": "567",
        "spend": "123.45",
        "reach": "10000",
        "frequency": "1.23",
        "ctr": "4.59",
        "cpc": "0.22",
        "cpm": "10.00",
        "actions": [
            {"action_type": "link_click", "value": "567"},
            {"action_type": "post_engagement", "value": "234"},
        ],
        "date_start": "2025-01-01",
        "date_stop": "2025-01-31",
    }


def generate_mock_ad_account() -> Dict[str, Any]:
    """Generate mock ad account data for testing"""
    return {
        "id": "act_123456789",
        "account_id": "123456789",
        "name": "Test Ad Account",
        "currency": "USD",
        "timezone_name": "America/Los_Angeles",
        "account_status": 1,
        "balance": "50000",
        "amount_spent": "123456",
        "spend_cap": "1000000",
    }


