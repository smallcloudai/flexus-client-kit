"""
Tests for Facebook Ads utility functions.
"""

import pytest

from ..utils import (
    validate_ad_account_id,
    validate_budget,
    validate_targeting_spec,
    format_currency,
    format_account_status,
    normalize_insights_data,
    hash_for_audience,
)
from ..exceptions import FacebookValidationError


class TestValidateAdAccountId:
    """Tests for validate_ad_account_id."""

    def test_valid_with_prefix(self):
        """Test ID already has act_ prefix."""
        result = validate_ad_account_id("act_123456789")
        assert result == "act_123456789"

    def test_valid_without_prefix(self):
        """Test ID without act_ prefix gets it added."""
        result = validate_ad_account_id("123456789")
        assert result == "act_123456789"

    def test_empty_string_raises(self):
        """Test empty string raises error."""
        with pytest.raises(FacebookValidationError) as exc_info:
            validate_ad_account_id("")
        assert "ad_account_id" in str(exc_info.value)

    def test_none_raises(self):
        """Test None raises error."""
        with pytest.raises(FacebookValidationError):
            validate_ad_account_id(None)

    def test_whitespace_handling(self):
        """Test whitespace is stripped."""
        result = validate_ad_account_id("  123456789  ")
        assert result == "act_123456789"


class TestValidateBudget:
    """Tests for validate_budget."""

    def test_valid_budget(self):
        """Test valid budget passes."""
        result = validate_budget(5000)
        assert result == 5000

    def test_minimum_budget(self):
        """Test minimum budget (100 cents = $1)."""
        result = validate_budget(100)
        assert result == 100

    def test_below_minimum_raises(self):
        """Test budget below minimum raises error."""
        with pytest.raises(FacebookValidationError) as exc_info:
            validate_budget(50)
        assert "budget" in str(exc_info.value)
        assert "1.00" in str(exc_info.value)

    def test_string_coercion(self):
        """Test string budget is coerced to int."""
        result = validate_budget("5000")
        assert result == 5000
        assert isinstance(result, int)

    def test_invalid_type_raises(self):
        """Test invalid type raises error."""
        with pytest.raises(FacebookValidationError):
            validate_budget("not a number")


class TestValidateTargetingSpec:
    """Tests for validate_targeting_spec."""

    def test_valid_targeting(self):
        """Test valid targeting spec."""
        spec = {
            "geo_locations": {"countries": ["US"]},
            "age_min": 25,
            "age_max": 45,
        }
        valid, error = validate_targeting_spec(spec)
        assert valid is True
        assert error == ""

    def test_empty_spec(self):
        """Test empty spec is invalid."""
        valid, error = validate_targeting_spec({})
        assert valid is False
        assert "empty" in error.lower()

    def test_missing_geo_locations(self):
        """Test missing geo_locations is invalid."""
        spec = {"age_min": 25}
        valid, error = validate_targeting_spec(spec)
        assert valid is False
        assert "geo_locations" in error

    def test_empty_geo_locations(self):
        """Test empty geo_locations is invalid."""
        spec = {"geo_locations": {}}
        valid, error = validate_targeting_spec(spec)
        assert valid is False
        assert "geo_location" in error.lower()

    def test_age_validation(self):
        """Test age range validation."""
        # age_min > age_max
        spec = {
            "geo_locations": {"countries": ["US"]},
            "age_min": 50,
            "age_max": 30,
        }
        valid, error = validate_targeting_spec(spec)
        assert valid is False
        assert "age_min" in error

        # age_min too low
        spec = {
            "geo_locations": {"countries": ["US"]},
            "age_min": 10,
        }
        valid, error = validate_targeting_spec(spec)
        assert valid is False


class TestFormatCurrency:
    """Tests for format_currency."""

    def test_basic_formatting(self):
        """Test basic currency formatting."""
        assert format_currency(5000) == "50.00 USD"
        assert format_currency(100) == "1.00 USD"
        assert format_currency(0) == "0.00 USD"

    def test_different_currency(self):
        """Test different currency codes."""
        assert format_currency(5000, "EUR") == "50.00 EUR"
        assert format_currency(5000, "GBP") == "50.00 GBP"

    def test_decimal_handling(self):
        """Test cents to dollars conversion."""
        assert format_currency(5050) == "50.50 USD"
        assert format_currency(99) == "0.99 USD"


class TestFormatAccountStatus:
    """Tests for format_account_status."""

    def test_known_statuses(self):
        """Test known status codes."""
        assert format_account_status(1) == "Active"
        assert format_account_status(2) == "Disabled"
        assert format_account_status(3) == "Unsettled"

    def test_unknown_status(self):
        """Test unknown status code."""
        result = format_account_status(999)
        assert "Unknown" in result
        assert "999" in result


class TestNormalizeInsightsData:
    """Tests for normalize_insights_data."""

    def test_basic_normalization(self):
        """Test basic insights normalization."""
        raw = {
            "impressions": "125000",
            "clicks": "3450",
            "spend": "500.00",
        }
        insights = normalize_insights_data(raw)
        assert insights.impressions == 125000
        assert insights.clicks == 3450
        assert insights.spend == 500.0

    def test_calculated_metrics(self):
        """Test CTR/CPC/CPM calculation when not provided."""
        raw = {
            "impressions": "10000",
            "clicks": "100",
            "spend": "50.00",
        }
        insights = normalize_insights_data(raw)

        # CTR = clicks / impressions * 100 = 1%
        assert insights.ctr == pytest.approx(1.0, rel=0.01)

        # CPC = spend / clicks = $0.50
        assert insights.cpc == pytest.approx(0.5, rel=0.01)

        # CPM = spend / impressions * 1000 = $5.00
        assert insights.cpm == pytest.approx(5.0, rel=0.01)

    def test_provided_metrics_used(self):
        """Test that provided metrics are used instead of calculated."""
        raw = {
            "impressions": "10000",
            "clicks": "100",
            "spend": "50.00",
            "ctr": "2.5",  # Different from calculated
            "cpc": "0.75",
        }
        insights = normalize_insights_data(raw)
        assert insights.ctr == 2.5
        assert insights.cpc == 0.75

    def test_empty_data(self):
        """Test handling of empty data."""
        insights = normalize_insights_data({})
        assert insights.impressions == 0
        assert insights.clicks == 0
        assert insights.spend == 0.0


class TestHashForAudience:
    """Tests for hash_for_audience."""

    def test_email_hashing(self):
        """Test email normalization and hashing."""
        hash1 = hash_for_audience("Test@Example.com", "EMAIL")
        hash2 = hash_for_audience("test@example.com", "EMAIL")
        assert hash1 == hash2  # Should be same after normalization

    def test_phone_hashing(self):
        """Test phone normalization (digits only)."""
        hash1 = hash_for_audience("+1 (555) 123-4567", "PHONE")
        hash2 = hash_for_audience("15551234567", "PHONE")
        assert hash1 == hash2  # Should be same after normalization

    def test_name_hashing(self):
        """Test name normalization (no spaces)."""
        hash1 = hash_for_audience("John Doe", "FN")
        hash2 = hash_for_audience("johndoe", "FN")
        assert hash1 == hash2
