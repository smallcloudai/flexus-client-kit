from __future__ import annotations
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple

from flexus_client_kit.integrations.facebook.exceptions import FacebookValidationError
from flexus_client_kit.integrations.facebook.models import Insights

logger = logging.getLogger("facebook.utils")


def validate_ad_account_id(ad_account_id: str) -> str:
    if not ad_account_id:
        raise FacebookValidationError("ad_account_id", "is required")
    ad_account_id = str(ad_account_id).strip()
    if not ad_account_id:
        raise FacebookValidationError("ad_account_id", "cannot be empty")
    if not ad_account_id.startswith("act_"):
        return f"act_{ad_account_id}"
    return ad_account_id


def validate_budget(budget: int, min_budget: int = 100, currency: str = "USD") -> int:
    if not isinstance(budget, int):
        try:
            budget = int(budget)
        except (TypeError, ValueError):
            raise FacebookValidationError("budget", "must be an integer (cents)")
    if budget < min_budget:
        raise FacebookValidationError("budget", f"must be at least {format_currency(min_budget, currency)}")
    return budget


def validate_targeting_spec(spec: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        if not spec:
            return False, "Targeting spec cannot be empty"
        if "geo_locations" not in spec:
            return False, "geo_locations is required in targeting"
        geo = spec["geo_locations"]
        if not isinstance(geo, dict):
            return False, "geo_locations must be a dictionary"
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
    return f"{cents / 100:.2f} {currency}"


def format_account_status(status_code: int) -> str:
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


def normalize_insights_data(raw_data: Dict[str, Any]) -> Insights:
    try:
        impressions = int(raw_data.get("impressions", 0))
        clicks = int(raw_data.get("clicks", 0))
        spend = float(raw_data.get("spend", 0.0))
        reach = int(raw_data.get("reach", 0))
        frequency = float(raw_data.get("frequency", 0.0))
        ctr = raw_data.get("ctr")
        if ctr:
            ctr = float(ctr)
        elif impressions > 0:
            ctr = (clicks / impressions) * 100
        else:
            ctr = 0.0
        cpc = raw_data.get("cpc")
        if cpc:
            cpc = float(cpc)
        elif clicks > 0:
            cpc = spend / clicks
        else:
            cpc = 0.0
        cpm = raw_data.get("cpm")
        if cpm:
            cpm = float(cpm)
        elif impressions > 0:
            cpm = (spend / impressions) * 1000
        else:
            cpm = 0.0
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
        return Insights()


def hash_for_audience(value: str, field_type: str) -> str:
    value = value.strip().lower()
    if field_type == "PHONE":
        value = ''.join(c for c in value if c.isdigit())
    elif field_type in ["FN", "LN", "CT", "ST"]:
        value = value.replace(" ", "")
    return hashlib.sha256(value.encode()).hexdigest()
