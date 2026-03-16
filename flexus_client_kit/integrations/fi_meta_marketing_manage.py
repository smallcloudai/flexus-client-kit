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
from flexus_client_kit.integrations.facebook.campaigns import (
    list_campaigns, create_campaign, update_campaign, duplicate_campaign,
    archive_campaign, bulk_update_campaigns, get_campaign, delete_campaign,
)
from flexus_client_kit.integrations.facebook.adsets import (
    list_adsets, create_adset, update_adset, validate_targeting,
    get_adset, delete_adset, list_adsets_for_account,
)
from flexus_client_kit.integrations.facebook.ads import (
    upload_image, create_creative, create_ad, preview_ad,
    list_ads, get_ad, update_ad, delete_ad,
    list_creatives, get_creative, update_creative, delete_creative, preview_creative,
    upload_video, list_videos,
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

logger = logging.getLogger("meta_marketing_manage")

# Use case: "Create & manage ads with Marketing API"
# Covers campaigns, ad sets, ads, creatives, audiences, pixels, targeting, rules.
PROVIDER_NAME = "meta_marketing_manage"

_HELP = """meta_marketing_manage: Create & manage ads with Meta Marketing API.
op=help | status | list_methods | call(args={method_id, ...})

Campaign management:
  list_campaigns(ad_account_id, status?)
  get_campaign(campaign_id)
  create_campaign(ad_account_id, name, objective, daily_budget?, lifetime_budget?, status?)
  update_campaign(campaign_id, name?, status?, daily_budget?, lifetime_budget?)
  delete_campaign(campaign_id)
  duplicate_campaign(campaign_id, new_name, ad_account_id?)
  archive_campaign(campaign_id)
  bulk_update_campaigns(campaigns)

Ad set management:
  list_adsets(campaign_id)
  list_adsets_for_account(ad_account_id, status_filter?)
  get_adset(adset_id)
  create_adset(ad_account_id, campaign_id, name, targeting, optimization_goal?, billing_event?, status?)
  update_adset(adset_id, name?, status?, daily_budget?, targeting?)
  delete_adset(adset_id)
  validate_targeting(targeting_spec, ad_account_id?)

Ad & creative management:
  list_ads(ad_account_id?, adset_id?, status_filter?)
  get_ad(ad_id)
  create_ad(ad_account_id, adset_id, creative_id, name?, status?)
  update_ad(ad_id, name?, status?)
  delete_ad(ad_id)
  preview_ad(ad_id, ad_format?)
  list_creatives(ad_account_id)
  get_creative(creative_id)
  create_creative(ad_account_id, name, page_id, message?, link?, image_hash?, video_id?, call_to_action_type?)
  update_creative(creative_id, name?)
  delete_creative(creative_id)
  preview_creative(creative_id, ad_format?)
  upload_image(image_path?, image_url?, ad_account_id?)
  upload_video(video_url, ad_account_id?, title?, description?)
  list_videos(ad_account_id)

Audiences:
  list_custom_audiences(ad_account_id)
  get_custom_audience(audience_id)
  create_custom_audience(ad_account_id, name, subtype?, description?, customer_file_source?)
  create_lookalike_audience(ad_account_id, origin_audience_id, country, ratio?, name?)
  update_custom_audience(audience_id, name?, description?)
  delete_custom_audience(audience_id)
  add_users_to_audience(audience_id, emails, phones?)

Pixels:
  list_pixels(ad_account_id)
  create_pixel(ad_account_id, name)
  get_pixel_stats(pixel_id, start_time?, end_time?, aggregation?)

Targeting research:
  search_interests(q, limit?)
  search_behaviors(q, limit?)
  get_reach_estimate(ad_account_id, targeting, optimization_goal?)
  get_delivery_estimate(ad_account_id, targeting, optimization_goal?, bid_amount?)

Automation rules:
  list_ad_rules(ad_account_id)
  create_ad_rule(ad_account_id, name, evaluation_spec, execution_spec, schedule_spec?, status?)
  update_ad_rule(rule_id, name?, status?)
  delete_ad_rule(rule_id)
  execute_ad_rule(rule_id)
"""

# Maps op string -> lambda(client, args) for the generic dispatch table.
_HANDLERS: Dict[str, Any] = {
    "list_campaigns": lambda c, a: list_campaigns(c, a.get("ad_account_id"), a.get("status")),
    "get_campaign": lambda c, a: get_campaign(c, a.get("campaign_id", "")),
    "create_campaign": lambda c, a: create_campaign(
        c, a.get("ad_account_id", ""), a.get("name", ""),
        a.get("objective", "OUTCOME_AWARENESS"),
        a.get("daily_budget"), a.get("lifetime_budget"),
        a.get("status", "PAUSED"),
    ),
    "update_campaign": lambda c, a: update_campaign(
        c, a.get("campaign_id", ""), a.get("name"), a.get("status"),
        a.get("daily_budget"), a.get("lifetime_budget"),
    ),
    "delete_campaign": lambda c, a: delete_campaign(c, a.get("campaign_id", "")),
    "duplicate_campaign": lambda c, a: duplicate_campaign(c, a.get("campaign_id", ""), a.get("new_name", ""), a.get("ad_account_id")),
    "archive_campaign": lambda c, a: archive_campaign(c, a.get("campaign_id", "")),
    "bulk_update_campaigns": lambda c, a: bulk_update_campaigns(c, a.get("campaigns", [])),
    "list_adsets": lambda c, a: list_adsets(c, a.get("campaign_id", "")),
    "list_adsets_for_account": lambda c, a: list_adsets_for_account(c, a.get("ad_account_id", ""), a.get("status_filter")),
    "get_adset": lambda c, a: get_adset(c, a.get("adset_id", "")),
    "create_adset": lambda c, a: create_adset(
        c, a.get("ad_account_id", ""), a.get("campaign_id", ""),
        a.get("name", ""), a.get("targeting", {}),
        a.get("optimization_goal"), a.get("billing_event"),
        a.get("daily_budget"), a.get("lifetime_budget"),
        a.get("status", "PAUSED"),
    ),
    "update_adset": lambda c, a: update_adset(c, a.get("adset_id", ""), a.get("name"), a.get("status"), a.get("daily_budget"), a.get("targeting")),
    "delete_adset": lambda c, a: delete_adset(c, a.get("adset_id", "")),
    "validate_targeting": lambda c, a: validate_targeting(c, a.get("targeting_spec", a.get("targeting", {})), a.get("ad_account_id")),
    "list_ads": lambda c, a: list_ads(c, a.get("ad_account_id"), a.get("adset_id"), a.get("status_filter")),
    "get_ad": lambda c, a: get_ad(c, a.get("ad_id", "")),
    "create_ad": lambda c, a: create_ad(c, a.get("ad_account_id", ""), a.get("adset_id", ""), a.get("creative_id", ""), a.get("name"), a.get("status", "PAUSED")),
    "update_ad": lambda c, a: update_ad(c, a.get("ad_id", ""), a.get("name"), a.get("status")),
    "delete_ad": lambda c, a: delete_ad(c, a.get("ad_id", "")),
    "preview_ad": lambda c, a: preview_ad(c, a.get("ad_id", ""), a.get("ad_format", "DESKTOP_FEED_STANDARD")),
    "list_creatives": lambda c, a: list_creatives(c, a.get("ad_account_id", "")),
    "get_creative": lambda c, a: get_creative(c, a.get("creative_id", "")),
    "create_creative": lambda c, a: create_creative(
        c, a.get("ad_account_id", ""), a.get("name", ""),
        a.get("page_id", ""), a.get("message"), a.get("link"),
        a.get("image_hash"), a.get("video_id"), a.get("call_to_action_type"),
    ),
    "update_creative": lambda c, a: update_creative(c, a.get("creative_id", ""), a.get("name")),
    "delete_creative": lambda c, a: delete_creative(c, a.get("creative_id", "")),
    "preview_creative": lambda c, a: preview_creative(c, a.get("creative_id", ""), a.get("ad_format", "DESKTOP_FEED_STANDARD")),
    "upload_image": lambda c, a: upload_image(c, a.get("image_path"), a.get("image_url"), a.get("ad_account_id")),
    "upload_video": lambda c, a: upload_video(c, a.get("video_url", ""), a.get("ad_account_id"), a.get("title"), a.get("description")),
    "list_videos": lambda c, a: list_videos(c, a.get("ad_account_id", "")),
    "list_custom_audiences": lambda c, a: list_custom_audiences(c, a.get("ad_account_id", "")),
    "get_custom_audience": lambda c, a: get_custom_audience(c, a.get("audience_id", "")),
    "create_custom_audience": lambda c, a: create_custom_audience(c, a.get("ad_account_id", ""), a.get("name", ""), a.get("subtype", "CUSTOM"), a.get("description"), a.get("customer_file_source")),
    "create_lookalike_audience": lambda c, a: create_lookalike_audience(c, a.get("ad_account_id", ""), a.get("origin_audience_id", ""), a.get("country", ""), float(a.get("ratio", 0.01)), a.get("name")),
    "update_custom_audience": lambda c, a: update_custom_audience(c, a.get("audience_id", ""), a.get("name"), a.get("description")),
    "delete_custom_audience": lambda c, a: delete_custom_audience(c, a.get("audience_id", "")),
    "add_users_to_audience": lambda c, a: add_users_to_audience(c, a.get("audience_id", ""), a.get("emails", []), a.get("phones")),
    "list_pixels": lambda c, a: list_pixels(c, a.get("ad_account_id", "")),
    "create_pixel": lambda c, a: create_pixel(c, a.get("ad_account_id", ""), a.get("name", "")),
    "get_pixel_stats": lambda c, a: get_pixel_stats(c, a.get("pixel_id", ""), a.get("start_time"), a.get("end_time"), a.get("aggregation", "day")),
    "search_interests": lambda c, a: search_interests(c, a.get("q", ""), int(a.get("limit", 20))),
    "search_behaviors": lambda c, a: search_behaviors(c, a.get("q", ""), int(a.get("limit", 20))),
    "get_reach_estimate": lambda c, a: get_reach_estimate(c, a.get("ad_account_id", ""), a.get("targeting", {}), a.get("optimization_goal", "LINK_CLICKS")),
    "get_delivery_estimate": lambda c, a: get_delivery_estimate(c, a.get("ad_account_id", ""), a.get("targeting", {}), a.get("optimization_goal", "LINK_CLICKS"), a.get("bid_amount")),
    "list_ad_rules": lambda c, a: list_ad_rules(c, a.get("ad_account_id", "")),
    "create_ad_rule": lambda c, a: create_ad_rule(c, a.get("ad_account_id", ""), a.get("name", ""), a.get("evaluation_spec", {}), a.get("execution_spec", {}), a.get("schedule_spec"), a.get("status", "ENABLED")),
    "update_ad_rule": lambda c, a: update_ad_rule(c, a.get("rule_id", ""), a.get("name"), a.get("status")),
    "delete_ad_rule": lambda c, a: delete_ad_rule(c, a.get("rule_id", "")),
    "execute_ad_rule": lambda c, a: execute_ad_rule(c, a.get("rule_id", "")),
}


class IntegrationMetaMarketingManage:
    # Wraps FacebookAdsClient and delegates all manage operations through _HANDLERS.
    # Uses OAuth token from rcx (Flexus stores the Meta access token per persona).
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
            logger.info("meta_marketing_manage api error: %s", e)
            return e.format_for_user()
        except FacebookValidationError as e:
            return f"Error: {e.message}"
        except Exception as e:
            logger.error("Unexpected error in meta_marketing_manage op=%s", (model_produced_args or {}).get("op"), exc_info=e)
            return f"Error: {e}"

    async def _status(self) -> str:
        try:
            auth_error = await self.client.ensure_auth()
            if auth_error:
                return auth_error
            return "meta_marketing_manage: connected. Use op=help to see available operations."
        except (FacebookAuthError, FacebookAPIError, FacebookValidationError) as e:
            return e.message
        except Exception as e:
            logger.error("Unexpected error in meta_marketing_manage status", exc_info=e)
            return f"Error: {e}"
