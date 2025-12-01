"""
Facebook Ads Mock Data Generators

Provides mock data for testing without hitting the actual Facebook API.
"""

from __future__ import annotations

import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models import (
    Campaign,
    CampaignObjective,
    CampaignStatus,
    AdSet,
    Ad,
    Creative,
    AdAccount,
    AccountStatus,
    Insights,
    TargetingSpec,
    GeoLocation,
    OptimizationGoal,
    BillingEvent,
    CallToActionType,
)


def _random_id(prefix: str = "") -> str:
    """Generate a random ID."""
    digits = ''.join(random.choices(string.digits, k=15))
    return f"{prefix}{digits}" if prefix else digits


def generate_mock_campaign(
    id: Optional[str] = None,
    name: str = "Test Campaign",
    objective: CampaignObjective = CampaignObjective.TRAFFIC,
    status: CampaignStatus = CampaignStatus.ACTIVE,
    daily_budget: int = 5000,
) -> Campaign:
    """
    Generate a mock Campaign for testing.

    Args:
        id: Campaign ID (auto-generated if not provided)
        name: Campaign name
        objective: Campaign objective
        status: Campaign status
        daily_budget: Daily budget in cents

    Returns:
        Campaign model instance
    """
    return Campaign(
        id=id or _random_id(),
        name=name,
        objective=objective,
        status=status,
        daily_budget=daily_budget,
        created_time=datetime.now() - timedelta(days=30),
        updated_time=datetime.now(),
    )


def generate_mock_adset(
    id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    name: str = "Test Ad Set",
    status: CampaignStatus = CampaignStatus.ACTIVE,
    daily_budget: int = 2000,
    countries: List[str] = None,
) -> AdSet:
    """
    Generate a mock AdSet for testing.

    Args:
        id: Ad set ID
        campaign_id: Parent campaign ID
        name: Ad set name
        status: Ad set status
        daily_budget: Daily budget in cents
        countries: Target countries

    Returns:
        AdSet model instance
    """
    if countries is None:
        countries = ["US"]

    return AdSet(
        id=id or _random_id(),
        campaign_id=campaign_id or _random_id(),
        name=name,
        status=status,
        optimization_goal=OptimizationGoal.LINK_CLICKS,
        billing_event=BillingEvent.IMPRESSIONS,
        daily_budget=daily_budget,
        targeting=TargetingSpec(
            geo_locations=GeoLocation(countries=countries),
            age_min=25,
            age_max=45,
        ),
    )


def generate_mock_ad(
    id: Optional[str] = None,
    adset_id: Optional[str] = None,
    creative_id: Optional[str] = None,
    name: str = "Test Ad",
    status: CampaignStatus = CampaignStatus.ACTIVE,
) -> Ad:
    """
    Generate a mock Ad for testing.

    Args:
        id: Ad ID
        adset_id: Parent ad set ID
        creative_id: Creative ID
        name: Ad name
        status: Ad status

    Returns:
        Ad model instance
    """
    return Ad(
        id=id or _random_id(),
        name=name,
        adset_id=adset_id or _random_id(),
        creative_id=creative_id or _random_id(),
        status=status,
    )


def generate_mock_creative(
    id: Optional[str] = None,
    name: str = "Test Creative",
    page_id: Optional[str] = None,
    link: str = "https://example.com",
) -> Creative:
    """
    Generate a mock Creative for testing.

    Args:
        id: Creative ID
        name: Creative name
        page_id: Facebook page ID
        link: Destination URL

    Returns:
        Creative model instance
    """
    return Creative(
        id=id or _random_id(),
        name=name,
        page_id=page_id or _random_id(),
        image_hash="abc123def456",
        link=link,
        message="Check out our product!",
        call_to_action_type=CallToActionType.LEARN_MORE,
    )


