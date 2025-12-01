"""
Tests for Facebook Ads operations using mock client.
"""

import pytest

from ..testing import MockFacebookClient
from ..operations import (
    list_ad_accounts,
    get_ad_account_info,
    list_campaigns,
    create_campaign,
    update_campaign,
    list_adsets,
    create_adset,
    upload_image,
    create_creative,
    create_ad,
)


@pytest.fixture
def mock_client():
    """Create a mock Facebook client for testing."""
    return MockFacebookClient(ad_account_id="act_123456789")


class TestAccountOperations:
    """Tests for ad account operations."""

    @pytest.mark.asyncio
    async def test_list_ad_accounts(self, mock_client):
        """Test listing ad accounts."""
        result = await list_ad_accounts(mock_client)
        assert "ad account" in result.lower()
        assert "act_" in result

    @pytest.mark.asyncio
    async def test_get_ad_account_info_requires_id(self, mock_client):
        """Test get_ad_account_info requires account ID."""
        result = await get_ad_account_info(mock_client, "")
        assert "ERROR" in result
        assert "required" in result.lower()

    @pytest.mark.asyncio
    async def test_get_ad_account_info(self, mock_client):
        """Test getting ad account info."""
        result = await get_ad_account_info(mock_client, "act_123456789")
        assert "Account" in result
        assert "Currency" in result


class TestCampaignOperations:
    """Tests for campaign operations."""

    @pytest.mark.asyncio
    async def test_list_campaigns(self, mock_client):
        """Test listing campaigns."""
        result = await list_campaigns(mock_client, "act_123456789")
        assert "campaign" in result.lower()

    @pytest.mark.asyncio
    async def test_create_campaign_requires_name(self, mock_client):
        """Test create_campaign requires name."""
        result = await create_campaign(
            mock_client,
            ad_account_id="act_123",
            name="",
            objective="OUTCOME_TRAFFIC",
        )
        assert "ERROR" in result
        assert "name" in result.lower()

    @pytest.mark.asyncio
    async def test_create_campaign_validates_objective(self, mock_client):
        """Test create_campaign validates objective."""
        result = await create_campaign(
            mock_client,
            ad_account_id="act_123",
            name="Test Campaign",
            objective="INVALID_OBJECTIVE",
        )
        assert "ERROR" in result
        assert "objective" in result.lower()

    @pytest.mark.asyncio
    async def test_create_campaign_success(self, mock_client):
        """Test successful campaign creation."""
        result = await create_campaign(
            mock_client,
            ad_account_id="act_123",
            name="Test Campaign",
            objective="OUTCOME_TRAFFIC",
            daily_budget=5000,
        )
        assert "created" in result.lower()
        assert "Test Campaign" in result

    @pytest.mark.asyncio
    async def test_update_campaign_requires_field(self, mock_client):
        """Test update_campaign requires at least one field."""
        result = await update_campaign(mock_client, "123456789")
        assert "ERROR" in result
        assert "field" in result.lower()

    @pytest.mark.asyncio
    async def test_update_campaign_validates_status(self, mock_client):
        """Test update_campaign validates status value."""
        result = await update_campaign(
            mock_client,
            "123456789",
            status="INVALID_STATUS",
        )
        assert "ERROR" in result
        assert "status" in result.lower()


class TestAdSetOperations:
    """Tests for ad set operations."""

    @pytest.mark.asyncio
    async def test_list_adsets_requires_campaign_id(self, mock_client):
        """Test list_adsets requires campaign ID."""
        result = await list_adsets(mock_client, "")
        assert "ERROR" in result
        assert "campaign_id" in result.lower()

    @pytest.mark.asyncio
    async def test_create_adset_validates_targeting(self, mock_client):
        """Test create_adset validates targeting."""
        result = await create_adset(
            mock_client,
            ad_account_id="act_123",
            campaign_id="123456",
            name="Test Ad Set",
            targeting={},  # Empty targeting
        )
        assert "ERROR" in result
        assert "targeting" in result.lower()

    @pytest.mark.asyncio
    async def test_create_adset_success(self, mock_client):
        """Test successful ad set creation."""
        result = await create_adset(
            mock_client,
            ad_account_id="act_123",
            campaign_id="123456",
            name="Test Ad Set",
            targeting={"geo_locations": {"countries": ["US"]}},
            daily_budget=2000,
        )
        assert "created" in result.lower()
        assert "Test Ad Set" in result


class TestAdsOperations:
    """Tests for creative and ad operations."""

    @pytest.mark.asyncio
    async def test_upload_image_requires_source(self, mock_client):
        """Test upload_image requires image_path or image_url."""
        result = await upload_image(mock_client)
        assert "ERROR" in result
        assert "image_path" in result.lower() or "image_url" in result.lower()

    @pytest.mark.asyncio
    async def test_create_creative_requires_fields(self, mock_client):
        """Test create_creative requires all fields."""
        result = await create_creative(
            mock_client,
            name="",
            page_id="123",
            image_hash="abc",
            link="https://example.com",
        )
        assert "ERROR" in result
        assert "name" in result.lower()

    @pytest.mark.asyncio
    async def test_create_ad_requires_fields(self, mock_client):
        """Test create_ad requires all fields."""
        result = await create_ad(
            mock_client,
            name="Test Ad",
            adset_id="",
            creative_id="789",
        )
        assert "ERROR" in result
        assert "adset_id" in result.lower()

    @pytest.mark.asyncio
    async def test_create_ad_validates_status(self, mock_client):
        """Test create_ad validates status."""
        result = await create_ad(
            mock_client,
            name="Test Ad",
            adset_id="456",
            creative_id="789",
            status="INVALID",
        )
        assert "ERROR" in result
        assert "status" in result.lower()
