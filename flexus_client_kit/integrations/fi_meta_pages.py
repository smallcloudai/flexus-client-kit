from __future__ import annotations

import logging
from typing import Any, Dict, TYPE_CHECKING

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.integrations.facebook.client import FacebookAdsClient
from flexus_client_kit.integrations.facebook.exceptions import (
    FacebookAPIError,
    FacebookAuthError,
    FacebookValidationError,
)
from flexus_client_kit.integrations.facebook.accounts import (
    list_ad_accounts, get_ad_account_info, update_spending_limit,
    list_account_users, list_pages,
)

if TYPE_CHECKING:
    from flexus_client_kit import ckit_bot_exec

logger = logging.getLogger("meta_pages")

# Use case: "Manage everything on your Page"
# Covers Facebook Pages, ad accounts, users — the account-level layer above campaigns.
PROVIDER_NAME = "meta_pages"

_HELP = """meta_pages: Manage Facebook Pages and ad accounts.
op=help | status | list_methods | call(args={method_id, ...})

  list_pages()  -- Facebook Pages you manage (needed for ad creatives)
  list_ad_accounts()  -- All ad accounts accessible with your token
  get_ad_account_info(ad_account_id)
  update_spending_limit(ad_account_id, spending_limit)
  list_account_users(ad_account_id)
"""

_HANDLERS: Dict[str, Any] = {
    "list_pages": lambda c, a: list_pages(c),
    "list_ad_accounts": lambda c, a: list_ad_accounts(c),
    "get_ad_account_info": lambda c, a: get_ad_account_info(c, a.get("ad_account_id", "")),
    "update_spending_limit": lambda c, a: update_spending_limit(c, a.get("ad_account_id", ""), a.get("spending_limit", 0)),
    "list_account_users": lambda c, a: list_account_users(c, a.get("ad_account_id", "")),
}


class IntegrationMetaPages:
    # Wraps FacebookAdsClient for page/account-level operations.
    def __init__(self, rcx: "ckit_bot_exec.RobotContext"):
        self.client = FacebookAdsClient(rcx.fclient, rcx)

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Dict[str, Any],
    ) -> str:
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
                return f"Error: unknown method_id={method_id!r}. Use op=list_methods to see available methods."
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