def generate_mock_ad_account(
    id: Optional[str] = None,
    name: str = "Test Ad Account",
    currency: str = "USD",
    status: AccountStatus = AccountStatus.ACTIVE,
) -> AdAccount:
    """
    Generate a mock AdAccount for testing.

    Args:
        id: Account ID (with act_ prefix)
        name: Account name
        currency: Currency code
        status: Account status

    Returns:
        AdAccount model instance
    """
    account_id = id or f"act_{_random_id()}"
    return AdAccount(
        id=account_id,
        account_id=account_id.replace("act_", ""),
        name=name,
        currency=currency,
        timezone_name="America/Los_Angeles",
        account_status=status,
        balance=50000,  # $500
        amount_spent=123456,  # $1234.56
        spend_cap=1000000,  # $10,000
        created_time=datetime.now() - timedelta(days=365),
    )


def generate_mock_insights(
    impressions: int = 125000,
    clicks: int = 3450,
    spend: float = 500.00,
) -> Insights:
    """
    Generate mock Insights for testing.

    Args:
        impressions: Number of impressions
        clicks: Number of clicks
        spend: Total spend in dollars

    Returns:
        Insights model instance
    """
    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    cpc = (spend / clicks) if clicks > 0 else 0
    cpm = (spend / impressions * 1000) if impressions > 0 else 0

    return Insights(
        impressions=impressions,
        clicks=clicks,
        spend=spend,
        reach=int(impressions * 0.8),
        frequency=1.25,
        ctr=ctr,
        cpc=cpc,
        cpm=cpm,
        actions=[
            {"action_type": "link_click", "value": clicks},
            {"action_type": "post_engagement", "value": int(clicks * 0.4)},
        ],
        date_start="2025-01-01",
        date_stop="2025-01-31",
    )


class MockFacebookClient:
    """
    Mock Facebook client for testing.

    Simulates Facebook API responses without making actual API calls.
    """

    def __init__(self, ad_account_id: str = "act_123456789"):
        self.ad_account_id = ad_account_id
        self._access_token = "mock_access_token"
        self._campaigns: Dict[str, Campaign] = {}
        self._adsets: Dict[str, AdSet] = {}
        self._ads: Dict[str, Ad] = {}
        self._creatives: Dict[str, Creative] = {}

        # Pre-populate with some test data
        self._setup_test_data()

    def _setup_test_data(self) -> None:
        """Set up default test data."""
        campaign1 = generate_mock_campaign(
            id="123456789",
            name="Test Campaign 1",
            status=CampaignStatus.ACTIVE,
        )
        campaign2 = generate_mock_campaign(
            id="987654321",
            name="Test Campaign 2",
            status=CampaignStatus.PAUSED,
        )
        self._campaigns[campaign1.id] = campaign1
        self._campaigns[campaign2.id] = campaign2

        adset1 = generate_mock_adset(
            id="234567890",
            campaign_id="123456789",
            name="Test Ad Set 1",
        )
        self._adsets[adset1.id] = adset1

    @property
    def is_test_mode(self) -> bool:
        return True

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def problems(self) -> List[str]:
        return []

    async def ensure_auth(self) -> Optional[str]:
        return None

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Mock GET request."""
        if "campaigns" in endpoint:
            return {"data": [c.model_dump() for c in self._campaigns.values()]}
        elif "adsets" in endpoint:
            return {"data": [a.model_dump() for a in self._adsets.values()]}
        elif "insights" in endpoint:
            insights = generate_mock_insights()
            return {"data": [insights.model_dump()]}
        elif "adaccounts" in endpoint:
            account = generate_mock_ad_account(id=self.ad_account_id)
            return {"data": [account.model_dump()]}
        else:
            return {"data": []}

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Mock POST request."""
        if "campaigns" in endpoint:
            campaign_id = _random_id()
            return {"id": campaign_id, "success": True}
        elif "adsets" in endpoint:
            adset_id = _random_id()
            return {"id": adset_id, "success": True}
        elif "adcreatives" in endpoint:
            creative_id = _random_id()
            return {"id": creative_id, "success": True}
        elif "ads" in endpoint:
            ad_id = _random_id()
            return {"id": ad_id, "success": True}
        elif "adimages" in endpoint:
            return {"images": {"img": {"hash": "abc123def456"}}}
        else:
            return {"success": True}

    async def delete(
        self,
        endpoint: str,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Mock DELETE request."""
        return {"success": True}
