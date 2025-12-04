from __future__ import annotations
import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

from flexus_client_kit import ckit_cloudtool
from flexus_client_kit.integrations.facebook.client import FacebookAdsClient
from flexus_client_kit.integrations.facebook.exceptions import (
    FacebookAPIError,
    FacebookAuthError,
    FacebookValidationError,
)
from flexus_client_kit.integrations.facebook.accounts import list_ad_accounts, get_ad_account_info, update_spending_limit
from flexus_client_kit.integrations.facebook.campaigns import list_campaigns, create_campaign, update_campaign, duplicate_campaign, archive_campaign, bulk_update_campaigns, get_insights
from flexus_client_kit.integrations.facebook.adsets import list_adsets, create_adset, update_adset, validate_targeting
from flexus_client_kit.integrations.facebook.ads import upload_image, create_creative, create_ad, preview_ad

if TYPE_CHECKING:
    from flexus_client_kit import ckit_client, ckit_bot_exec

logger = logging.getLogger("facebook")

FACEBOOK_TOOL = ckit_cloudtool.CloudTool(
    name="facebook",
    description="Interact with Facebook/Instagram Marketing API. Call with op=\"help\" for usage.",
    parameters={
        "type": "object",
        "properties": {
            "op": {
                "type": "string",
                "description": "Operation name (e.g., 'status', 'list_campaigns', 'create_campaign')"
            },
            "args": {
                "type": "object",
                "description": "Arguments for the operation"
            },
        },
        "required": ["op"]
    },
)

HELP = """Help:
**Account Operations:**
facebook(op="list_ad_accounts")
    Lists all accessible ad accounts.
facebook(op="get_ad_account_info", args={"ad_account_id": "act_123"})
    Get detailed info about an ad account.
facebook(op="status", args={"ad_account_id": "act_123"})
    Shows current ad account status and active campaigns.
**Campaign Operations:**
facebook(op="list_campaigns", args={"ad_account_id": "act_123", "status": "ACTIVE"})
    Lists campaigns. Optional filters: status (ACTIVE, PAUSED, ARCHIVED).
facebook(op="create_campaign", args={
    "ad_account_id": "act_123",
    "name": "Summer Sale 2025",
    "objective": "OUTCOME_TRAFFIC",
    "daily_budget": 5000,
    "status": "PAUSED"
})
    Creates a new campaign. Budget is in cents (5000 = $50.00).
facebook(op="update_campaign", args={"campaign_id": "123", "status": "ACTIVE"})
    Update campaign settings.
facebook(op="get_insights", args={"campaign_id": "123456", "days": 30})
    Gets performance metrics.
**Ad Set Operations:**
facebook(op="list_adsets", args={"campaign_id": "123"})
    Lists ad sets for a campaign.
facebook(op="create_adset", args={
    "ad_account_id": "act_123",
    "campaign_id": "123456",
    "name": "US 18-35",
    "targeting": {"geo_locations": {"countries": ["US"]}}
})
    Creates an ad set with targeting.
**Creative & Ads Operations:**
facebook(op="upload_image", args={"image_url": "https://..."})
    Upload image for ad creative.
facebook(op="create_creative", args={
    "name": "Product Creative",
    "page_id": "123",
    "image_hash": "abc123",
    "link": "https://..."
})
    Create ad creative.
facebook(op="create_ad", args={
    "adset_id": "456",
    "creative_id": "789",
    "name": "Product Ad"
})
    Create ad from creative.
"""

