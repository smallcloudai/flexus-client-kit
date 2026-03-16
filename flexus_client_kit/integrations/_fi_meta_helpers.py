from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import httpx
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    from flexus_client_kit import ckit_client, ckit_bot_exec

# ── Exceptions ────────────────────────────────────────────────────────────────

logger = logging.getLogger("meta")


class FacebookError(Exception):
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}\n{self.details}"
        return self.message


class FacebookAPIError(FacebookError):
    CODE_INVALID_PARAMS = 100
    CODE_AUTH_EXPIRED = 190
    CODE_RATE_LIMIT_1 = 4
    CODE_RATE_LIMIT_2 = 17
    CODE_RATE_LIMIT_3 = 32
    CODE_INSUFFICIENT_PERMISSIONS = 80004
    CODE_AD_ACCOUNT_DISABLED = 2635
    CODE_BUDGET_TOO_LOW = 1487387
    RATE_LIMIT_CODES = {CODE_RATE_LIMIT_1, CODE_RATE_LIMIT_2, CODE_RATE_LIMIT_3}

    def __init__(
        self,
        code: int,
        message: str,
        error_type: str = "",
        user_title: Optional[str] = None,
        user_msg: Optional[str] = None,
        fbtrace_id: Optional[str] = None,
    ):
        self.code = code
        self.error_type = error_type
        self.user_title = user_title
        self.user_msg = user_msg
        self.fbtrace_id = fbtrace_id
        details_parts = []
        if user_title:
            details_parts.append(f"**{user_title}**")
        if user_msg:
            details_parts.append(user_msg)
        if not details_parts:
            details_parts.append(message)
        super().__init__(message, "\n".join(details_parts))

    @property
    def is_rate_limit(self) -> bool:
        return self.code in self.RATE_LIMIT_CODES

    @property
    def is_auth_error(self) -> bool:
        return self.code == self.CODE_AUTH_EXPIRED

    def format_for_user(self) -> str:
        if self.code == self.CODE_AUTH_EXPIRED:
            return f"Authentication failed. Please reconnect Facebook.\n{self.details}"
        elif self.is_rate_limit:
            return f"Rate limit reached. Please try again in a few minutes.\n{self.details}"
        elif self.code == self.CODE_INVALID_PARAMS:
            return f"Invalid parameters (code {self.code}):\n{self.details}"
        elif self.code == self.CODE_AD_ACCOUNT_DISABLED:
            return f"Ad account is disabled.\n{self.details}"
        elif self.code == self.CODE_BUDGET_TOO_LOW:
            return f"Budget too low:\n{self.details}"
        elif self.code == self.CODE_INSUFFICIENT_PERMISSIONS:
            return f"Insufficient permissions.\n{self.details}"
        else:
            return f"Facebook API Error ({self.code}):\n{self.details}"


class FacebookAuthError(FacebookError):
    def __init__(self, message: str = "Facebook authentication required"):
        super().__init__(message)


class FacebookValidationError(FacebookError):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validation error for '{field}': {message}")


class FacebookTimeoutError(FacebookError):
    def __init__(self, timeout: float):
        super().__init__(f"Request timed out after {timeout} seconds")


async def parse_api_error(response: httpx.Response) -> FacebookAPIError:
    try:
        error_data = response.json()
        if "error" in error_data:
            err = error_data["error"]
            return FacebookAPIError(
                code=err.get("code", response.status_code),
                message=err.get("message", "Unknown error"),
                error_type=err.get("type", ""),
                user_title=err.get("error_user_title"),
                user_msg=err.get("error_user_msg"),
                fbtrace_id=err.get("fbtrace_id"),
            )
        return FacebookAPIError(code=response.status_code, message=f"HTTP {response.status_code}: {response.text[:500]}")
    except (KeyError, ValueError) as e:
        logger.warning("Error parsing FB API error response", exc_info=e)
        return FacebookAPIError(code=response.status_code, message=f"HTTP {response.status_code}: {response.text[:500]}")


# ── Models ────────────────────────────────────────────────────────────────────

class CustomAudienceSubtype(str, Enum):
    CUSTOM = "CUSTOM"
    WEBSITE = "WEBSITE"
    APP = "APP"
    ENGAGEMENT = "ENGAGEMENT"
    LOOKALIKE = "LOOKALIKE"
    VIDEO = "VIDEO"
    LEAD_GENERATION = "LEAD_GENERATION"
    ON_SITE_LEAD = "ON_SITE_LEAD"


