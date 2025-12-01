"""
Facebook Ads API Integration

A comprehensive integration for Facebook Marketing API, providing:
- Type-safe Pydantic models for all Facebook Ads entities
- Authenticated HTTP client with retry logic
- Operations for campaigns, ad sets, ads, and creatives
- Support for test/mock mode

Usage:
    from flexus_client_kit.integrations.facebook import (
        IntegrationFacebook,
        FACEBOOK_TOOL,
        FacebookAdsClient,
        Campaign,
        AdSet,
    )

    # In your bot:
    fb = IntegrationFacebook(fclient, rcx, ad_account_id="act_123456")
    result = await fb.called_by_model(toolcall, {"op": "status"})
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

from flexus_client_kit import ckit_cloudtool

from .client import FacebookAdsClient
from .models import (
    Campaign,
    CampaignObjective,
    CampaignStatus,
    AdSet,
    Ad,
    Creative,
    AdAccount,
    Insights,
    TargetingSpec,
    GeoLocation,
    OptimizationGoal,
    BillingEvent,
    CallToActionType,
    AdFormat,
)
from .exceptions import (
    FacebookError,
    FacebookAPIError,
    FacebookAuthError,
    FacebookValidationError,
    FacebookRateLimitError,
)
from .utils import (
    validate_ad_account_id,
    validate_budget,
    validate_targeting_spec,
    format_currency,
)
from . import operations

if TYPE_CHECKING:
    from flexus_client_kit import ckit_client, ckit_bot_exec

logger = logging.getLogger("facebook")

__all__ = [
    # Main integration class
    "IntegrationFacebook",
    "FACEBOOK_TOOL",
    # Client
    "FacebookAdsClient",
    # Models
    "Campaign",
    "CampaignObjective",
    "CampaignStatus",
    "AdSet",
    "Ad",
    "Creative",
    "AdAccount",
    "Insights",
    "TargetingSpec",
    "GeoLocation",
    "OptimizationGoal",
    "BillingEvent",
    "CallToActionType",
    "AdFormat",
    # Exceptions
    "FacebookError",
    "FacebookAPIError",
    "FacebookAuthError",
    "FacebookValidationError",
    "FacebookRateLimitError",
    # Utils
    "validate_ad_account_id",
    "validate_budget",
    "validate_targeting_spec",
    "format_currency",
    # Operations module
    "operations",
]


# Tool definition exposed to AI model via OpenAI function calling format
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


# Help text returned when model calls facebook(op="help")
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


# Operation name -> handler function mapping
_OPERATION_HANDLERS = {
    # Account operations
    "list_ad_accounts": lambda client, args: operations.list_ad_accounts(client),
    "get_ad_account_info": lambda client, args: operations.get_ad_account_info(
        client, args.get("ad_account_id", "")
    ),
    "update_spending_limit": lambda client, args: operations.update_spending_limit(
        client, args.get("ad_account_id", ""), args.get("spending_limit", 0)
    ),
    # Campaign operations
    "list_campaigns": lambda client, args: operations.list_campaigns(
        client, args.get("ad_account_id"), args.get("status")
    ),
    "create_campaign": lambda client, args: operations.create_campaign(
        client,
        args.get("ad_account_id", ""),
        args.get("name", ""),
        args.get("objective", "OUTCOME_TRAFFIC"),
        args.get("status", "PAUSED"),
        args.get("daily_budget"),
        args.get("lifetime_budget"),
        args.get("special_ad_categories"),
    ),
    "update_campaign": lambda client, args: operations.update_campaign(
        client,
        args.get("campaign_id", ""),
        args.get("name"),
        args.get("status"),
        args.get("daily_budget"),
        args.get("lifetime_budget"),
    ),
    "duplicate_campaign": lambda client, args: operations.duplicate_campaign(
        client, args.get("campaign_id", ""), args.get("new_name", ""), args.get("ad_account_id")
    ),
    "archive_campaign": lambda client, args: operations.archive_campaign(
        client, args.get("campaign_id", "")
    ),
    "bulk_update_campaigns": lambda client, args: operations.bulk_update_campaigns(
        client, args.get("campaigns", [])
    ),
    "get_insights": lambda client, args: operations.get_insights(
        client, args.get("campaign_id", ""), int(args.get("days", 30))
    ),
    # Ad set operations
    "list_adsets": lambda client, args: operations.list_adsets(
        client, args.get("campaign_id", "")
    ),
    "create_adset": lambda client, args: operations.create_adset(
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
    "update_adset": lambda client, args: operations.update_adset(
        client,
        args.get("adset_id", ""),
        args.get("name"),
        args.get("status"),
        args.get("daily_budget"),
        args.get("bid_amount"),
    ),
    "validate_targeting": lambda client, args: operations.validate_targeting(
        client, args.get("targeting_spec", args.get("targeting", {})), args.get("ad_account_id")
    ),
    # Ads operations
    "upload_image": lambda client, args: operations.upload_image(
        client, args.get("image_path"), args.get("image_url"), args.get("ad_account_id")
    ),
    "create_creative": lambda client, args: operations.create_creative(
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
    "create_ad": lambda client, args: operations.create_ad(
        client,
        args.get("name", ""),
        args.get("adset_id", ""),
        args.get("creative_id", ""),
        args.get("status", "PAUSED"),
        args.get("ad_account_id"),
    ),
    "preview_ad": lambda client, args: operations.preview_ad(
        client, args.get("ad_id", ""), args.get("ad_format", "DESKTOP_FEED_STANDARD")
    ),
}


class IntegrationFacebook:
    """
    Facebook Marketing API integration for Flexus bots.

    Provides a unified interface for all Facebook Ads operations.
    Handles OAuth token retrieval, API calls, and response formatting.

    Usage:
        fb = IntegrationFacebook(fclient, rcx, ad_account_id="act_123456")
        result = await fb.called_by_model(toolcall, {"op": "status"})
    """

    def __init__(
        self,
        fclient: "ckit_client.FlexusClient",
        rcx: "ckit_bot_exec.RobotContext",
        ad_account_id: str = "",
    ):
        """
        Initialize Facebook integration.

        Args:
            fclient: Flexus client for backend calls
            rcx: Robot context with persona and thread info
            ad_account_id: Default Facebook ad account ID (act_123... or just 123...)
        """
        self.client = FacebookAdsClient(fclient, rcx, ad_account_id)
        self.fclient = fclient
        self.rcx = rcx

    @property
    def ad_account_id(self) -> str:
        """Current ad account ID."""
        return self.client.ad_account_id

    @ad_account_id.setter
    def ad_account_id(self, value: str) -> None:
        """Set ad account ID."""
        self.client.ad_account_id = value

    @property
    def is_fake(self) -> bool:
        """Check if running in test mode."""
        return self.client.is_test_mode

    @property
    def problems(self) -> list[str]:
        """List of problems encountered."""
        return self.client.problems

    async def ensure_headers(self) -> Optional[str]:
        """Ensure authentication is ready. Returns error message or None."""
        return await self.client.ensure_auth()

    async def called_by_model(
        self,
        toolcall: ckit_cloudtool.FCloudtoolCall,
        model_produced_args: Optional[Dict[str, Any]],
    ) -> str:
        """
        Handle tool calls from AI model.

        Routes to appropriate handler based on 'op' parameter.

        Args:
            toolcall: Tool call metadata from Flexus
            model_produced_args: Arguments from model (op, args)

        Returns:
            Formatted string response for the model
        """
        if not model_produced_args:
            return HELP

        op = model_produced_args.get("op", "")
        args = model_produced_args.get("args", {})

        # Allow top-level args to be used if args dict is empty
        for key in ["ad_account_id", "campaign_id", "adset_id", "creative_id", "ad_id"]:
            if key in model_produced_args and key not in args:
                args[key] = model_produced_args[key]

        # Handle help
        if not op or "help" in op.lower():
            return HELP

        # Handle status specially (uses ad_account_id from args or default)
        if op == "status":
            return await self._handle_status(args)

        # Find handler
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
        """Handle status operation."""
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
        campaigns_result = await operations.list_campaigns(
            self.client, self.client.ad_account_id, "ACTIVE"
        )
        result += campaigns_result

        return result
