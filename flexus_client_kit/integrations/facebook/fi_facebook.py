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
from flexus_client_kit.integrations.facebook.accounts import (
    list_ad_accounts, get_ad_account_info, update_spending_limit,
    list_account_users, list_pages,
)
from flexus_client_kit.integrations.facebook.campaigns import (
    list_campaigns, create_campaign, update_campaign, duplicate_campaign,
    archive_campaign, bulk_update_campaigns, get_insights,
    get_campaign, delete_campaign,
)
from flexus_client_kit.integrations.facebook.adsets import (
    list_adsets, create_adset, update_adset, validate_targeting,
    get_adset, delete_adset, list_adsets_for_account,
)
from flexus_client_kit.integrations.facebook.ads import (
    upload_image, create_creative, create_ad, preview_ad,
    get_ad, update_ad, delete_ad, list_ads,
    list_creatives, get_creative, update_creative, delete_creative, preview_creative,
    upload_video, list_videos,
)
from flexus_client_kit.integrations.facebook.insights import (
    get_account_insights, get_campaign_insights, get_adset_insights, get_ad_insights,
    create_async_report, get_async_report_status,
)
from flexus_client_kit.integrations.facebook.audiences import (
    list_custom_audiences, create_custom_audience, create_lookalike_audience,
    get_custom_audience, update_custom_audience, delete_custom_audience, add_users_to_audience,
)
from flexus_client_kit.integrations.facebook.pixels import list_pixels, create_pixel, get_pixel_stats
from flexus_client_kit.integrations.facebook.targeting import (
    search_interests, search_behaviors, get_reach_estimate, get_delivery_estimate,
)
from flexus_client_kit.integrations.facebook.rules import (
    list_ad_rules, create_ad_rule, update_ad_rule, delete_ad_rule, execute_ad_rule,
)

if TYPE_CHECKING:
    from flexus_client_kit import ckit_client, ckit_bot_exec

logger = logging.getLogger("facebook")

