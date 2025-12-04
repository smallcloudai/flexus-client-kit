from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
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
class AdAccount(BaseModel):
    id: str
    account_id: Optional[str] = None
    name: str
    currency: str = "USD"
    timezone_name: str = "America/Los_Angeles"
    account_status: AccountStatus = AccountStatus.ACTIVE
    balance: int = 0
    amount_spent: int = 0
    spend_cap: int = 0
    min_daily_budget: Optional[int] = None
    business: Optional[Dict[str, Any]] = None
    created_time: Optional[datetime] = None
    model_config = ConfigDict(extra="allow")
    @property
    def is_active(self) -> bool:
        return self.account_status == AccountStatus.ACTIVE
    @property
    def remaining_budget(self) -> int:
        if self.spend_cap <= 0:
            return 0
        return max(0, self.spend_cap - self.amount_spent)
class Campaign(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=400)
    objective: CampaignObjective
    status: CampaignStatus = CampaignStatus.PAUSED
    daily_budget: Optional[int] = Field(None, ge=100)
    lifetime_budget: Optional[int] = Field(None, ge=100)
    special_ad_categories: List[str] = Field(default_factory=list)
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    model_config = ConfigDict(extra="allow")
    @field_validator("daily_budget", "lifetime_budget", mode="before")
    @classmethod
    def coerce_budget(cls, v):
        if v is None:
            return None
        return int(v)
class AdSet(BaseModel):
    id: Optional[str] = None
    campaign_id: str
    name: str = Field(..., min_length=1, max_length=400)
    status: CampaignStatus = CampaignStatus.PAUSED
    optimization_goal: OptimizationGoal = OptimizationGoal.LINK_CLICKS
    billing_event: BillingEvent = BillingEvent.IMPRESSIONS
    bid_strategy: BidStrategy = BidStrategy.LOWEST_COST_WITHOUT_CAP
    bid_amount: Optional[int] = None
    daily_budget: Optional[int] = Field(None, ge=100)
    lifetime_budget: Optional[int] = Field(None, ge=100)
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
        if not self.image_hash and not self.image_url:
            raise ValueError("Either image_hash or image_url is required")
        return self
class Ad(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=400)
    adset_id: str
    creative_id: str
    status: CampaignStatus = CampaignStatus.PAUSED
    model_config = ConfigDict(extra="allow")
class ActionBreakdown(BaseModel):
    action_type: str
    value: int
    @field_validator("value", mode="before")
    @classmethod
    def coerce_value(cls, v):
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
    def coerce_int(cls, v):
        return int(v) if v else 0
    @field_validator("spend", "frequency", "ctr", "cpc", "cpm", mode="before")
    @classmethod
    def coerce_float(cls, v):
        return float(v) if v else 0.0