class InsightsBreakdown(str, Enum):
    AGE = "age"
    GENDER = "gender"
    COUNTRY = "country"
    REGION = "region"
    PLACEMENT = "publisher_platform"
    DEVICE = "device_platform"
    IMPRESSION_DEVICE = "impression_device"
    PLATFORM_POSITION = "platform_position"


class InsightsDatePreset(str, Enum):
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7D = "last_7d"
    LAST_14D = "last_14d"
    LAST_28D = "last_28d"
    LAST_30D = "last_30d"
    LAST_90D = "last_90d"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    MAXIMUM = "maximum"


class AdRuleStatus(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    DELETED = "DELETED"
    HAS_ISSUES = "HAS_ISSUES"


class CampaignObjective(str, Enum):
    TRAFFIC = "OUTCOME_TRAFFIC"
    SALES = "OUTCOME_SALES"
    ENGAGEMENT = "OUTCOME_ENGAGEMENT"
    AWARENESS = "OUTCOME_AWARENESS"
    LEADS = "OUTCOME_LEADS"
    APP_PROMOTION = "OUTCOME_APP_PROMOTION"


class CampaignStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"


class AccountStatus(int, Enum):
    ACTIVE = 1
    DISABLED = 2
    UNSETTLED = 3
    PENDING_RISK_REVIEW = 7
    PENDING_SETTLEMENT = 8
    IN_GRACE_PERIOD = 9
    PENDING_CLOSURE = 100
    CLOSED = 101
    TEMPORARILY_UNAVAILABLE = 201


class OptimizationGoal(str, Enum):
    LINK_CLICKS = "LINK_CLICKS"
    LANDING_PAGE_VIEWS = "LANDING_PAGE_VIEWS"
    IMPRESSIONS = "IMPRESSIONS"
    REACH = "REACH"
    CONVERSIONS = "CONVERSIONS"
    VALUE = "VALUE"
    LEAD_GENERATION = "LEAD_GENERATION"
    APP_INSTALLS = "APP_INSTALLS"
    OFFSITE_CONVERSIONS = "OFFSITE_CONVERSIONS"
    POST_ENGAGEMENT = "POST_ENGAGEMENT"
    VIDEO_VIEWS = "VIDEO_VIEWS"
    THRUPLAY = "THRUPLAY"


class BillingEvent(str, Enum):
    IMPRESSIONS = "IMPRESSIONS"
    LINK_CLICKS = "LINK_CLICKS"
    APP_INSTALLS = "APP_INSTALLS"
    THRUPLAY = "THRUPLAY"


class BidStrategy(str, Enum):
    LOWEST_COST_WITHOUT_CAP = "LOWEST_COST_WITHOUT_CAP"
    LOWEST_COST_WITH_BID_CAP = "LOWEST_COST_WITH_BID_CAP"
    COST_CAP = "COST_CAP"


class CallToActionType(str, Enum):
    LEARN_MORE = "LEARN_MORE"
    SHOP_NOW = "SHOP_NOW"
    SIGN_UP = "SIGN_UP"
    BOOK_NOW = "BOOK_NOW"
    DOWNLOAD = "DOWNLOAD"
    GET_OFFER = "GET_OFFER"
    GET_QUOTE = "GET_QUOTE"
    CONTACT_US = "CONTACT_US"
    SUBSCRIBE = "SUBSCRIBE"
    APPLY_NOW = "APPLY_NOW"
    BUY_NOW = "BUY_NOW"
    WATCH_MORE = "WATCH_MORE"


class AdFormat(str, Enum):
    DESKTOP_FEED_STANDARD = "DESKTOP_FEED_STANDARD"
    MOBILE_FEED_STANDARD = "MOBILE_FEED_STANDARD"
    INSTAGRAM_STANDARD = "INSTAGRAM_STANDARD"
    INSTAGRAM_STORY = "INSTAGRAM_STORY"
    MOBILE_BANNER = "MOBILE_BANNER"
    MOBILE_INTERSTITIAL = "MOBILE_INTERSTITIAL"
    MOBILE_NATIVE = "MOBILE_NATIVE"
    RIGHT_COLUMN_STANDARD = "RIGHT_COLUMN_STANDARD"


class GeoLocation(BaseModel):
    countries: List[str] = Field(default_factory=list)
    regions: List[Dict[str, Any]] = Field(default_factory=list)
    cities: List[Dict[str, Any]] = Field(default_factory=list)
    zips: List[Dict[str, Any]] = Field(default_factory=list)
    location_types: List[str] = Field(default_factory=lambda: ["home", "recent"])
    model_config = ConfigDict(extra="allow")


class TargetingSpec(BaseModel):
    geo_locations: GeoLocation
    age_min: int = Field(default=18, ge=13, le=65)
    age_max: int = Field(default=65, ge=13, le=65)
    genders: List[int] = Field(default_factory=list)
    interests: List[Dict[str, Any]] = Field(default_factory=list)
    behaviors: List[Dict[str, Any]] = Field(default_factory=list)
    custom_audiences: List[Dict[str, Any]] = Field(default_factory=list)
    excluded_custom_audiences: List[Dict[str, Any]] = Field(default_factory=list)
    locales: List[int] = Field(default_factory=list)
    publisher_platforms: List[str] = Field(default_factory=list)
    device_platforms: List[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_geo_locations(self) -> "TargetingSpec":
        geo = self.geo_locations
        if not geo.countries and not geo.regions and not geo.cities:
            raise ValueError("At least one geo_location (country, region, or city) is required")
        return self

    @model_validator(mode="after")
    def validate_age_range(self) -> "TargetingSpec":
        if self.age_min > self.age_max:
            raise ValueError("age_min cannot be greater than age_max")
        return self


class ActionBreakdown(BaseModel):
    action_type: str
    value: int

    @field_validator("value", mode="before")
    @classmethod
    def coerce_value(cls, v: Any) -> int:
        return int(v)


class Insights(BaseModel):
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    reach: int = 0
    frequency: float = 0.0
    ctr: float = 0.0
    cpc: float = 0.0
    cpm: float = 0.0
    actions: List[ActionBreakdown] = Field(default_factory=list)
    date_start: Optional[str] = None
    date_stop: Optional[str] = None
    model_config = ConfigDict(extra="allow")

    @field_validator("impressions", "clicks", "reach", mode="before")
    @classmethod
    def coerce_int(cls, v: Any) -> int:
        return int(v) if v else 0

    @field_validator("spend", "frequency", "ctr", "cpc", "cpm", mode="before")
    @classmethod
    def coerce_float(cls, v: Any) -> float:
        return float(v) if v else 0.0


# ── Utils ─────────────────────────────────────────────────────────────────────

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
    except (KeyError, TypeError, ValueError) as e:
        return False, f"Validation error: {str(e)}"


def format_currency(cents: int, currency: str = "USD") -> str:
    return f"{cents / 100:.2f} {currency}"


def format_account_status(status_code: int) -> str:
    status_map = {
        1: "Active", 2: "Disabled", 3: "Unsettled", 7: "Pending Risk Review",
        8: "Pending Settlement", 9: "In Grace Period", 100: "Pending Closure",
        101: "Closed", 201: "Temporarily Unavailable",
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
        ctr = float(ctr) if ctr else ((clicks / impressions) * 100 if impressions > 0 else 0.0)
        cpc = raw_data.get("cpc")
        cpc = float(cpc) if cpc else (spend / clicks if clicks > 0 else 0.0)
        cpm = raw_data.get("cpm")
        cpm = float(cpm) if cpm else ((spend / impressions) * 1000 if impressions > 0 else 0.0)
        actions = []
        for action in raw_data.get("actions", []):
            if isinstance(action, dict):
                actions.append({"action_type": action.get("action_type", "unknown"), "value": int(action.get("value", 0))})
        return Insights(
            impressions=impressions, clicks=clicks, spend=spend, reach=reach,
            frequency=frequency, ctr=ctr, cpc=cpc, cpm=cpm, actions=actions,
            date_start=raw_data.get("date_start"), date_stop=raw_data.get("date_stop"),
        )
    except (KeyError, TypeError, ValueError) as e:
        logger.warning("Error normalizing insights data", exc_info=e)
        return Insights()


def hash_for_audience(value: str, field_type: str) -> str:
    value = value.strip().lower()
    if field_type == "PHONE":
        value = ''.join(c for c in value if c.isdigit())
    elif field_type in ["FN", "LN", "CT", "ST"]:
        value = value.replace(" ", "")
    return hashlib.sha256(value.encode()).hexdigest()


# ── HTTP Client ───────────────────────────────────────────────────────────────

API_BASE = "https://graph.facebook.com"
API_VERSION = "v19.0"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0


class FacebookAdsClient:
    # Handles OAuth token retrieval, HTTP request execution, and retry-with-backoff.
    # All fi_meta_*.py integration classes use this as their sole HTTP layer.
    def __init__(
        self,
        fclient: "ckit_client.FlexusClient",
        rcx: "ckit_bot_exec.RobotContext",
        ad_account_id: str = "",
    ):
        self.fclient = fclient
        self.rcx = rcx
        self._ad_account_id = ""
        if ad_account_id:
            self._ad_account_id = validate_ad_account_id(ad_account_id)
        self._access_token: str = ""
        self._headers: Dict[str, str] = {}

    @property
    def ad_account_id(self) -> str:
        return self._ad_account_id

    @ad_account_id.setter
    def ad_account_id(self, value: str) -> None:
        self._ad_account_id = validate_ad_account_id(value) if value else ""

    @property
    def is_test_mode(self) -> bool:
        return self.rcx.running_test_scenario

    @property
    def access_token(self) -> str:
        return self._access_token

    async def ensure_auth(self) -> Optional[str]:
        try:
            if self.is_test_mode:
                return None
            if not self._access_token:
                self._access_token = await self._fetch_token()
            self._headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            }
            return None
        except (AttributeError, KeyError, ValueError) as e:
            logger.info("Failed to get Facebook token", exc_info=e)
            return await self._prompt_oauth_connection()

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> Dict[str, Any]:
        auth_error = await self.ensure_auth()
        if auth_error:
            raise FacebookAuthError(auth_error)
        url = f"{API_BASE}/{API_VERSION}/{endpoint}"

        async def _make() -> Dict[str, Any]:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url, params=params, headers=self._headers, timeout=timeout)
                elif method == "POST":
                    if form_data:
                        response = await client.post(url, data=form_data, timeout=timeout)
                    else:
                        response = await client.post(url, json=data, headers=self._headers, timeout=timeout)
                elif method == "DELETE":
                    response = await client.delete(url, json=data, headers=self._headers, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                return response.json()

        return await self._retry_with_backoff(_make)

    async def _retry_with_backoff(self, func, max_retries: int = MAX_RETRIES, initial_delay: float = INITIAL_RETRY_DELAY) -> Dict[str, Any]:
        last_exception = None
        for attempt in range(max_retries):
            try:
                return await func()
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                last_exception = e
                if attempt == max_retries - 1:
                    raise FacebookTimeoutError(DEFAULT_TIMEOUT)
                delay = initial_delay * (2 ** attempt)
                logger.warning("Retry %s/%s after %.1fs due to: %s", attempt + 1, max_retries, delay, e)
                await asyncio.sleep(delay)
            except FacebookAPIError as e:
                if e.is_rate_limit:
                    last_exception = e
                    if attempt == max_retries - 1:
                        raise
                    delay = initial_delay * (2 ** attempt) * 2
                    logger.warning("Rate limit hit, retry %s/%s after %.1fs", attempt + 1, max_retries, delay)
                    await asyncio.sleep(delay)
                else:
                    raise
        if last_exception:
            raise last_exception
        raise FacebookAPIError(500, "Unexpected retry loop exit")

    async def _fetch_token(self) -> str:
        facebook_auth = self.rcx.external_auth.get("facebook") or {}
        token_obj = facebook_auth.get("token") or {}
        access_token = token_obj.get("access_token", "")
        if not access_token:
            raise ValueError("No Facebook OAuth connection found")
        logger.info("Facebook token retrieved for %s", self.rcx.persona.owner_fuser_id)
        return access_token

    async def _prompt_oauth_connection(self) -> str:
        from flexus_client_kit import ckit_client
        http = await self.fclient.use_http()
        async with http as h:
            result = await h.execute(
                ckit_client.gql.gql("""
                    query GetFacebookToken($fuser_id: String!, $ws_id: String!, $provider: String!, $scopes: [String!]!) {
                        external_auth_token(fuser_id: $fuser_id ws_id: $ws_id provider: $provider scopes: $scopes)
                    }
                """),
                variable_values={
                    "fuser_id": self.rcx.persona.owner_fuser_id,
                    "ws_id": self.rcx.persona.ws_id,
                    "provider": "facebook",
                    "scopes": ["ads_management", "ads_read", "business_management", "pages_manage_ads"],
                },
            ),
        auth_url = result.get("external_auth_token", "")
        return f"Facebook authorization required.\n\nClick this link to connect:\n{auth_url}\n\nAfter authorizing, return here and try again."