FACEBOOK_TOOL = ckit_cloudtool.CloudTool(
    strict=False,
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

HELP = """Facebook Marketing API — Available Operations:

**Connection:**
  connect — Generate OAuth link to connect your Facebook account.

**Account Operations:**
  list_ad_accounts — List all accessible ad accounts.
  get_ad_account_info(ad_account_id) — Detailed info about an ad account.
  update_spending_limit(ad_account_id, spending_limit) — Set monthly spending cap (cents).
  list_account_users(ad_account_id) — List users with access to an ad account.
  list_pages() — List Facebook Pages you manage (for page_id in creatives).
  status(ad_account_id) — Current account status and active campaigns.

**Campaign Operations:**
  list_campaigns(ad_account_id, status?) — List campaigns, optional status filter.
  get_campaign(campaign_id) — Get full details of a single campaign.
  create_campaign(ad_account_id, name, objective, daily_budget?, lifetime_budget?, status?) — Create campaign. Budget in cents.
  update_campaign(campaign_id, name?, status?, daily_budget?, lifetime_budget?) — Update campaign.
  delete_campaign(campaign_id) — Permanently delete a campaign.
  duplicate_campaign(campaign_id, new_name, ad_account_id?) — Duplicate a campaign.
  archive_campaign(campaign_id) — Archive a campaign.
  bulk_update_campaigns(campaigns) — Bulk update multiple campaigns.

**Ad Set Operations:**
  list_adsets(campaign_id) — List ad sets in a campaign.
  list_adsets_for_account(ad_account_id, status_filter?) — List all ad sets in an account.
  get_adset(adset_id) — Get full details of a single ad set.
  create_adset(ad_account_id, campaign_id, name, targeting, optimization_goal?, billing_event?, status?) — Create ad set.
  update_adset(adset_id, name?, status?, daily_budget?, bid_amount?) — Update ad set.
  delete_adset(adset_id) — Permanently delete an ad set.
  validate_targeting(targeting_spec, ad_account_id?) — Validate targeting spec.

**Ads Operations:**
  list_ads(ad_account_id?, adset_id?, status_filter?) — List ads in account or ad set.
  get_ad(ad_id) — Get full details of a single ad.
  create_ad(name, adset_id, creative_id, status?, ad_account_id?) — Create an ad.
  update_ad(ad_id, name?, status?) — Update ad name or status.
  delete_ad(ad_id) — Permanently delete an ad.
  preview_ad(ad_id, ad_format?) — Generate ad preview.

**Creative Operations:**
  list_creatives(ad_account_id) — List all ad creatives in account.
  get_creative(creative_id) — Get creative details.
  create_creative(name, page_id, image_hash, link, message?, headline?, description?, call_to_action_type?, ad_account_id?) — Create creative.
  update_creative(creative_id, name) — Update creative name.
  delete_creative(creative_id) — Delete a creative.
  preview_creative(creative_id, ad_format?) — Preview a creative.
  upload_image(image_url?, image_path?, ad_account_id?) — Upload image, returns image_hash.
  upload_video(video_url, ad_account_id?, title?, description?) — Upload video from URL.
  list_videos(ad_account_id) — List ad videos in account.

**Insights & Reporting:**
  get_insights(campaign_id, days?) — Campaign performance metrics.
  get_account_insights(ad_account_id, days?, breakdowns?, metrics?, date_preset?) — Account-level insights.
  get_campaign_insights(campaign_id, days?, breakdowns?, metrics?, date_preset?) — Campaign insights with breakdowns.
  get_adset_insights(adset_id, days?, breakdowns?, metrics?, date_preset?) — Ad set insights.
  get_ad_insights(ad_id, days?, breakdowns?, metrics?, date_preset?) — Ad-level insights.
  create_async_report(ad_account_id, level?, fields?, date_preset?, breakdowns?) — Create async report job.
  get_async_report_status(report_run_id) — Check async report status.

**Custom Audiences:**
  list_custom_audiences(ad_account_id) — List custom audiences.
  create_custom_audience(ad_account_id, name, subtype?, description?) — Create custom audience. Subtypes: CUSTOM, WEBSITE, APP, ENGAGEMENT.
  create_lookalike_audience(ad_account_id, origin_audience_id, country, ratio?, name?) — Create lookalike audience (ratio: 0.01–0.20).
  get_custom_audience(audience_id) — Get audience details.
  update_custom_audience(audience_id, name?, description?) — Update audience.
  delete_custom_audience(audience_id) — Delete audience.
  add_users_to_audience(audience_id, emails, phones?) — Add users via SHA-256 hashed emails/phones.

**Pixels:**
  list_pixels(ad_account_id) — List Meta pixels in account.
  create_pixel(ad_account_id, name) — Create new pixel.
  get_pixel_stats(pixel_id, start_time?, end_time?, aggregation?) — Get pixel event stats.

**Targeting Research:**
  search_interests(q, limit?) — Search interest targeting options by keyword.
  search_behaviors(q, limit?) — Search behavior targeting options by keyword.
  get_reach_estimate(ad_account_id, targeting, optimization_goal?) — Estimate audience reach.
  get_delivery_estimate(ad_account_id, targeting, optimization_goal?, bid_amount?) — Estimate delivery curve.

**Ad Rules Engine:**
  list_ad_rules(ad_account_id) — List automated ad rules.
  create_ad_rule(ad_account_id, name, evaluation_spec, execution_spec, schedule_spec?, status?) — Create automated rule.
  update_ad_rule(rule_id, name?, status?) — Update rule name or status.
  delete_ad_rule(rule_id) — Delete a rule.
  execute_ad_rule(rule_id) — Manually trigger a rule immediately.
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
    # Account extensions
    "list_account_users": lambda client, args: list_account_users(client, args.get("ad_account_id", "")),
    "list_pages": lambda client, args: list_pages(client),
    # Campaign extensions
    "get_campaign": lambda client, args: get_campaign(client, args.get("campaign_id", "")),
    "delete_campaign": lambda client, args: delete_campaign(client, args.get("campaign_id", "")),
    # Ad set extensions
    "get_adset": lambda client, args: get_adset(client, args.get("adset_id", "")),
    "delete_adset": lambda client, args: delete_adset(client, args.get("adset_id", "")),
    "list_adsets_for_account": lambda client, args: list_adsets_for_account(client, args.get("ad_account_id", ""), args.get("status_filter")),
    # Ads extensions
    "get_ad": lambda client, args: get_ad(client, args.get("ad_id", "")),
    "update_ad": lambda client, args: update_ad(client, args.get("ad_id", ""), args.get("name"), args.get("status")),
    "delete_ad": lambda client, args: delete_ad(client, args.get("ad_id", "")),
    "list_ads": lambda client, args: list_ads(client, args.get("ad_account_id"), args.get("adset_id"), args.get("status_filter")),
    "list_creatives": lambda client, args: list_creatives(client, args.get("ad_account_id", "")),
    "get_creative": lambda client, args: get_creative(client, args.get("creative_id", "")),
    "update_creative": lambda client, args: update_creative(client, args.get("creative_id", ""), args.get("name")),
    "delete_creative": lambda client, args: delete_creative(client, args.get("creative_id", "")),
    "preview_creative": lambda client, args: preview_creative(client, args.get("creative_id", ""), args.get("ad_format", "DESKTOP_FEED_STANDARD")),
    "upload_video": lambda client, args: upload_video(client, args.get("video_url", ""), args.get("ad_account_id"), args.get("title"), args.get("description")),
    "list_videos": lambda client, args: list_videos(client, args.get("ad_account_id", "")),
    # Insights
    "get_account_insights": lambda client, args: get_account_insights(client, args.get("ad_account_id", ""), int(args.get("days", 30)), args.get("breakdowns"), args.get("metrics"), args.get("date_preset")),
    "get_campaign_insights": lambda client, args: get_campaign_insights(client, args.get("campaign_id", ""), int(args.get("days", 30)), args.get("breakdowns"), args.get("metrics"), args.get("date_preset")),
    "get_adset_insights": lambda client, args: get_adset_insights(client, args.get("adset_id", ""), int(args.get("days", 30)), args.get("breakdowns"), args.get("metrics"), args.get("date_preset")),
    "get_ad_insights": lambda client, args: get_ad_insights(client, args.get("ad_id", ""), int(args.get("days", 30)), args.get("breakdowns"), args.get("metrics"), args.get("date_preset")),
    "create_async_report": lambda client, args: create_async_report(client, args.get("ad_account_id", ""), args.get("level", "campaign"), args.get("fields"), args.get("date_preset", "last_30d"), args.get("breakdowns")),
    "get_async_report_status": lambda client, args: get_async_report_status(client, args.get("report_run_id", "")),
    # Audiences
    "list_custom_audiences": lambda client, args: list_custom_audiences(client, args.get("ad_account_id", "")),
    "create_custom_audience": lambda client, args: create_custom_audience(client, args.get("ad_account_id", ""), args.get("name", ""), args.get("subtype", "CUSTOM"), args.get("description"), args.get("customer_file_source")),
    "create_lookalike_audience": lambda client, args: create_lookalike_audience(client, args.get("ad_account_id", ""), args.get("origin_audience_id", ""), args.get("country", ""), float(args.get("ratio", 0.01)), args.get("name")),
    "get_custom_audience": lambda client, args: get_custom_audience(client, args.get("audience_id", "")),
    "update_custom_audience": lambda client, args: update_custom_audience(client, args.get("audience_id", ""), args.get("name"), args.get("description")),
    "delete_custom_audience": lambda client, args: delete_custom_audience(client, args.get("audience_id", "")),
    "add_users_to_audience": lambda client, args: add_users_to_audience(client, args.get("audience_id", ""), args.get("emails", []), args.get("phones")),
    # Pixels
    "list_pixels": lambda client, args: list_pixels(client, args.get("ad_account_id", "")),
    "create_pixel": lambda client, args: create_pixel(client, args.get("ad_account_id", ""), args.get("name", "")),
    "get_pixel_stats": lambda client, args: get_pixel_stats(client, args.get("pixel_id", ""), args.get("start_time"), args.get("end_time"), args.get("aggregation", "day")),
    # Targeting
    "search_interests": lambda client, args: search_interests(client, args.get("q", ""), int(args.get("limit", 20))),
    "search_behaviors": lambda client, args: search_behaviors(client, args.get("q", ""), int(args.get("limit", 20))),
    "get_reach_estimate": lambda client, args: get_reach_estimate(client, args.get("ad_account_id", ""), args.get("targeting", {}), args.get("optimization_goal", "LINK_CLICKS")),
    "get_delivery_estimate": lambda client, args: get_delivery_estimate(client, args.get("ad_account_id", ""), args.get("targeting", {}), args.get("optimization_goal", "LINK_CLICKS"), args.get("bid_amount")),
    # Ad Rules
    "list_ad_rules": lambda client, args: list_ad_rules(client, args.get("ad_account_id", "")),
    "create_ad_rule": lambda client, args: create_ad_rule(client, args.get("ad_account_id", ""), args.get("name", ""), args.get("evaluation_spec", {}), args.get("execution_spec", {}), args.get("schedule_spec"), args.get("status", "ENABLED")),
    "update_ad_rule": lambda client, args: update_ad_rule(client, args.get("rule_id", ""), args.get("name"), args.get("status")),
    "delete_ad_rule": lambda client, args: delete_ad_rule(client, args.get("rule_id", "")),
    "execute_ad_rule": lambda client, args: execute_ad_rule(client, args.get("rule_id", "")),
}


class IntegrationFacebook:
    def __init__(
        self,
        fclient: "ckit_client.FlexusClient",
        rcx: "ckit_bot_exec.RobotContext",
        ad_account_id: str = "",
        pdoc_integration: Optional[Any] = None,
    ):
        self.client = FacebookAdsClient(fclient, rcx, ad_account_id)
        self.fclient = fclient
        self.rcx = rcx
        self.pdoc_integration = pdoc_integration

    async def _ensure_ad_account_id(self, toolcall: ckit_cloudtool.FCloudtoolCall) -> None:
        if self.client.ad_account_id or not self.pdoc_integration:
            return
        try:
            config = await self.pdoc_integration.pdoc_cat("/company/ad-ops-config", fcall_untrusted_key=toolcall.fcall_untrusted_key)
            ad_account_id = config.pdoc_content.get("facebook_ad_account_id", "")
            if ad_account_id:
                self.client.ad_account_id = ad_account_id
        except (AttributeError, KeyError, ValueError) as e:
            logger.debug("Could not load ad_account_id from pdoc", exc_info=e)

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
        # Auto-load ad_account_id from pdoc before operations that need it
        if op not in ["connect", "list_ad_accounts", "help"]:
            await self._ensure_ad_account_id(toolcall)
        if op == "connect":
            return await self._handle_connect()
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
            logger.error("Unexpected error in %s", op, exc_info=e)
            return f"ERROR: {str(e)}"

    async def _handle_connect(self) -> str:
        return """Click this link to connect your Facebook account in workspace settings.

After authorizing, return here and try your request again.

Requirements:
- Facebook Business Manager account
- Access to an Ad Account (starts with act_...)"""

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
