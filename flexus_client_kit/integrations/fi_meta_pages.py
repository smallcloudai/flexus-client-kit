from __future__ import annotations

import logging
from typing import Any, Dict, List, TYPE_CHECKING

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.integrations._fi_meta_helpers import (
    FacebookAdsClient,
    FacebookAPIError,
    FacebookAuthError,
    FacebookValidationError,
    format_currency,
    format_account_status,
    validate_ad_account_id,
)

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

logger = logging.getLogger("meta_pages")

# Use case: "Manage Facebook Pages, ad accounts, users"
PROVIDER_NAME = "meta_pages"

_HELP = """meta_pages: Manage Facebook Pages and ad accounts.
op=help | status | list_methods | call(args={method_id, ...})

  list_ad_accounts()
  get_ad_account_info(ad_account_id)
  update_spending_limit(ad_account_id, spending_limit)
  list_account_users(ad_account_id)
  list_pages()
"""

_AD_ACCOUNT_FIELDS = "id,account_id,name,currency,timezone_name,account_status,balance,amount_spent,spend_cap,business{id,name}"
_AD_ACCOUNT_DETAIL_FIELDS = "id,account_id,name,currency,timezone_name,account_status,balance,amount_spent,spend_cap,business,funding_source_details,min_daily_budget,created_time"


async def _list_ad_accounts(client: FacebookAdsClient) -> str:
    if client.is_test_mode:
        return "Found 1 ad account:\n  Test Ad Account (ID: act_MOCK_TEST_000) — USD — Active\n"
    data = await client.request("GET", "me/adaccounts", params={"fields": _AD_ACCOUNT_FIELDS, "limit": 50})
    accounts = data.get("data", [])
    if not accounts:
        return "No ad accounts found. You may need to create one in Facebook Business Manager."
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
        result += f"Business: {biz_name} ({len(biz_accounts)} accounts)\n"
        for acc in biz_accounts:
            result += _format_account_summary(acc)
    if personal_accounts:
        result += f"Personal Accounts ({len(personal_accounts)}):\n"
        for acc in personal_accounts:
            result += _format_account_summary(acc)
    return result


def _format_account_summary(acc: Dict[str, Any]) -> str:
    currency = acc.get("currency", "USD")
    status_text = format_account_status(int(acc.get("account_status", 1)))
    result = f"  {acc.get('name', 'Unnamed')} (ID: {acc['id']})\n"
    result += f"     Status: {status_text} | Currency: {currency}\n"
    if "amount_spent" in acc:
        result += f"     Spent: {format_currency(int(acc['amount_spent']), currency)}\n"
    return result


async def _get_ad_account_info(client: FacebookAdsClient, ad_account_id: str) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    try:
        ad_account_id = validate_ad_account_id(ad_account_id)
    except FacebookValidationError as e:
        return f"ERROR: {e.message}"
    if client.is_test_mode:
        return f"Ad Account:\n  {ad_account_id}\n  Status: Active\n  Currency: USD\n  Spent: $1,234.56\n"
    acc = await client.request("GET", ad_account_id, params={"fields": _AD_ACCOUNT_DETAIL_FIELDS})
    currency = acc.get("currency", "USD")
    status_text = format_account_status(int(acc.get("account_status", 1)))
    result = f"Ad Account Details:\n\n  {acc.get('name', 'Unnamed')} (ID: {acc['id']})\n"
    result += f"  Status: {status_text}\n  Currency: {currency}\n  Timezone: {acc.get('timezone_name', 'N/A')}\n"
    result += f"  Balance: {format_currency(int(acc.get('balance', 0)), currency)}\n"
    result += f"  Total Spent: {format_currency(int(acc.get('amount_spent', 0)), currency)}\n"
    spend_cap = int(acc.get("spend_cap", 0))
    if spend_cap > 0:
        amount_spent = int(acc.get("amount_spent", 0))
        result += f"  Spend Cap: {format_currency(spend_cap, currency)}\n"
        result += f"  Remaining: {format_currency(spend_cap - amount_spent, currency)}\n"
    if acc.get("business"):
        biz = acc["business"]
        result += f"  Business: {biz.get('name', 'N/A')} (ID: {biz.get('id', 'N/A')})\n"
    return result


