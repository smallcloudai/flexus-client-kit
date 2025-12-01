"""
Facebook Ad Account Operations

Operations for managing Facebook Ad Accounts.
Ad accounts are the top-level containers for all Facebook advertising.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, TYPE_CHECKING

from ..models import AdAccount
from ..utils import format_currency, format_account_status, validate_ad_account_id
from ..exceptions import FacebookValidationError

if TYPE_CHECKING:
    from ..client import FacebookAdsClient

logger = logging.getLogger("facebook.operations.accounts")

# Fields to request from API
AD_ACCOUNT_FIELDS = (
    "id,account_id,name,currency,timezone_name,account_status,"
    "balance,amount_spent,spend_cap,business{id,name}"
)
AD_ACCOUNT_DETAIL_FIELDS = (
    "id,account_id,name,currency,timezone_name,account_status,"
    "balance,amount_spent,spend_cap,business,funding_source_details,"
    "min_daily_budget,created_time"
)


async def list_ad_accounts(client: "FacebookAdsClient") -> str:
    """
    List all ad accounts accessible by the authenticated user.

    Groups accounts by business portfolio and personal accounts.

    Args:
        client: Authenticated Facebook client

    Returns:
        Formatted string with account list
    """
    if client.is_test_mode:
        return _mock_list_ad_accounts()

    data = await client.get(
        "me/adaccounts",
        params={"fields": AD_ACCOUNT_FIELDS, "limit": 50}
    )
    accounts = data.get("data", [])

    if not accounts:
        return (
            "No ad accounts found. You may need to:\n"
            "1. Create an ad account in Facebook Business Manager\n"
            "2. Ensure you have proper permissions"
        )

    # Group by business
    business_accounts: Dict[str, List[Any]] = {}
    personal_accounts: List[Any] = []

    for acc in accounts:
        business = acc.get("business")
        if business:
            biz_name = business.get("name", f"Business {business.get('id', 'Unknown')}")
            if biz_name not in business_accounts:
                business_accounts[biz_name] = []
            business_accounts[biz_name].append(acc)
        else:
            personal_accounts.append(acc)

    result = f"Found {len(accounts)} ad account{'s' if len(accounts) != 1 else ''}:\n\n"

    for biz_name, biz_accounts in business_accounts.items():
        count = len(biz_accounts)
        result += f"**Business Portfolio: {biz_name}** ({count} account{'s' if count != 1 else ''})\n\n"
        for acc in biz_accounts:
            result += _format_account_summary(acc)

    if personal_accounts:
        count = len(personal_accounts)
        result += f"**Personal Account** ({count} account{'s' if count != 1 else ''})\n\n"
        for acc in personal_accounts:
            result += _format_account_summary(acc)

    return result


async def get_ad_account_info(
    client: "FacebookAdsClient",
    ad_account_id: str,
) -> str:
    """
    Get detailed information about a specific ad account.

    Args:
        client: Authenticated Facebook client
        ad_account_id: Ad account ID (with or without act_ prefix)

    Returns:
        Formatted string with account details
    """
    if not ad_account_id:
        return "ERROR: ad_account_id parameter is required"

    try:
        ad_account_id = validate_ad_account_id(ad_account_id)
    except FacebookValidationError as e:
        return f"ERROR: {e.message}"

    if client.is_test_mode:
        return _mock_get_ad_account_info(ad_account_id)

    acc = await client.get(
        ad_account_id,
        params={"fields": AD_ACCOUNT_DETAIL_FIELDS}
    )

    account_status = acc.get("account_status", 1)
    status_text = format_account_status(account_status)
    currency = acc.get("currency", "USD")

    result = "Ad Account Details:\n\n"
    result += f"**{acc.get('name', 'Unnamed')}**\n"
    result += f"   ID: {acc['id']}\n"
    result += f"   Account ID: {acc.get('account_id', 'N/A')}\n"
    result += f"   Currency: {currency}\n"
    result += f"   Timezone: {acc.get('timezone_name', 'N/A')}\n"
    result += f"   Status: {status_text}\n"
    result += f"   Created: {acc.get('created_time', 'N/A')}\n"

    result += "\n**Financial Info:**\n"
    balance = int(acc.get('balance', 0))
    amount_spent = int(acc.get('amount_spent', 0))
    spend_cap = int(acc.get('spend_cap', 0))

    result += f"   Balance: {format_currency(balance, currency)}\n"
    result += f"   Total Spent: {format_currency(amount_spent, currency)}\n"

    if spend_cap > 0:
        result += f"   Spend Cap: {format_currency(spend_cap, currency)}\n"
        remaining = spend_cap - amount_spent
        result += f"   Remaining: {format_currency(remaining, currency)}\n"

        percent_used = (amount_spent / spend_cap) * 100 if spend_cap > 0 else 0
        if percent_used > 90:
            result += f"   Warning: {percent_used:.1f}% of spend cap used!\n"

    if 'min_daily_budget' in acc:
        result += f"   Min Daily Budget: {format_currency(int(acc['min_daily_budget']), currency)}\n"

    if 'business' in acc:
        business = acc['business']
        result += f"\n**Business:** {business.get('name', 'N/A')} (ID: {business.get('id', 'N/A')})\n"

    return result


async def update_spending_limit(
    client: "FacebookAdsClient",
    ad_account_id: str,
    spending_limit: int,
) -> str:
    """
    Update spending limit (spend cap) for an ad account.

    Args:
        client: Authenticated Facebook client
        ad_account_id: Ad account ID
        spending_limit: New spending limit in cents

    Returns:
        Formatted result string
    """
    if not ad_account_id:
        return "ERROR: ad_account_id parameter is required"

    try:
        ad_account_id = validate_ad_account_id(ad_account_id)
    except FacebookValidationError as e:
        return f"ERROR: {e.message}"

    spending_limit = int(spending_limit)
    if spending_limit < 0:
        return "ERROR: spending_limit must be a positive number"

    if client.is_test_mode:
        return f"Spending limit updated to {format_currency(spending_limit)} for account {ad_account_id}\n\n(Note: This is a test/mock operation)"

    result = await client.post(
        ad_account_id,
        data={"spend_cap": spending_limit}
    )

    if result.get("success"):
        return f"Spending limit updated to {format_currency(spending_limit)} for account {ad_account_id}"
    else:
        return f"Failed to update spending limit. Response: {result}"


# =============================================================================
# Helper Functions
# =============================================================================

def _format_account_summary(acc: Dict[str, Any]) -> str:
    """Format a single ad account for list display."""
    account_status = acc.get("account_status", 1)
    status_text = format_account_status(account_status)
    currency = acc.get("currency", "USD")

    result = f"   **{acc.get('name', 'Unnamed')}**\n"
    result += f"      ID: {acc['id']}\n"
    result += f"      Currency: {currency}\n"
    result += f"      Timezone: {acc.get('timezone_name', 'N/A')}\n"
    result += f"      Status: {status_text}\n"

    if 'balance' in acc:
        result += f"      Balance: {format_currency(int(acc['balance']), currency)}\n"
    if 'amount_spent' in acc:
        result += f"      Total Spent: {format_currency(int(acc['amount_spent']), currency)}\n"
    if 'spend_cap' in acc and int(acc.get('spend_cap', 0)) > 0:
        result += f"      Spend Cap: {format_currency(int(acc['spend_cap']), currency)}\n"

    result += "\n"
    return result


# =============================================================================
# Mock Responses (Test Mode)
# =============================================================================

def _mock_list_ad_accounts() -> str:
    return """Found 1 ad account:

**Test Ad Account**
   ID: act_MOCK_TEST_000
   Currency: USD
   Status: Active
   Balance: 500.00 USD
   Spend Cap: 10000.00 USD
"""


def _mock_get_ad_account_info(ad_account_id: str) -> str:
    return f"""Ad Account Details:

**Test Ad Account**
   ID: {ad_account_id}
   Account ID: MOCK_TEST_000
   Currency: USD
   Timezone: America/Los_Angeles
   Status: Active

**Financial Info:**
   Balance: 500.00 USD
   Total Spent: 1234.56 USD
   Spend Cap: 10000.00 USD
   Remaining: 8765.44 USD
"""
