"""
Facebook Ads API - Pydantic Models

Defines type-safe models for all Facebook Ads entities with validation.
All budget values are in cents (5000 = $50.00).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# =============================================================================
# Enums
# =============================================================================

class CampaignObjective(str, Enum):
    """Facebook campaign objectives (ODAX format)."""
    TRAFFIC = "OUTCOME_TRAFFIC"
    SALES = "OUTCOME_SALES"
    ENGAGEMENT = "OUTCOME_ENGAGEMENT"
    AWARENESS = "OUTCOME_AWARENESS"
    LEADS = "OUTCOME_LEADS"
    APP_PROMOTION = "OUTCOME_APP_PROMOTION"


class CampaignStatus(str, Enum):
    """Campaign/AdSet/Ad status values."""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"


class AccountStatus(int, Enum):
    """Facebook Ad Account status codes."""
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
    """Ad Set optimization goals."""
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
    """Ad Set billing events."""
    IMPRESSIONS = "IMPRESSIONS"
    LINK_CLICKS = "LINK_CLICKS"
    APP_INSTALLS = "APP_INSTALLS"
    THRUPLAY = "THRUPLAY"


class BidStrategy(str, Enum):
    """Ad Set bid strategies."""
    LOWEST_COST_WITHOUT_CAP = "LOWEST_COST_WITHOUT_CAP"
    LOWEST_COST_WITH_BID_CAP = "LOWEST_COST_WITH_BID_CAP"
    COST_CAP = "COST_CAP"


class CallToActionType(str, Enum):
    """Creative call-to-action button types."""
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
    """Ad preview formats."""
    DESKTOP_FEED_STANDARD = "DESKTOP_FEED_STANDARD"
    MOBILE_FEED_STANDARD = "MOBILE_FEED_STANDARD"
    INSTAGRAM_STANDARD = "INSTAGRAM_STANDARD"
    INSTAGRAM_STORY = "INSTAGRAM_STORY"
    MOBILE_BANNER = "MOBILE_BANNER"
    MOBILE_INTERSTITIAL = "MOBILE_INTERSTITIAL"
    MOBILE_NATIVE = "MOBILE_NATIVE"
    RIGHT_COLUMN_STANDARD = "RIGHT_COLUMN_STANDARD"


class DatePreset(str, Enum):
    """Facebook Insights date presets."""
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_3D = "last_3d"
    LAST_7D = "last_7d"
    LAST_14D = "last_14d"
    LAST_30D = "last_30d"
    LAST_90D = "last_90d"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_QUARTER = "this_quarter"
    LAST_QUARTER = "last_quarter"
    THIS_YEAR = "this_year"
    LAST_YEAR = "last_year"
    MAXIMUM = "maximum"


# =============================================================================
# Targeting Models
# =============================================================================

class GeoLocation(BaseModel):
    """Geographic targeting specification."""
    countries: List[str] = Field(default_factory=list)
    regions: List[Dict[str, Any]] = Field(default_factory=list)
    cities: List[Dict[str, Any]] = Field(default_factory=list)
    zips: List[Dict[str, Any]] = Field(default_factory=list)
    location_types: List[str] = Field(default_factory=lambda: ["home", "recent"])

    model_config = ConfigDict(extra="allow")


class TargetingSpec(BaseModel):
    """
    Facebook targeting specification.

    At minimum requires geo_locations with at least one country, region, or city.
    """
    geo_locations: GeoLocation
    age_min: int = Field(default=18, ge=13, le=65)
    age_max: int = Field(default=65, ge=13, le=65)
    genders: List[int] = Field(default_factory=list)  # 1=male, 2=female
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
        """Ensure at least one geographic location is specified."""
        geo = self.geo_locations
        if not geo.countries and not geo.regions and not geo.cities:
            raise ValueError("At least one geo_location (country, region, or city) is required")
        return self

    @model_validator(mode="after")
    def validate_age_range(self) -> "TargetingSpec":
        """Ensure age_min <= age_max."""
        if self.age_min > self.age_max:
            raise ValueError("age_min cannot be greater than age_max")
        return self


# =============================================================================
# Core Entity Models
# =============================================================================

class AdAccount(BaseModel):
    """Facebook Ad Account."""
    id: str
    account_id: Optional[str] = None
    name: str
    currency: str = "USD"
    timezone_name: str = "America/Los_Angeles"
    account_status: AccountStatus = AccountStatus.ACTIVE
    balance: int = 0  # cents
    amount_spent: int = 0  # cents
    spend_cap: int = 0  # cents
    min_daily_budget: Optional[int] = None  # cents
    business: Optional[Dict[str, Any]] = None
    created_time: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")

    @property
    def is_active(self) -> bool:
        return self.account_status == AccountStatus.ACTIVE

    @property
    def remaining_budget(self) -> int:
        """Remaining budget under spend cap (cents)."""
        if self.spend_cap <= 0:
            return 0
        return max(0, self.spend_cap - self.amount_spent)


class Campaign(BaseModel):
    """
    Facebook advertising campaign.

    Campaigns are the top-level container for ad sets and ads.
    """
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=400)
    objective: CampaignObjective
    status: CampaignStatus = CampaignStatus.PAUSED
    daily_budget: Optional[int] = Field(None, ge=100)  # cents, min $1
    lifetime_budget: Optional[int] = Field(None, ge=100)  # cents
    special_ad_categories: List[str] = Field(default_factory=list)
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")

    @field_validator("daily_budget", "lifetime_budget", mode="before")
    @classmethod
    def coerce_budget(cls, v):
        """Convert string/float budgets to int."""
        if v is None:
            return None
        return int(v)


class AdSet(BaseModel):
    """
    Facebook Ad Set.

    Ad sets contain targeting, budget allocation, and optimization settings.
    """
    id: Optional[str] = None
    campaign_id: str
    name: str = Field(..., min_length=1, max_length=400)
    status: CampaignStatus = CampaignStatus.PAUSED
    optimization_goal: OptimizationGoal = OptimizationGoal.LINK_CLICKS
    billing_event: BillingEvent = BillingEvent.IMPRESSIONS
    bid_strategy: BidStrategy = BidStrategy.LOWEST_COST_WITHOUT_CAP
    bid_amount: Optional[int] = None  # cents
    daily_budget: Optional[int] = Field(None, ge=100)  # cents
    lifetime_budget: Optional[int] = Field(None, ge=100)  # cents
    targeting: TargetingSpec
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    promoted_object: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(extra="allow")

    @field_validator("daily_budget", "lifetime_budget", "bid_amount", mode="before")
    @classmethod
    def coerce_budget(cls, v):
        if v is None:
            return None
        return int(v)


class Creative(BaseModel):
    """
    Facebook Ad Creative.

    Contains the actual ad content (image, text, link).
    """
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=400)
    page_id: str
    image_hash: Optional[str] = None
    image_url: Optional[str] = None
    link: str
    message: Optional[str] = None
    headline: Optional[str] = None
    description: Optional[str] = None
    call_to_action_type: CallToActionType = CallToActionType.LEARN_MORE

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_image(self) -> "Creative":
        """Ensure either image_hash or image_url is provided."""
        if not self.image_hash and not self.image_url:
            raise ValueError("Either image_hash or image_url is required")
        return self


class Ad(BaseModel):
    """
    Facebook Ad.

    Links an ad set to a creative.
    """
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=400)
    adset_id: str
    creative_id: str
    status: CampaignStatus = CampaignStatus.PAUSED

    model_config = ConfigDict(extra="allow")


# =============================================================================
# Insights & Analytics Models
# =============================================================================

class ActionBreakdown(BaseModel):
    """Single action from insights breakdown."""
    action_type: str
    value: int

    @field_validator("value", mode="before")
    @classmethod
    def coerce_value(cls, v):
        return int(v)


class Insights(BaseModel):
    """
    Campaign/AdSet/Ad performance metrics.

    All monetary values are in the account's currency.
    """
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    reach: int = 0
    frequency: float = 0.0
    ctr: float = 0.0  # Click-through rate (%)
    cpc: float = 0.0  # Cost per click
    cpm: float = 0.0  # Cost per mille (1000 impressions)
    actions: List[ActionBreakdown] = Field(default_factory=list)
    date_start: Optional[str] = None
    date_stop: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    @field_validator("impressions", "clicks", "reach", mode="before")
    @classmethod
    def coerce_int(cls, v):
        return int(v) if v else 0

    @field_validator("spend", "frequency", "ctr", "cpc", "cpm", mode="before")
    @classmethod
    def coerce_float(cls, v):
        return float(v) if v else 0.0


# =============================================================================
# API Response Models
# =============================================================================

class PagingCursor(BaseModel):
    """Facebook API pagination cursors."""
    before: Optional[str] = None
    after: Optional[str] = None


class Paging(BaseModel):
    """Facebook API pagination info."""
    cursors: Optional[PagingCursor] = None
    next: Optional[str] = None
    previous: Optional[str] = None


class FacebookResponse(BaseModel):
    """Generic Facebook API response wrapper."""
    data: List[Dict[str, Any]] = Field(default_factory=list)
    paging: Optional[Paging] = None
    success: Optional[bool] = None
    id: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class ImageUploadResult(BaseModel):
    """Result of image upload operation."""
    hash: str
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class AdPreview(BaseModel):
    """Ad preview result."""
    body: str
    format: AdFormat