async def _update_spending_limit(client: FacebookAdsClient, ad_account_id: str, spending_limit: int) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    try:
        ad_account_id = validate_ad_account_id(ad_account_id)
    except FacebookValidationError as e:
        return f"ERROR: {e.message}"
    spending_limit = int(spending_limit)
    if spending_limit < 0:
        return "ERROR: spending_limit must be positive"
    if client.is_test_mode:
        return f"Spending limit updated to {format_currency(spending_limit)} for {ad_account_id}"
    result = await client.request("POST", ad_account_id, data={"spend_cap": spending_limit})
    return f"Spending limit updated to {format_currency(spending_limit)} for {ad_account_id}" if result.get("success") else f"Failed. Response: {result}"


async def _list_account_users(client: FacebookAdsClient, ad_account_id: str) -> str:
    if not ad_account_id:
        return "ERROR: ad_account_id required"
    try:
        ad_account_id = validate_ad_account_id(ad_account_id)
    except FacebookValidationError as e:
        return f"ERROR: {e.message}"
    if client.is_test_mode:
        return f"Users for {ad_account_id}:\n  Test User (ID: 123456789) — ADMIN\n"
    data = await client.request("GET", f"{ad_account_id}/users", params={"fields": "id,name,role,status", "limit": 50})
    users = data.get("data", [])
    if not users:
        return f"No users found for {ad_account_id}"
    result = f"Users for {ad_account_id} ({len(users)}):\n\n"
    for u in users:
        result += f"  {u.get('name', 'Unknown')} (ID: {u.get('id', 'N/A')}) — {u.get('role', 'N/A')}\n"
    return result


async def _list_pages(client: FacebookAdsClient) -> str:
    if client.is_test_mode:
        return "Pages you manage:\n  Test Page (ID: 111111111) — ACTIVE\n"
    data = await client.request("GET", "me/accounts", params={"fields": "id,name,category,tasks,access_token", "limit": 50})
    pages = data.get("data", [])
    if not pages:
        return "No pages found. You need to be an admin of at least one Facebook Page to create ads."
    result = f"Pages you manage ({len(pages)}):\n\n"
    for page in pages:
        tasks = ", ".join(page.get("tasks", []))
        result += f"  {page.get('name', 'Unnamed')} (ID: {page['id']})\n"
        result += f"     Category: {page.get('category', 'N/A')}\n"
        if tasks:
            result += f"     Tasks: {tasks}\n"
        result += "\n"
    return result


_HANDLERS: Dict[str, Any] = {
    "list_ad_accounts": lambda c, a: _list_ad_accounts(c),
    "get_ad_account_info": lambda c, a: _get_ad_account_info(c, a.get("ad_account_id", "")),
    "update_spending_limit": lambda c, a: _update_spending_limit(c, a.get("ad_account_id", ""), int(a.get("spending_limit", 0))),
    "list_account_users": lambda c, a: _list_account_users(c, a.get("ad_account_id", "")),
    "list_pages": lambda c, a: _list_pages(c),
}


class IntegrationMetaPages:
    def __init__(self, rcx: "ckit_bot_exec.RobotContext"):
        self.client = FacebookAdsClient(rcx.fclient, rcx)

    async def called_by_model(self, toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        try:
            args = model_produced_args or {}
            op = str(args.get("op", "help")).strip()
            if op == "help":
                return _HELP
            if op == "status":
                return await self._status()
            if op == "list_methods":
                return "\n".join(sorted(_HANDLERS.keys()))
            if op != "call":
                return "Error: unknown op. Use help/status/list_methods/call."
            call_args = args.get("args") or {}
            method_id = str(call_args.get("method_id", "")).strip()
            if not method_id:
                return "Error: args.method_id required for op=call."
            handler = _HANDLERS.get(method_id)
            if handler is None:
                return f"Error: unknown method_id={method_id!r}. Use op=list_methods."
            return await handler(self.client, call_args)
        except FacebookAuthError as e:
            return e.message
        except FacebookAPIError as e:
            logger.info("meta_pages api error: %s", e)
            return e.format_for_user()
        except FacebookValidationError as e:
            return f"Error: {e.message}"
        except Exception as e:
            logger.error("Unexpected error in meta_pages op=%s", (model_produced_args or {}).get("op"), exc_info=e)
            return f"Error: {e}"

    async def _status(self) -> str:
        try:
            auth_error = await self.client.ensure_auth()
            if auth_error:
                return auth_error
            return "meta_pages: connected. Use op=help to see available operations."
        except (FacebookAuthError, FacebookAPIError, FacebookValidationError) as e:
            return e.message
        except Exception as e:
            logger.error("Unexpected error in meta_pages status", exc_info=e)
            return f"Error: {e}"