_OPERATION_HANDLERS = {
    "list_ad_accounts": lambda client, args: list_ad_accounts(client),
    "get_ad_account_info": lambda client, args: get_ad_account_info(client, args.get("ad_account_id", "")),
    "update_spending_limit": lambda client, args: update_spending_limit(client, args.get("ad_account_id", ""), args.get("spending_limit", 0)),
    "list_campaigns": lambda client, args: list_campaigns(client, args.get("ad_account_id"), args.get("status")),
    "create_campaign": lambda client, args: create_campaign(
        client,
        args.get("ad_account_id", ""),
        args.get("name", ""),
        args.get("objective", "OUTCOME_TRAFFIC"),
        args.get("status", "PAUSED"),
        args.get("daily_budget"),
        args.get("lifetime_budget"),
        args.get("special_ad_categories"),
    ),
    "update_campaign": lambda client, args: update_campaign(
        client,
        args.get("campaign_id", ""),
        args.get("name"),
        args.get("status"),
        args.get("daily_budget"),
        args.get("lifetime_budget"),
    ),
    "duplicate_campaign": lambda client, args: duplicate_campaign(client, args.get("campaign_id", ""), args.get("new_name", ""), args.get("ad_account_id")),
    "archive_campaign": lambda client, args: archive_campaign(client, args.get("campaign_id", "")),
    "bulk_update_campaigns": lambda client, args: bulk_update_campaigns(client, args.get("campaigns", [])),
    "get_insights": lambda client, args: get_insights(client, args.get("campaign_id", ""), int(args.get("days", 30))),
    "list_adsets": lambda client, args: list_adsets(client, args.get("campaign_id", "")),
    "create_adset": lambda client, args: create_adset(
        client,
        args.get("ad_account_id", ""),
        args.get("campaign_id", ""),
        args.get("name", ""),
        args.get("targeting", {}),
        args.get("optimization_goal", "LINK_CLICKS"),
        args.get("billing_event", "IMPRESSIONS"),
        args.get("bid_strategy", "LOWEST_COST_WITHOUT_CAP"),
        args.get("status", "PAUSED"),
        args.get("daily_budget"),
        args.get("lifetime_budget"),
        args.get("bid_amount"),
        args.get("start_time"),
        args.get("end_time"),
        args.get("promoted_object"),
    ),
    "update_adset": lambda client, args: update_adset(
        client,
        args.get("adset_id", ""),
        args.get("name"),
        args.get("status"),
        args.get("daily_budget"),
        args.get("bid_amount"),
    ),
    "validate_targeting": lambda client, args: validate_targeting(client, args.get("targeting_spec", args.get("targeting", {})), args.get("ad_account_id")),
    "upload_image": lambda client, args: upload_image(client, args.get("image_path"), args.get("image_url"), args.get("ad_account_id")),
    "create_creative": lambda client, args: create_creative(
        client,
        args.get("name", ""),
        args.get("page_id", ""),
        args.get("image_hash", ""),
        args.get("link", ""),
        args.get("message"),
        args.get("headline"),
        args.get("description"),
        args.get("call_to_action_type", "LEARN_MORE"),
        args.get("ad_account_id"),
    ),
    "create_ad": lambda client, args: create_ad(
        client,
        args.get("name", ""),
        args.get("adset_id", ""),
        args.get("creative_id", ""),
        args.get("status", "PAUSED"),
        args.get("ad_account_id"),
    ),
    "preview_ad": lambda client, args: preview_ad(client, args.get("ad_id", ""), args.get("ad_format", "DESKTOP_FEED_STANDARD")),
}


class IntegrationFacebook:
    def __init__(
        self,
        fclient: "ckit_client.FlexusClient",
        rcx: "ckit_bot_exec.RobotContext",
        ad_account_id: str = "",
    ):
        self.client = FacebookAdsClient(fclient, rcx, ad_account_id)
        self.fclient = fclient
        self.rcx = rcx

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        if not model_produced_args:
            return HELP
        op = model_produced_args.get("op", "")
        args = model_produced_args.get("args", {})
        for key in ["ad_account_id", "campaign_id", "adset_id", "creative_id", "ad_id"]:
            if key in model_produced_args and key not in args:
                args[key] = model_produced_args[key]
        if not op or "help" in op.lower():
            return HELP
        if op == "status":
            return await self._handle_status(args)
        handler = _OPERATION_HANDLERS.get(op)
        if not handler:
            return f"Unknown operation '{op}'. Try op=\"help\" for available operations."
        try:
            return await handler(self.client, args)
        except FacebookAuthError as e:
            return e.message
        except FacebookAPIError as e:
            logger.info(f"Facebook API error: {e}")
            return e.format_for_user()
        except FacebookValidationError as e:
            return f"ERROR: {e.message}"
        except Exception as e:
            logger.warning(f"Unexpected error in {op}: {e}", exc_info=e)
            return f"ERROR: {str(e)}"

    async def _handle_status(self, args: Dict[str, Any]) -> str:
        ad_account_id = args.get("ad_account_id", "") or self.client.ad_account_id
        if ad_account_id:
            self.client.ad_account_id = ad_account_id
        if not self.client.ad_account_id:
            return "ERROR: ad_account_id parameter required for status"
        if self.client.is_test_mode:
            return f"""Facebook Ads Account: {self.client.ad_account_id}
Active Campaigns (2):
  Test Campaign 1 (ID: 123456789)
     Status: ACTIVE, Objective: OUTCOME_TRAFFIC, Daily Budget: $50.00
  Test Campaign 2 (ID: 987654321)
     Status: ACTIVE, Objective: OUTCOME_SALES, Daily Budget: $100.00
"""
        result = f"Facebook Ads Account: {self.client.ad_account_id}\n"
        campaigns_result = await list_campaigns(self.client, self.client.ad_account_id, "ACTIVE")
        result += campaigns_result
        return result
