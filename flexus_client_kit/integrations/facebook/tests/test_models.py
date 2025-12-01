"""
Tests for Facebook Ads Pydantic models.
"""

import pytest
from pydantic import ValidationError

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
)


class TestCampaign:
    """Tests for Campaign model."""

    def test_create_campaign_minimal(self):
        """Test creating campaign with minimal required fields."""
        campaign = Campaign(
            name="Test Campaign",
            objective=CampaignObjective.TRAFFIC,
        )
        assert campaign.name == "Test Campaign"
        assert campaign.objective == CampaignObjective.TRAFFIC
        assert campaign.status == CampaignStatus.PAUSED  # default
        assert campaign.id is None

    def test_create_campaign_full(self):
        """Test creating campaign with all fields."""
        campaign = Campaign(
            id="123456789",
            name="Full Campaign",
            objective=CampaignObjective.SALES,
            status=CampaignStatus.ACTIVE,
            daily_budget=5000,
            special_ad_categories=["HOUSING"],
        )
        assert campaign.id == "123456789"
        assert campaign.daily_budget == 5000
        assert campaign.special_ad_categories == ["HOUSING"]

    def test_campaign_budget_validation(self):
        """Test budget minimum validation."""
        # Budget below minimum should raise error
        with pytest.raises(ValidationError):
            Campaign(
                name="Test",
                objective=CampaignObjective.TRAFFIC,
                daily_budget=50,  # Below 100 cents minimum
            )

    def test_campaign_name_validation(self):
        """Test name length validation."""
        # Empty name should fail
        with pytest.raises(ValidationError):
            Campaign(
                name="",
                objective=CampaignObjective.TRAFFIC,
            )

    def test_campaign_budget_coercion(self):
        """Test budget string/float coercion to int."""
        campaign = Campaign(
            name="Test",
            objective=CampaignObjective.TRAFFIC,
            daily_budget="5000",  # String should be coerced
        )
        assert campaign.daily_budget == 5000
        assert isinstance(campaign.daily_budget, int)


class TestTargetingSpec:
    """Tests for TargetingSpec model."""

    def test_valid_targeting(self):
        """Test valid targeting with countries."""
        targeting = TargetingSpec(
            geo_locations=GeoLocation(countries=["US", "CA"]),
            age_min=25,
            age_max=45,
        )
        assert targeting.age_min == 25
        assert targeting.age_max == 45
        assert "US" in targeting.geo_locations.countries

    def test_targeting_requires_geo(self):
        """Test that geo_locations is required."""
        with pytest.raises(ValidationError):
            TargetingSpec(
                geo_locations=GeoLocation(),  # Empty geo
                age_min=25,
            )

    def test_targeting_age_range_validation(self):
        """Test age_min <= age_max validation."""
        with pytest.raises(ValidationError):
            TargetingSpec(
                geo_locations=GeoLocation(countries=["US"]),
                age_min=50,
                age_max=30,  # age_min > age_max
            )

    def test_targeting_age_limits(self):
        """Test Facebook age limits (13-65)."""
        with pytest.raises(ValidationError):
            TargetingSpec(
                geo_locations=GeoLocation(countries=["US"]),
                age_min=10,  # Below 13
            )

        with pytest.raises(ValidationError):
            TargetingSpec(
                geo_locations=GeoLocation(countries=["US"]),
                age_max=70,  # Above 65
            )


class TestAdSet:
    """Tests for AdSet model."""

    def test_create_adset(self):
        """Test creating ad set with targeting."""
        adset = AdSet(
            campaign_id="123456",
            name="Test Ad Set",
            targeting=TargetingSpec(
                geo_locations=GeoLocation(countries=["US"]),
            ),
        )
        assert adset.campaign_id == "123456"
        assert adset.optimization_goal == OptimizationGoal.LINK_CLICKS  # default
        assert adset.status == CampaignStatus.PAUSED  # default


class TestCreative:
    """Tests for Creative model."""

    def test_creative_requires_image(self):
        """Test that either image_hash or image_url is required."""
        with pytest.raises(ValidationError):
            Creative(
                name="Test Creative",
                page_id="123",
                link="https://example.com",
                # No image_hash or image_url
            )

    def test_creative_with_image_hash(self):
        """Test creative with image hash."""
        creative = Creative(
            name="Test Creative",
            page_id="123",
            image_hash="abc123",
            link="https://example.com",
        )
        assert creative.image_hash == "abc123"

    def test_creative_with_image_url(self):
        """Test creative with image URL."""
        creative = Creative(
            name="Test Creative",
            page_id="123",
            image_url="https://example.com/image.jpg",
            link="https://example.com",
        )
        assert creative.image_url == "https://example.com/image.jpg"


class TestAdAccount:
    """Tests for AdAccount model."""

    def test_ad_account_is_active(self):
        """Test is_active property."""
        active_account = AdAccount(
            id="act_123",
            name="Test Account",
            account_status=AccountStatus.ACTIVE,
        )
        assert active_account.is_active is True

        disabled_account = AdAccount(
            id="act_456",
            name="Disabled Account",
            account_status=AccountStatus.DISABLED,
        )
        assert disabled_account.is_active is False

    def test_remaining_budget(self):
        """Test remaining_budget property."""
        account = AdAccount(
            id="act_123",
            name="Test Account",
            spend_cap=10000,
            amount_spent=3000,
        )
        assert account.remaining_budget == 7000


class TestInsights:
    """Tests for Insights model."""

    def test_insights_coercion(self):
        """Test that string values are coerced to proper types."""
        insights = Insights(
            impressions="125000",
            clicks="3450",
            spend="500.00",
            ctr="2.76",
        )
        assert insights.impressions == 125000
        assert isinstance(insights.impressions, int)
        assert insights.spend == 500.0
        assert isinstance(insights.spend, float)
