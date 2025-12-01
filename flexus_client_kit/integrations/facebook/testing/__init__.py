"""
Facebook Ads Testing Utilities

Provides mock data generators and test fixtures for Facebook Ads integration testing.
"""

from .mocks import (
    generate_mock_campaign,
    generate_mock_adset,
    generate_mock_ad,
    generate_mock_creative,
    generate_mock_ad_account,
    generate_mock_insights,
    MockFacebookClient,
)

__all__ = [
    "generate_mock_campaign",
    "generate_mock_adset",
    "generate_mock_ad",
    "generate_mock_creative",
    "generate_mock_ad_account",
    "generate_mock_insights",
    "MockFacebookClient",
]
