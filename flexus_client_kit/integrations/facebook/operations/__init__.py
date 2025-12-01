"""
Facebook Ads Operations Package

Contains operation modules for different Facebook Ads entities.
"""

from .accounts import (
    list_ad_accounts,
    get_ad_account_info,
    update_spending_limit,
)
from .campaigns import (
    list_campaigns,
    create_campaign,
    update_campaign,
    duplicate_campaign,
    archive_campaign,
    bulk_update_campaigns,
    get_insights,
)
from .adsets import (
    list_adsets,
    create_adset,
    update_adset,
    validate_targeting,
)
from .ads import (
    upload_image,
    create_creative,
    create_ad,
    preview_ad,
)

__all__ = [
    # Accounts
    "list_ad_accounts",
    "get_ad_account_info",
    "update_spending_limit",
    # Campaigns
    "list_campaigns",
    "create_campaign",
    "update_campaign",
    "duplicate_campaign",
    "archive_campaign",
    "bulk_update_campaigns",
    "get_insights",
    # Ad Sets
    "list_adsets",
    "create_adset",
    "update_adset",
    "validate_targeting",
    # Ads
    "upload_image",
    "create_creative",
    "create_ad",
    "preview_ad",
]
