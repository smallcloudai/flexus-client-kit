"""
Facebook Ads API - Utility Functions

Common utilities for validation, formatting, and data processing.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import FacebookValidationError
from .models import DatePreset, Insights, TargetingSpec

logger = logging.getLogger("facebook.utils")


# =============================================================================
# Validation Functions
# =============================================================================

def validate_ad_account_id(ad_account_id: str) -> str:
    """
    Validate and normalize ad account ID to act_ format.

    Args:
        ad_account_id: Account ID with or without act_ prefix

    Returns:
        Normalized ID with act_ prefix

    Raises:
        FacebookValidationError: If ad_account_id is empty or invalid
    """
    if not ad_account_id:
        raise FacebookValidationError("ad_account_id", "is required")

    ad_account_id = str(ad_account_id).strip()

    if not ad_account_id:
        raise FacebookValidationError("ad_account_id", "cannot be empty")

    if not ad_account_id.startswith("act_"):
        return f"act_{ad_account_id}"

    return ad_account_id


def validate_budget(budget: int, min_budget: int = 100, currency: str = "USD") -> int:
    """
    Validate budget meets Facebook minimum requirements.

    Args:
        budget: Budget in cents
        min_budget: Minimum allowed (default 100 = $1.00)
        currency: Currency code for error message

    Returns:
        Validated budget value

    Raises:
        FacebookValidationError: If budget invalid or too low
    """
    if not isinstance(budget, int):
        try:
            budget = int(budget)
        except (TypeError, ValueError):
            raise FacebookValidationError("budget", "must be an integer (cents)")

    if budget < min_budget:
        raise FacebookValidationError(
            "budget",
            f"must be at least {format_currency(min_budget, currency)}"
        )

    return budget


def validate_targeting_spec(spec: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate basic targeting specification structure.

    Checks required fields and value ranges before sending to Facebook.
    Facebook does additional validation on their end.

    Args:
        spec: Targeting specification dict

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not spec:
            return False, "Targeting spec cannot be empty"

        # geo_locations is required by Facebook
        if "geo_locations" not in spec:
            return False, "geo_locations is required in targeting"

        geo = spec["geo_locations"]
        if not isinstance(geo, dict):
            return False, "geo_locations must be a dictionary"

        if not geo.get("countries") and not geo.get("regions") and not geo.get("cities"):
            return False, "At least one geo_location (country, region, or city) is required"

        # Facebook age limits: 13-65
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


def validate_date_preset(preset: str) -> DatePreset:
    """
    Validate Facebook Insights date preset.

    Args:
        preset: Date preset string

    Returns:
        Validated DatePreset enum

    Raises:
        FacebookValidationError: If preset not recognized
    """
    try:
        return DatePreset(preset)
    except ValueError:
        valid_presets = [p.value for p in DatePreset]
        raise FacebookValidationError(
            "date_preset",
            f"Invalid preset. Must be one of: {', '.join(valid_presets)}"
        )


# =============================================================================
# Formatting Functions
# =============================================================================

def format_currency(cents: int, currency: str = "USD") -> str:
    """
    Format cents to readable currency string.

    Args:
        cents: Amount in cents (5000 = $50.00)
        currency: Currency code (USD, EUR, etc.)

    Returns:
        Formatted string like "50.00 USD"
    """
    return f"{cents / 100:.2f} {currency}"


def format_account_status(status_code: int) -> str:
    """
    Convert account status code to human-readable string.

    Args:
        status_code: Facebook account status code

    Returns:
        Human-readable status string
    """
    status_map = {
        1: "Active",
        2: "Disabled",
        3: "Unsettled",
        7: "Pending Risk Review",
        8: "Pending Settlement",
        9: "In Grace Period",
        100: "Pending Closure",
        101: "Closed",
        201: "Temporarily Unavailable",
    }
    return status_map.get(status_code, f"Unknown ({status_code})")


def format_number(value: int) -> str:
    """Format number with thousands separators."""
    return f"{value:,}"


# =============================================================================
# Data Processing
# =============================================================================

def normalize_insights_data(raw_data: Dict[str, Any]) -> Insights:
    """
    Normalize raw insights data from Facebook API.

    Converts string numbers to proper types, calculates derived metrics
    (CTR, CPC, CPM) if not provided by Facebook.

    Args:
        raw_data: Raw insights response from Facebook

    Returns:
        Normalized Insights model
    """
    try:
        impressions = int(raw_data.get("impressions", 0))
        clicks = int(raw_data.get("clicks", 0))
        spend = float(raw_data.get("spend", 0.0))
        reach = int(raw_data.get("reach", 0))
        frequency = float(raw_data.get("frequency", 0.0))

        # CTR (Click-Through Rate) = clicks / impressions * 100
        ctr = raw_data.get("ctr")
        if ctr:
            ctr = float(ctr)
        elif impressions > 0:
            ctr = (clicks / impressions) * 100
        else:
            ctr = 0.0

        # CPC (Cost Per Click) = spend / clicks
        cpc = raw_data.get("cpc")
        if cpc:
            cpc = float(cpc)
        elif clicks > 0:
            cpc = spend / clicks
        else:
            cpc = 0.0

        # CPM (Cost Per Mille) = spend / impressions * 1000
        cpm = raw_data.get("cpm")
        if cpm:
            cpm = float(cpm)
        elif impressions > 0:
            cpm = (spend / impressions) * 1000
        else:
            cpm = 0.0

        # Actions breakdown
        actions = []
        raw_actions = raw_data.get("actions", [])
        if isinstance(raw_actions, list):
            for action in raw_actions:
                actions.append({
                    "action_type": action.get("action_type", "unknown"),
                    "value": int(action.get("value", 0)),
                })

        return Insights(
            impressions=impressions,
            clicks=clicks,
            spend=spend,
            reach=reach,
            frequency=frequency,
            ctr=ctr,
            cpc=cpc,
            cpm=cpm,
            actions=actions,
            date_start=raw_data.get("date_start"),
            date_stop=raw_data.get("date_stop"),
        )

    except Exception as e:
        logger.warning(f"Error normalizing insights data: {e}", exc_info=e)
        # Return empty insights on error
        return Insights()


def hash_for_audience(value: str, field_type: str) -> str:
    """
    Hash PII data for Custom Audiences.

    Facebook requires SHA256 hashing of personal data (email, phone, etc.)
    when uploading to Custom Audiences.

    Args:
        value: Raw value to hash (email, phone, name)
        field_type: Type of field (EMAIL, PHONE, FN, LN, CT, ST)

    Returns:
        SHA256 hex digest of normalized value
    """
    value = value.strip().lower()

    # Normalize based on field type
    if field_type == "EMAIL":
        pass  # Email just needs lowercase
    elif field_type == "PHONE":
        value = ''.join(c for c in value if c.isdigit())  # Keep only digits
    elif field_type in ["FN", "LN", "CT", "ST"]:
        value = value.replace(" ", "")  # Remove spaces

    return hashlib.sha256(value.encode()).hexdigest()


def extract_id_from_response(response: Dict[str, Any]) -> Optional[str]:
    """Extract ID from Facebook API create response."""
    if "id" in response:
        return response["id"]
    return None


def build_fields_param(fields: List[str]) -> str:
    """Build comma-separated fields parameter for API request."""
    return ",".join(fields)


# =============================================================================
# Response Formatting for Model
# =============================================================================

def format_campaign_list(campaigns: List[Dict[str, Any]]) -> str:
    """Format list of campaigns for model response."""
    if not campaigns:
        return "No campaigns found."

    lines = [f"Found {len(campaigns)} campaign{'s' if len(campaigns) != 1 else ''}:"]
    for c in campaigns:
        lines.append(f"  {c.get('name', 'Unnamed')} (ID: {c['id']}) - {c.get('status', 'UNKNOWN')}")

    return "\n".join(lines)


def format_error_response(error: str) -> str:
    """Format error message for model response."""
    return f"ERROR: {error}"


def format_success_response(message: str) -> str:
    """Format success message for model response."""
    return f"SUCCESS: {message}"
